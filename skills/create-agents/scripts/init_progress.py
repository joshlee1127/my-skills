#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""從工時估算表展開出 progress.md：整張計畫表 + 進度表合一。

用法：
    python init_progress.py <estimate.xlsx> --out progress.md [--date 2026-08-11] [--sheet <name>]

為什麼要預先展開：邊做邊長的進度檔只回答得了「做過什麼」，回答不了「還剩多少沒做」。
一開始就把估算表的每一列展開成一列進度，代理人才有辦法判斷覆蓋率與剩餘工作。

重跑安全：目標檔已存在時會**保留既有狀態**（以「項次＋作業項目」比對），只補上新增的項目。
估算表已刪除、但進度檔還有紀錄的項目不會被靜靜丟掉，會集中列在檔尾等人工確認。
"""

import argparse
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from read_estimate import parse, emit, die  # noqa: E402

STATUS_TODO = "未開始"
HEADER = "| 項次 | 作業項目 | 狀態 | 更新日期 | 備註 |"
SEPARATOR = "|---|---|---|---|---|"
ORPHAN_HEADING = "## ⚠️ 估算表已無此項（待人工確認）"

# 進度檔的表格列：| 1.1 | 健檢標的訂閱清單確認 | 未開始 |  |  |
ROW_RE = re.compile(r"^\|\s*(?P<no>[^|]*?)\s*\|\s*(?P<task>[^|]+?)\s*\|\s*(?P<status>[^|]*?)\s*\|"
                    r"\s*(?P<date>[^|]*?)\s*\|\s*(?P<note>[^|]*?)\s*\|\s*$")


def escape_cell(text):
    """作業項目偶爾含有 | 或換行，會把 Markdown 表格撐破。"""
    return text.replace("|", "\\|").replace("\n", " ")


def key_of(no, task):
    """比對鍵：項次可能被手工改動或缺漏，所以作業項目才是主鍵，項次僅輔助。"""
    return escape_cell(task).strip()


def read_existing(path):
    """撈出既有進度，回傳 {作業項目: (狀態, 日期, 備註)}。"""
    if not os.path.exists(path):
        return {}
    existing = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("|---") or line.startswith("| 項次"):
                continue
            m = ROW_RE.match(line)
            if not m:
                continue
            task = m.group("task").strip()
            if not task:
                continue
            existing[key_of(m.group("no"), task)] = (
                m.group("status").strip() or STATUS_TODO,
                m.group("date").strip(),
                m.group("note").strip(),
            )
    return existing


def build(data, existing, today, source):
    lines = [
        "# 作業進度",
        "",
        f"來源：`{source}`（工作表：{data['sheet']}）　產生日期：{today}",
        "",
        "本檔由估算表展開，同時是**計畫表**與**進度表**：所有作業項目一開始就在這裡，"
        "狀態自「未開始」推進到「進行中」→「已完成」。",
        "動作前先讀本檔確認剩餘工作；動作前後更新對應列。狀態欄只填"
        "「未開始／進行中／已完成／延後／不適用」，備註欄不得寫入帳密、金鑰、Token。",
        "",
    ]

    total = 0
    done = 0
    seen = set()
    body = []

    for cat in data["categories"]:
        body.append(f"## {cat['category']}")
        body.append("")
        body.append(HEADER)
        body.append(SEPARATOR)
        for item in cat["items"]:
            task = escape_cell(item["task"])
            k = key_of(item.get("no", ""), item["task"])
            seen.add(k)
            status, date, note = existing.get(k, (STATUS_TODO, "", ""))
            total += 1
            if status == "已完成":
                done += 1
            body.append(
                "| %s | %s | %s | %s | %s |"
                % (escape_cell(item.get("no", "")), task, status, date, note)
            )
        body.append("")

    orphans = [(k, v) for k, v in existing.items() if k not in seen]
    if orphans:
        body.append(ORPHAN_HEADING)
        body.append("")
        body.append("以下項目存在於既有進度檔，但這次的估算表已經沒有。"
                    "可能是估算表改版，也可能是作業項目被手工改過名稱——確認後再刪除。")
        body.append("")
        body.append(HEADER)
        body.append(SEPARATOR)
        for k, (status, date, note) in sorted(orphans):
            body.append("|  | %s | %s | %s | %s |" % (k, status, date, note))
        body.append("")

    lines.append(f"覆蓋率：{done} / {total} 項已完成。")
    lines.append("")
    lines.extend(body)
    return "\n".join(lines).rstrip() + "\n", total, len(orphans)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="工時估算表路徑")
    ap.add_argument("--out", default="progress.md", help="輸出的進度檔（預設 progress.md）")
    ap.add_argument("--sheet")
    ap.add_argument("--date", help="產生日期，預設今天")
    args = ap.parse_args()

    today = args.date or datetime.date.today().isoformat()
    data = parse(args.path, args.sheet)
    if not data["categories"]:
        die("估算表解析結果沒有任何作業項目，不產生進度檔。")

    existing = read_existing(args.out)
    content, total, orphan_count = build(data, existing, today, args.path)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(content)

    kept = sum(1 for v in existing.values() if v[0] != STATUS_TODO)
    emit("wrote %s（%d 個分類、%d 個作業項目）" % (args.out, len(data["categories"]), total),
         sys.stdout)
    if existing:
        emit("保留既有狀態 %d 列" % kept, sys.stdout)
    if orphan_count:
        emit("WARNING: %d 列在估算表已不存在，已移到檔尾「估算表已無此項」等人工確認。"
             % orphan_count)
    for w in data.get("warnings", []):
        emit("WARNING: " + w)


if __name__ == "__main__":
    main()
