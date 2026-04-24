# Code Folder

## Main files

- `01_conflict_shift_analysis.ipynb`: one-cell notebook mirror of the finalized report narrative
- `project_utils.py`: shared data cleaning and plotting utilities
- `Z_create_notebook.py`: regenerates the notebook mirror so it matches the current final report baseline
- `Z_generate_report.py`: syncs the finalized DOCX manuscript into `docs/index.html`

## Synchronization

If the report baseline needs to be resynchronized:

```bash
python3 code/Z_create_notebook.py
python3 code/Z_generate_report.py
```

The final webpage's Figure 4 map slider is yearly rather than cumulative, so the notebook mirror and supporting docs should describe it the same way.
