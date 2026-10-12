# run_atlas.R
# Master execution pipeline for the China Urban Growth Ratlas (1985–2015)

cat("=================================================================\n")
cat("          CHINA URBAN GROWTH RATLAS PIPELINE (1985–2015)          \n")
cat("=================================================================\n\n")

# Step 1: Create City Geodatabase
cat("[1/5] Building city geodatabase & boundary metadata...\n")
system("python3 scripts/create_city_registry.py")

# Step 2: Fetch and crop WSF Evolution raster tiles
cat("\n[2/5] Fetching & caching DLR WSF Evolution 30m rasters (47 cities)...\n")
source("R/02_fetch_and_crop_wsf.R")

# Step 3: Compute quantitative growth metrics
cat("\n[3/5] Computing multi-epoch spatial metrics & growth multipliers...\n")
source("R/03_compute_growth_metrics.R")

# Step 4: Batch generate cartographic maps & analytical plots
cat("\n[4/5] Generating publication-grade maps (hero rings, small multiples, insets, plots)...\n")
source("R/04_generate_atlas_maps.R")

# Step 5: Generate Quarto pages and render website
cat("\n[5/5] Generating Quarto markdown pages and compiling static website...\n")
system("python3 scripts/generate_quarto_pages.py")
system("quarto render")

cat("\n=================================================================\n")
cat("RATLAS BUILD COMPLETE! Static website ready in 'docs/' for GitHub Pages.\n")
cat("Run 'quarto preview' to inspect locally.\n")
cat("=================================================================\n")
