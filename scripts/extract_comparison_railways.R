# scripts/extract_comparison_railways.R
# Extracts rail networks and transit hubs for comparison cities from Natural Earth North America Railroads

suppressPackageStartupMessages({
  library(sf)
  library(jsonlite)
})

if (!file.exists("data/comparison_cities.json")) {
  stop("data/comparison_cities.json not found!")
}

comp_cities <- fromJSON("data/comparison_cities.json")
rr_na_path <- "data/raw/ne_10m_railroads_north_america.geojson"

if (!file.exists(rr_na_path)) {
  cat("Downloading Natural Earth North America railroads...\n")
  url <- "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_railroads_north_america.geojson"
  download.file(url, rr_na_path, quiet = TRUE)
}

rr_na <- st_read(rr_na_path, quiet = TRUE)
existing_rails <- if (file.exists("data/processed/city_rails.rds")) readRDS("data/processed/city_rails.rds") else list()
rail_summary <- if (file.exists("data/processed/city_rail_summary.json")) fromJSON("data/processed/city_rail_summary.json") else list()

stations_data <- list(
  chicago = data.frame(
    name = c("Chicago Union Station", "Ogilvie Transportation Center", "Millennium Station", "LaSalle Street Station", "O'Hare Transit Center", "Midway Airport Station"),
    name_en = c("Chicago Union Station", "Ogilvie Transportation Center", "Millennium Station", "LaSalle Street Station", "O'Hare Transit Center", "Midway Airport Station"),
    lon = c(-87.6403, -87.6403, -87.6247, -87.6322, -87.9073, -87.7371),
    lat = c(41.8787, 41.8824, 41.8841, 41.8756, 41.9742, 41.7858)
  ),
  milwaukee = data.frame(
    name = c("Milwaukee Intermodal Station", "Milwaukee Airport Rail Station"),
    name_en = c("Milwaukee Intermodal Station", "Milwaukee Airport Rail Station"),
    lon = c(-87.9171, -87.9158),
    lat = c(43.0339, 42.9405)
  ),
  charlotte = data.frame(
    name = c("Charlotte Amtrak Station", "Charlotte Gateway Station", "CTC / Arena Station", "I-485 / South Blvd", "UNC Charlotte Station"),
    name_en = c("Charlotte Amtrak Station", "Charlotte Gateway Station", "CTC / Arena Station", "I-485 / South Blvd", "UNC Charlotte Station"),
    lon = c(-80.8262, -80.8492, -80.8422, -80.8804, -80.7335),
    lat = c(35.2442, 35.2285, 35.2253, 35.1098, 35.3113)
  )
)

corridors_data <- list(
  chicago = c("Metra Commuter Rail System", "Amtrak Midwest Hub Corridors", "BNSF Railway Mainline", "Union Pacific West/North Lines", "Norfolk Southern Chicago Terminal"),
  milwaukee = c("Amtrak Hiawatha Corridor", "CPKC Mainline Corridor", "Union Pacific Lakeshore Line"),
  charlotte = c("CATS Lynx Blue Line Light Rail", "Norfolk Southern Piedmont Mainline", "CSX Transportation Charlotte Corridor")
)

dir.create("data/processed/city_rails", showWarnings = FALSE, recursive = TRUE)

for (i in seq_len(nrow(comp_cities))) {
  c_id <- comp_cities$id[i]
  c_name <- comp_cities$name_en[i]
  bbox <- comp_cities$bbox[[i]]
  bb_sf <- st_as_sfc(st_bbox(c(xmin=bbox[1], ymin=bbox[2], xmax=bbox[3], ymax=bbox[4]), crs = 4326))
  
  inter <- suppressWarnings(st_intersection(rr_na, bb_sf))
  
  if (nrow(inter) > 0) {
    inter$id <- paste0("ne_rr_", seq_len(nrow(inter)))
    inter$name <- paste(c_name, "Rail Trunk", seq_len(nrow(inter)))
    inter$name_en <- inter$name
    inter$is_hsr <- FALSE
    inter$railway_type <- "Conventional Rail / Mainline Trunk"
    inter$layer <- NA_character_
    inter$city_id <- c_id
    rails_clean <- inter[, c("id", "name", "name_en", "is_hsr", "railway_type", "layer", "city_id", "geometry")]
  } else {
    rails_clean <- NULL
  }
  
  st_df <- stations_data[[c_id]]
  if (!is.null(st_df)) {
    stations_sf <- st_as_sf(st_df, coords = c("lon", "lat"), crs = 4326)
    stations_sf$id <- paste0("st_", seq_len(nrow(stations_sf)))
    stations_sf$is_hsr <- FALSE
    stations_sf$railway_type <- "Passenger Hub"
    stations_sf$layer <- NA_character_
    stations_sf$city_id <- c_id
    stations_clean <- stations_sf[, c("id", "name", "name_en", "is_hsr", "railway_type", "layer", "city_id", "geometry")]
  } else {
    stations_clean <- NULL
  }
  
  existing_rails[[c_id]] <- list(rails = rails_clean, stations = stations_clean)
  
  if (!is.null(rails_clean)) {
    st_write(rails_clean, sprintf("data/processed/city_rails/%s.geojson", c_id), delete_dsn = TRUE, quiet = TRUE)
  }
  
  rail_summary[[c_id]] <- list(
    city_id = c_id,
    total_rail_segments = if (!is.null(rails_clean)) nrow(rails_clean) else 0,
    hsr_segments = 0,
    conventional_segments = if (!is.null(rails_clean)) nrow(rails_clean) else 0,
    station_count = if (!is.null(stations_clean)) nrow(stations_clean) else 0,
    major_corridors = corridors_data[[c_id]],
    key_stations = if (!is.null(st_df)) st_df$name else list()
  )
  cat(sprintf("[Comparison Rails] %s: %d rail segments, %d stations extracted.\n", 
              c_name, if (!is.null(rails_clean)) nrow(rails_clean) else 0, if (!is.null(stations_clean)) nrow(stations_clean) else 0))
}

saveRDS(existing_rails, "data/processed/city_rails.rds")
write_json(rail_summary, "data/processed/city_rail_summary.json", pretty = TRUE, auto_unbox = TRUE)
cat("Comparison railways extracted and saved successfully.\n")
