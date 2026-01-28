from __future__ import annotations

import re
from pathlib import Path
from openpyxl import Workbook

from importer.processing.highlight_validation import (
    is_valid_highlight,
    is_fragment_quote,
)
from importer.processing.notes import get_type_and_note, extract_rating_from_note
from importer.config import INPUT_FILE, EXCEL_FILE

VOCABULARY_TYPE = 99  # 🔤 Vocabulary


def _parse_added_at(meta_info: str) -> str:
    m = re.search(r"Added on (.+)$", meta_info)
    return m.group(1).strip() if m else ""


def _ranges_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start <= b_end and b_start <= a_end


def _word_in_text(word: str, text: str) -> bool:
    if not word or not text:
        return False

    pattern = rf"\b{re.escape(word.lower())}\b"
    return re.search(pattern, text.lower()) is not None


def _choose_best_highlight(cluster: list[dict]) -> dict | None:
    if not cluster:
        return None

    non_frag = [h for h in cluster if not is_fragment_quote(h.get("quote", ""))]
    candidates = non_frag if non_frag else cluster

    best = None
    for h in candidates:
        if best is None:
            best = h
            continue

        if (
            h.get("added_at", "") > best.get("added_at", "")
            or (
                h.get("added_at", "") == best.get("added_at", "")
                and len(h.get("quote", "")) > len(best.get("quote", ""))
            )
        ):
            best = h

    return best


def _dedupe_highlights_by_overlap_safe(highlights_list: list[dict]) -> list[dict]:
    items = sorted(
        highlights_list,
        key=lambda x: (x.get("location_start", 0), x.get("location_end", 0)),
    )

    clusters: list[list[dict]] = []

    for h in items:
        placed = False
        for cluster in clusters:
            if any(
                _ranges_overlap(
                    h.get("location_start", 0),
                    h.get("location_end", 0),
                    c.get("location_start", 0),
                    c.get("location_end", 0),
                )
                for c in cluster
            ):
                cluster.append(h)
                placed = True
                break

        if not placed:
            clusters.append([h])

    final = []
    for cluster in clusters:
        best = _choose_best_highlight(cluster)
        if best is not None:
            merged_notes: list[dict] = []
            for item in cluster:
                merged_notes.extend(item.get("notes", []) or [])
            if merged_notes:
                best = dict(best)
                best["notes"] = merged_notes
            final.append(best)

    final.sort(key=lambda x: (x.get("location_start", 0), x.get("location_end", 0)))
    return final


def _choose_best_note(notes: list[dict]) -> dict | None:
    valid: list[dict] = []

    for n in notes:
        if not isinstance(n, dict):
            continue

        note_type = n.get("type", 0)
        if note_type == 0:
            continue

        note_text = (n.get("note") or "").strip()
        added_at = n.get("added_at", "")

        valid.append({
            "type": note_type,
            "note": note_text,
            "added_at": added_at,
            "_has_text": bool(note_text),
        })

    if not valid:
        return None

    valid.sort(
        key=lambda n: (
            not n["_has_text"],   # notas com texto primeiro
            n["added_at"],        # MAIS RECENTE vence
            -len(n["note"]),      # desempate final
        ),
        reverse=True
    )

    best = valid[0]
    return {"type": best["type"], "note": best["note"]}


def _note_loc_compatible(note_loc: int, h_start: int, h_end: int) -> bool:
    return (h_start - 2) <= note_loc <= (h_end + 2)


def _find_best_highlight_for_orphan(
    highlights: list[dict],
    book_title: str,
    author: str,
    note_loc: int,
) -> dict | None:
    candidates: list[tuple[int, int, int, dict]] = []

    for h in highlights:
        if h.get("book") != book_title or h.get("author") != author:
            continue

        h_start = int(h.get("location_start", 0) or 0)
        h_end = int(h.get("location_end", 0) or 0)

        if h_start <= note_loc <= h_end:
            pri, dist = 0, 0
        elif note_loc == h_start:
            pri, dist = 1, 0
        else:
            pri = 2
            dist = min(abs(note_loc - h_start), abs(note_loc - h_end))

        if dist <= 3:
            seq = int(h.get("_seq", 0) or 0)
            candidates.append((pri, dist, -seq, h))

    if not candidates:
        return None

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return candidates[0][3]


def process_clippings(
    input_file: Path = INPUT_FILE,
    output_excel: Path = EXCEL_FILE,
):
    wb = Workbook()
    ws = wb.active
    ws.title = "Valid Quotes"

    ws.append([
        "Page", "Type", "Quote", "Author", "Book", "Note",
        "LocationStart", "LocationEnd",
    ])

    raw_data = input_file.read_text(encoding="utf-8")
    blocks = [b.strip() for b in raw_data.split("==========") if b.strip()]

    highlights_by_book_author: dict[tuple[str, str], list[dict]] = {}
    all_highlights_in_order: list[dict] = []
    last_highlight_by_book_author: dict[tuple[str, str], dict] = {}

    orphan_notes: list[dict] = []
    ratings_detected: list[dict] = []
    vocabularies_detected: list[dict] = []

    seq = 0

    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if len(lines) < 2:
            continue

        book_info = lines[0]
        if "(" in book_info and ")" in book_info:
            book_title = book_info.split("(")[0].strip()
            author = book_info.split("(")[-1].replace(")", "").strip()
        else:
            book_title = book_info.strip()
            author = "Unknown"

        meta_info = lines[1]
        meta_lower = meta_info.lower()
        added_at = _parse_added_at(meta_info)

        page = None
        if "page" in meta_lower:
            parts = [p for p in meta_info.split("|") if "page" in p.lower()]
            if parts:
                try:
                    page = int(parts[0].split()[-1])
                except ValueError:
                    page = None

        loc_match = re.search(r"location\s+(\d+)(?:-(\d+))?", meta_lower)
        if not loc_match:
            continue

        loc_start = int(loc_match.group(1))
        loc_end = int(loc_match.group(2)) if loc_match.group(2) else loc_start

        content = "\n".join(lines[2:]).strip()

        if content.startswith("<You have reached") or "<You have reached" in content:
            continue

        if "highlight" in meta_lower and content.lower().startswith("nota"):
            continue

        key = (book_title, author)

        if "highlight" in meta_lower:
            h = {
                "page": page,
                "quote": content,
                "author": author,
                "book": book_title,
                "location_start": loc_start,
                "location_end": loc_end,
                "added_at": added_at,
                "notes": [],
                "_seq": seq,
            }
            seq += 1
            highlights_by_book_author.setdefault(key, []).append(h)
            all_highlights_in_order.append(h)
            last_highlight_by_book_author[key] = h

        elif "note" in meta_lower:
            note_type, note_text = get_type_and_note(content)
            if note_type == 0:
                continue

            note_obj = {
                "type": note_type,
                "note": note_text,
                "location": loc_start,
                "book": book_title,
                "author": author,
                "added_at": added_at,
                "_seq": seq,
            }
            seq += 1

            last_h = last_highlight_by_book_author.get(key)

            if last_h is not None and _note_loc_compatible(
                loc_start,
                last_h["location_start"],
                last_h["location_end"],
            ):
                last_h["notes"].append({
                    "type": note_type,
                    "note": note_text,
                    "added_at": added_at,
                })
            else:
                orphan_notes.append(note_obj)

    attached_ids = set()
    for n in orphan_notes:
        target = _find_best_highlight_for_orphan(
            highlights=all_highlights_in_order,
            book_title=n["book"],
            author=n["author"],
            note_loc=n["location"],
        )
        if target is not None:
            target["notes"].append({
                "type": n["type"],
                "note": n["note"],
                "added_at": n["added_at"],
            })
            attached_ids.add(id(n))

    for n in orphan_notes:
        if id(n) in attached_ids:
            continue

        for h in all_highlights_in_order:
            if (
                h["book"] == n["book"]
                and h["author"] == n["author"]
                and h["_seq"] > n["_seq"]
            ):
                h["notes"].append({
                    "type": n["type"],
                    "note": n["note"],
                    "added_at": n["added_at"],
                })
                break

    final_highlights: list[dict] = []
    for hs in highlights_by_book_author.values():
        final_highlights.extend(_dedupe_highlights_by_overlap_safe(hs))

    for h in final_highlights:
        final_type = 0
        final_note = ""

        best_note = _choose_best_note(h.get("notes", []) or [])
        if best_note:
            final_type = best_note["type"]
            final_note = best_note["note"]

        if (final_note or "").lower().startswith("nota"):
            rating = extract_rating_from_note(final_note)
            if rating is not None:
                ratings_detected.append({
                    "book": h["book"],
                    "author": h["author"],
                    "rating": rating,
                })
            continue

        if not is_valid_highlight(h.get("quote", ""), final_type):
            continue

        if final_type == VOCABULARY_TYPE:
            word = (final_note or "").strip()
            quote_text = (h.get("quote") or "").strip()

            if not word:
                continue

            if not _word_in_text(word, quote_text):
                continue

            vocabularies_detected.append({
                "book": h["book"],
                "author": h["author"],
                "location_start": h["location_start"],
                "location_end": h["location_end"],
                "word": word,
                "text": quote_text,
                "page": h.get("page"),
            })
            continue

        ws.append([
            h.get("page"),
            final_type,
            (h.get("quote") or "").strip(),
            h.get("author") or "",
            h.get("book") or "",
            (final_note or "").strip(),
            h.get("location_start") or 0,
            h.get("location_end") or 0,
        ])

    wb.save(output_excel)

    return ratings_detected, vocabularies_detected
