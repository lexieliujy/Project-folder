from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Dict
from functools import lru_cache

VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
if VENDOR_DIR.exists():
    sys.path.append(str(VENDOR_DIR))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = ROOT_DIR / "docs"
RAW_DATA_PATH = DATA_DIR / "ACLED Data_MENA_Raw.csv"
BOUNDARY_DATA_PATH = DATA_DIR / "support" / "ne_50m_admin_0_countries.zip"
TARGET_REGIONS = ["Middle East", "Northern Africa"]
BORDER_DISTANCE_KM = 50

CAPITALS_BY_COUNTRY: Dict[str, str] = {
    "Algeria": "Algiers",
    "Bahrain": "Manama",
    "Egypt": "Cairo",
    "Iran": "Tehran",
    "Iraq": "Baghdad",
    "Israel": "Jerusalem",
    "Jordan": "Amman",
    "Kuwait": "Kuwait City",
    "Lebanon": "Beirut",
    "Libya": "Tripoli",
    "Morocco": "Rabat",
    "Oman": "Muscat",
    "Saudi Arabia": "Riyadh",
    "Sudan": "Khartoum",
    "Syria": "Damascus",
    "Turkey": "Ankara",
    "Tunisia": "Tunis",
    "United Arab Emirates": "Abu Dhabi",
    "Yemen": "Sanaa",
}

REQUIRED_COLUMNS = [
    "event_date",
    "year",
    "event_type",
    "sub_event_type",
    "country",
    "admin1",
    "location",
    "latitude",
    "longitude",
    "notes",
    "fatalities",
]

BORDER_PATTERN = re.compile(
    r"\bborder\b|cross-border|cross border|frontier|boundary|border crossing",
    re.IGNORECASE,
)

PALETTE = {
    "capital_remote": "#c44536",
    "border_battles": "#1f4e79",
    "remote_total": "#d98b5f",
    "other": "#6c7a89",
    "civilians": "#d8a47f",
}


def load_raw_data() -> pd.DataFrame:
    return pd.read_csv(RAW_DATA_PATH)


def _is_capital_area(row: pd.Series) -> bool:
    capital = CAPITALS_BY_COUNTRY.get(row["country"])
    if not capital or pd.isna(row["location"]):
        return False
    location = str(row["location"])
    return location == capital or location.startswith(f"{capital} -")


def prepare_analysis_data() -> pd.DataFrame:
    df = load_raw_data().copy()
    df = df[df["region"].isin(TARGET_REGIONS)].copy()
    df = df.dropna(subset=REQUIRED_COLUMNS).copy()
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df = df.dropna(subset=["event_date"]).copy()
    df["notes"] = df["notes"].astype(str)
    df["capital_city"] = df["country"].map(CAPITALS_BY_COUNTRY)
    df["is_capital_area"] = df.apply(_is_capital_area, axis=1)
    df["is_border_mentioned"] = df["notes"].str.contains(BORDER_PATTERN, regex=True)
    df["is_remote"] = df["event_type"].eq("Explosions/Remote violence")
    df["is_battle"] = df["event_type"].eq("Battles")
    df["border_distance_km"] = _compute_border_distance_km(df)
    df["is_border_proximate"] = df["border_distance_km"].le(BORDER_DISTANCE_KM)
    df["capital_remote_event"] = df["is_capital_area"] & df["is_remote"]
    df["border_battle_event"] = df["is_border_proximate"] & df["is_battle"]
    df["capital_targeting_proxy"] = df["capital_remote_event"].map({True: "Yes", False: "No"})
    df["border_clash_proxy"] = df["border_battle_event"].map({True: "Yes", False: "No"})
    df["spatial_bucket"] = "Other areas"
    df.loc[df["is_border_proximate"], "spatial_bucket"] = "Border-proximate areas"
    df.loc[df["is_capital_area"], "spatial_bucket"] = "Capital areas"
    return df


def _load_mena_country_geometries() -> gpd.GeoDataFrame:
    world = gpd.read_file(f"zip://{BOUNDARY_DATA_PATH}")[["ADMIN", "geometry"]].copy()
    world = world.rename(columns={"ADMIN": "country_name"})
    mena_countries = list(CAPITALS_BY_COUNTRY.keys()) + ["Palestine"]
    world = world[world["country_name"].isin(mena_countries)].copy()
    world = world.dissolve(by="country_name", as_index=False)
    return world.to_crs(3395)


@lru_cache(maxsize=1)
def _load_world_geojson() -> dict:
    world = gpd.read_file(f"zip://{BOUNDARY_DATA_PATH}")[["ADMIN", "geometry"]].copy()
    world = world.rename(columns={"ADMIN": "country_name"})
    return json.loads(world.to_json())


def _build_country_border_lines() -> dict[str, object]:
    countries = _load_mena_country_geometries()
    border_lines: dict[str, object] = {}
    for _, row in countries.iterrows():
        country = row["country_name"]
        own_geometry = row.geometry
        neighbors_union = countries.loc[countries["country_name"] != country, "geometry"].union_all()
        border_lines[country] = own_geometry.boundary.intersection(neighbors_union)
    return border_lines


def _compute_border_distance_km(df: pd.DataFrame) -> pd.Series:
    border_lines = _build_country_border_lines()
    name_map = {"Palestine": "Palestine"}
    geo_df = gpd.GeoDataFrame(
        df[["country", "longitude", "latitude"]].copy(),
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326",
    ).to_crs(3395)
    distances = pd.Series(index=df.index, dtype="float64")
    for country in sorted(df["country"].dropna().unique()):
        border_country = name_map.get(country, country)
        border_geometry = border_lines.get(border_country)
        idx = geo_df["country"].eq(country)
        if border_geometry is None or border_geometry.is_empty:
            distances.loc[idx] = float("inf")
        else:
            distances.loc[idx] = geo_df.loc[idx, "geometry"].distance(border_geometry) / 1000.0
    return distances


def summarize_yearly(df: pd.DataFrame) -> pd.DataFrame:
    years = pd.Index(range(int(df["year"].min()), int(df["year"].max()) + 1), name="year")
    yearly = pd.DataFrame(index=years)
    yearly["all_events"] = df.groupby("year").size()
    yearly["all_battles"] = df[df["is_battle"]].groupby("year").size()
    yearly["all_remote_events"] = df[df["is_remote"]].groupby("year").size()
    yearly["drone_events"] = (
        df[df["sub_event_type"].eq("Air/drone strike")].groupby("year").size()
    )
    yearly["capital_remote_events"] = df[df["capital_remote_event"]].groupby("year").size()
    yearly["border_battle_events"] = df[df["border_battle_event"]].groupby("year").size()
    yearly["capital_remote_fatalities"] = (
        df[df["capital_remote_event"]].groupby("year")["fatalities"].sum()
    )
    yearly["border_battle_fatalities"] = (
        df[df["border_battle_event"]].groupby("year")["fatalities"].sum()
    )
    yearly = yearly.fillna(0).astype(int).reset_index()
    yearly["capital_share_of_remote_pct"] = yearly.apply(
        lambda row: round(100 * row["capital_remote_events"] / row["all_remote_events"], 2)
        if row["all_remote_events"]
        else 0.0,
        axis=1,
    )
    yearly["border_share_of_battles_pct"] = yearly.apply(
        lambda row: round(100 * row["border_battle_events"] / row["all_battles"], 2)
        if row["all_battles"]
        else 0.0,
        axis=1,
    )
    yearly["drone_share_of_remote_pct"] = yearly.apply(
        lambda row: round(100 * row["drone_events"] / row["all_remote_events"], 2)
        if row["all_remote_events"]
        else 0.0,
        axis=1,
    )
    return yearly


def summarize_spatial_bucket(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("spatial_bucket")
        .agg(
            events=("event_id_cnty", "count"),
            fatalities=("fatalities", "sum"),
            remote_events=("is_remote", "sum"),
            battles=("is_battle", "sum"),
        )
        .reset_index()
    )
    summary["remote_share_pct"] = (summary["remote_events"] / summary["events"] * 100).round(2)
    summary["battle_share_pct"] = (summary["battles"] / summary["events"] * 100).round(2)
    return summary.sort_values("events", ascending=False)


def summarize_country_patterns(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("country")
        .agg(
            total_events=("event_id_cnty", "count"),
            remote_events=("is_remote", "sum"),
            capital_remote_events=("capital_remote_event", "sum"),
            border_battle_events=("border_battle_event", "sum"),
            fatalities=("fatalities", "sum"),
        )
        .reset_index()
    )
    grouped["remote_share_pct"] = (grouped["remote_events"] / grouped["total_events"] * 100).round(2)
    capital_share = grouped["capital_remote_events"] / grouped["remote_events"].replace(0, pd.NA) * 100
    grouped["capital_remote_share_pct"] = capital_share.fillna(0).round(2)
    return grouped.sort_values("total_events", ascending=False)


def build_trend_figure(yearly: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=yearly["year"],
            y=yearly["border_battle_events"],
            mode="lines+markers",
            name="Border-proximate battles",
            line={"color": PALETTE["border_battles"], "width": 3},
            marker={"size": 6},
            hovertemplate="Year %{x}<br>Events %{y}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=yearly["year"],
            y=yearly["capital_remote_events"],
            mode="lines+markers",
            name="Capital-area remote attacks",
            line={"color": PALETTE["capital_remote"], "width": 3},
            marker={"size": 6},
            hovertemplate="Year %{x}<br>Events %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Border-proximate battles remain more common than capital-area remote attacks",
        template="plotly_white",
        height=430,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        margin={"l": 40, "r": 20, "t": 70, "b": 45},
        xaxis_title="Year",
        yaxis_title="Recorded events",
    )
    return fig


def build_remote_growth_figure(yearly: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=yearly["year"],
            y=yearly["drone_events"],
            name="Air/drone strikes",
            marker_color=PALETTE["capital_remote"],
            opacity=0.82,
            hovertemplate="Year %{x}<br>Drone events %{y}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=yearly["year"],
            y=yearly["all_remote_events"],
            mode="lines+markers",
            name="All remote violence events",
            line={"color": PALETTE["border_battles"], "width": 3},
            marker={"size": 6},
            hovertemplate="Year %{x}<br>Remote events %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Drone strikes and remote violence both rise sharply over time in MENA",
        template="plotly_white",
        height=430,
        margin={"l": 40, "r": 20, "t": 70, "b": 45},
        xaxis_title="Year",
        yaxis_title="Recorded events",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
    )
    return fig


def build_share_figure(yearly: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=yearly["year"],
            y=yearly["border_share_of_battles_pct"],
            name="Border-proximate share of all battles",
            mode="lines+markers",
            line={"color": PALETTE["border_battles"], "width": 3},
            marker={"size": 7},
            hovertemplate="Year %{x}<br>%{y}% of battles<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=yearly["year"],
            y=yearly["capital_share_of_remote_pct"],
            mode="lines+markers",
            name="Capital-area share of all remote attacks",
            line={"color": PALETTE["capital_remote"], "width": 3},
            marker={"size": 7},
            hovertemplate="Year %{x}<br>%{y}% of remote events<extra></extra>",
        )
    )
    fig.update_layout(
        title="Neither share shows a clean shift from border conflict to capital targeting",
        template="plotly_white",
        height=430,
        margin={"l": 40, "r": 20, "t": 70, "b": 45},
        xaxis_title="Year",
        yaxis={"title": "Share (%)"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
    )
    return fig


def build_spatial_composition_figure(df: pd.DataFrame) -> go.Figure:
    composition = (
        pd.crosstab(df["spatial_bucket"], df["event_type"], normalize="index")
        .mul(100)
        .reset_index()
        .melt(id_vars="spatial_bucket", var_name="event_type", value_name="share_pct")
    )
    fig = px.bar(
        composition,
        x="spatial_bucket",
        y="share_pct",
        color="event_type",
        barmode="stack",
        category_orders={
            "spatial_bucket": ["Capital areas", "Border-proximate areas", "Other areas"]
        },
        color_discrete_map={
            "Battles": PALETTE["border_battles"],
            "Explosions/Remote violence": PALETTE["capital_remote"],
            "Violence against civilians": PALETTE["civilians"],
        },
        labels={
            "spatial_bucket": "",
            "share_pct": "Share of events (%)",
            "event_type": "Event type",
        },
        title="Capital areas are more remote than the rest of the region, but not dominant",
    )
    fig.update_layout(
        template="plotly_white",
        height=420,
        margin={"l": 40, "r": 20, "t": 70, "b": 45},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
    )
    fig.update_traces(hovertemplate="%{x}<br>%{fullData.name}: %{y:.1f}%<extra></extra>")
    return fig


def build_map_figure(df: pd.DataFrame) -> go.Figure:
    plot_df = df[df["capital_remote_event"] | df["border_battle_event"]].copy()
    plot_df["map_category"] = "Border-proximate battles"
    plot_df.loc[plot_df["capital_remote_event"], "map_category"] = "Capital-area remote attacks"
    plot_df["display_fatalities"] = plot_df["fatalities"].clip(lower=0).fillna(0)
    plot_df["marker_size"] = (
        plot_df["display_fatalities"].clip(upper=400).pow(0.5) * 1.6 + 7
    ).round(1)

    capital_points = []
    for country, capital in CAPITALS_BY_COUNTRY.items():
        capital_rows = df[
            (df["country"] == country)
            & (
                df["location"].astype(str).eq(capital)
                | df["location"].astype(str).str.startswith(f"{capital} -")
            )
        ][["latitude", "longitude"]].drop_duplicates()
        if len(capital_rows):
            point = capital_rows.iloc[0].to_dict()
            point["country"] = country
            point["capital"] = capital
            capital_points.append(point)
    capitals_df = pd.DataFrame(capital_points)
    world_geojson = _load_world_geojson()
    fig = go.Figure()
    fig.add_trace(
        go.Choroplethmap(
            geojson=world_geojson,
            locations=[feature["properties"]["country_name"] for feature in world_geojson["features"]],
            z=[1] * len(world_geojson["features"]),
            featureidkey="properties.country_name",
            colorscale=[[0, "#f7f3eb"], [1, "#f7f3eb"]],
            showscale=False,
            hoverinfo="skip",
            marker={"line": {"color": "#6b7280", "width": 1.0}},
            name="Country borders",
            showlegend=False,
        )
    )
    for category, color in [
        ("Capital-area remote attacks", PALETTE["capital_remote"]),
        ("Border-proximate battles", PALETTE["border_battles"]),
    ]:
        sub = plot_df[plot_df["map_category"] == category].copy()
        fig.add_trace(
            go.Scattermap(
                lat=sub["latitude"],
                lon=sub["longitude"],
                mode="markers",
                name=category,
                customdata=sub[
                    ["country", "year", "event_type", "sub_event_type", "fatalities", "border_distance_km"]
                ],
                text=sub["location"],
                hovertemplate=(
                    "%{text}<br>%{customdata[0]}<br>Year %{customdata[1]}"
                    "<br>%{customdata[2]} | %{customdata[3]}"
                    "<br>Fatalities %{customdata[4]}"
                    "<br>Border distance %{customdata[5]:.1f} km<extra></extra>"
                ),
                marker={
                    "size": sub["marker_size"],
                    "color": color,
                    "opacity": 0.62,
                },
            )
        )
    if not capitals_df.empty:
        fig.add_trace(
            go.Scattermap(
                lat=capitals_df["latitude"],
                lon=capitals_df["longitude"],
                text=[""] * len(capitals_df),
                mode="markers",
                name="Capital cities",
                textposition="top center",
                hovertemplate="%{customdata[1]}<br>%{customdata[0]}<extra></extra>",
                customdata=capitals_df[["country", "capital"]],
                marker={
                    "size": 11,
                    "symbol": "diamond",
                    "color": "#111827",
                },
                textfont={"size": 10, "color": "#111827"},
            )
        )
    fig.update_layout(
        template="plotly_white",
        height=560,
        margin={"l": 20, "r": 20, "t": 70, "b": 20},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        title="Spatial contrast between capital-area remote attacks and border-proximate battles",
        map={
            "style": "white-bg",
            "center": {"lat": 31, "lon": 31},
            "zoom": 3.05,
            "bearing": 0,
            "pitch": 0,
        },
    )
    return fig


def build_country_table(df: pd.DataFrame) -> pd.DataFrame:
    table = df.groupby("country").agg(
        capital_remote_events=("capital_remote_event", "sum"),
        border_battle_events=("border_battle_event", "sum"),
        remote_events=("is_remote", "sum"),
        total_events=("event_id_cnty", "count"),
    )
    table = table.reset_index().sort_values(
        ["capital_remote_events", "border_battle_events", "total_events"],
        ascending=[False, False, False],
    )
    return table


def export_processed_files(df: pd.DataFrame, yearly: pd.DataFrame) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    processed = df.copy()
    processed["event_date"] = processed["event_date"].dt.strftime("%Y-%m-%d")
    processed.to_csv(DATA_DIR / "acled_mena_processed.csv", index=False)
    yearly.to_csv(DATA_DIR / "yearly_shift_summary.csv", index=False)
    summarize_spatial_bucket(df).to_csv(DATA_DIR / "spatial_bucket_summary.csv", index=False)
    summarize_country_patterns(df).to_csv(DATA_DIR / "country_pattern_summary.csv", index=False)
