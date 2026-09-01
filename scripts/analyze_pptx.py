#!/usr/bin/env python3
"""Extract textbook illustration tasks from a marked-up PPTX using stdlib only."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}
R_ID = f"{{{NS['r']}}}id"
TYPE_META = {
    "bottom": {"cn": "底层", "dir": "底层图", "aspect": "16:9", "transparent": False},
    "plot": {"cn": "剧情", "dir": "剧情图", "aspect": "4:3", "transparent": False},
    "atmosphere": {"cn": "氛围", "dir": "氛围图", "aspect": "free", "transparent": True},
    "element": {"cn": "元素", "dir": "元素图", "aspect": "free", "transparent": True},
}
CHARACTERS = ("小思", "小高", "小括狐")


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    cx: float
    cy: float


def q(prefix: str, name: str) -> str:
    return f"{{{NS[prefix]}}}{name}"


def read_xml(zf: zipfile.ZipFile, name: str) -> ET.Element:
    return ET.fromstring(zf.read(name))


def slide_order(zf: zipfile.ZipFile) -> list[str]:
    presentation = read_xml(zf, "ppt/presentation.xml")
    rels = read_xml(zf, "ppt/_rels/presentation.xml.rels")
    targets = {rel.get("Id"): rel.get("Target") for rel in rels.findall("pr:Relationship", NS)}
    result: list[str] = []
    for sld_id in presentation.findall(".//p:sldId", NS):
        target = targets.get(sld_id.get(R_ID))
        if not target:
            continue
        normalized = str(PurePosixPath("ppt") / target).replace("ppt/../", "")
        result.append(normalized)
    if result:
        return result
    names = [n for n in zf.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
    return sorted(names, key=lambda n: int(re.search(r"\d+", Path(n).stem).group()))


def slide_size(zf: zipfile.ZipFile) -> tuple[int, int]:
    root = read_xml(zf, "ppt/presentation.xml")
    size = root.find("p:sldSz", NS)
    if size is None:
        return 12192000, 6858000
    return int(size.get("cx", "12192000")), int(size.get("cy", "6858000"))


def text_from_paragraph(p: ET.Element) -> str:
    chunks: list[str] = []
    for node in p.iter():
        if node.tag == q("a", "t") and node.text:
            chunks.append(node.text)
        elif node.tag == q("a", "br"):
            chunks.append("\n")
        elif node.tag == q("a", "tab"):
            chunks.append("\t")
    return "".join(chunks).strip()


def shape_text(shape: ET.Element) -> str:
    return "\n".join(filter(None, (text_from_paragraph(p) for p in shape.findall(".//a:p", NS)))).strip()


def xfrm_box(xfrm: ET.Element | None) -> Box | None:
    if xfrm is None:
        return None
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    return Box(float(off.get("x", "0")), float(off.get("y", "0")), float(ext.get("cx", "0")), float(ext.get("cy", "0")))


def apply_group(box: Box, group_stack: list[tuple[Box, Box]]) -> Box:
    current = box
    for outer, child in reversed(group_stack):
        sx = outer.cx / child.cx if child.cx else 1.0
        sy = outer.cy / child.cy if child.cy else 1.0
        current = Box(
            outer.x + (current.x - child.x) * sx,
            outer.y + (current.y - child.y) * sy,
            current.cx * sx,
            current.cy * sy,
        )
    return current


def iter_shapes(parent: ET.Element, groups: list[tuple[Box, Box]] | None = None) -> Iterable[tuple[ET.Element, Box | None]]:
    groups = groups or []
    for child in list(parent):
        if child.tag == q("p", "sp"):
            local = xfrm_box(child.find("p:spPr/a:xfrm", NS))
            yield child, apply_group(local, groups) if local else None
        elif child.tag == q("p", "grpSp"):
            gx = child.find("p:grpSpPr/a:xfrm", NS)
            outer = xfrm_box(gx)
            if gx is None or outer is None:
                yield from iter_shapes(child, groups)
                continue
            ch_off = gx.find("a:chOff", NS)
            ch_ext = gx.find("a:chExt", NS)
            if ch_off is None or ch_ext is None:
                yield from iter_shapes(child, groups)
                continue
            inner = Box(float(ch_off.get("x", "0")), float(ch_off.get("y", "0")), float(ch_ext.get("cx", "0")), float(ch_ext.get("cy", "0")))
            yield from iter_shapes(child, groups + [(outer, inner)])


def shape_fill(shape: ET.Element) -> tuple[str | None, str | None]:
    solid = shape.find("p:spPr/a:solidFill", NS)
    if solid is None or not list(solid):
        return None, None
    color = list(solid)[0]
    if color.tag == q("a", "schemeClr"):
        return "scheme", color.get("val")
    if color.tag == q("a", "srgbClr"):
        return "rgb", color.get("val")
    return None, None


def is_blue_plot_box(shape: ET.Element, box: Box | None, slide_cx: int, slide_cy: int, text: str) -> bool:
    if box is None or len(re.sub(r"\s+", "", text)) < 8:
        return False
    wr, hr = box.cx / slide_cx, box.cy / slide_cy
    if wr < 0.28 or hr < 0.15 or wr * hr < 0.05:
        return False
    kind, value = shape_fill(shape)
    if kind == "scheme" and value in {"accent1", "accent5", "hlink"}:
        return True
    if kind == "rgb" and value and re.fullmatch(r"[0-9A-Fa-f]{6}", value):
        r, g, b = int(value[:2], 16), int(value[2:4], 16), int(value[4:], 16)
        return b >= 120 and b > r * 1.15 and b >= g * 0.9
    return False


def page_pair(text_blocks: list[str]) -> tuple[list[int], str]:
    pages: list[int] = []
    for text in text_blocks:
        for match in re.finditer(r"(?<!\d)(\d{1,3})\s*页", text):
            value = int(match.group(1))
            if value not in pages:
                pages.append(value)
    pages = pages[:2]
    if len(pages) == 2:
        return pages, f"{pages[0]}-{pages[1]}"
    if len(pages) == 1:
        return pages, str(pages[0])
    return [], "unknown"


def clean_spec(text: str) -> str:
    return re.sub(r"^[\s:：\-—]+|[\s]+$", "", text.replace("\u3000", " "))


def split_assets(description: str) -> list[str]:
    variant_match = re.fullmatch(r"(.+?)[（(]([^）)]+)[）)]", description)
    if variant_match and re.search(r"[、；;]", variant_match.group(2)):
        base = re.sub(r"^[一二两三四五六七八九十\d]+(?:个|张|只|把|件)", "", clean_spec(variant_match.group(1)))
        variants = [clean_spec(item) for item in re.split(r"[、；;]+", variant_match.group(2)) if clean_spec(item)]
        return [f"{base}（{variant}）" for variant in variants]
    parts = [clean_spec(x) for x in re.split(r"[、；;]+", description) if clean_spec(x)]
    return parts or [clean_spec(description)]


def characters_in(text: str) -> list[str]:
    found = [character for character in CHARACTERS if character in text]
    if re.search(r"三人|三小只|三位伙伴|三个伙伴", text):
        return list(CHARACTERS)
    return found


def extract_marked_specs(text_blocks: list[str]) -> list[tuple[str, str, bool]]:
    specs: list[tuple[str, str, bool]] = []
    patterns = (
        ("bottom", re.compile(r"底层(?:大图|图)?\s*\d*\s*[:：]?\s*(.+)")),
        ("atmosphere", re.compile(r"氛围图\s*\d*\s*[:：]?\s*(.+)")),
        ("element", re.compile(r"元素图\s*\d*\s*[:：]?\s*(.+)")),
    )
    for block in text_blocks:
        for line in block.splitlines():
            normalized = re.sub(r"\s+", " ", line).strip()
            for kind, pattern in patterns:
                match = pattern.search(normalized)
                if not match:
                    continue
                description = clean_spec(match.group(1))
                if not description:
                    continue
                if kind in {"atmosphere", "element"}:
                    parts = split_assets(description)
                    ambiguous = len(parts) == 1 and bool(re.search(r"\S+\s+\S+", description)) and not re.search(r"[、；;]", description)
                    specs.extend((kind, part, ambiguous) for part in parts)
                else:
                    specs.append((kind, description, False))
                break
    return specs


def finalize_filenames(tasks: list[dict]) -> None:
    counts: dict[tuple[str, str], int] = {}
    positions: dict[tuple[str, str], int] = {}
    for task in tasks:
        key = (task["page_pair"], task["type"])
        counts[key] = counts.get(key, 0) + 1
    for task in tasks:
        key = (task["page_pair"], task["type"])
        positions[key] = positions.get(key, 0) + 1
        index = positions[key]
        meta = TYPE_META[task["type"]]
        if task["type"] == "bottom":
            suffix = ""
        elif task["type"] == "plot" and counts[key] == 1:
            suffix = ""
        else:
            suffix = str(index)
        filename = f"{task['page_pair']}{meta['cn']}{suffix}.png"
        task["sequence"] = index
        task["filename"] = filename
        task["relative_path"] = f"{meta['dir']}/{filename}"
        task["id"] = f"{task['page_pair']}-{task['type']}-{index}"


def analyze(pptx: Path) -> dict:
    with zipfile.ZipFile(pptx) as zf:
        slide_cx, slide_cy = slide_size(zf)
        slide_paths = slide_order(zf)
        slides: list[dict] = []
        tasks: list[dict] = []
        warnings: list[str] = []
        for slide_number, slide_path in enumerate(slide_paths, 1):
            root = read_xml(zf, slide_path)
            sp_tree = root.find(".//p:spTree", NS)
            shape_records = list(iter_shapes(sp_tree)) if sp_tree is not None else []
            text_blocks = [shape_text(shape) for shape, _ in shape_records]
            text_blocks = [text for text in text_blocks if text]
            pages, pair = page_pair(text_blocks)
            slide_record = {"slide": slide_number, "page_numbers": pages, "page_pair": pair, "text_blocks": text_blocks}
            slides.append(slide_record)

            for kind, description, ambiguous in extract_marked_specs(text_blocks):
                meta = TYPE_META[kind]
                task_warnings = []
                if pair == "unknown":
                    task_warnings.append("No page number was detected on the source slide.")
                if ambiguous:
                    task_warnings.append("Description may contain multiple joined assets; confirm split during stage-one review.")
                tasks.append({
                    "type": kind,
                    "source_slide": slide_number,
                    "page_pair": pair,
                    "source_text": description,
                    "characters": characters_in(description),
                    "aspect_ratio": meta["aspect"],
                    "transparent": meta["transparent"],
                    "warnings": task_warnings,
                })

            for shape, box in shape_records:
                text = shape_text(shape)
                if not is_blue_plot_box(shape, box, slide_cx, slide_cy, text):
                    continue
                tasks.append({
                    "type": "plot",
                    "source_slide": slide_number,
                    "page_pair": pair,
                    "source_text": re.sub(r"\s+", " ", text).strip(),
                    "characters": characters_in(text),
                    "aspect_ratio": "4:3",
                    "transparent": False,
                    "box": {
                        "x_ratio": round(box.x / slide_cx, 4),
                        "y_ratio": round(box.y / slide_cy, 4),
                        "width_ratio": round(box.cx / slide_cx, 4),
                        "height_ratio": round(box.cy / slide_cy, 4),
                    } if box else None,
                    "warnings": [] if pair != "unknown" else ["No page number was detected on the source slide."],
                })

        tasks.sort(key=lambda t: (t["source_slide"], 0 if t["type"] == "bottom" else 1 if t["type"] == "plot" else 2 if t["type"] == "atmosphere" else 3))
        finalize_filenames(tasks)
        for task in tasks:
            warnings.extend(f"{task['id']}: {message}" for message in task.get("warnings", []))
        return {
            "schema_version": 1,
            "source_pptx": str(pptx.resolve()),
            "slide_count": len(slides),
            "slide_size_emu": {"width": slide_cx, "height": slide_cy},
            "workflow": {"stage_1": "review manifest", "stage_2": "generate only after approval"},
            "style_contract": {
                "bottom": "opaque PNG, exact 16:9",
                "plot": "opaque PNG, exact 4:3, one image per large blue box",
                "atmosphere": "transparent PNG, unrestricted aspect ratio, one isolated asset",
                "element": "transparent PNG, unrestricted aspect ratio, one isolated asset",
            },
            "tasks": tasks,
            "warnings": warnings,
            "slides": slides,
        }


def review_text(manifest: dict) -> str:
    counts = {kind: 0 for kind in TYPE_META}
    for task in manifest["tasks"]:
        counts[task["type"]] += 1
    lines = [
        "PPT 插图任务审核",
        f"源文件: {manifest['source_pptx']}",
        f"幻灯片: {manifest['slide_count']}",
        f"任务总数: {len(manifest['tasks'])}",
        f"底层图: {counts['bottom']} | 剧情图: {counts['plot']} | 氛围图: {counts['atmosphere']} | 元素图: {counts['element']}",
        "",
        "确认后才能开始生成。请重点检查合并词组是否需要拆成多个透明素材。",
        "",
    ]
    for task in manifest["tasks"]:
        warning = f" [需确认: {'; '.join(task['warnings'])}]" if task.get("warnings") else ""
        lines.append(f"- {task['relative_path']} | 第{task['source_slide']}张 | {task['source_text']}{warning}")
    if manifest["warnings"]:
        lines.extend(["", "警告:"] + [f"- {item}" for item in manifest["warnings"]])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("illustration-plan"))
    args = parser.parse_args()
    if not args.pptx.is_file():
        parser.error(f"PPTX not found: {args.pptx}")
    try:
        manifest = analyze(args.pptx)
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        print(f"Failed to parse PPTX: {exc}", file=sys.stderr)
        return 2
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "illustration-tasks.json"
    review_path = args.output_dir / "review.txt"
    json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(review_text(manifest), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {review_path}")
    print(f"Detected {len(manifest['tasks'])} tasks and {len(manifest['warnings'])} warnings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
