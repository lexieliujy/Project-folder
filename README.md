# MENA Conflict Geography

**POLI 3148 Assignment 1 · Interactive data report · Spring 2026**

This repository contains an interactive data report examining whether the rise of drones and other remote attacks in the Middle East and North Africa has been accompanied by a spatial shift from border-proximate conflict toward attacks on capital areas.

Public webpage: <https://lexieliujy.github.io/POLI3148_PS1/>

Repository: <https://github.com/lexieliujy/POLI3148_PS1>

## Project note

This repository is my POLI 3148 Assignment 1 data project submission. It contains the data, notebooks, and public webpage required for the assignment.

The analysis is descriptive. It does not claim to establish a causal relationship between remote attack technologies and the geography of conflict. The report uses ACLED event data and Natural Earth boundary data to build reproducible spatial indicators, then compares patterns across time and space.

For authoritative data, documentation, and citation information, use the original sources directly:

- ACLED: <https://acleddata.com/>
- Natural Earth: <https://www.naturalearthdata.com/>

See [`note_on_ai_use.md`](note_on_ai_use.md) for the AI use statement.

## What's in this repo

| File | Purpose |
| --- | --- |
| [`docs/index.html`](docs/index.html) | Final interactive HTML report served through GitHub Pages. |
| [`code/01_data_cleaning.ipynb`](code/01_data_cleaning.ipynb) | Cleans the raw ACLED data, creates spatial indicators, and writes the processed and summary CSV files. |
| [`code/02_analysis.ipynb`](code/02_analysis.ipynb) | Reproduces the headline checks, analysis tables, and figures used in the report. |
| [`data/ACLED Data_MENA_Raw.csv`](data/ACLED%20Data_MENA_Raw.csv) | Raw ACLED MENA export used as the primary source data. |
| [`data/acled_mena_processed.csv`](data/acled_mena_processed.csv) | Cleaned event-level dataset with added spatial and event-type indicators. |
| [`data/yearly_shift_summary.csv`](data/yearly_shift_summary.csv) | Yearly summary table used for the time-series figures. |
| [`data/spatial_bucket_summary.csv`](data/spatial_bucket_summary.csv) | Summary table comparing capital areas, border-proximate areas, and other areas. |
| [`data/country_pattern_summary.csv`](data/country_pattern_summary.csv) | Country-level summary statistics. |
| [`data/support/ne_50m_admin_0_countries.zip`](data/support/ne_50m_admin_0_countries.zip) | Natural Earth country boundary data used for border-distance calculations. |
| [`note_on_ai_use.md`](note_on_ai_use.md) | Statement describing how AI assistance was used in the project workflow. |

## Running the project

Run the notebooks in order:

```bash
# 1. Open and run the data-cleaning notebook
code/01_data_cleaning.ipynb

# 2. Open and run the analysis notebook
code/02_analysis.ipynb
```

The first notebook writes:

- `data/acled_mena_processed.csv`
- `data/yearly_shift_summary.csv`
- `data/spatial_bucket_summary.csv`
- `data/country_pattern_summary.csv`

The second notebook reads those files and reproduces the analysis checks and figures.

Large CSV files are tracked with Git LFS. If a CSV opens as a small text pointer beginning with `version https://git-lfs`, run:

```bash
git lfs pull
```

## GitHub Pages deployment

This project is set up to deploy through GitHub Pages using the `/docs` folder.

In the repository settings, Pages should be configured as:

| Setting | Value |
| --- | --- |
| Source | Deploy from a branch |
| Branch | `main` |
| Folder | `/docs` |

The live report is available at:

<https://lexieliujy.github.io/POLI3148_PS1/>

## Data

Primary source: ACLED event data for the Middle East and Northern Africa.

Support data: Natural Earth 1:50m administrative country boundaries.

Analytical sample:

- Region: ACLED `Middle East` and `Northern Africa`
- Years used in the report: 1997-2024
- Cleaned sample size: 343,901 event observations
- Spatial definitions:
  - `Capital-area event`: an event located in a national capital or a sub-location beginning with the capital's name.
  - `Border-proximate event`: an event within 50 km of an international land border.
  - `Spatial bucket`: capital areas, border-proximate areas, and other areas.

## Main analysis

The report asks whether remote violence is associated with a shift from frontier conflict toward capital targeting.

The project focuses on four descriptive checks:

1. Whether capital-area remote attacks become a larger share of all remote violence.
2. Whether border-proximate remote violence remains more common than capital-area remote violence.
3. Whether yearly all-event shares show a spatial shift toward capital areas.
4. Whether the map-level geography supports or weakens the capital-shift expectation.

The main descriptive conclusion is that border-linked space remains the heavier conflict geography in MENA relative to capital space. The data do not support a simple regional story in which conflict moved from borders to capitals.

## Design choices

- Single public report page: `docs/index.html`.
- GitHub Pages uses the `/docs` folder so the report is accessible as a webpage.
- The notebooks are self-contained: data cleaning logic is in `01_data_cleaning.ipynb`, and analysis / figure logic is in `02_analysis.ipynb`.
- Figure 4 uses a yearly time slider so each selected year shows that year's event points rather than cumulative totals.

## Author

Liu Jing Yi  
UID: 3035844247  
POLI 3148: Data Science in Politics and Public Administration  
Spring 2026
