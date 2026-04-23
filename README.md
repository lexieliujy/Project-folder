# POLI3148 Assignment 1 Project

## Project overview

This project studies whether contemporary conflict dynamics across the Middle East and Northern Africa show a spatial shift from border-based clashes to remote attacks targeting capital areas. The project uses ACLED as the primary dataset, follows a fully Python-based workflow, and produces both a reproducible Jupyter notebook and an interactive HTML report.

## Data sources

- Primary dataset: [`data/ACLED Data_MENA_Raw.csv`](data/ACLED%20Data_MENA_Raw.csv)
- Original source file retained for reference: `data/ACLED Data_MENA_Raw.numbers`
- Assignment brief: `Instructions.pdf`
- Initial idea note: `Workflow.docx`

The analytical sample combines both `Middle East` and `Northern Africa`, matching the full MENA scope of the updated file.

## Methodology

The project uses a transparent proxy-based design:

- `Capital-area remote attacks` are events coded as `Explosions/Remote violence` whose location is either a capital city or a sub-location beginning with the capital name.
- `Border-referenced battles` are `Battles` events whose ACLED notes mention `border`, `cross-border`, `cross border`, `frontier`, `boundary`, or `border crossing`.
- Before analysis, rows with NA values in the core analytical fields are removed directly.
- The analysis compares these patterns over time, across countries, and on an interactive map.

Main tools used:

- `pandas` for data cleaning and summary tables
- `plotly` for interactive visualizations
- `Jupyter Notebook` for documented analysis
- `Python` scripts for reproducible report generation

## Key findings

- Remote violence is highly prevalent across the MENA sample.
- Capital-area remote attacks are important, but still only a small share of all remote violence.
- Border-referenced battles remain visible across major frontier theatres, especially in Yemen, Syria, Iraq, Palestine, and Sudan.
- The overall pattern suggests layered conflict geography rather than a simple regional move from borders to capitals.

## Limitations

- The border measure is conservative because it relies on explicit textual mentions in ACLED notes.
- The capital-area measure is broader than an exact-city rule, but it still cannot capture every indirect attempt to influence a capital.
- Fatality counts in ACLED are reported estimates and should be interpreted cautiously.
- The raw data file is a supplied export, so the retrieval discussion is limited to the structure of the provided file.

## Project structure

- [`code/01_conflict_shift_analysis.ipynb`](code/01_conflict_shift_analysis.ipynb): main notebook
- [`code/Z_generate_report.py`](code/Z_generate_report.py): generates the HTML report and processed data
- [`code/project_utils.py`](code/project_utils.py): shared analysis functions
- [`data/acled_mena_processed.csv`](data/acled_mena_processed.csv): processed event-level data
- [`data/yearly_shift_summary.csv`](data/yearly_shift_summary.csv): yearly comparison table
- [`docs/index.html`](docs/index.html): interactive report
- [`note_on_ai_use.md`](note_on_ai_use.md): required note on AI use

## Author

Lexie Liu  
POLI3148: Data Science in Politics and Public Administration  
Spring 2026
