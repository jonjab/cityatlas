# scripts/generate_comparison_maps.R
# Generates publication-grade maps and analytical charts for US comparison cities:
# Chicago, Milwaukee, Charlotte, and cross-national benchmark comparisons.

suppressPackageStartupMessages({
  library(terra)
  library(sf)
  library(ggplot2)
  library(tidyterra)
  library(patchwork)
  library(ragg)
  library(dplyr)
  library(tidyr)
  library(jsonlite)
})

dir.create("output/maps", recursive = TRUE, showWarnings = FALSE)
dir.create("output/plots", recursive = TRUE, showWarnings = FALSE)

comp_stats <- fromJSON("data/processed/comparison_growth_stats.json")
china_stats <- fromJSON("data/processed/city_growth_stats.json")
city_rails <- if (file.exists("data/processed/city_rails.rds")) readRDS("data/processed/city_rails.rds") else list()

# Load US Admin Boundaries
states_path <- "data/raw/ne_110m_admin_1_states_provinces.geojson"
countries_path <- "data/raw/ne_110m_admin_0_countries.geojson"
us_states <- if (file.exists(states_path)) {
  s <- st_read(states_path, quiet = TRUE)
  s[s$sov_a3 %in% c("USA", "US1"), ]
} else NULL

us_country <- if (file.exists(countries_path)) {
  c_sf <- st_read(countries_path, quiet = TRUE)
  c_sf[c_sf$ADM0_A3 %in% c("USA"), ]
} else NULL

rcl_hero <- matrix(c(
  -Inf, 1984, NA,
  1984.5, 1985.5, 1,
  1985.5, 1995.5, 2,
  1995.5, 2005.5, 3,
  2005.5, 2015.5, 4
), ncol = 3, byrow = TRUE)

epoch_cols <- c(
  "Pre-1985"   = "#F59E0B", # Amber gold
  "1986–1995" = "#EF4444", # Crimson coral
  "1996–2005" = "#06B6D4", # Electric cyan
  "2006–2015" = "#10B981"  # Emerald green
)

render_comparison_city <- function(i) {
  c_info <- comp_stats[i, ]
  c_id <- c_info$id
  tif_path <- sprintf("data/processed/wsf/%s.tif", c_id)
  
  if (!file.exists(tif_path)) return(FALSE)
  
  hero_out <- sprintf("output/maps/%s_hero.png", c_id)
  rail_out <- sprintf("output/maps/%s_rail.png", c_id)
  sm_out   <- sprintf("output/maps/%s_small_multiples.png", c_id)
  ctx_out  <- sprintf("output/maps/%s_context.png", c_id)
  traj_out <- sprintf("output/plots/%s_trajectory.png", c_id)
  
  cat(sprintf("Rendering visual suite for %s (%s)...\n", c_info$name_en, c_info$name_zh))
  
  r <- rast(tif_path)
  
  c_rail_data <- city_rails[[c_id]]
  rails_layer <- if (!is.null(c_rail_data)) c_rail_data$rails else NULL
  stations_layer <- if (!is.null(c_rail_data)) c_rail_data$stations else NULL
  
  # 1. Hero Map (Expansion Rings + Rail Overlay)
  r_epoch <- classify(r, rcl_hero)
  r_epoch <- as.factor(r_epoch)
  levels(r_epoch) <- data.frame(ID = 1:4, epoch = c("Pre-1985", "1986–1995", "1996–2005", "2006–2015"))
  
  p_hero <- ggplot() +
    geom_spatraster(data = r_epoch, maxcell = 6e5) +
    scale_fill_manual(values = epoch_cols, na.translate = FALSE, name = "Expansion Epoch")
  
  if (!is.null(rails_layer) && nrow(rails_layer) > 0) {
    p_hero <- p_hero +
      geom_sf(data = rails_layer, color = "#0369A1", linewidth = 0.65, alpha = 0.4) +
      geom_sf(data = rails_layer, color = "#CBD5E1", linewidth = 0.35, alpha = 0.8)
  }
  if (!is.null(stations_layer) && nrow(stations_layer) > 0) {
    p_hero <- p_hero +
      geom_sf(data = stations_layer, color = "#F59E0B", size = 1.3, alpha = 0.9)
  }
  
  p_hero <- p_hero +
    coord_sf(xlim = c(xmin(r), xmax(r)), ylim = c(ymin(r), ymax(r)), expand = FALSE) +
    labs(
      title = sprintf("%s  %s — POINT OF COMPARISON", toupper(c_info$name_en), c_info$name_zh),
      subtitle = sprintf("%s, USA · City Pop: %0.2fM (Metro: %0.2fM) · 30-Year Growth: %0.2f× · %s",
                         c_info$province_en, c_info$pop_million, c_info$pop_metro_million, c_info$growth_multiple, c_info$archetype),
      caption = "Sources: DLR World Settlement Footprint Evolution 30m (Marconcini et al., 2020) · Natural Earth 10m Railroads · 2020 US Census"
    ) +
    theme_void(base_family = "Droid Sans Fallback") +
    theme(
      plot.background = element_rect(fill = "#0B0F19", color = NA),
      panel.background = element_rect(fill = "#0F172A", color = "#1E293B", linewidth = 1),
      plot.margin = margin(16, 16, 16, 16),
      plot.title = element_text(color = "white", size = 19, face = "bold", margin = margin(b = 4)),
      plot.subtitle = element_text(color = "#94A3B8", size = 10, margin = margin(b = 10)),
      plot.caption = element_text(color = "#64748B", size = 7.5, margin = margin(t = 8)),
      legend.position = "bottom",
      legend.background = element_rect(fill = "#0B0F19", color = NA),
      legend.text = element_text(color = "#E2E8F0", size = 9),
      legend.title = element_text(color = "white", size = 10, face = "bold")
    )
  
  agg_png(hero_out, width = 1400, height = 1100, res = 150)
  print(p_hero)
  dev.off()
  
  # 1B. Transit Network Map
  r_built <- classify(r, matrix(c(-Inf, 1984, NA, 1984.5, 2015.5, 1, 2015.5, Inf, NA), ncol = 3, byrow = TRUE))
  
  p_rail <- ggplot() +
    geom_spatraster(data = r_built, maxcell = 3e5) +
    scale_fill_gradient(low = "#1E293B", high = "#1E293B", na.value = "transparent", guide = "none")
  
  if (!is.null(rails_layer) && nrow(rails_layer) > 0) {
    p_rail <- p_rail +
      geom_sf(data = rails_layer, aes(color = "Railroad Corridors"), linewidth = 0.55, alpha = 0.85)
  }
  if (!is.null(stations_layer) && nrow(stations_layer) > 0) {
    p_rail <- p_rail +
      geom_sf(data = stations_layer, aes(shape = "Key Passenger Hub / Terminal"), color = "#F59E0B", size = 1.6, alpha = 0.95)
  }
  
  p_rail <- p_rail +
    scale_color_manual(values = c("Railroad Corridors" = "#38BDF8"), name = "Corridor Network") +
    scale_shape_manual(values = c("Key Passenger Hub / Terminal" = 16), name = "Transit Facilities") +
    coord_sf(xlim = c(xmin(r), xmax(r)), ylim = c(ymin(r), ymax(r)), expand = FALSE) +
    labs(
      title = sprintf("%s  %s — TRANSIT & RAIL CORRIDORS", toupper(c_info$name_en), c_info$name_zh),
      subtitle = "Continental Railway Lines & Major Terminals overlaid on 2015 Urban Built Footprint",
      caption = "Sources: Natural Earth 10m North America Railroads · DLR WSF Evolution 30m"
    ) +
    theme_void(base_family = "Droid Sans Fallback") +
    theme(
      plot.background = element_rect(fill = "#0B0F19", color = NA),
      panel.background = element_rect(fill = "#090D16", color = "#1E293B", linewidth = 1),
      plot.margin = margin(16, 16, 16, 16),
      plot.title = element_text(color = "white", size = 16, face = "bold", margin = margin(b = 4)),
      plot.subtitle = element_text(color = "#94A3B8", size = 10, margin = margin(b = 10)),
      plot.caption = element_text(color = "#64748B", size = 7.5, margin = margin(t = 8)),
      legend.position = "bottom",
      legend.box = "horizontal",
      legend.background = element_rect(fill = "#0B0F19", color = NA),
      legend.text = element_text(color = "#E2E8F0", size = 9),
      legend.title = element_text(color = "white", size = 9.5, face = "bold")
    )
  
  agg_png(rail_out, width = 1400, height = 1100, res = 150)
  print(p_rail)
  dev.off()
  
  # 2. Small Multiples (4-Panel Progression)
  make_panel <- function(r, yr, title_text, col) {
    r_bin <- classify(r, matrix(c(
      -Inf, 1984, NA,
      1984.5, yr + 0.5, 1,
      yr + 0.5, Inf, NA
    ), ncol = 3, byrow = TRUE))
    
    ggplot() +
      geom_spatraster(data = r_bin, maxcell = 2e5) +
      scale_fill_gradient(low = col, high = col, na.value = "transparent", guide = "none") +
      coord_sf(expand = FALSE) +
      labs(subtitle = title_text) +
      theme_void(base_family = "Droid Sans Fallback") +
      theme(
        plot.background = element_rect(fill = "#0B0F19", color = NA),
        panel.background = element_rect(fill = "#0F172A", color = "#1E293B", linewidth = 0.5),
        plot.subtitle = element_text(color = "white", size = 11, face = "bold", hjust = 0.5, margin = margin(b = 4))
      )
  }
  
  p1 <- make_panel(r, 1985, sprintf("1985 Base · %0.1f km²", c_info$area_1985), "#F59E0B")
  p2 <- make_panel(r, 1995, sprintf("1995 · %0.1f km²", c_info$area_1995), "#EF4444")
  p3 <- make_panel(r, 2005, sprintf("2005 · %0.1f km²", c_info$area_2005), "#06B6D4")
  p4 <- make_panel(r, 2015, sprintf("2015 · %0.1f km²", c_info$area_2015), "#10B981")
  
  p_sm <- (p1 | p2) / (p3 | p4) +
    plot_annotation(
      title = sprintf("%s (%s) — 30-Year Urban Footprint Evolution", c_info$name_en, c_info$name_zh),
      subtitle = sprintf("Uniform spatial extents across four landmark development epochs (Total Growth: %0.2f×)", c_info$growth_multiple),
      caption = "Source: DLR World Settlement Footprint Evolution (WSF-Evo 30m, 1985–2015)",
      theme = theme(
        plot.background = element_rect(fill = "#0B0F19", color = NA),
        plot.title = element_text(color = "white", size = 16, face = "bold", family = "Droid Sans Fallback"),
        plot.subtitle = element_text(color = "#94A3B8", size = 10, family = "Droid Sans Fallback"),
        plot.caption = element_text(color = "#64748B", size = 8, family = "Droid Sans Fallback")
      )
    )
  
  agg_png(sm_out, width = 1400, height = 1200, res = 150)
  print(p_sm)
  dev.off()
  
  # 3. Regional Context Inset Map (Continental US)
  p_ctx <- ggplot() +
    geom_sf(data = us_states, fill = "#1E293B", color = "#334155", linewidth = 0.25)
    
  state_match <- us_states[grepl(c_info$province_en, us_states$name, ignore.case = TRUE), ]
  if (nrow(state_match) > 0) {
    p_ctx <- p_ctx +
      geom_sf(data = state_match, fill = "#0284C7", color = "#38BDF8", linewidth = 0.5, alpha = 0.5)
  }
  
  p_ctx <- p_ctx +
    geom_point(data = c_info, aes(x = lon, y = lat), color = "#F59E0B", size = 3.5) +
    geom_point(data = c_info, aes(x = lon, y = lat), color = "#FEF08A", size = 1.5) +
    coord_sf(xlim = c(-125, -67), ylim = c(24, 50), expand = FALSE) +
    labs(
      title = sprintf("%s (%s)", c_info$name_en, c_info$name_zh),
      subtitle = sprintf("%s, USA · %0.2f°N, %0.2f°W · Pop: %0.2fM", c_info$province_en, c_info$lat, abs(c_info$lon), c_info$pop_million),
      caption = "Sources: Natural Earth 110m Admin-1 · 2020 US Census"
    ) +
    theme_void(base_family = "Droid Sans Fallback") +
    theme(
      plot.background = element_rect(fill = "#0B0F19", color = NA),
      panel.background = element_rect(fill = "#0F172A", color = "#1E293B", linewidth = 0.5),
      plot.title = element_text(color = "white", size = 11, face = "bold", margin = margin(t = 6, b = 2)),
      plot.subtitle = element_text(color = "#94A3B8", size = 9, margin = margin(b = 4)),
      plot.caption = element_text(color = "#64748B", size = 7, margin = margin(b = 4))
    )
  
  agg_png(ctx_out, width = 600, height = 450, res = 150)
  print(p_ctx)
  dev.off()
  
  # 4. Expansion Trajectory Chart
  ts_data <- tibble(
    year = c(1985, 1990, 1995, 2000, 2005, 2010, 2015),
    area = c(c_info$area_1985, c_info$area_1990, c_info$area_1995, 
             c_info$area_2000, c_info$area_2005, c_info$area_2010, c_info$area_2015)
  )
  
  p_traj <- ggplot(ts_data, aes(x = year, y = area)) +
    geom_area(fill = "#0284C7", alpha = 0.25) +
    geom_line(color = "#38BDF8", linewidth = 1.2) +
    geom_point(color = "#F59E0B", size = 2.5) +
    geom_text(aes(label = sprintf("%0.0f", area)), vjust = -0.9, color = "white", size = 3, family = "Droid Sans Fallback") +
    scale_x_continuous(breaks = c(1985, 1990, 1995, 2000, 2005, 2010, 2015)) +
    scale_y_continuous(expand = expansion(mult = c(0.05, 0.25))) +
    labs(
      title = "Physical Urban Expansion (1985–2015)",
      subtitle = sprintf("Built footprint: %0.1f → %0.1f km² (CAGR: %0.2f%%/yr)", 
                         c_info$area_1985, c_info$area_2015, c_info$cagr_pct),
      caption = "Source: Computed from DLR WSF Evolution 30m Satellite Time Series (1985–2015)",
      x = "Year",
      y = "Footprint (km²)"
    ) +
    theme_minimal(base_family = "Droid Sans Fallback") +
    theme(
      plot.background = element_rect(fill = "#0B0F19", color = NA),
      panel.background = element_rect(fill = "#0F172A", color = "#1E293B"),
      panel.grid.major = element_line(color = "#1E293B", linewidth = 0.4),
      panel.grid.minor = element_blank(),
      plot.title = element_text(color = "white", size = 11, face = "bold"),
      plot.subtitle = element_text(color = "#94A3B8", size = 9),
      plot.caption = element_text(color = "#64748B", size = 7.5, margin = margin(t = 6)),
      axis.title = element_text(color = "#94A3B8", size = 9),
      axis.text = element_text(color = "#CBD5E1", size = 8)
    )
  
  agg_png(traj_out, width = 700, height = 450, res = 150)
  print(p_traj)
  dev.off()
  
  return(TRUE)
}

for (i in seq_len(nrow(comp_stats))) {
  render_comparison_city(i)
}

# ------------------------------------------------------------------------------
# 5. Comparative Analytical Charts: China vs. US Points of Comparison
# ------------------------------------------------------------------------------
cat("Rendering Cross-National Analytical Visualizations...\n")

# A. Trajectory Comparison: Charlotte vs Chengdu, Chicago vs Xi'an, Milwaukee vs Dandong/Harbin
years <- c(1985, 1990, 1995, 2000, 2005, 2010, 2015)

selected_cities <- list(
  list(id = "charlotte", name = "Charlotte (US Sunbelt)", group = "US Comparison", color = "#F59E0B", linetype = "solid"),
  list(id = "chengdu",   name = "Chengdu (China Mega-Sprawl)", group = "China Ratlas", color = "#10B981", linetype = "solid"),
  list(id = "chicago",   name = "Chicago (US Great Lakes Core)", group = "US Comparison", color = "#38BDF8", linetype = "solid"),
  list(id = "xian",      name = "Xi'an (China Inland Hub)", group = "China Ratlas", color = "#EC4899", linetype = "solid"),
  list(id = "milwaukee", name = "Milwaukee (US Rust Belt)", group = "US Comparison", color = "#A855F7", linetype = "solid"),
  list(id = "dandong",   name = "Dandong (China Border Gateway)", group = "China Ratlas", color = "#E2E8F0", linetype = "dashed")
)

all_stats <- bind_rows(
  china_stats %>% mutate(dataset = "China Ratlas"),
  comp_stats %>% mutate(dataset = "US Benchmark")
)

traj_rows <- list()
for (item in selected_cities) {
  row <- all_stats %>% filter(id == item$id)
  if (nrow(row) == 0) next
  for (yr in years) {
    colname <- paste0("area_", yr)
    traj_rows[[length(traj_rows) + 1]] <- tibble(
      id = item$id,
      label = item$name,
      group = item$group,
      color = item$color,
      year = yr,
      area = as.numeric(row[[colname]])
    )
  }
}
df_comp_traj <- bind_rows(traj_rows)

p_traj_comp <- ggplot(df_comp_traj, aes(x = year, y = area, color = label, group = label)) +
  geom_line(linewidth = 1.3) +
  geom_point(size = 2.8) +
  # Annotation highlighting Charlotte vs Chengdu baseline parallel
  annotate("rect", xmin = 1984.5, xmax = 1986.5, ymin = 170, ymax = 245, fill = "#F59E0B", alpha = 0.2, color = "#F59E0B", linetype = "dotted") +
  annotate("text", x = 1988, y = 290, label = "1985 Identical Baseline:\nChengdu: 208 km² vs. Charlotte: 208 km²", 
           color = "#FEF08A", size = 3.2, hjust = 0, family = "Droid Sans Fallback") +
  annotate("segment", x = 1987.8, y = 250, xend = 1986, yend = 215, color = "#FEF08A", arrow = arrow(length = unit(0.2, "cm"))) +
  # Annotation highlighting divergence in 2015
  annotate("text", x = 2011, y = 1620, label = "Chengdu 2015: 1,564 km² (7.5×)\nvs. Charlotte 2015: 620 km² (3.0×)",
           color = "#10B981", size = 3.2, hjust = 1, family = "Droid Sans Fallback") +
  scale_color_manual(
    values = c(
      "Charlotte (US Sunbelt)" = "#F59E0B",
      "Chengdu (China Mega-Sprawl)" = "#10B981",
      "Chicago (US Great Lakes Core)" = "#38BDF8",
      "Xi'an (China Inland Hub)" = "#EC4899",
      "Milwaukee (US Rust Belt)" = "#A855F7",
      "Dandong (China Border Gateway)" = "#94A3B8"
    ),
    name = "Metropolitan Profile"
  ) +
  scale_x_continuous(breaks = years) +
  scale_y_continuous(labels = scales::comma_format(suffix = " km²")) +
  labs(
    title = "CROSS-NATIONAL EXPANSION TRAJECTORIES: CHINA VS. US BENCHMARKS",
    subtitle = "Comparing 30-year built-up growth (1985–2015): Note the identical 1985 baseline for Charlotte and Chengdu",
    caption = "Source: DLR World Settlement Footprint Evolution 30m (WSF-Evo 1985–2015) · Consistent pixel metrics across all cities",
    x = "Year",
    y = "Total Built-Up Area (km²)"
  ) +
  theme_minimal(base_family = "Droid Sans Fallback") +
  theme(
    plot.background = element_rect(fill = "#0B0F19", color = NA),
    panel.background = element_rect(fill = "#0F172A", color = "#1E293B"),
    panel.grid.major = element_line(color = "#1E293B", linewidth = 0.5),
    panel.grid.minor = element_blank(),
    plot.title = element_text(color = "white", size = 15, face = "bold", margin = margin(b = 4)),
    plot.subtitle = element_text(color = "#94A3B8", size = 10.5, margin = margin(b = 14)),
    plot.caption = element_text(color = "#64748B", size = 8, margin = margin(t = 10)),
    axis.title = element_text(color = "#94A3B8", size = 10.5),
    axis.text = element_text(color = "#CBD5E1", size = 9),
    legend.position = "right",
    legend.background = element_rect(fill = "#0B0F19", color = NA),
    legend.text = element_text(color = "#E2E8F0", size = 9),
    legend.title = element_text(color = "white", size = 10, face = "bold")
  )

agg_png("output/plots/china_vs_us_comparison.png", width = 1500, height = 950, res = 150)
print(p_traj_comp)
dev.off()

# B. Growth Multiplier Comparison Chart (US cities placed alongside China Distribution)
comp_bar_data <- bind_rows(
  china_stats %>% 
    select(name_en, growth_multiple) %>% 
    mutate(type = "Chinese Atlas City"),
  comp_stats %>% 
    select(name_en, growth_multiple) %>% 
    mutate(type = "US Benchmark")
) %>%
  arrange(growth_multiple)

# Pick representative Chinese cities across the spectrum + 3 US cities
highlight_cities <- c("Heyuan", "Chengdu", "Taizhou", "Shenzhen", "Binzhou", "Wuhan", 
                      "Xi'an", "Zhengzhou", "Jinan", "Harbin", "Dandong", "Lanzhou", "Urumqi", "Korla",
                      "Charlotte", "Milwaukee", "Chicago")

filtered_bar <- comp_bar_data %>%
  filter(name_en %in% highlight_cities) %>%
  arrange(growth_multiple) %>%
  mutate(name_en = factor(name_en, levels = name_en))

p_mult_comp <- ggplot(filtered_bar, aes(x = growth_multiple, y = name_en, fill = type)) +
  geom_col(width = 0.72) +
  geom_text(aes(label = sprintf("%0.2f×", growth_multiple)), 
            hjust = -0.15, size = 3.3, color = "#F8FAFC", family = "Droid Sans Fallback") +
  scale_fill_manual(
    values = c("Chinese Atlas City" = "#0284C7", "US Benchmark" = "#F59E0B"),
    name = "City Category"
  ) +
  scale_x_continuous(limits = c(0, 10.2), breaks = seq(0, 10, 2), expand = expansion(mult = c(0, 0.05))) +
  labs(
    title = "30-YEAR GROWTH MULTIPLIER: CHINA RATLAS VS. US BENCHMARKS",
    subtitle = "Physical expansion ratio (2015 area ÷ 1985 area) illustrating American stability vs. Chinese explosive urbanization",
    caption = "Source: Computed from DLR World Settlement Footprint Evolution (WSF Evolution) 30m dataset",
    x = "Growth Multiple (2015 Footprint / 1985 Footprint)",
    y = NULL
  ) +
  theme_minimal(base_family = "Droid Sans Fallback") +
  theme(
    plot.background = element_rect(fill = "#0B0F19", color = NA),
    panel.background = element_rect(fill = "#0F172A", color = "#1E293B"),
    panel.grid.major.x = element_line(color = "#1E293B", linewidth = 0.5),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    plot.title = element_text(color = "white", size = 14, face = "bold", margin = margin(b = 4)),
    plot.subtitle = element_text(color = "#94A3B8", size = 10, margin = margin(b = 12)),
    plot.caption = element_text(color = "#64748B", size = 8, margin = margin(t = 10)),
    axis.text = element_text(color = "#CBD5E1", size = 9.5),
    axis.title = element_text(color = "#94A3B8", size = 10),
    legend.position = "bottom",
    legend.background = element_rect(fill = "#0B0F19", color = NA),
    legend.text = element_text(color = "#E2E8F0", size = 9),
    legend.title = element_text(color = "white", size = 10, face = "bold")
  )

agg_png("output/plots/comparison_growth_multipliers.png", width = 1400, height = 950, res = 150)
print(p_mult_comp)
dev.off()

cat("All comparison visual assets rendered successfully!\n")
