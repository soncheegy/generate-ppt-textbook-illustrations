#!/usr/bin/env python3
"""Validate generated illustration dimensions, PNG format, naming, and alpha contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required for output validation. Install pillow in the active Python environment.") from exc


def ratio_ok(width: int, height: int, target: float, tolerance: float = 0.015) -> bool:
    return height > 0 and abs(width / height - target) <= tolerance


def validate_task(task: dict, output_root: Path) -> dict:
    path = output_root / Path(task["relative_path"])
    errors: list[str] = []
    info: dict = {"task_id": task["id"], "path": str(path), "errors": errors}
    if not path.is_file():
        errors.append("missing file")
        return info
    try:
        with Image.open(path) as image:
            image.load()
            width, height = image.size
            bands = image.getbands()
            info.update({"width": width, "height": height, "mode": image.mode, "format": image.format})
            if image.format != "PNG":
                errors.append(f"expected PNG, got {image.format}")
            if task["type"] == "bottom" and not ratio_ok(width, height, 16 / 9):
                errors.append(f"bottom-layer ratio must be 16:9, got {width}:{height}")
            if task["type"] == "plot" and not ratio_ok(width, height, 4 / 3):
                errors.append(f"plot ratio must be 4:3, got {width}:{height}")
            if task.get("transparent"):
                if "A" not in bands:
                    errors.append("transparent asset has no alpha channel")
                else:
                    alpha = image.getchannel("A")
                    alpha_min, alpha_max = alpha.getextrema()
                    info["alpha_extrema"] = [alpha_min, alpha_max]
                    if alpha_min > 0:
                        errors.append("alpha channel contains no fully transparent pixels")
                    if alpha_max < 240:
                        errors.append("asset has no substantially opaque subject")
                    corners = (alpha.getpixel((0, 0)), alpha.getpixel((width - 1, 0)), alpha.getpixel((0, height - 1)), alpha.getpixel((width - 1, height - 1)))
                    info["corner_alpha"] = list(corners)
                    if any(value > 10 for value in corners):
                        errors.append("one or more corners are not transparent")
            elif "A" in bands:
                alpha_min, alpha_max = image.getchannel("A").getextrema()
                if alpha_min < 255:
                    errors.append("opaque asset contains transparency")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"cannot read image: {exc}")
    return info


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    results = [validate_task(task, args.output_root) for task in manifest["tasks"]]
    failed = [item for item in results if item["errors"]]
    report = {
        "manifest": str(args.manifest.resolve()),
        "output_root": str(args.output_root.resolve()),
        "task_count": len(results),
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "results": results,
    }
    report_path = args.report or (args.output_root / "qa-report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Validated {len(results)} tasks: {report['passed']} passed, {report['failed']} failed")
    print(f"Wrote {report_path}")
    for item in failed:
        print(f"FAIL {item['task_id']}: {'; '.join(item['errors'])}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
