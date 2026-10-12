# R/03_compute_growth_metrics.R
# Calculates exact spatial expansion metrics for all 47 cities across 1985-2015.

suppressPackageStartupMessages({
  library(terra)
  library(jsonlite)
  library(dplyr)
  library(readr)
})

cities <- fromJSON("data/cities.json")
cat(sprintf("Calculating growth metrics for %d cities...\n", nrow(cities)))

results <- list()

for (i in seq_len(nrow(cities))) {
  c_id <- cities$id[i]
  c_name <- cities$name_en[i]
  c_zh <- cities$name_zh[i]
  tif_path <- sprintf("data/processed/wsf/%s.tif", c_id)
  
  if (!file.exists(tif_path)) {
    warning(sprintf("Missing raster for %s", c_id))
    next
  }
  
  r <- rast(tif_path)
  cs <- cellSize(r, unit = "km")
  
  v <- values(r, mat = FALSE)
  a <- values(cs, mat = FALSE)
  
  valid <- !is.na(v) & v >= 1985
  
  # Calculate cumulative area at each milestone
  a_1985 <- round(sum(a[valid & v <= 1985]), 2)
  a_1990 <- round(sum(a[valid & v <= 1990]), 2)
  a_1995 <- round(sum(a[valid & v <= 1995]), 2)
  a_2000 <- round(sum(a[valid & v <= 2000]), 2)
  a_2005 <- round(sum(a[valid & v <= 2005]), 2)
  a_2010 <- round(sum(a[valid & v <= 2010]), 2)
  a_2015 <- round(sum(a[valid & v <= 2015]), 2)
  
  net_gain <- round(a_2015 - a_1985, 2)
  mult <- round(a_2015 / max(a_1985, 0.1), 2)
  cagr <- round(((a_2015 / max(a_1985, 0.1))^(1/30) - 1) * 100, 2)
  
  results[[i]] <- tibble(
    id = c_id,
    name_en = c_name,
    name_zh = c_zh,
    pinyin = cities$pinyin[i],
    province_en = cities$province_en[i],
    province_zh = cities$province_zh[i],
    region = cities$region[i],
    lat = cities$lat[i],
    lon = cities$lon[i],
    area_1985 = a_1985,
    area_1990 = a_1990,
    area_1995 = a_1995,
    area_2000 = a_2000,
    area_2005 = a_2005,
    area_2010 = a_2010,
    area_2015 = a_2015,
    net_gain_km2 = net_gain,
    growth_multiple = mult,
    cagr_pct = cagr
  )
}

df_growth <- bind_rows(results) %>%
  arrange(desc(growth_multiple)) %>%
  mutate(rank_multiplier = row_number())

write_csv(df_growth, "data/processed/city_growth_stats.csv")
write_json(df_growth, "data/processed/city_growth_stats.json", pretty = TRUE)

cat("Successfully calculated and saved city growth statistics!\n")
cat("\nTop 10 Cities by 30-Year Urban Growth Multiple:\n")
print(df_growth %>% select(name_en, name_zh, province_en, area_1985, area_2015, growth_multiple) %>% head(10))
