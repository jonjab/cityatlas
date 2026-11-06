# scripts/process_chinese_rail_subway.R
# Clips authentic Chinese 12306 national rail network and incorporates AMap subway systems
# for each atlas city, updating data/processed/city_rails.rds and data/processed/city_rail_summary.json

suppressPackageStartupMessages({
  library(sf)
  library(terra)
  library(jsonlite)
  library(dplyr)
})

cat("Processing Chinese-sourced railway & subway layers...\n")

# Load cities metadata
cities_df <- fromJSON("data/processed/city_growth_stats.json")
subway_summary <- if (file.exists("data/processed/city_subway_summary.json")) {
  fromJSON("data/processed/city_subway_summary.json")
} else {
  list()
}

# 1. Read National 12306 Railway GeoJSON
raw_rail_lines <- st_read("data/raw/china_railway_12306_lines.geojson", quiet = TRUE)
raw_stations <- st_read("data/raw/china_railway_12306_stations.geojson", quiet = TRUE)

# Read metadata lookup
meta_lines <- fromJSON("data/raw/china_railway_12306_line_metadata.json")
meta_lookup <- setNames(meta_lines$speed, meta_lines$name)
type_lookup <- setNames(meta_lines$type, meta_lines$name)

# Ensure CRS is EPSG:4326
st_crs(raw_rail_lines) <- 4326
st_crs(raw_stations) <- 4326

# Enhance lines attributes
raw_rail_lines$speed <- as.integer(raw_rail_lines$s)
raw_rail_lines$is_hsr <- raw_rail_lines$speed >= 200
raw_rail_lines$name <- raw_rail_lines$n
raw_rail_lines$railway_type <- ifelse(raw_rail_lines$is_hsr, "High-Speed Rail (高铁/动车)", "Conventional Rail (普速干线)")

# Save cleaned national railway RDS
saveRDS(raw_rail_lines, "data/processed/china_rail_network_12306.rds")
cat(sprintf("National 12306 Rail Network saved: %d lines.\n", nrow(raw_rail_lines)))

# Prepare city structures
city_rails <- list()
city_rail_summary <- list()

for (i in 1:nrow(cities_df)) {
  c_info <- cities_df[i, ]
  c_id <- c_info$id
  c_name <- c_info$name_en
  c_zh <- c_info$name_zh
  
  # Determine spatial extent from WSF raster
  tif_path <- sprintf("data/processed/wsf/%s.tif", c_id)
  if (!file.exists(tif_path)) next
  
  r <- rast(tif_path)
  bbox_poly <- st_as_sfc(st_bbox(c(
    xmin = xmin(r), xmax = xmax(r),
    ymin = ymin(r), ymax = ymax(r)
  ), crs = st_crs(4326)))
  
  # Clip national rail lines to city extent
  lines_intersect <- suppressWarnings(st_intersection(raw_rail_lines, bbox_poly))
  lines_clean <- if (nrow(lines_intersect) > 0) {
    # Keep LineString / MultiLineString
    lines_intersect <- lines_intersect[st_geometry_type(lines_intersect) %in% c("LINESTRING", "MULTILINESTRING"), ]
    if (nrow(lines_intersect) > 0) {
      data.frame(
        id = sprintf("cr_%s_%d", c_id, 1:nrow(lines_intersect)),
        name = lines_intersect$name,
        name_en = NA_character_,
        speed = lines_intersect$speed,
        is_hsr = lines_intersect$is_hsr,
        railway_type = lines_intersect$railway_type,
        layer = "12306 National Rail",
        city_id = c_id,
        geometry = st_geometry(lines_intersect)
      ) %>% st_as_sf()
    } else NULL
  } else NULL
  
  # Clip 12306 passenger stations to city extent
  stations_intersect <- suppressWarnings(st_intersection(raw_stations, bbox_poly))
  stations_clean <- if (nrow(stations_intersect) > 0) {
    data.frame(
      id = sprintf("cr_st_%s_%d", c_id, 1:nrow(stations_intersect)),
      name = stations_intersect$name,
      name_en = stations_intersect$pinyin,
      city = stations_intersect$city,
      telecode = stations_intersect$telecode,
      tier = stations_intersect$tier,
      rank = stations_intersect$rank,
      railway_type = "Passenger Station (12306)",
      city_id = c_id,
      geometry = st_geometry(stations_intersect)
    ) %>% st_as_sf()
  } else NULL
  
  # Check if city has a subway system from AMap
  subway_path <- sprintf("data/processed/city_subways/%s_subway.geojson", c_id)
  subway_lines_sf <- NULL
  subway_stations_sf <- NULL
  sub_info <- subway_summary[[c_id]]
  has_subway <- !is.null(sub_info) && file.exists(subway_path)
  
  if (has_subway) {
    sub_raw <- suppressWarnings(st_read(subway_path, quiet = TRUE))
    st_crs(sub_raw) <- 4326
    sub_lines <- sub_raw[st_geometry_type(sub_raw) %in% c("LINESTRING", "MULTILINESTRING"), ]
    sub_stations <- sub_raw[st_geometry_type(sub_raw) == "POINT", ]
    
    # Clip to city extent if needed
    if (nrow(sub_lines) > 0) {
      subway_lines_sf <- suppressWarnings(st_intersection(sub_lines, bbox_poly))
      if (nrow(subway_lines_sf) > 0) {
        subway_lines_sf <- subway_lines_sf[st_geometry_type(subway_lines_sf) %in% c("LINESTRING", "MULTILINESTRING"), ]
      } else {
        subway_lines_sf <- NULL
      }
    }
    if (nrow(sub_stations) > 0) {
      subway_stations_sf <- suppressWarnings(st_intersection(sub_stations, bbox_poly))
      if (nrow(subway_stations_sf) == 0) subway_stations_sf <- NULL
    }
  }
  
  # Store in city_rails list
  city_rails[[c_id]] <- list(
    rails = lines_clean,
    stations = stations_clean,
    subway_lines = subway_lines_sf,
    subway_stations = subway_stations_sf,
    has_subway = has_subway
  )
  
  # Compute summary metrics
  hsr_count <- if (!is.null(lines_clean)) sum(lines_clean$is_hsr == TRUE) else 0
  conv_count <- if (!is.null(lines_clean)) sum(lines_clean$is_hsr == FALSE) else 0
  st_count <- if (!is.null(stations_clean)) nrow(stations_clean) else 0
  
  major_corridors <- if (!is.null(lines_clean) && nrow(lines_clean) > 0) {
    unique(na.omit(lines_clean$name))
  } else character(0)
  
  key_stations <- if (!is.null(stations_clean) && nrow(stations_clean) > 0) {
    # Order by rank
    stations_ordered <- stations_clean %>% arrange(desc(rank))
    head(unique(stations_ordered$name), 10)
  } else character(0)
  
  city_rail_summary[[c_id]] <- list(
    city_id = c_id,
    total_rail_segments = if (!is.null(lines_clean)) nrow(lines_clean) else 0,
    hsr_segments = hsr_count,
    conventional_segments = conv_count,
    station_count = st_count,
    major_corridors = major_corridors,
    key_stations = key_stations,
    has_subway = has_subway,
    subway_lines_count = if (has_subway) sub_info$lines_count else 0,
    subway_station_count = if (has_subway) sub_info$total_stations else 0,
    subway_line_names = if (has_subway) sub_info$line_names else character(0)
  )
  
  sub_str <- if (has_subway) sprintf(" + %d subway lines (%d stations)", sub_info$lines_count, sub_info$total_stations) else ""
  cat(sprintf("[%02d/47] %s (%s): %d 12306 rail lines, %d stations%s\n",
              i, c_name, c_zh, length(major_corridors), st_count, sub_str))
}

# Preserve US comparison cities in city_rails if they exist
if (file.exists("data/processed/comparison_growth_stats.json")) {
  comp_df <- fromJSON("data/processed/comparison_growth_stats.json")
  old_rails <- if (file.exists("data/processed/city_rails.rds")) readRDS("data/processed/city_rails.rds") else list()
  for (cid in comp_df$id) {
    if (!is.null(old_rails[[cid]])) {
      city_rails[[cid]] <- old_rails[[cid]]
      city_rail_summary[[cid]] <- list(
        city_id = cid,
        total_rail_segments = if (!is.null(old_rails[[cid]]$rails)) nrow(old_rails[[cid]]$rails) else 0,
        hsr_segments = 0,
        conventional_segments = if (!is.null(old_rails[[cid]]$rails)) nrow(old_rails[[cid]]$rails) else 0,
        station_count = if (!is.null(old_rails[[cid]]$stations)) nrow(old_rails[[cid]]$stations) else 0,
        major_corridors = character(0),
        key_stations = character(0),
        has_subway = FALSE,
        subway_lines_count = 0,
        subway_station_count = 0
      )
    }
  }
}

saveRDS(city_rails, "data/processed/city_rails.rds")
write_json(city_rail_summary, "data/processed/city_rail_summary.json", pretty = TRUE, auto_unbox = TRUE)

cat("Successfully generated authentic Chinese-sourced city_rails.rds & city_rail_summary.json!\n")
