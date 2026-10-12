# R/04_generate_atlas_maps.R
# Batch generates all maps and charts for the China Urban Growth Ratlas.
# Includes High-Speed Rail (HSR) network, 2020 Census populations, and regional maps.

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
  library(parallel)
})

dir.create("output/maps", recursive = TRUE, showWarnings = FALSE)
dir.create("output/plots", recursive = TRUE, showWarnings = FALSE)

stats <- fromJSON("data/processed/city_growth_stats.json")
admin <- readRDS("data/processed/china_admin_layers.rds")
hsr   <- readRDS("data/processed/china_hsr.rds")
cat(sprintf("Loaded stats for %d cities, China admin layers, and HSR network.\n", nrow(stats)))

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

# ------------------------------------------------------------------------------
# 1. National Overview Maps (with High-Speed Rail Network)
# ------------------------------------------------------------------------------
render_national_visuals <- function() {
  cat("Generating National Overview Map with High-Speed Rail Network...\n")
  
  p_nat <- ggplot() +
    geom_sf(data = admin$country, fill = "#151C2C", color = "#475569", linewidth = 0.45) +
    geom_sf(data = admin$provinces, fill = "#0F172A", color = "#1E293B", linewidth = 0.25) +
    # High-Speed Rail lines
    geom_sf(data = hsr, color = "#0284C7", linewidth = 1.2, alpha = 0.5) +
    geom_sf(data = hsr, color = "#38BDF8", linewidth = 0.6, alpha = 0.9) +
    # City points: sized by Population, colored by 30-Year Growth Multiple
    geom_point(data = stats, aes(x = lon, y = lat, size = pop_million, color = growth_multiple), alpha = 0.9) +
    scale_size_continuous(range = c(2.5, 9.5), name = "Population (M, 2020)") +
    scale_color_viridis_c(option = "inferno", direction = -1, name = "Growth Multiple") +
    coord_sf(xlim = c(73, 135), ylim = c(18, 54), expand = FALSE) +
    labs(
      title = "CHINA URBAN GROWTH RATLAS: 47 CITIES & HIGH-SPEED RAIL",
      subtitle = "30-Year Footprint Expansion (1985–2015) vs. 2020 Census Population, with China HSR Network (CRH 高铁)",
      caption = "Source: DLR WSF Evolution (30m) · China 7th National Census (七普) · HSR Network"
    ) +
    theme_void(base_family = "Droid Sans Fallback") +
    theme(
      plot.background = element_rect(fill = "#0B0F19", color = NA),
      panel.background = element_rect(fill = "#090D16", color = "#1E293B", linewidth = 1),
      plot.margin = margin(20, 20, 20, 20),
      plot.title = element_text(color = "white", size = 17, face = "bold", margin = margin(b = 4)),
      plot.subtitle = element_text(color = "#94A3B8", size = 10.5, margin = margin(b = 12)),
      plot.caption = element_text(color = "#64748B", size = 8.5, margin = margin(t = 10)),
      legend.position = "right",
      legend.background = element_rect(fill = "#0B0F19", color = NA),
      legend.text = element_text(color = "#CBD5E1", size = 8.5),
      legend.title = element_text(color = "white", size = 9.5, face = "bold")
    )
  
  agg_png("output/maps/china_overview_map.png", width = 1600, height = 1100, res = 150)
  print(p_nat)
  dev.off()
  
  # Dedicated High-Speed Rail Corridor Map
  cat("Generating Dedicated High-Speed Rail & Urban Hierarchy Map...\n")
  p_hsr <- ggplot() +
    geom_sf(data = admin$country, fill = "#151C2C", color = "#475569", linewidth = 0.45) +
    geom_sf(data = admin$provinces, fill = "#0F172A", color = "#1E293B", linewidth = 0.25) +
    geom_sf(data = hsr, color = "#0284C7", linewidth = 1.6, alpha = 0.4) +
    geom_sf(data = hsr, aes(linetype = "High-Speed Rail"), color = "#38BDF8", linewidth = 0.8) +
    geom_point(data = stats, aes(x = lon, y = lat, size = pop_million), color = "#F59E0B", alpha = 0.85) +
    geom_text(data = stats %>% filter(pop_million >= 6.0), 
              aes(x = lon, y = lat, label = sprintf("%s\n%0.1fM", name_en, pop_million)),
              color = "#F8FAFC", size = 2.6, vjust = -0.6, family = "Droid Sans Fallback", fontface = "bold") +
    scale_size_continuous(range = c(2, 8), name = "Population (2020 M)") +
    scale_linetype_manual(values = c("High-Speed Rail" = "solid"), name = "Transit Backbone") +
    coord_sf(xlim = c(73, 135), ylim = c(18, 54), expand = FALSE) +
    labs(
      title = "CHINA HIGH-SPEED RAIL ARTERIES & ATLAS URBAN NODES",
      subtitle = "Corridors catalyzing post-2005 expansion across regional metropolises and secondary centers",
      caption = "China High-Speed Rail Grid (CRH 八纵八横主通道) · DLR WSF Evolution"
    ) +
    theme_void(base_family = "Droid Sans Fallback") +
    theme(
      plot.background = element_rect(fill = "#0B0F19", color = NA),
      panel.background = element_rect(fill = "#090D16", color = "#1E293B", linewidth = 1),
      plot.margin = margin(20, 20, 20, 20),
      plot.title = element_text(color = "white", size = 17, face = "bold", margin = margin(b = 4)),
      plot.subtitle = element_text(color = "#94A3B8", size = 10.5, margin = margin(b = 12)),
      plot.caption = element_text(color = "#64748B", size = 8.5, margin = margin(t = 10)),
      legend.position = "right",
      legend.background = element_rect(fill = "#0B0F19", color = NA),
      legend.text = element_text(color = "#CBD5E1", size = 8.5),
      legend.title = element_text(color = "white", size = 9.5, face = "bold")
    )
  
  agg_png("output/maps/china_hsr_overview.png", width = 1600, height = 1100, res = 150)
  print(p_hsr)
  dev.off()
  
  # Growth Multiplier Ranking Chart (Retained as requested!)
  cat("Generating National Growth Multiplier Ranking Chart...\n")
  top_stats <- stats %>%
    arrange(desc(growth_multiple)) %>%
    head(25) %>%
    mutate(city_label = sprintf("%s (%s)", name_en, name_zh))
  
  p_rank <- ggplot(top_stats, aes(x = reorder(city_label, growth_multiple), y = growth_multiple, fill = region)) +
    geom_col(alpha = 0.9, width = 0.75) +
    geom_text(aes(label = sprintf("%0.1f×", growth_multiple)), hjust = -0.15, color = "white", size = 3, family = "Droid Sans Fallback") +
    coord_flip() +
    scale_fill_brewer(palette = "Set2", name = "Geographic Region") +
    scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
    labs(
      title = "Top 25 Chinese Cities by 30-Year Urban Growth Multiple (1985–2015)",
      subtitle = "Physical built-up area ratio (2015 footprint ÷ 1985 footprint)",
      x = NULL,
      y = "Growth Multiple"
    ) +
    theme_minimal(base_family = "Droid Sans Fallback") +
    theme(
      plot.background = element_rect(fill = "#0B0F19", color = NA),
      panel.background = element_rect(fill = "#0F172A", color = "#1E293B"),
      panel.grid.major.x = element_line(color = "#1E293B", linewidth = 0.4),
      panel.grid.major.y = element_blank(),
      panel.grid.minor = element_blank(),
      plot.title = element_text(color = "white", size = 13, face = "bold"),
      plot.subtitle = element_text(color = "#94A3B8", size = 10, margin = margin(b = 10)),
      axis.text = element_text(color = "#CBD5E1", size = 9),
      axis.title = element_text(color = "#94A3B8", size = 10),
      legend.position = "bottom",
      legend.background = element_rect(fill = "#0B0F19", color = NA),
      legend.text = element_text(color = "#CBD5E1", size = 9),
      legend.title = element_text(color = "white", size = 10, face = "bold")
    )
  
  agg_png("output/plots/national_growth_ranking.png", width = 1400, height = 1000, res = 150)
  print(p_rank)
  dev.off()
  
  # Regional Exploration Map (for clickable image map)
  cat("Generating Regional Exploration Map...\n")
  # Color provinces by their regional assignment
  provs <- admin$provinces
  # Region assignment lookup
  reg_lookup <- list(
    "Northeast Rust Belt" = c("Heilongjiang", "Jilin", "Liaoning"),
    "Yellow River & North Plain" = c("Hebei", "Shanxi", "Shandong", "Henan", "Tianjin", "Beijing"),
    "Yangtze Delta & East" = c("Jiangsu", "Anhui", "Zhejiang", "Shanghai"),
    "Yangtze Basin & Central" = c("Hubei", "Hunan", "Jiangxi", "Sichuan", "Chongqing"),
    "Pearl River & South Coast" = c("Guangdong", "Fujian", "Hainan", "HongKong", "Macau"),
    "Western Frontier & Steppe" = c("XinjiangUygur", "Gansu", "Shaanxi", "NeiMongol", "NingxiaHui", "Qinghai", "Xizang", "Yunnan", "Guangxi", "Guizhou")
  )
  
  provs$macro_region <- "Other"
  for (rname in names(reg_lookup)) {
    targets <- reg_lookup[[rname]]
    for (t in targets) {
      provs$macro_region[grepl(t, provs$NAME_1, ignore.case = TRUE)] <- rname
    }
  }
  
  region_palette <- c(
    "Northeast Rust Belt" = "#3B82F6",       # Blue
    "Yellow River & North Plain" = "#EAB308", # Amber Yellow
    "Yangtze Delta & East" = "#10B981",       # Emerald Green
    "Yangtze Basin & Central" = "#8B5CF6",    # Purple
    "Pearl River & South Coast" = "#EC4899",   # Pink / Coral
    "Western Frontier & Steppe" = "#F97316"   # Orange
  )
  
  p_reg <- ggplot() +
    geom_sf(data = admin$country, fill = "#151C2C", color = "#475569", linewidth = 0.45) +
    geom_sf(data = provs %>% filter(macro_region != "Other"), aes(fill = macro_region), color = "#0F172A", linewidth = 0.35, alpha = 0.75) +
    geom_sf(data = hsr, color = "#FFFFFF", linewidth = 0.5, alpha = 0.4) +
    geom_point(data = stats, aes(x = lon, y = lat), color = "#FFFFFF", size = 2.2, alpha = 0.95) +
    scale_fill_manual(values = region_palette, name = "Geographic Macro-Region") +
    coord_sf(xlim = c(73, 135), ylim = c(18, 54), expand = FALSE) +
    labs(
      title = "THE SIX GEOGRAPHIC MACRO-REGIONS OF CHINA",
      subtitle = "Click on any region on the map below or use the regional cards to explore cities",
      caption = "China Urban Growth Ratlas · Interactive Regional Map"
    ) +
    theme_void(base_family = "Droid Sans Fallback") +
    theme(
      plot.background = element_rect(fill = "#0B0F19", color = NA),
      panel.background = element_rect(fill = "#090D16", color = "#1E293B", linewidth = 1),
      plot.margin = margin(20, 20, 20, 20),
      plot.title = element_text(color = "white", size = 16, face = "bold", margin = margin(b = 4)),
      plot.subtitle = element_text(color = "#94A3B8", size = 10.5, margin = margin(b = 12)),
      plot.caption = element_text(color = "#64748B", size = 8.5, margin = margin(t = 10)),
      legend.position = "bottom",
      legend.background = element_rect(fill = "#0B0F19", color = NA),
      legend.text = element_text(color = "#CBD5E1", size = 8.5),
      legend.title = element_text(color = "white", size = 9.5, face = "bold")
    )
  
  agg_png("output/maps/china_regions_map.png", width = 1600, height = 1100, res = 150)
  print(p_reg)
  dev.off()
  
  cat("All national and regional visual assets rendered successfully!\n")
}

# Run national & regional visuals
render_national_visuals()
