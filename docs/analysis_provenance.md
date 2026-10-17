# Analysis provenance

## Field and EO linkage

The original feature cube was extracted from the project GeoTIFF archive at canonical PSP locations and contains plot-centred optical, radar, terrain, hydrological and contextual summaries. The raw raster-extraction stage is not reproduced from GitHub because the source files are multi-gigabyte and exact monitoring-site coordinates are not included in the public bundle.

## Public reproducibility boundary

The scripts in `src/` reproduce analyses downstream of the processed feature cube:

1. Hellinger-based coarse and fine assemblage clustering;
2. random, geographic-block and leave-one-year-out classifier validation;
3. full versus cross-year harmonized predictor sensitivity;
4. fine-assemblage transition summaries;
5. year-adjusted species–salinity GLMs from the 2010/2020/2024 benchmark subset;
6. manuscript validation figures.

The manuscript's previously archived PERMANOVA and continuous multivariate community-model predictions are supplied as result tables rather than re-created from the raw raster archive.

## Validation principle

Random CV is an optimistic diagnostic only. The principal methodological interpretation is based on geographic blocking, leave-one-year-out transfer and cross-year predictor harmonization.
