# R/04_generate_atlas_maps.R
# Batch generates all maps and charts for the China Urban Growth Ratlas.

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
cat(sprintf("Loaded stats for %d cities and China administrative layers.\n", nrow(stats)))

# Reclassification matrix for Epochs:
# 1985 -> 1 (Pre-1985)
# 1986-1995 -> 2 (1986-1995)
# 1996-2005 -> 3 (1996-2005)
# 2006-2015 -> 4 (2006-2015)
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

render_city_visuals <- function(i) {
  c_info <- stats[i, ]
  c_id <- c_info$id
  tif_path <- sprintf("data/processed/wsf/%s.tif", c_id)
  
  if (!file.exists(tif_path)) return(FALSE)
  
  hero_out <- sprintf("output/maps/%s_hero.png", c_id)
  sm_out   <- sprintf("output/maps/%s_small_multiples.png", c_id)
  ctx_out  <- sprintf("output/maps/%s_context.png", c_id)
  traj_out <- sprintf("output/plots/%s_trajectory.png", c_id)
  
  # Check if all 4 exist
  if (file.exists(hero_out) && file.exists(sm_out) && 
      file.exists(ctx_out) && file.exists(traj_out)) {
    return(TRUE)
  }
  
  r <- rast(tif_path)
  
  # ----------------------------------------------------
  # 1. Hero Map (Urban Growth Rings)
  # ----------------------------------------------------
  if (!file.exists(hero_out)) {
    r_epoch <- classify(r, rcl_hero)
    r_epoch <- as.factor(r_epoch)
    levels(r_epoch) <- data.frame(ID = 1:4, epoch = c("Pre-1985", "1986–1995", "1996–2005", "2006–2015"))
    
    p_hero <- ggplot() +
      geom_spatraster(data = r_epoch, maxcell = 6e5) +
      scale_fill_manual(values = epoch_cols, na.translate = FALSE, name = "Expansion Epoch") +
      coord_sf(expand = FALSE) +
      labs(
        title = sprintf("%s  %s", toupper(c_info$name_en), c_info$name_zh),
        subtitle = sprintf("%s Province · %s · 1985: %0.1f km² → 2015: %0.1f km² (%0.1f× Growth)",
                           c_info$province_en, c_info$region, c_info$area_1985, c_info$area_2015, c_info$growth_multiple),
        caption = "China Urban Growth Ratlas · Data: DLR WSF Evolution (30m) · 1985–2015"
      ) +
      theme_void(base_family = "Droid Sans Fallback") +
      theme(
        plot.background = element_rect(fill = "#0B0F19", color = NA),
        panel.background = element_rect(fill = "#0F172A", color = "#1E293B", linewidth = 1),
        plot.margin = margin(16, 16, 16, 16),
        plot.title = element_text(color = "white", size = 20, face = "bold", margin = margin(b = 4)),
        plot.subtitle = element_text(color = "#94A3B8", size = 11, margin = margin(b = 10)),
        plot.caption = element_text(color = "#64748B", size = 8, margin = margin(t = 8)),
        legend.position = "bottom",
        legend.background = element_rect(fill = "#0B0F19", color = NA),
        legend.text = element_text(color = "#E2E8F0", size = 9),
        legend.title = element_text(color = "white", size = 10, face = "bold")
      )
    
    agg_png(hero_out, width = 1400, height = 1100, res = 150)
    print(p_hero)
    dev.off()
  }
  
  # ----------------------------------------------------
  # 2. Small Multiples (4-Panel Progression)
  # ----------------------------------------------------
  if (!file.exists(sm_out)) {
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
        subtitle = sprintf("Uniform spatial extents across four landmark development epochs (Total Growth: %0.1f×)", c_info$growth_multiple),
        theme = theme(
          plot.background = element_rect(fill = "#0B0F19", color = NA),
          plot.title = element_text(color = "white", size = 16, face = "bold", family = "Droid Sans Fallback"),
          plot.subtitle = element_text(color = "#94A3B8", size = 10, family = "Droid Sans Fallback")
        )
      )
    
    agg_png(sm_out, width = 1400, height = 1200, res = 150)
    print(p_sm)
    dev.off()
  }
  
  # ----------------------------------------------------
  # 3. Regional Context Inset Map
  # ----------------------------------------------------
  if (!file.exists(ctx_out)) {
    prov_match <- admin$provinces[grepl(c_info$province_en, admin$provinces$NAME_1, ignore.case = TRUE), ]
    
    p_ctx <- ggplot() +
      geom_sf(data = admin$country, fill = "#1E293B", color = "#475569", linewidth = 0.3) +
      geom_sf(data = admin$provinces, fill = "#1E293B", color = "#334155", linewidth = 0.2) +
      geom_sf(data = prov_match, fill = "#0284C7", color = "#38BDF8", linewidth = 0.5, alpha = 0.4) +
      geom_point(data = c_info, aes(x = lon, y = lat), color = "#F59E0B", size = 3.5) +
      geom_point(data = c_info, aes(x = lon, y = lat), color = "#FEF08A", size = 1.5) +
      coord_sf(xlim = c(73, 135), ylim = c(18, 54), expand = FALSE) +
      labs(
        title = sprintf("%s (%s)", c_info$name_en, c_info$name_zh),
        subtitle = sprintf("%s Province · %0.2f°N, %0.2f°E", c_info$province_en, c_info$lat, c_info$lon)
      ) +
      theme_void(base_family = "Droid Sans Fallback") +
      theme(
        plot.background = element_rect(fill = "#0B0F19", color = NA),
        panel.background = element_rect(fill = "#0F172A", color = "#1E293B", linewidth = 0.5),
        plot.title = element_text(color = "white", size = 11, face = "bold", margin = margin(t = 6, b = 2)),
        plot.subtitle = element_text(color = "#94A3B8", size = 9, margin = margin(b = 6))
      )
    
    agg_png(ctx_out, width = 600, height = 450, res = 150)
    print(p_ctx)
    dev.off()
  }
  
  # ----------------------------------------------------
  # 4. Expansion Trajectory Chart
  # ----------------------------------------------------
  if (!file.exists(traj_out)) {
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
      scale_y_continuous(expand = expansion(mult = c(0.05, 0.2))) +
      labs(
        title = "Physical Urban Expansion (1985–2015)",
        subtitle = sprintf("Built footprint: %0.1f → %0.1f km² (CAGR: %0.1f%%/yr)", 
                           c_info$area_1985, c_info$area_2015, c_info$cagr_pct),
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
        axis.title = element_text(color = "#94A3B8", size = 9),
        axis.text = element_text(color = "#CBD5E1", size = 8)
      )
    
    agg_png(traj_out, width = 700, height = 450, res = 150)
    print(p_traj)
    dev.off()
  }
  
  cat(sprintf("[%02d/%02d] %s (%s) — Generated maps & plots.\n", i, nrow(stats), c_info$name_en, c_info$name_zh))
  return(TRUE)
}

# ----------------------------------------------------
# 5. National Overview Map & Comparative Ranking
# ----------------------------------------------------
render_national_visuals <- function() {
  cat("Generating National Overview Map...\n")
  
  p_nat <- ggplot() +
    geom_sf(data = admin$country, fill = "#1E293B", color = "#475569", linewidth = 0.4) +
    geom_sf(data = admin$provinces, fill = "#0F172A", color = "#334155", linewidth = 0.25) +
    geom_point(data = stats, aes(x = lon, y = lat, size = area_2015, color = growth_multiple), alpha = 0.85) +
    scale_size_continuous(range = c(2, 9), name = "2015 Built km²") +
    scale_color_viridis_c(option = "inferno", direction = -1, name = "Growth Multiple") +
    coord_sf(xlim = c(73, 135), ylim = c(18, 54), expand = FALSE) +
    labs(
      title = "CHINA URBAN GROWTH RATLAS: 47 CITIES (1985–2015)",
      subtitle = "Spatial footprint expansion across 47 Chinese metropolises, border gateways, and regional hubs",
      caption = "Source: DLR World Settlement Footprint Evolution (WSF Evolution) 30m"
    ) +
    theme_void(base_family = "Droid Sans Fallback") +
    theme(
      plot.background = element_rect(fill = "#0B0F19", color = NA),
      panel.background = element_rect(fill = "#090D16", color = "#1E293B", linewidth = 1),
      plot.margin = margin(20, 20, 20, 20),
      plot.title = element_text(color = "white", size = 18, face = "bold", margin = margin(b = 4)),
      plot.subtitle = element_text(color = "#94A3B8", size = 11, margin = margin(b = 12)),
      plot.caption = element_text(color = "#64748B", size = 9, margin = margin(t = 10)),
      legend.position = "right",
      legend.background = element_rect(fill = "#0B0F19", color = NA),
      legend.text = element_text(color = "#CBD5E1", size = 9),
      legend.title = element_text(color = "white", size = 10, face = "bold")
    )
  
  agg_png("output/maps/china_overview_map.png", width = 1600, height = 1100, res = 150)
  print(p_nat)
  dev.off()
  
  cat("Generating National Growth Multiplier Ranking Chart...\n")
  top_stats <- stats %>%
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
  
  cat("National overview visual assets completed!\n")
}

# Run National Visuals
render_national_visuals()

# Run all 47 cities in parallel
cat(sprintf("Rendering visual map suites for %d cities across 4 cores...\n", nrow(stats)))
res <- mclapply(seq_len(nrow(stats)), render_city_visuals, mc.cores = 4)
cat(sprintf("Completed map generation: %d of %d succeeded.\n", sum(unlist(res)), nrow(stats)))
