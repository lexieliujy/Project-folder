from __future__ import annotations

import json
from pathlib import Path


def markdown_cell(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().splitlines()],
    }


REPORT_TEXT = """
# Final Report Text Mirror

This notebook mirrors the finalized report baseline published in `docs/index.html`.

---

**MENA Conflict Geography: From Border Clashes to Capital Attacks?**

Has the rise of drones and other remote attacks in the Middle East and North Africa (MENA) been accompanied by a spatial shift from border-proximate clashes toward attacks on capital areas?

**Research Question and Framing**

In recent years, the use of drones and other forms of remote violence has increased significantly in conflicts worldwide (Carboni & Ciro, 2025). Compared to traditional modes of attack, remote methods enable strikes over longer distances at lower cost than conventional missiles, making them accessible even to relatively resource-constrained militant groups. These technologies also reduce the need for territorial proximity, potentially allowing actors to bypass frontlines and directly target politically or symbolically significant locations.

Against this backdrop, this report examines whether the rise of remote violence in the MENA region has been accompanied by a spatial shift, from traditional border clashes toward attacks targeting capital areas. This expectation reflects a plausible strategic intuition: as the cost of projecting force over distance declines, conflict actors may increasingly target politically significant locations rather than remain confined to geographically constrained battle zones.

At the same time, existing research on civil war and irregular conflict suggests that violence remains closely tied to territorial control, logistics, and cross-border networks, which are often concentrated in frontier regions. This creates a tension between two competing expectations: one emphasizing technological transformation and spatial reach, and the other emphasizing enduring territorial constraints.

It is important to emphasize, however, that this analysis does not seek to establish a causal relationship between the proliferation of remote attack technologies and any potential spatial transformation, as such causal inference is beyond the scope of the available data. Instead, the analysis evaluates whether the observed spatial distribution of conflict events is consistent with the expectation of a shift toward capital targeting.

**Data and Geographic Definitions**

The cleaned sample used in this report (1997-2024) comprises 343,901 ACLED observations, after applying missing-value cleaning and excluding the 2025 records. The dataset retains an event-level structure, allowing for fine-grained spatial and temporal analysis of conflict patterns across the region. The large number of observations also makes it possible to identify aggregate trends that may not be visible at the level of individual conflicts.

Geographic definitions are constructed using event coordinates together with an international-border distance measure based on Natural Earth boundaries, providing a reproducible spatial proxy. This approach prioritizes consistency and scalability across countries. By contrast, a notes-based keyword approach identifying events based on explicit references to "border" or "cross-border" in the notes field is too narrow and likely to undercount relevant events, as many border dynamics are not explicitly labeled in textual descriptions.

A **Capital-area event** is defined as any event located in a national capital or in a sub-location whose name begins with that capital. This broader definition helps capture administrative and urban spillover zones that are functionally part of capital regions, rather than restricting the analysis to narrowly defined city centers.

A **Border-proximate event** is defined as any event occurring within 50 km of an international land border. This threshold reflects a compromise between capturing meaningful cross-border dynamics and avoiding excessive inclusion of interior events that are unlikely to be directly shaped by frontier conditions.

A key caveat concerns overlap between these categories, as some capitals are geographically close to borders. In this sample, 1,531 events satisfy both definitions. This overlap is explicitly reported and incorporated into the analysis to avoid imposing a misleading binary distinction between capital and border spaces. Rather than treating these categories as mutually exclusive, the analysis recognizes that some locations may simultaneously exhibit characteristics of both.

**Remote attacks expanded, but the strategic center of conflict remained border-oriented.**

**Capital targeting did not become the dominant remote-war pattern.**

Contrary to the expectation, the empirical findings do not support the hypothesis. Remote violence is already widespread across the MENA sample and constitutes a dominant form of conflict in many years. Yet, only 2.72% of such events occur in capital areas, and their share within remote violence shows no sustained increase over time. This suggests that even as the means of delivering violence evolve, the spatial distribution of that violence does not necessarily follow the same trajectory.

Even when focusing on remote violence, where any shift toward capital targeting should be most visible, border-proximate events account for a larger share than capital-area events in most years, with the gap widening after the mid-2010s. This widening gap is particularly notable because it occurs precisely during the period when remote technologies become more prevalent, reinforcing the conclusion that technological change has not overridden existing spatial patterns.

At the aggregate level, border-proximate remote events total 116,845 (56.05%), compared to 5,673 (2.72%) events in capital areas. The magnitude of this difference is substantial and cannot be explained by short-term fluctuations or measurement artifacts alone.

These patterns indicate that the expansion of remote attack methods has not been accompanied by a spatial reorientation of conflict toward capital areas, with activity remaining more concentrated in border-proximate regions. In other words, the increased capacity to strike at a distance has not translated into a systematic shift toward capital-focused conflict.

Figure 1. Within remote attacks, border-proximate share remains above capital-area share across most years.

**Border zones remained the region's core strategic battlespace.**

This pattern extends beyond remote violence and remains visible in the overall distribution of conflict events. Border-proximate events consistently account for a larger share of total activity than capital-area events throughout the period. This suggests that the observed pattern is not confined to a specific mode of warfare, but reflects a broader structural feature of conflict geography in the region.

At the aggregate level, border-proximate events total 165,192 (48.03%), compared to 11,081 (3.22%) in capital areas. The persistence of this gap across both remote and non-remote categories further strengthens the conclusion that border regions play a central role in organizing conflict activity.

The presence of overlap between Capital-area events and Border-proximate events does not compromise this pattern. While 1,531 events fall into both classifications, non-capital border-proximate events still number 163,661, indicating that the prominence of border regions is not simply driven by capitals located near borders.

Taken together, this means that conflict in MENA remains closely tied to borderlands, border crossings, and transboundary military activity despite the growing capacity to project force across distance. Far from being peripheral, these areas appear to function as critical operational zones where control over movement, supply routes, and cross-border linkages can be established and contested (Salehyan, 2007). In this sense, the persistence and, in some cases, increasing prominence of border-proximate violence indicates that territorial considerations remain central to the conduct of war.

This interpretation is consistent with existing research emphasizing that violence tends to concentrate in areas of contested control rather than in symbolically salient locations (Kalyvas, 2006), and that remote or air-based strikes, while expanding the reach of violence, are limited in their ability to produce decisive outcomes without corresponding territorial pressure (Pape, 2005).

Figure 2. On the all-event denominator, border share still remains above capital share.

**Simple Spatial Map**

The final webpage also includes a simplified map focused on the contrast between capital-area events and border-proximate events. Its time slider is yearly rather than cumulative, so each selected year shows only that year's event points.

Figure 4. Simple map with country borders, capital names, and a year slider for yearly event points.

**Conclusion and Implications**

The evidence supports one stable conclusion: border-linked space remains the heavier conflict geography in MENA relative to capital space. It does not support a neat regional story in which MENA conflict moved from borders to capitals. What the data show instead is a layered conflict geography. Remote violence is highly prevalent, but capital-area remote attacks remain only a small subset of it. Border-proximate battles also persist at meaningful levels rather than fading away.

The analysis still has limits: first, the border measure now uses an approximate distance-to-border rule based on Natural Earth country polygons and a 50-kilometer threshold, so it is a spatial proxy rather than a perfect identification of all frontier conflict; second, the capital-area rule is broader than an exact-city match, but it still cannot capture every attempt to influence a capital from nearby locations; finally, the analysis focuses on event counts rather than intensity or strategic impact, meaning that it does not distinguish between low-level incidents and high-impact attacks.

**References**

ACLED. "Codebook." https://acleddata.com/knowledge-base/codebook/.

Carboni, Andrea, and Ciro Murillo. "What's driving conflict today? A review of global trends." ACLED, 11 December 2025. https://acleddata.com/report/whats-driving-conflict-today-review-global-trends.

Kalyvas, S. N. (2006). The logic of violence in civil war. Cambridge University Press.

Pape, R. A. (2005). Dying to win: The strategic logic of suicide terrorism. Random House.

Salehyan, I. (2007). Transnational Rebels: Neighboring States as Sanctuary for Rebel Groups. World Politics, 59(2), 217-242. https://doi.org/10.1353/wp.2007.0024.
"""


NOTEBOOK = {
    "cells": [markdown_cell(REPORT_TEXT)],
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


def main() -> None:
    output_path = Path(__file__).resolve().parent / "01_conflict_shift_analysis.ipynb"
    output_path.write_text(json.dumps(NOTEBOOK, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote notebook to {output_path}")


if __name__ == "__main__":
    main()
