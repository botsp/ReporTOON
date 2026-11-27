"""Count GPT-5.4 tokens locally for matching RTF and TOON files.

Counts are for each complete decoded file as plain text, not API message
framing, output tokens, or provider-specific file-upload processing.
"""

import argparse
import csv
import statistics
from importlib.metadata import version
from pathlib import Path

try:
    import tiktoken
except ImportError as exc:
    raise SystemExit("Install dependencies with: python -m pip install -r requirements.txt") from exc


MODEL = "gpt-5.4"


def count_pair(rtf_path, toon_path, tokenizer):
    # Decode bytes directly so line endings are not normalized by text mode.
    rtf_bytes = rtf_path.read_bytes()
    toon_bytes = toon_path.read_bytes()
    rtf_text = rtf_bytes.decode("cp1252")
    toon_text = toon_bytes.decode("utf-8")
    rtf_tokens = len(tokenizer.encode_ordinary(rtf_text))
    toon_tokens = len(tokenizer.encode_ordinary(toon_text))
    if not rtf_tokens:
        raise ValueError(f"RTF contains no tokens: {rtf_path.name}")
    return {
        "file": rtf_path.name,
        "rtf_bytes": len(rtf_bytes),
        "toon_bytes": len(toon_bytes),
        "rtf_tokens": rtf_tokens,
        "toon_tokens": toon_tokens,
        "reduction_percent": round(100 * (rtf_tokens - toon_tokens) / rtf_tokens, 2),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rtf_dir", type=Path)
    parser.add_argument("toon_dir", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    if not args.rtf_dir.is_dir() or not args.toon_dir.is_dir():
        parser.error("RTF and TOON inputs must be existing directories")
    if args.output_csv.exists():
        parser.error("Output CSV already exists; choose a different name")
    if not args.output_csv.parent.is_dir():
        parser.error("Output CSV parent folder does not exist")
    rtf_files = sorted(p for p in args.rtf_dir.glob("*.rtf") if p.is_file())
    sources = [p for p in rtf_files if not p.name.startswith("~$")]
    skipped = len(rtf_files) - len(sources)
    if not sources:
        parser.error("No RTF files found")
    missing = [p.name for p in sources if not (args.toon_dir / (p.stem + ".toon")).is_file()]
    if missing:
        parser.error("Missing matching TOON files: " + ", ".join(missing))
    source_stems = {p.stem.casefold() for p in sources}
    extra = sorted(
        p.name for p in args.toon_dir.glob("*.toon")
        if p.is_file() and p.stem.casefold() not in source_stems
    )
    if extra:
        parser.error("TOON files without matching RTF files: " + ", ".join(extra))

    tokenizer = tiktoken.encoding_for_model(MODEL)
    print(
        f"Model: {MODEL}; encoding: {tokenizer.name}; "
        f"tiktoken: {version('tiktoken')}; counting {len(sources)} pairs; "
        f"skipped {skipped} Word lock files.",
        flush=True,
    )
    rows = []
    for index, source in enumerate(sources, 1):
        rows.append(count_pair(source, args.toon_dir / (source.stem + ".toon"), tokenizer))
        if index % 20 == 0 or index == len(sources):
            print(f"Counted {index}/{len(sources)}.", flush=True)

    with args.output_csv.open("x", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    rtf_total = sum(row["rtf_tokens"] for row in rows)
    toon_total = sum(row["toon_tokens"] for row in rows)
    reduction = 100 * (rtf_total - toon_total) / rtf_total
    median = statistics.median(row["reduction_percent"] for row in rows)
    print(f"RTF tokens: {rtf_total:,}; TOON tokens: {toon_total:,}.")
    print(f"Aggregate reduction: {reduction:.2f}%; median per file: {median:.2f}%.")
    print(f"Saved {args.output_csv}")


if __name__ == "__main__":
    main()
