from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "docs"
DEFAULT_SOURCE_DOCX = Path(
    "/Users/lexieliu/Desktop/POLI3148/Assignment 1/Expanded Report text.docx"
)


def sync_docx_to_html(source_docx: Path, output_html: Path) -> None:
    if not source_docx.exists():
        raise FileNotFoundError(f"Source DOCX not found: {source_docx}")

    output_html.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "textutil",
            "-convert",
            "html",
            str(source_docx),
            "-output",
            str(output_html),
        ],
        check=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync finalized DOCX manuscript to docs/index.html"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE_DOCX,
        help="Path to finalized DOCX manuscript",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DOCS_DIR / "index.html",
        help="Output HTML path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sync_docx_to_html(args.source, args.output)
    print(f"Synced {args.source} -> {args.output}")


if __name__ == "__main__":
    main()
