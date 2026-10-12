# R/02_fetch_and_crop_wsf.R
# Fetches and crops WSF Evolution rasters for all cities in data/cities.json
# Uses terra and vsicurl streaming with local caching.

suppressPackageStartupMessages({
  library(terra)
  library(jsonlite)
  library(parallel)
})

dir.create("data/processed/wsf", recursive = TRUE, showWarnings = FALSE)

cities <- fromJSON("data/cities.json")
cat(sprintf("Loaded %d cities from data/cities.json\n", nrow(cities)))

process_single_city <- function(i) {
  c_id <- cities$id[i]
  c_name <- cities$name_en[i]
  c_zh <- cities$name_zh[i]
  bbox <- cities$bbox[[i]]
  tiles <- cities$wsf_tiles[[i]]
  
  dest_file <- sprintf("data/processed/wsf/%s.tif", c_id)
  if (file.exists(dest_file) && file.size(dest_file) > 1000) {
    cat(sprintf("[%02d/%02d] %s (%s) - Already cached (%0.1f KB)\n", 
                i, nrow(cities), c_name, c_zh, file.size(dest_file)/1024))
    return(TRUE)
  }
  
  cat(sprintf("[%02d/%02d] %s (%s) - Downloading & cropping...\n", 
              i, nrow(cities), c_name, c_zh))
  
  city_ext <- ext(bbox[1], bbox[3], bbox[2], bbox[4])
  rasters <- list()
  
  for (t in tiles) {
    url <- sprintf("/vsicurl/https://download.geoservice.dlr.de/WSF_EVO/files/%s/%s.tif", t, t)
    rc <- tryCatch({
      r <- rast(url)
      inter <- intersect(ext(r), city_ext)
      if (!is.null(inter)) {
        crop(r, inter)
      } else {
        NULL
      }
    }, error = function(e) {
      NULL
    })
    
    if (!is.null(rc)) {
      rasters[[t]] <- rc
    }
  }
  
  if (length(rasters) == 0) {
    cat(sprintf("FAILED: [%s] No raster data retrieved!\n", c_id))
    return(FALSE)
  }
  
  merged_r <- if (length(rasters) == 1) {
    rasters[[1]]
  } else {
    merge(sprc(rasters))
  }
  
  final_r <- tryCatch({
    crop(merged_r, city_ext)
  }, error = function(e) merged_r)
  
  writeRaster(final_r, dest_file, overwrite = TRUE, 
              gdal = c("COMPRESS=DEFLATE", "PREDICTOR=2", "ZLEVEL=6"))
  
  cat(sprintf("[%02d/%02d] %s - Done! Cached (%0.1f KB)\n", 
              i, nrow(cities), c_name, file.size(dest_file)/1024))
  return(TRUE)
}

# Run across cities using parallel workers
cat(sprintf("Starting WSF Evolution cropping across %d cities...\n", nrow(cities)))
results <- mclapply(seq_len(nrow(cities)), process_single_city, mc.cores = 4)

successes <- sum(unlist(results))
cat(sprintf("\nCompleted: %d of %d cities successfully processed and cached in data/processed/wsf/\n",
            successes, nrow(cities)))
