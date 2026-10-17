# Sundarbans mangrove community reorganization — reproducibility package

This repository accompanies the manuscript:

**Salinity-associated mangrove community reorganization in the Bangladesh Sundarbans: long-term field records, multisensor Earth observation and transferability-aware validation**

## Why this study is distinctive

The study combines a 15-year permanent-sample-plot record with multisensor Earth observation and explicitly tests whether apparent community-classification skill survives changes in validation design. The central reproducibility target is the contrast among:

- random five-fold cross-validation;
- geographic block validation at 3, 5 and 10 block resolutions;
- leave-one-year-out temporal transfer; and
- a cross-year harmonized predictor set that removes most year-specific sensor availability.

This is important because a multi-year classifier can exploit sensor/year structure even when geographic leakage is controlled.

## Repository scope

The repository reproduces the **processed-data analyses** used in the revised manuscript. It does not contain the multi-gigabyte raw GeoTIFF archive. Exact permanent-plot coordinates are also excluded from the public bundle by default; pre-assigned spatial block IDs are supplied so the reported validation can be reproduced without publishing long-term monitoring locations.

### Included

- processed multisensor PSP-year feature cube;
- field assemblage and transition tables;
- public spatial block assignments;
- model validation and sensitivity results;
- scripts for coarse assemblage validation, transition analysis, field salinity models and figures;
- high-resolution PNG figures;
- data dictionary and analysis provenance notes.

### Not included

- raw Landsat, Sentinel-2, PALSAR/PALSAR-2, GEDI or ancillary rasters;
- exact PSP coordinates;
- proprietary or permission-restricted source data.

## Quick start

```bash
conda env create -f environment.yml
conda activate sundarbans-rsase

python src/01_validate_assemblage_models.py
python src/02_transition_analysis.py
python src/03_field_salinity_models.py
python src/04_make_figures.py
```

Outputs are written to `outputs/` when the scripts are run.

## Principal validation result

Using the full multisensor predictor set, coarse assemblage classification remains strong under geographic blocking. When the model is restricted to predictors consistently available across years, balanced accuracy falls substantially. The repository is designed to make that sensitivity transparent rather than to maximize a single accuracy metric.

## Data-sharing note

The public feature cube deliberately omits latitude and longitude. If the authors have permission to release exact PSP coordinates, they can add them in a separate controlled or DOI-minting data repository. The raw EO rasters should likewise be archived outside GitHub because of file size and source-data licensing.

## Citation and DOI

Complete `CITATION_TEMPLATE.cff` and replace the repository/DOI placeholders after the manuscript and data package are deposited.

## License

No license is imposed by this draft package. The authors should choose separate software and data licenses that are consistent with institutional and source-data permissions.
