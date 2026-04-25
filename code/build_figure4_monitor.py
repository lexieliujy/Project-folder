from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


REPORT_START_DATE = "1997-01-01"
REPORT_END_DATE = "2024-12-31"
DEFAULT_START_DATE = "2024-01-01"
DEFAULT_END_DATE = REPORT_END_DATE

DATA_JS_NAME = "figure4_monitor_data.js"
HTML_NAME = "figure4_monitor_map.html"

CATEGORY_ORDER = ["Capital-area events", "Border-proximate events"]
CATEGORY_COLORS = {
    "Capital-area events": "#c44536",
    "Border-proximate events": "#1f4e79",
}


def build_monitor_points(data_dir: Path) -> tuple[list[dict], dict]:
    usecols = [
        "event_date",
        "country",
        "location",
        "latitude",
        "longitude",
        "event_type",
        "sub_event_type",
        "fatalities",
        "border_distance_km",
        "is_capital_area",
        "is_border_proximate",
    ]
    df = pd.read_csv(data_dir / "acled_mena_processed.csv", usecols=usecols, parse_dates=["event_date"])
    df = df[
        df["event_date"].between(REPORT_START_DATE, REPORT_END_DATE)
        & (df["is_capital_area"] | df["is_border_proximate"])
    ].copy()

    df["map_category"] = "Border-proximate events"
    df.loc[df["is_capital_area"], "map_category"] = "Capital-area events"
    df["week"] = df["event_date"].dt.to_period("W-SUN").dt.start_time.dt.strftime("%Y-%m-%d")
    df["fatalities"] = df["fatalities"].fillna(0).astype(int)
    df["border_distance_km"] = df["border_distance_km"].fillna(-1).round(1)
    df["latitude"] = df["latitude"].round(4)
    df["longitude"] = df["longitude"].round(4)

    group_cols = [
        "week",
        "country",
        "location",
        "latitude",
        "longitude",
        "map_category",
        "event_type",
        "sub_event_type",
    ]
    grouped = (
        df.groupby(group_cols, dropna=False)
        .agg(
            n=("event_date", "size"),
            fatalities=("fatalities", "sum"),
            border_distance_km=("border_distance_km", "min"),
        )
        .reset_index()
        .sort_values(["week", "country", "location", "map_category"])
    )

    points = [
        {
            "w": row.week,
            "c": row.country,
            "l": row.location,
            "lat": row.latitude,
            "lon": row.longitude,
            "cat": row.map_category,
            "eventType": row.event_type,
            "subType": row.sub_event_type,
            "n": int(row.n),
            "f": int(row.fatalities),
            "dist": None if row.border_distance_km < 0 else float(row.border_distance_km),
        }
        for row in grouped.itertuples(index=False)
    ]

    meta = {
        "startDate": REPORT_START_DATE,
        "endDate": REPORT_END_DATE,
        "defaultStartDate": DEFAULT_START_DATE,
        "defaultEndDate": DEFAULT_END_DATE,
        "sourceRows": int(len(df)),
        "pointRows": int(len(points)),
        "countries": sorted(df["country"].dropna().unique().tolist()),
        "categoryOrder": CATEGORY_ORDER,
        "categoryColors": CATEGORY_COLORS,
    }
    return points, meta


def build_country_geojson(data_dir: Path, country_names: list[str]) -> dict:
    boundary_path = data_dir / "support" / "ne_50m_admin_0_countries.zip"
    world = gpd.read_file(f"zip://{boundary_path}")[["ADMIN", "geometry"]].copy()
    world = world.rename(columns={"ADMIN": "name"})
    world = world[world["name"].isin(country_names)].dissolve(by="name", as_index=False)
    return json.loads(world.to_json())


def write_data_js(docs_dir: Path, payload: dict) -> Path:
    data_js_path = docs_dir / DATA_JS_NAME
    data_js_path.write_text(
        "window.FIGURE4_MONITOR_DATA = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    return data_js_path


def write_html(docs_dir: Path) -> Path:
    html_path = docs_dir / HTML_NAME
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Figure 4 Monitor Map</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    :root {
      --navy: #15314b;
      --navy-2: #1f4e79;
      --capital: #c44536;
      --border: #1f4e79;
      --ink: #1f2933;
      --line: #d9e1e8;
      --panel: rgba(255, 255, 255, 0.94);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      color: var(--ink);
      font-family: "Trebuchet MS", "Segoe UI", Arial, sans-serif;
      background: #fff;
    }

    .timeline-wrap {
      height: 224px;
      padding: 4px 18px 0;
      background: #fff;
      border-bottom: 1px solid var(--line);
    }

    #timeline {
      width: 100%;
      height: 100%;
    }

    .monitor {
      position: relative;
      height: 640px;
      min-height: 640px;
      overflow: hidden;
      background: #e7f0e2;
    }

    #map {
      width: 100%;
      height: 100%;
      background: #edf3eb;
    }

    .control-panel {
      position: absolute;
      top: 18px;
      left: 22px;
      z-index: 700;
      width: 360px;
      padding: 16px 18px;
      background: var(--panel);
      border: 1px solid rgba(160, 174, 192, 0.58);
      box-shadow: 0 16px 34px rgba(15, 23, 42, 0.16);
    }

    .control-title {
      margin: 0 0 8px;
      color: #111827;
      font-size: 1rem;
      font-weight: 800;
    }

    .date-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 12px;
    }

    .date-grid label {
      display: block;
      margin-bottom: 4px;
      font-weight: 700;
      font-size: 0.88rem;
    }

    input[type="date"] {
      width: 100%;
      border: 1px solid #cfd8e3;
      border-radius: 0;
      padding: 9px 10px;
      font-size: 0.92rem;
      background: #fff;
      color: #111827;
    }

    .link-btn {
      display: inline-block;
      border: 0;
      padding: 0;
      color: #111;
      background: transparent;
      text-decoration: underline;
      font-size: 0.92rem;
      font-weight: 800;
      cursor: pointer;
    }

    .status-badge {
      position: absolute;
      top: 18px;
      left: 50%;
      z-index: 700;
      transform: translateX(-50%);
      padding: 9px 14px;
      color: #fff;
      background: rgba(31, 78, 121, 0.94);
      font-size: 1rem;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.16);
      white-space: nowrap;
    }

    .legend-card {
      position: absolute;
      top: 18px;
      right: 22px;
      z-index: 700;
      width: 320px;
      padding: 16px;
      background: var(--panel);
      border: 1px solid rgba(160, 174, 192, 0.65);
      box-shadow: 0 16px 34px rgba(15, 23, 42, 0.16);
    }

    .legend-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      align-items: start;
    }

    .legend-title {
      margin: 0 0 10px;
      font-weight: 900;
      color: #111;
      font-size: 0.9rem;
    }

    .legend-item {
      display: grid;
      grid-template-columns: 18px 1fr auto;
      gap: 8px;
      align-items: center;
      margin-bottom: 10px;
      font-size: 0.84rem;
      font-weight: 800;
    }

    .dot {
      width: 18px;
      height: 18px;
      border-radius: 999px;
      display: inline-block;
    }

    .size-demo {
      position: relative;
      height: 112px;
    }

    .ring {
      position: absolute;
      left: 18px;
      bottom: 10px;
      border: 2px solid #22475f;
      border-radius: 999px;
      background: rgba(31, 78, 121, 0.08);
    }

    .ring-label {
      position: absolute;
      left: 106px;
      color: #111;
      font-size: 0.78rem;
    }

    .event-card {
      position: absolute;
      right: 22px;
      bottom: 22px;
      z-index: 700;
      width: 320px;
      color: #fff;
      background: var(--navy-2);
      box-shadow: 0 14px 34px rgba(15, 23, 42, 0.22);
    }

    .event-card h3 {
      margin: 0;
      padding: 12px 16px;
      font-size: 1rem;
    }

    .event-card .body {
      padding: 14px 16px 16px;
      background: #fff;
      color: #111827;
      display: grid;
      gap: 10px;
    }

    .metric-row {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      border-bottom: 1px solid #edf2f7;
      padding-bottom: 6px;
      font-weight: 700;
    }

    .leaflet-container {
      font-family: "Trebuchet MS", "Segoe UI", Arial, sans-serif;
    }

    .leaflet-popup-content {
      margin: 12px 14px;
      min-width: 220px;
      font-size: 0.9rem;
      line-height: 1.45;
    }

    .popup-title {
      font-weight: 900;
      margin-bottom: 6px;
      color: #102a43;
    }

    @media (max-width: 900px) {
      .timeline-wrap { height: 230px; padding: 0 6px; }
      .monitor { height: 780px; }
      .control-panel, .legend-card, .event-card {
        position: relative;
        left: auto;
        right: auto;
        top: auto;
        bottom: auto;
        width: auto;
        margin: 12px;
      }
      .status-badge {
        position: relative;
        left: auto;
        top: auto;
        transform: none;
        display: inline-block;
        margin: 12px;
        white-space: normal;
      }
    }
  </style>
</head>
<body>
  <section class="timeline-wrap">
    <div id="timeline"></div>
  </section>

  <section class="monitor">
    <div id="map"></div>

    <aside class="control-panel" aria-label="Map controls">
      <h2 class="control-title">Select date range</h2>
      <div class="date-grid">
        <div>
          <label for="from-date">From</label>
          <input id="from-date" type="date">
        </div>
        <div>
          <label for="to-date">To</label>
          <input id="to-date" type="date">
        </div>
      </div>
      <button id="reset-date" class="link-btn" type="button">Reset to 2024</button>
    </aside>

    <div id="status-badge" class="status-badge">Showing events in: MENA</div>

    <aside class="legend-card" aria-label="Map legend">
      <div class="legend-grid">
        <div>
          <h3 class="legend-title">Events</h3>
          <div id="color-legend"></div>
        </div>
        <div>
          <h3 class="legend-title">Number of Events</h3>
          <div class="size-demo">
            <span class="ring" style="width:70px;height:70px;"></span>
            <span class="ring" style="width:48px;height:48px;left:29px;"></span>
            <span class="ring" style="width:29px;height:29px;left:38px;"></span>
            <span class="ring" style="width:14px;height:14px;left:46px;"></span>
            <span class="ring-label" style="top:8px;">largest</span>
            <span class="ring-label" style="top:34px;">medium</span>
            <span class="ring-label" style="top:60px;">small</span>
            <span class="ring-label" style="top:86px;">1</span>
          </div>
        </div>
      </div>
    </aside>

    <aside class="event-card" aria-label="Event summary">
      <h3>Events</h3>
      <div id="event-summary" class="body"></div>
    </aside>
  </section>

  <script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="__DATA_JS__"></script>
  <script>
    (function() {
      const payload = window.FIGURE4_MONITOR_DATA;
      const points = payload.points;
      const meta = payload.meta;
      const categories = meta.categoryOrder;
      const colors = meta.categoryColors;
      const state = {
        from: meta.defaultStartDate,
        to: meta.defaultEndDate
      };

      const map = L.map("map", {
        preferCanvas: true,
        zoomControl: false,
        attributionControl: true
      }).setView([31.2, 35.5], 4);

      L.control.zoom({position: "bottomright"}).addTo(map);
      L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
        maxZoom: 10,
        minZoom: 3,
        attribution: "&copy; OpenStreetMap contributors &copy; CARTO"
      }).addTo(map);

      L.geoJSON(payload.countries, {
        interactive: false,
        style: {
          color: "#111827",
          weight: 1.05,
          opacity: 0.88,
          fillOpacity: 0
        }
      }).addTo(map);

      const markerLayer = L.layerGroup().addTo(map);
      const fromInput = document.getElementById("from-date");
      const toInput = document.getElementById("to-date");
      const badge = document.getElementById("status-badge");
      const eventSummary = document.getElementById("event-summary");
      const colorLegend = document.getElementById("color-legend");

      function addDays(dateString, days) {
        const d = new Date(`${dateString}T00:00:00`);
        d.setDate(d.getDate() + days);
        return d.toISOString().slice(0, 10);
      }

      function formatDate(dateString) {
        const d = new Date(`${dateString}T00:00:00`);
        return d.toLocaleDateString("en-US", {month: "short", day: "2-digit", year: "numeric"});
      }

      function setDateInputs() {
        fromInput.min = meta.startDate;
        fromInput.max = meta.endDate;
        toInput.min = meta.startDate;
        toInput.max = meta.endDate;
        fromInput.value = state.from;
        toInput.value = state.to;
      }

      function resetDateRange() {
        state.from = meta.defaultStartDate;
        state.to = meta.defaultEndDate;
        setDateInputs();
      }

      function filteredPoints(includeDateRange) {
        return points.filter((point) => {
          if (!includeDateRange) return true;
          return point.w >= state.from && point.w <= state.to;
        });
      }

      function aggregateMapRows(rows) {
        const grouped = new Map();
        rows.forEach((point) => {
          const key = `${point.lat}|${point.lon}|${point.cat}|${point.l}|${point.c}`;
          const current = grouped.get(key) || {
            lat: point.lat,
            lon: point.lon,
            location: point.l,
            country: point.c,
            category: point.cat,
            eventType: point.eventType,
            subType: point.subType,
            count: 0,
            fatalities: 0,
            dist: point.dist
          };
          current.count += point.n;
          current.fatalities += point.f;
          grouped.set(key, current);
        });
        return Array.from(grouped.values()).sort((a, b) => b.count - a.count);
      }

      function radiusFor(count) {
        return Math.max(4, Math.min(28, 3.8 + Math.sqrt(count) * 2.15));
      }

      function renderMap(rows) {
        markerLayer.clearLayers();
        const markerRows = aggregateMapRows(rows).slice(0, 18000);

        markerRows.forEach((row) => {
          const marker = L.circleMarker([row.lat, row.lon], {
            radius: radiusFor(row.count),
            color: "#ffffff",
            weight: 0.75,
            fillColor: colors[row.category],
            fillOpacity: 0.76,
            opacity: 0.92
          });
          const distanceText = row.dist === null ? "not available" : `${row.dist.toFixed(1)} km`;
          marker.bindPopup(`
            <div class="popup-title">${row.location}</div>
            <div>${row.country}</div>
            <div><strong>${row.category}</strong></div>
            <div>${row.eventType} | ${row.subType}</div>
            <div>Events: ${row.count.toLocaleString()}</div>
            <div>Fatalities: ${row.fatalities.toLocaleString()}</div>
            <div>Border distance: ${distanceText}</div>
          `);
          markerLayer.addLayer(marker);
        });
      }

      function buildWeekly(rows) {
        const weekly = new Map();
        rows.forEach((point) => {
          if (!weekly.has(point.w)) {
            weekly.set(point.w, Object.fromEntries(categories.map((category) => [category, 0])));
          }
          weekly.get(point.w)[point.cat] += point.n;
        });
        return Array.from(weekly.entries())
          .sort((a, b) => a[0].localeCompare(b[0]))
          .map(([week, values]) => ({week, ...values}));
      }

      function renderTimeline() {
        const weeklyRows = buildWeekly(filteredPoints(false));
        const traces = categories.map((category) => ({
          type: "bar",
          name: category,
          x: weeklyRows.map((row) => row.week),
          y: weeklyRows.map((row) => row[category]),
          marker: {color: colors[category]},
          hovertemplate: `Week of %{x}<br>${category}: %{y}<extra></extra>`
        }));

        Plotly.react("timeline", traces, {
          barmode: "stack",
          showlegend: false,
          margin: {l: 54, r: 18, t: 18, b: 42},
          paper_bgcolor: "#ffffff",
          plot_bgcolor: "#ffffff",
          xaxis: {
            title: {text: "Date (Week of)", font: {size: 13, color: "#111"}},
            showgrid: false,
            tickfont: {size: 11, color: "#111"},
            range: [meta.startDate, addDays(meta.endDate, 21)]
          },
          yaxis: {
            title: {text: "Count", font: {size: 13, color: "#111"}},
            gridcolor: "#d7e0ea",
            zeroline: false,
            tickfont: {size: 11, color: "#111"}
          },
          shapes: [{
            type: "rect",
            xref: "x",
            yref: "paper",
            x0: state.from,
            x1: state.to,
            y0: 0,
            y1: 1,
            fillcolor: "rgba(31, 78, 121, 0.10)",
            line: {color: "rgba(31, 78, 121, 0.42)", width: 1},
            layer: "below"
          }]
        }, {displayModeBar: false, responsive: true});

        const timeline = document.getElementById("timeline");
        timeline.on("plotly_click", (evt) => {
          const week = evt.points && evt.points[0] && evt.points[0].x;
          if (!week) return;
          state.from = week;
          state.to = addDays(week, 6);
          setDateInputs();
          renderAll();
        });
      }

      function renderLegend(counts) {
        colorLegend.innerHTML = categories.map((category) => `
          <div class="legend-item">
            <span class="dot" style="background:${colors[category]}"></span>
            <span>${category}</span>
            <span>${(counts[category] || 0).toLocaleString()}</span>
          </div>
        `).join("");
      }

      function renderSummary(rows) {
        const totals = {
          events: 0,
          fatalities: 0,
          countries: new Set(),
          locations: new Set()
        };
        const counts = Object.fromEntries(categories.map((category) => [category, 0]));

        rows.forEach((point) => {
          totals.events += point.n;
          totals.fatalities += point.f;
          totals.countries.add(point.c);
          totals.locations.add(`${point.c}|${point.l}|${point.lat}|${point.lon}`);
          counts[point.cat] += point.n;
        });

        eventSummary.innerHTML = `
          <div class="metric-row"><span>Total events</span><strong>${totals.events.toLocaleString()}</strong></div>
          <div class="metric-row"><span>Fatalities</span><strong>${totals.fatalities.toLocaleString()}</strong></div>
          <div class="metric-row"><span>Countries</span><strong>${totals.countries.size.toLocaleString()}</strong></div>
          <div class="metric-row"><span>Locations</span><strong>${totals.locations.size.toLocaleString()}</strong></div>
        `;
        renderLegend(counts);
      }

      function renderBadge(rows) {
        const totalEvents = rows.reduce((sum, point) => sum + point.n, 0);
        badge.textContent = `Showing events in: MENA | ${formatDate(state.from)} - ${formatDate(state.to)} | ${totalEvents.toLocaleString()} capital/border events`;
      }

      function renderAll() {
        const dateRows = filteredPoints(true);
        renderMap(dateRows);
        renderTimeline();
        renderSummary(dateRows);
        renderBadge(dateRows);
      }

      document.getElementById("reset-date").addEventListener("click", () => {
        resetDateRange();
        renderAll();
      });

      [fromInput, toInput].forEach((input) => {
        input.addEventListener("change", () => {
          state.from = fromInput.value || meta.startDate;
          state.to = toInput.value || meta.endDate;
          if (state.from > state.to) {
            const oldFrom = state.from;
            state.from = state.to;
            state.to = oldFrom;
          }
          setDateInputs();
          renderAll();
        });
      });

      resetDateRange();
      renderAll();
    })();
  </script>
</body>
</html>
"""
    html_path.write_text(html.replace("__DATA_JS__", DATA_JS_NAME), encoding="utf-8")
    return html_path


def build_figure4_monitor(root_dir: str | Path | None = None) -> dict[str, Path]:
    root = Path(root_dir) if root_dir is not None else Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    docs_dir = root / "docs"
    docs_dir.mkdir(exist_ok=True)

    points, meta = build_monitor_points(data_dir)
    countries = build_country_geojson(data_dir, meta["countries"])
    payload = {"meta": meta, "countries": countries, "points": points}

    data_js_path = write_data_js(docs_dir, payload)
    html_path = write_html(docs_dir)
    return {"html": html_path, "data": data_js_path}


if __name__ == "__main__":
    paths = build_figure4_monitor()
    print(f"Wrote {paths['html']}")
    print(f"Wrote {paths['data']}")
