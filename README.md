# POLI3148 Assignment 1 Project

This repository contains the final project files for POLI3148: Data Science in Politics and Public Administration.

## Report

- [`docs/index.html`](docs/index.html): canonical final HTML report for submission and GitHub Pages.
- Public webpage: <https://lexieliujy.github.io/POLI3148_PS1/>
- Repository: <https://github.com/lexieliujy/POLI3148_PS1>
- GitHub Pages source: `main` branch, `/docs` folder.
- [`note_on_ai_use.md`](note_on_ai_use.md): final AI use statement.

## Code

- [`code/01_data_cleaning.ipynb`](code/01_data_cleaning.ipynb): documents how the raw ACLED export is cleaned and how the processed and summary CSV files are generated.
- [`code/02_analysis.ipynb`](code/02_analysis.ipynb): reproduces the main analysis, summary checks, and figures used in the report.

## Data

- [`data/ACLED Data_MENA_Raw.csv`](data/ACLED%20Data_MENA_Raw.csv): raw ACLED MENA export used as the primary source data.
- [`data/acled_mena_processed.csv`](data/acled_mena_processed.csv): processed event-level dataset after filtering and cleaning.
- [`data/yearly_shift_summary.csv`](data/yearly_shift_summary.csv): yearly comparison table used for report figures.
- [`data/spatial_bucket_summary.csv`](data/spatial_bucket_summary.csv): event composition across capital, border-proximate, and other areas.
- [`data/country_pattern_summary.csv`](data/country_pattern_summary.csv): country-level summary statistics.
- [`data/support/ne_50m_admin_0_countries.zip`](data/support/ne_50m_admin_0_countries.zip): Natural Earth country boundary support data.

The analytical sample combines `Middle East` and `Northern Africa` ACLED records from 1997-2024. Large CSV files are tracked with Git LFS.

## Notes

This project keeps one final report version: `docs/index.html` is the only submission webpage, and future edits should be applied directly to that canonical report baseline.

The final webpage's Figure 4 map uses a yearly time slider, so each selected year shows only that year's event points rather than cumulative totals.

To update the published webpage, edit files under `docs/`, commit the changes, and push to `main`. GitHub Pages rebuilds automatically from the `/docs` folder.

## Author

Lexie Liu  
POLI3148: Data Science in Politics and Public Administration  
Spring 2026
