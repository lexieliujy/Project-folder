from __future__ import annotations

from project_utils import (
    BORDER_DISTANCE_KM,
    DOCS_DIR,
    build_country_table,
    build_map_figure,
    build_remote_growth_figure,
    build_share_figure,
    build_spatial_composition_figure,
    export_processed_files,
    prepare_analysis_data,
    summarize_yearly,
)


def fig_block(
    fig, include_js: bool, div_id: str | None = None, scroll_zoom: bool = False
) -> str:
    return fig.to_html(
        full_html=False,
        include_plotlyjs="inline" if include_js else False,
        config={"displayModeBar": False, "responsive": True, "scrollZoom": scroll_zoom},
        div_id=div_id,
    )


def build_report_html() -> str:
    df = prepare_analysis_data()
    yearly = summarize_yearly(df)
    export_processed_files(df, yearly)

    remote_growth_html = fig_block(build_remote_growth_figure(yearly), include_js=True)
    share_html = fig_block(build_share_figure(yearly), include_js=False)
    composition_html = fig_block(build_spatial_composition_figure(df), include_js=False)
    map_html = fig_block(
        build_map_figure(df),
        include_js=False,
        div_id="mena-map-figure",
        scroll_zoom=True,
    )

    total_events = len(df)
    total_remote = int(df["is_remote"].sum())
    capital_remote = int(df["capital_remote_event"].sum())
    border_battles = int(df["border_battle_event"].sum())
    total_battles = int(df["is_battle"].sum())
    total_civilians = int(df["event_type"].eq("Violence against civilians").sum())
    total_regions = ", ".join(df["region"].value_counts().index.tolist())
    dropped_rows = 355183 - total_events
    capital_share = round(capital_remote / total_remote * 100, 2)
    border_share = round(border_battles / total_battles * 100, 2)
    peak_capital = yearly.loc[yearly["capital_remote_events"].idxmax()]
    peak_border = yearly.loc[yearly["border_battle_events"].idxmax()]
    top_capital_country = (
        df[df["capital_remote_event"]]
        .groupby("country")
        .size()
        .sort_values(ascending=False)
        .head(5)
    )
    top_border_country = (
        df[df["border_battle_event"]]
        .groupby("country")
        .size()
        .sort_values(ascending=False)
        .head(5)
    )
    country_table = build_country_table(df).head(8).to_html(index=False, classes="summary-table")

    top_capital_sentence = ", ".join(
        [f"{country} ({count})" for country, count in top_capital_country.items()]
    )
    top_border_sentence = ", ".join(
        [f"{country} ({count})" for country, count in top_border_country.items()]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>From Border Clashes to Capital Attacks in MENA?</title>
  <style>
    :root {{
      --bg: #f6f1e8;
      --paper: #fffdf8;
      --ink: #1f2933;
      --muted: #52606d;
      --accent: #c44536;
      --accent-2: #1f4e79;
      --line: #ded6c8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(196,69,54,0.08), transparent 30%),
        radial-gradient(circle at top right, rgba(31,78,121,0.10), transparent 25%),
        var(--bg);
      line-height: 1.68;
    }}
    .wrap {{
      width: min(1100px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0 56px;
    }}
    header {{
      background: linear-gradient(135deg, rgba(196,69,54,0.1), rgba(31,78,121,0.12));
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 32px;
      margin-bottom: 24px;
    }}
    h1, h2 {{
      line-height: 1.2;
      margin: 0 0 12px;
    }}
    h1 {{
      font-size: clamp(2rem, 4vw, 3.2rem);
      max-width: 12ch;
    }}
    h2 {{
      font-size: 1.6rem;
      margin-top: 28px;
    }}
    p {{
      margin: 0 0 16px;
    }}
    .deck {{
      color: var(--muted);
      max-width: 70ch;
      font-size: 1.05rem;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .meta span {{
      background: rgba(255,255,255,0.7);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 12px;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin: 24px 0;
    }}
    .stat-card, .section-card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 18px 20px;
      box-shadow: 0 12px 30px rgba(31,41,51,0.05);
    }}
    .stat-card strong {{
      display: block;
      font-size: 1.8rem;
      margin-bottom: 6px;
    }}
    .label {{
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .section-card {{
      margin-bottom: 22px;
      padding: 24px;
    }}
    .viz {{
      margin: 20px 0 8px;
      padding: 10px;
      background: #fff;
      border-radius: 18px;
      border: 1px solid var(--line);
    }}
    .map-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 10px 0 14px;
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .map-controls input[type="range"] {{
      width: min(320px, 100%);
      accent-color: var(--accent-2);
    }}
    .caption {{
      color: var(--muted);
      font-size: 0.94rem;
      margin-bottom: 18px;
    }}
    .summary-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 0.96rem;
    }}
    .summary-table th,
    .summary-table td {{
      border-bottom: 1px solid var(--line);
      padding: 10px 12px;
      text-align: left;
    }}
    .summary-table th {{
      background: #faf6ef;
    }}
    .refs a {{
      color: var(--accent-2);
    }}
    footer {{
      color: var(--muted);
      font-size: 0.94rem;
      margin-top: 28px;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>From Border Clashes to Capital Attacks in MENA?</h1>
      <p class="deck">Has the rise of drones and other remote attacks in the Middle East and North Africa (MENA) been accompanied by a spatial shift from border-proximate clashes toward attacks on capital areas?</p>
      <div class="meta">
        <span>Primary data: ACLED</span>
        <span>Regions analyzed: {total_regions}</span>
        <span>Method: Python + Jupyter + Plotly</span>
      </div>
    </header>

    <section class="section-card">
      <h2>Research Question and Framing</h2>
      <p>In recent years, the use of drones and other forms of remote violence has increased significantly in conflicts worldwide (Carboni &amp; Ciro, 2025). Compared to traditional modes of attack, remote methods enable strikes over longer distances at lower cost than conventional missiles, making them accessible even to relatively resource-constrained militant groups. Against this backdrop, this report examines whether the rise of remote violence in the MENA region has been accompanied by a spatial shift, from traditional border clashes toward attacks targeting capital areas. It is important to emphasize, however, that this analysis does not seek to establish a causal relationship between the proliferation of remote attack technologies and any potential spatial transformation, as such causal inference is beyond the scope of the available data.</p>
      <div class="viz">{remote_growth_html}</div>
      <p class="caption">Figure 1. Air/drone strikes and remote violence both rise sharply over time in MENA, especially after the mid-2010s.</p>
      <p>Contrary to the expectation, the empirical findings do not support the hypothesis. Remote violence is already widespread across the MENA sample and constitutes a dominant form of conflict in many years. Yet, only {capital_share}% of remote violence events are recorded in capital areas. Despite the growing prevalence of remote attack methods, conflict remains heavily concentrated in border-proximate regions, rather than exhibiting a clear shift toward capital-centered patterns.</p>
    </section>

    <section class="section-card">
      <h2>Data and Cleaning Strategy</h2>
      <p>The updated raw file contains ACLED observations from two regions: Middle East and Northern Africa. I combine them to create a full MENA sample. Before cleaning, the file contains 355,183 rows. I then drop any event with missing data in the core analytical fields used in this project: date, year, event type, sub-event type, country, first-level admin area, location, coordinates, notes, and fatalities. This removes {dropped_rows} rows and leaves {total_events:,} observations for analysis.</p>
      <p>ACLED’s unit of observation is the event. Each record reports a date, actors, event type, sub-event type, location, coordinates, and reported fatalities. ACLED notes that locations are coded at the most precise level possible and fatalities are conservative reported estimates rather than verified totals. Those design choices make ACLED especially useful for a spatial analysis like this one, while also reminding us that the dataset is not a perfect census of all violence.</p>
      <p>I define the two key categories in a straightforward way. First, a <strong>capital-area remote attack</strong> is any event coded as <em>Explosions/Remote violence</em> whose location is either the capital city itself or a sub-location beginning with the capital name. Second, a <strong>border-proximate battle</strong> is any <em>Battles</em> event located within {BORDER_DISTANCE_KM} kilometres of an international land border. Initially, I defined a battle as a border-proximate battle only when the notes explicitly mentioned “border” or “cross-border”, but the produced sample is too small and too selective to represent frontier conflict well. Therefore, I replaced it with the distance-based rule to have a broader and more geographically defensible measure of border-zone fighting.</p>
    </section>

    <section class="section-card">
      <h2>Finding 1: Remote Violence Dominates the Region, but Not Mainly Through Capitals</h2>
      <p>The first and most important result is that remote violence is already central to MENA conflict dynamics. The cleaned dataset records {total_remote:,} remote events, far exceeding the total number of battles. This means the argument cannot simply be that the region is only now becoming remote in method. In many cases, it already is. The more important question is spatial: where is this remote violence occurring?</p>
      <p>On that question, capital areas matter but do not dominate. The dataset contains {capital_remote:,} remote events in capital areas, with the largest concentrations in {top_capital_sentence}. Yet even with a broad capital-area definition, the capital share of all remote violence remains low. The highest annual count of capital-area remote attacks occurs in {int(peak_capital['year'])}, when the dataset records {int(peak_capital['capital_remote_events']):,} such events, but even that peak sits within a much larger regional pattern of remote warfare.</p>
      <p>This distinction matters because, contrary to the initial expectation, the rise of remote violence does not necessarily mean that conflict is becoming more concentrated in capital areas. In fact, the share of capital-area attacks within all remote violence fluctuates but shows no sustained upward trend. The evidence therefore suggests that the spread of remote violence has not been accompanied by a clear shift toward capital-centred conflict.</p>
      <div class="viz">{share_html}</div>
      <p class="caption">Figure 2. The capital-area share of all remote violence fluctuates over time and remains much smaller than the total regional volume of remote events.</p>
    </section>

    <section class="section-card">
      <h2>Finding 2: Border Logics Still Matter</h2>
      <p>The share data point in the opposite direction: rather than declining, border-proximate conflict remains highly visible and in many years becomes more prominent within the overall battles category.</p>
      <p>The second result is that border-based conflict has not disappeared. The cleaned sample contains {border_battles:,} battles occurring within {BORDER_DISTANCE_KM} kilometers of an international land border, and these events cluster in recognisable frontier theatres rather than appearing as isolated outliers. The biggest contributors are {top_border_sentence}. In practice, this means that conflict in MENA remains closely tied to borderlands, border crossings, and transboundary military activity even in a period when remote violence is extremely common.</p>
      <p>The yearly pattern reinforces this point. Border-proximate battles peak in {int(peak_border['year'])}, when the cleaned data record {int(peak_border['border_battle_events']):,} such events. That peak is driven largely by Yemen and other active frontier theatres, which shows why a territorial reading of conflict still has explanatory force. Armed actors continue to exploit cross-border movement, peripheral sanctuaries, and the difficulties states face when projecting authority to margins and frontier zones.</p>
      <p>In other words, the spread of remote violence does not automatically erase older spatial logics. It can coexist with them, overlap with them, and in some conflicts even intensify them.</p>
      <div class="viz">{composition_html}</div>
      <p class="caption">Figure 3. Event-type composition differs less dramatically across capital areas, border-proximate areas, and other areas than a simple “old versus new” spatial transition would imply.</p>
      {country_table}
    </section>

    <section class="section-card">
      <h2>Finding 3: MENA Looks Like Layered Conflict, Not a Clean Spatial Transition</h2>
      <p>The map makes the broader interpretation clearer. Capital-area remote attacks appear in several political centres, but they do not form the single dominant geography of the regional conflict system. Border-proximate battles, meanwhile, remain distributed across enduring frontier theatres. The two categories overlap in the same macro-region, yet they are not the same pattern unfolding at different moments in time. They look more like layered logics operating simultaneously.</p>
      <p>This leads to a more careful conclusion. The MENA data are consistent with the growing importance of remote warfare, but they do not show a simple replacement of border conflict by capital targeting. Instead, the region combines stand-off violence, urban targeting, and frontier conflict within the same broader conflict environment. That is a stronger empirical conclusion than either saying “nothing changed” or claiming that warfare has simply migrated to capitals.</p>
      <div class="map-controls">
        <label for="mena-map-zoom">Zoom</label>
        <input id="mena-map-zoom" type="range" min="1.5" max="10" step="0.1" value="3.05">
      </div>
      <div class="viz">{map_html}</div>
      <script>
        (function() {{
          const mapEl = document.getElementById('mena-map-figure');
          const zoomSlider = document.getElementById('mena-map-zoom');
          if (!mapEl || !window.Plotly) return;
          const capitalTraceIndex = mapEl.data.length - 1;
          const labelZoomThreshold = 3.0;
          function updateCapitalLabels() {{
            const zoom = (mapEl.layout && mapEl.layout.map && mapEl.layout.map.zoom) || 0;
            const mode = zoom >= labelZoomThreshold ? 'markers+text' : 'markers';
            const labels = mapEl.data[capitalTraceIndex].customdata.map(row => zoom >= labelZoomThreshold ? row[1] : '');
            Plotly.restyle(mapEl, {{mode: mode, text: [labels]}}, [capitalTraceIndex]);
            if (zoomSlider) zoomSlider.value = zoom;
          }}
          function updateMapZoom() {{
            if (!zoomSlider) return;
            Plotly.relayout(mapEl, {{'map.zoom': Number(zoomSlider.value)}});
          }}
          mapEl.on('plotly_afterplot', updateCapitalLabels);
          mapEl.on('plotly_relayout', updateCapitalLabels);
          if (zoomSlider) {{
            zoomSlider.addEventListener('input', updateMapZoom);
          }}
          setTimeout(updateCapitalLabels, 50);
        }})();
      </script>
      <p class="caption">Figure 4. Capital-area remote attacks and border-proximate battles are both present in MENA, but they are distributed across different kinds of conflict spaces.</p>
    </section>

    <section class="section-card">
      <h2>Conclusion and Limitations</h2>
      <p>The evidence does not support a neat regional story in which MENA conflict moved from borders to capitals. What the data show instead is a layered conflict geography. Remote violence is highly prevalent, but capital-area remote attacks remain only a small subset of it. Border-proximate battles also persist at meaningful levels rather than fading away. The stronger conclusion is that newer remote methods have expanded within MENA without fully displacing territorial and frontier-based forms of armed conflict.</p>
      <p>The analysis still has limits. The border measure now uses an approximate distance-to-border rule based on Natural Earth country polygons and a {BORDER_DISTANCE_KM}-kilometer threshold, so it is a spatial proxy rather than a perfect identification of all frontier conflict. The capital-area rule is broader than an exact-city match, but it still cannot capture every attempt to influence a capital from nearby locations. ACLED fatalities are reported estimates and should be interpreted cautiously. Finally, because the raw file was supplied as a project file rather than downloaded through an API in this notebook, the retrieval discussion is limited to the structure of the provided export.</p>
    </section>

    <section class="section-card refs">
      <h2>References</h2>
      <p>ACLED. “Codebook.” <a href="https://acleddata.com/knowledge-base/codebook/">https://acleddata.com/knowledge-base/codebook/</a>.</p>
      <p>Carboni, Andrea, and Ciro Murillo. “What’s driving conflict today? A review of global trends.” ACLED, 11 December 2025. <a href="https://acleddata.com/report/whats-driving-conflict-today-review-global-trends">https://acleddata.com/report/whats-driving-conflict-today-review-global-trends</a>. This report provided the project’s initial inspiration, especially its discussion of the rapid spread of drone use by armed groups.</p>
      <p>ACLED dataset supplied in the project folder as <code>data/ACLED Data_MENA_Raw.csv</code>.</p>
      <p>POLI3148 Assignment Instructions supplied as <code>Instructions.pdf</code>.</p>
    </section>

    <footer>
      Generated with <code>code/Z_generate_report.py</code> from the cleaned MENA analysis pipeline.
    </footer>
  </div>
</body>
</html>
"""


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DOCS_DIR / "index.html"
    output_path.write_text(build_report_html(), encoding="utf-8")
    print(f"Wrote report to {output_path}")


if __name__ == "__main__":
    main()
