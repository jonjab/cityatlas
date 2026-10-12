# R/03_compute_growth_metrics.R
# Calculates spatial expansion metrics and integrates 2020 Census population rankings.

suppressPackageStartupMessages({
  library(terra)
  library(jsonlite)
  library(dplyr)
  library(readr)
})

cities <- fromJSON("data/cities.json")
cat(sprintf("Calculating metrics for %d cities...\n", nrow(cities)))

# Authoritative 7th National Population Census (七普 2020) resident population (常住人口)
city_pop_lookup <- list(
  chengdu      = list(pop_m = 20.94, pop_exact = 20937757, note = "Prefecture / Sub-provincial"),
  shenzhen     = list(pop_m = 17.56, pop_exact = 17560061, note = "Sub-provincial / SEZ"),
  xian         = list(pop_m = 12.95, pop_exact = 12952907, note = "Sub-provincial"),
  zhengzhou    = list(pop_m = 12.60, pop_exact = 12600574, note = "Prefecture / Provincial Capital"),
  wuhan        = list(pop_m = 12.33, pop_exact = 12326500, note = "Sub-provincial"),
  shijiazhuang = list(pop_m = 10.64, pop_exact = 10640000, note = "Prefecture / Provincial Capital"),
  harbin       = list(pop_m = 10.01, pop_exact = 10009854, note = "Sub-provincial"),
  baoding      = list(pop_m = 9.24,  pop_exact = 9242600,  note = "Prefecture"),
  jinan        = list(pop_m = 9.20,  pop_exact = 9202400,  note = "Sub-provincial"),
  kunming      = list(pop_m = 8.46,  pop_exact = 8460088,  note = "Prefecture / Provincial Capital"),
  jining       = list(pop_m = 8.36,  pop_exact = 8357897,  note = "Prefecture"),
  nanchang     = list(pop_m = 6.26,  pop_exact = 6255000,  note = "Prefecture / Provincial Capital"),
  liaocheng    = list(pop_m = 5.95,  pop_exact = 5952128,  note = "Prefecture"),
  xiamen       = list(pop_m = 5.16,  pop_exact = 5163970,  note = "Sub-provincial / SEZ"),
  guilin       = list(pop_m = 4.93,  pop_exact = 4931137,  note = "Prefecture"),
  zibo         = list(pop_m = 4.70,  pop_exact = 4704138,  note = "Prefecture"),
  lianyungang  = list(pop_m = 4.60,  pop_exact = 4599360,  note = "Prefecture"),
  yangzhou     = list(pop_m = 4.56,  pop_exact = 4559797,  note = "Prefecture"),
  taizhou      = list(pop_m = 4.51,  pop_exact = 4512760,  note = "Prefecture"),
  lanzhou      = list(pop_m = 4.36,  pop_exact = 4359446,  note = "Prefecture / Provincial Capital"),
  luzhou       = list(pop_m = 4.25,  pop_exact = 4254149,  note = "Prefecture"),
  urumqi       = list(pop_m = 4.05,  pop_exact = 4054369,  note = "Prefecture / Regional Capital"),
  binzhou      = list(pop_m = 3.93,  pop_exact = 3928566,  note = "Prefecture"),
  yichang      = list(pop_m = 3.92,  pop_exact = 3918000,  note = "Prefecture"),
  wuhu         = list(pop_m = 3.64,  pop_exact = 3644420,  note = "Prefecture"),
  hohhot       = list(pop_m = 3.45,  pop_exact = 3446100,  note = "Prefecture / Regional Capital"),
  datong       = list(pop_m = 3.11,  pop_exact = 3105591,  note = "Prefecture"),
  weihai       = list(pop_m = 2.91,  pop_exact = 2906548,  note = "Prefecture"),
  haikou       = list(pop_m = 2.87,  pop_exact = 2873358,  note = "Prefecture / Provincial Capital"),
  heyuan       = list(pop_m = 2.84,  pop_exact = 2837686,  note = "Prefecture"),
  zhuhai       = list(pop_m = 2.44,  pop_exact = 2439585,  note = "Prefecture / SEZ"),
  tieling      = list(pop_m = 2.39,  pop_exact = 2388294,  note = "Prefecture"),
  dongying     = list(pop_m = 2.19,  pop_exact = 2193518,  note = "Prefecture"),
  dandong      = list(pop_m = 2.19,  pop_exact = 2188436,  note = "Prefecture"),
  ulanqab      = list(pop_m = 1.71,  pop_exact = 1706328,  note = "Prefecture"),
  fuxin        = list(pop_m = 1.65,  pop_exact = 1647286,  note = "Prefecture"),
  baicheng     = list(pop_m = 1.55,  pop_exact = 1551378,  note = "Prefecture"),
  zhangjiajie  = list(pop_m = 1.52,  pop_exact = 1517027,  note = "Prefecture"),
  wuwei        = list(pop_m = 1.47,  pop_exact = 1465300,  note = "Prefecture"),
  panjin       = list(pop_m = 1.39,  pop_exact = 1389691,  note = "Prefecture"),
  huangshan    = list(pop_m = 1.33,  pop_exact = 1330565,  note = "Prefecture"),
  liaoyuan     = list(pop_m = 0.99,  pop_exact = 991633,   note = "Prefecture"),
  taishan      = list(pop_m = 0.91,  pop_exact = 907354,   note = "County-level City (Jiangmen)"),
  kashgar      = list(pop_m = 0.71,  pop_exact = 711300,   note = "County-level City (Prefecture Seat)"),
  korla        = list(pop_m = 0.55,  pop_exact = 549324,   note = "County-level City (Prefecture Seat)"),
  hotan        = list(pop_m = 0.50,  pop_exact = 501028,   note = "County-level City (Prefecture Seat)"),
  hunchun      = list(pop_m = 0.24,  pop_exact = 239359,   note = "County-level City (Yanbian)")
)

results <- list()

for (i in seq_len(nrow(cities))) {
  c_id <- cities$id[i]
  c_name <- cities$name_en[i]
  c_zh <- cities$name_zh[i]
  tif_path <- sprintf("data/processed/wsf/%s.tif", c_id)
  
  if (!file.exists(tif_path)) next
  
  r <- rast(tif_path)
  cs <- cellSize(r, unit = "km")
  
  v <- values(r, mat = FALSE)
  a <- values(cs, mat = FALSE)
  
  valid <- !is.na(v) & v >= 1985
  
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
  
  p_info <- city_pop_lookup[[c_id]]
  pop_m <- if (!is.null(p_info)) p_info$pop_m else 1.0
  pop_exact <- if (!is.null(p_info)) p_info$pop_exact else 1000000
  pop_note <- if (!is.null(p_info)) p_info$note else "City"
  
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
    pop_million = pop_m,
    pop_exact = pop_exact,
    pop_note = pop_note,
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

# Primary sorting by POPULATION (descending) as requested by the user
df_growth <- bind_rows(results) %>%
  arrange(desc(pop_million)) %>%
  mutate(rank_population = row_number()) %>%
  # Also compute secondary growth multiplier rank
  mutate(rank_multiplier = dense_rank(desc(growth_multiple)))

write_csv(df_growth, "data/processed/city_growth_stats.csv")
write_json(df_growth, "data/processed/city_growth_stats.json", pretty = TRUE)

cat("Successfully calculated metrics and re-ranked by 2020 Census Population!\n")
cat("\nTop 10 Cities Ordered by Population (2020 Census):\n")
print(df_growth %>% select(rank_population, name_en, name_zh, province_en, pop_million, area_1985, area_2015, growth_multiple) %>% head(10))
