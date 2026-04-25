from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


def markdown_cell(text: str) -> dict:
    text = dedent(text).strip()
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.splitlines()],
    }


def code_cell(text: str) -> dict:
    text = dedent(text).strip()
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.splitlines()],
    }


def notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


DATA_CLEANING_NOTEBOOK = notebook(
    [
        markdown_cell(
            """
            # 01 Data Cleaning and Summary Generation

            This notebook documents how the project moves from the raw ACLED export to the processed event-level CSV and the summary CSV files used by the report.

            Outputs generated here:

            - `data/acled_mena_processed.csv`
            - `data/yearly_shift_summary.csv`
            - `data/spatial_bucket_summary.csv`
            - `data/country_pattern_summary.csv`
            """
        ),
        code_cell(
            """
            from pathlib import Path
            import subprocess
            import sys

            import pandas as pd

            REPO_URL = "https://github.com/lexieliujy/POLI3148_PS1.git"


            def find_project_root(start: Path) -> Path:
                for candidate in [start, *start.parents]:
                    if (candidate / "code" / "project_utils.py").exists() and (candidate / "data").exists():
                        return candidate
                raise FileNotFoundError("Could not find the project root folder.")


            try:
                ROOT_DIR = find_project_root(Path.cwd())
            except FileNotFoundError:
                ROOT_DIR = Path.cwd() / "POLI3148_PS1"
                if not (ROOT_DIR / "code" / "project_utils.py").exists():
                    subprocess.run(["git", "clone", REPO_URL, str(ROOT_DIR)], check=True)

            CODE_DIR = ROOT_DIR / "code"
            DATA_DIR = ROOT_DIR / "data"
            if str(CODE_DIR) not in sys.path:
                sys.path.insert(0, str(CODE_DIR))

            from project_utils import (
                prepare_analysis_data,
            )

            RAW_DATA_PATH = DATA_DIR / "ACLED Data_MENA_Raw.csv"
            PROCESSED_PATH = DATA_DIR / "acled_mena_processed.csv"
            YEARLY_SUMMARY_PATH = DATA_DIR / "yearly_shift_summary.csv"
            SPATIAL_SUMMARY_PATH = DATA_DIR / "spatial_bucket_summary.csv"
            COUNTRY_SUMMARY_PATH = DATA_DIR / "country_pattern_summary.csv"

            if not RAW_DATA_PATH.exists():
                raise FileNotFoundError(f"Raw data file not found: {RAW_DATA_PATH}")
            if RAW_DATA_PATH.read_text(errors="ignore", encoding="utf-8")[:80].startswith("version https://git-lfs"):
                raise RuntimeError(
                    "The raw CSV is still a Git LFS pointer. Run `git lfs pull` in the project folder, "
                    "or download the LFS files from GitHub before running the cleaning notebook."
                )

            RAW_DATA_PATH
            """
        ),
        markdown_cell(
            """
            ## Step 1: Load, filter, and classify events

            `prepare_analysis_data()` performs the shared cleaning logic:

            - loads the raw ACLED CSV,
            - keeps `Middle East` and `Northern Africa`,
            - drops rows missing core fields,
            - parses dates,
            - creates capital-area and remote-violence indicators,
            - calculates distance to international land borders using Natural Earth boundaries,
            - creates border-proximate and spatial-bucket variables.
            """
        ),
        code_cell(
            """
            processed = prepare_analysis_data()
            processed.to_csv(PROCESSED_PATH, index=False)

            processed.shape, PROCESSED_PATH
            """
        ),
        markdown_cell(
            """
            ## Step 2: Create the report sample

            The processed event-level file keeps the cleaned event records. The final report's analytical sample excludes 2025 and uses 1997-2024, matching the text and published webpage.
            """
        ),
        code_cell(
            """
            report_df = processed[processed["year"].between(1997, 2024)].copy()

            {
                "processed_rows": len(processed),
                "report_rows_1997_2024": len(report_df),
                "min_year": int(report_df["year"].min()),
                "max_year": int(report_df["year"].max()),
            }
            """
        ),
        markdown_cell(
            """
            ## Step 3: Build and write summary CSV files

            I create three summary files from `report_df` so the report can use smaller, interpretable tables instead of recalculating everything from the event-level dataset each time.
            """
        ),
        markdown_cell(
            """
            ### 3.1 Yearly summary

            I group events by `year` to count the main event categories used in the trend figures: all events, battles, remote violence, air/drone strikes, capital-area remote attacks, and border-proximate battles. I then calculate percentage columns by dividing each focal count by its relevant yearly denominator.
            """
        ),
        code_cell(
            """
            years = pd.Index(
                range(int(report_df["year"].min()), int(report_df["year"].max()) + 1),
                name="year",
            )
            yearly = pd.DataFrame(index=years)

            yearly["all_events"] = report_df.groupby("year").size()
            yearly["all_battles"] = report_df[report_df["is_battle"]].groupby("year").size()
            yearly["all_remote_events"] = report_df[report_df["is_remote"]].groupby("year").size()
            yearly["drone_events"] = report_df[
                report_df["sub_event_type"].eq("Air/drone strike")
            ].groupby("year").size()
            yearly["capital_remote_events"] = report_df[
                report_df["capital_remote_event"]
            ].groupby("year").size()
            yearly["border_battle_events"] = report_df[
                report_df["border_battle_event"]
            ].groupby("year").size()
            yearly["capital_remote_fatalities"] = report_df[
                report_df["capital_remote_event"]
            ].groupby("year")["fatalities"].sum()
            yearly["border_battle_fatalities"] = report_df[
                report_df["border_battle_event"]
            ].groupby("year")["fatalities"].sum()

            yearly = yearly.fillna(0).astype(int).reset_index()
            yearly["capital_share_of_remote_pct"] = (
                yearly["capital_remote_events"] / yearly["all_remote_events"].replace(0, pd.NA) * 100
            ).fillna(0).round(2)
            yearly["border_share_of_battles_pct"] = (
                yearly["border_battle_events"] / yearly["all_battles"].replace(0, pd.NA) * 100
            ).fillna(0).round(2)
            yearly["drone_share_of_remote_pct"] = (
                yearly["drone_events"] / yearly["all_remote_events"].replace(0, pd.NA) * 100
            ).fillna(0).round(2)

            yearly.to_csv(YEARLY_SUMMARY_PATH, index=False)
            yearly.head()
            """
        ),
        markdown_cell(
            """
            ### 3.2 Spatial-bucket summary

            I group events by `spatial_bucket` to compare capital areas, border-proximate areas, and other areas. For each bucket, I count total events, fatalities, remote events, and battles, then calculate the share of events in that bucket that are remote violence or battles.
            """
        ),
        code_cell(
            """
            spatial = (
                report_df.groupby("spatial_bucket")
                .agg(
                    events=("event_id_cnty", "count"),
                    fatalities=("fatalities", "sum"),
                    remote_events=("is_remote", "sum"),
                    battles=("is_battle", "sum"),
                )
                .reset_index()
            )
            spatial["remote_share_pct"] = (
                spatial["remote_events"] / spatial["events"] * 100
            ).round(2)
            spatial["battle_share_pct"] = (
                spatial["battles"] / spatial["events"] * 100
            ).round(2)
            spatial = spatial.sort_values("events", ascending=False)

            spatial.to_csv(SPATIAL_SUMMARY_PATH, index=False)
            spatial
            """
        ),
        markdown_cell(
            """
            ### 3.3 Country-level summary

            I group events by `country` to compare how conflict patterns vary across countries. For each country, I calculate total events, remote events, capital-area remote attacks, border-proximate battles, fatalities, and two percentage measures: remote events as a share of all events, and capital-area remote attacks as a share of remote events.
            """
        ),
        code_cell(
            """
            country = (
                report_df.groupby("country")
                .agg(
                    total_events=("event_id_cnty", "count"),
                    remote_events=("is_remote", "sum"),
                    capital_remote_events=("capital_remote_event", "sum"),
                    border_battle_events=("border_battle_event", "sum"),
                    fatalities=("fatalities", "sum"),
                )
                .reset_index()
            )
            country["remote_share_pct"] = (
                country["remote_events"] / country["total_events"] * 100
            ).round(2)
            country["capital_remote_share_pct"] = (
                country["capital_remote_events"] / country["remote_events"].replace(0, pd.NA) * 100
            ).fillna(0).round(2)
            country = country.sort_values("total_events", ascending=False)

            country.to_csv(COUNTRY_SUMMARY_PATH, index=False)
            country.head()
            """
        ),
        markdown_cell(
            """
            ### 3.4 Output paths

            I display the output paths to confirm where the three summary CSV files were written.
            """
        ),
        code_cell(
            """
            [YEARLY_SUMMARY_PATH, SPATIAL_SUMMARY_PATH, COUNTRY_SUMMARY_PATH]
            """
        ),
        markdown_cell(
            """
            ## Step 4: Sanity checks

            These checks reproduce the headline counts cited in the report.
            """
        ),
        code_cell(
            """
            checks = {
                "all_events_1997_2024": len(report_df),
                "border_proximate_events": int(report_df["is_border_proximate"].sum()),
                "capital_area_events": int(report_df["is_capital_area"].sum()),
                "overlap_events": int((report_df["is_border_proximate"] & report_df["is_capital_area"]).sum()),
                "noncapital_border_proximate_events": int((report_df["is_border_proximate"] & ~report_df["is_capital_area"]).sum()),
                "capital_remote_events": int(report_df["capital_remote_event"].sum()),
            }

            checks
            """
        ),
        code_cell(
            """
            yearly.tail()
            """
        ),
    ]
)


ANALYSIS_NOTEBOOK = notebook(
    [
        markdown_cell(
            """
            # 02 Analysis

            This notebook uses the processed data and summary CSV files to reproduce the core analysis behind the interactive report in `docs/index.html`.
            """
        ),
        code_cell(
            """
            from pathlib import Path
            import subprocess
            import sys

            import pandas as pd
            import plotly.graph_objects as go

            REPO_URL = "https://github.com/lexieliujy/POLI3148_PS1.git"


            def find_project_root(start: Path) -> Path:
                for candidate in [start, *start.parents]:
                    if (candidate / "code" / "project_utils.py").exists() and (candidate / "data").exists():
                        return candidate
                raise FileNotFoundError("Could not find the project root folder.")


            try:
                ROOT_DIR = find_project_root(Path.cwd())
            except FileNotFoundError:
                ROOT_DIR = Path.cwd() / "POLI3148_PS1"
                if not (ROOT_DIR / "code" / "project_utils.py").exists():
                    subprocess.run(["git", "clone", REPO_URL, str(ROOT_DIR)], check=True)

            CODE_DIR = ROOT_DIR / "code"
            DATA_DIR = ROOT_DIR / "data"
            if str(CODE_DIR) not in sys.path:
                sys.path.insert(0, str(CODE_DIR))

            from project_utils import build_geography_map_figure

            processed = pd.read_csv(DATA_DIR / "acled_mena_processed.csv", parse_dates=["event_date"])
            yearly = pd.read_csv(DATA_DIR / "yearly_shift_summary.csv")
            spatial = pd.read_csv(DATA_DIR / "spatial_bucket_summary.csv")
            country = pd.read_csv(DATA_DIR / "country_pattern_summary.csv")

            if processed.empty:
                raise RuntimeError("Processed data loaded as empty; check the data files.")

            report_df = processed[processed["year"].between(1997, 2024)].copy()
            report_df.shape
            """
        ),
        markdown_cell(
            """
            ## Research question

            Has the rise of drones and other remote attacks in the Middle East and North Africa been accompanied by a spatial shift from border-proximate conflict toward attacks on capital areas?

            The analysis is descriptive rather than causal: it evaluates whether the observed spatial distribution of events is consistent with a shift toward capital targeting.
            """
        ),
        code_cell(
            """
            headline = {
                "all_events": len(report_df),
                "border_proximate_events": int(report_df["is_border_proximate"].sum()),
                "border_proximate_share_pct": round(report_df["is_border_proximate"].mean() * 100, 2),
                "capital_area_events": int(report_df["is_capital_area"].sum()),
                "capital_area_share_pct": round(report_df["is_capital_area"].mean() * 100, 2),
                "capital_remote_events": int(report_df["capital_remote_event"].sum()),
                "capital_remote_share_of_remote_pct": round(
                    report_df["capital_remote_event"].sum() / report_df["is_remote"].sum() * 100, 2
                ),
            }

            headline
            """
        ),
        markdown_cell(
            """
            ## Figure 1: Within remote attacks

            Border-proximate remote violence remains much more common than capital-area remote violence across most of the period.
            """
        ),
        code_cell(
            """
            remote_yearly = (
                report_df.groupby("year")
                .agg(
                    all_remote_events=("is_remote", "sum"),
                    border_remote_events=("is_border_proximate", lambda x: int((x & report_df.loc[x.index, "is_remote"]).sum())),
                    capital_remote_events=("capital_remote_event", "sum"),
                )
                .reset_index()
            )
            remote_yearly["border_remote_share_pct"] = (
                remote_yearly["border_remote_events"] / remote_yearly["all_remote_events"] * 100
            ).round(2)
            remote_yearly["capital_remote_share_pct"] = (
                remote_yearly["capital_remote_events"] / remote_yearly["all_remote_events"] * 100
            ).round(2)

            fig1 = go.Figure()
            fig1.add_trace(
                go.Scatter(
                    x=remote_yearly["year"],
                    y=remote_yearly["border_remote_share_pct"],
                    mode="lines+markers",
                    name="Border-proximate share of remote attacks",
                    line={"color": "#1f4e79", "width": 3.2},
                )
            )
            fig1.add_trace(
                go.Scatter(
                    x=remote_yearly["year"],
                    y=remote_yearly["capital_remote_share_pct"],
                    mode="lines+markers",
                    name="Capital-area share of remote attacks",
                    line={"color": "#c44536", "width": 3.0},
                )
            )
            fig1.update_layout(
                title="Within remote attacks, border-proximate share remains above capital-area share",
                template="plotly_white",
                xaxis_title="Year",
                yaxis_title="Share (%)",
                legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
            )
            fig1.show()
            """
        ),
        markdown_cell(
            """
            ## Figure 2: Yearly all-event denominator

            This figure uses yearly shares of all events. The blue segment uses non-capital border-proximate events so the stacked bars do not double-count locations that are both capital-area and border-proximate.
            """
        ),
        code_cell(
            """
            yearly_geo = (
                report_df.assign(noncapital_border=report_df["is_border_proximate"] & ~report_df["is_capital_area"])
                .groupby("year")
                .agg(
                    all_events=("event_id_cnty", "count"),
                    noncapital_border_events=("noncapital_border", "sum"),
                    capital_area_events=("is_capital_area", "sum"),
                )
                .reset_index()
            )
            yearly_geo["noncapital_border_share_pct"] = (
                yearly_geo["noncapital_border_events"] / yearly_geo["all_events"] * 100
            ).round(2)
            yearly_geo["capital_area_share_pct"] = (
                yearly_geo["capital_area_events"] / yearly_geo["all_events"] * 100
            ).round(2)

            fig2 = go.Figure()
            fig2.add_trace(
                go.Bar(
                    x=yearly_geo["year"],
                    y=yearly_geo["noncapital_border_share_pct"],
                    name="Non-capital border-proximate share",
                    marker={"color": "#1f4e79"},
                )
            )
            fig2.add_trace(
                go.Bar(
                    x=yearly_geo["year"],
                    y=yearly_geo["capital_area_share_pct"],
                    name="Capital-area share",
                    marker={"color": "#c44536"},
                )
            )
            fig2.update_layout(
                title="Yearly all-event shares: border-proximate space remains heavier than capital space",
                template="plotly_white",
                barmode="stack",
                xaxis_title="Year",
                yaxis_title="Share of all events (%)",
                legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
            )
            fig2.show()
            """
        ),
        markdown_cell(
            """
            ## Summary tables

            The summary CSV files provide the aggregate values used in the report narrative.
            """
        ),
        code_cell(
            """
            spatial
            """
        ),
        code_cell(
            """
            country.head(10)
            """
        ),
        markdown_cell(
            """
            ## Figure 4 map

            The published HTML report uses a simplified yearly map slider. The helper below builds the full Plotly map from the processed event-level data.
            """
        ),
        code_cell(
            """
            # This can be browser-heavy because it plots event-level geography.
            # Uncomment to render inside the notebook.
            # build_geography_map_figure(report_df).show()
            """
        ),
        markdown_cell(
            """
            ## Conclusion

            The evidence supports one stable conclusion: border-linked space remains the heavier conflict geography in MENA relative to capital space. The data do not support a simple regional story in which conflict moved from borders to capitals.
            """
        ),
    ]
)


def write_notebook(path: Path, contents: dict) -> None:
    path.write_text(json.dumps(contents, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote notebook to {path}")


def main() -> None:
    output_dir = Path(__file__).resolve().parent
    write_notebook(output_dir / "01_data_cleaning.ipynb", DATA_CLEANING_NOTEBOOK)
    write_notebook(output_dir / "02_analysis.ipynb", ANALYSIS_NOTEBOOK)


if __name__ == "__main__":
    main()
