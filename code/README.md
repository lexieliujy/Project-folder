# Code Folder

## Main files

- `01_conflict_shift_analysis.ipynb`: the main assignment notebook
- `project_utils.py`: shared functions for cleaning data, building summary tables, and producing Plotly figures
- `Z_generate_report.py`: generates the processed CSV outputs and the final report in `docs/index.html`
- `Z_create_notebook.py`: writes the notebook file in a reproducible way

## Run order

If the project needs to be regenerated from scratch:

```bash
python3 code/Z_create_notebook.py
python3 code/Z_generate_report.py
```

The notebook is the step-by-step analytical document, while the report script generates the polished HTML output for submission or GitHub Pages publication.
