#!/usr/bin/env python3
"""
recolor-icons.py · SVG 图标品牌色批量替换

将组件库 SVG 图标中的蓝色高亮部分（#1C66E5）批量替换为目标品牌色。
同时支持替换灰色主体（#4F586B / #6B758A）为自定义色。

用法:
  python3 recolor-icons.py --accent "#7c3aed"
  python3 recolor-icons.py --accent "#7c3aed" --base "#333333"
  python3 recolor-icons.py --accent "#7c3aed" --dir ./themes/meeting-classic/assets

参数:
  --accent    目标品牌色/强调色 (替换 #1C66E5)
  --base      目标主体灰色 (替换 #4F586B，可选)
  --secondary 目标次要灰色 (替换 #6B758A，可选)
  --dir       SVG 资产目录 (默认: 当前 skill 的 assets 目录)
  --dry-run   只打印会修改的文件，不实际写入
"""

import argparse
import os
import re
import sys

# 原始色值映射
DEFAULT_ACCENT = "#1C66E5"      # 蓝色高亮
DEFAULT_BASE = "#4F586B"        # 主体灰色
DEFAULT_SECONDARY = "#6B758A"   # 次要灰色

def find_svg_files(directory):
    """递归查找所有 SVG 文件"""
    svg_files = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.lower().endswith(".svg"):
                svg_files.append(os.path.join(root, f))
    return sorted(svg_files)


def replace_colors(content, replacements):
    """替换内容中的颜色值（大小写不敏感）"""
    modified = content
    for old_color, new_color in replacements.items():
        # 大小写不敏感替换
        pattern = re.compile(re.escape(old_color), re.IGNORECASE)
        modified = pattern.sub(new_color, modified)
    return modified


def main():
    parser = argparse.ArgumentParser(
        description="Recolor SVG icons to match brand theme"
    )
    parser.add_argument("--accent", required=True, help="Target accent/brand color (hex)")
    parser.add_argument("--base", default=None, help="Target base icon color (replaces #4F586B)")
    parser.add_argument("--secondary", default=None, help="Target secondary color (replaces #6B758A)")
    parser.add_argument("--dir", default=None, help="SVG assets directory")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")

    args = parser.parse_args()

    # 验证颜色格式
    for color_arg in [args.accent, args.base, args.secondary]:
        if color_arg and not re.match(r"^#[0-9a-fA-F]{6}$", color_arg):
            if color_arg:
                print("Error: Color must be 6-digit hex (e.g., #7c3aed)")
                sys.exit(1)

    # 确定 SVG 目录
    if args.dir:
        svg_dir = args.dir
    else:
        # 默认：skill 自身的 assets 目录
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        svg_dir = os.path.join(skill_dir, "assets", "themes", "meeting-classic", "assets")

    if not os.path.isdir(svg_dir):
        print("Error: Directory not found: {}".format(svg_dir))
        sys.exit(1)

    # 构建替换映射
    replacements = {DEFAULT_ACCENT: args.accent}
    if args.base:
        replacements[DEFAULT_BASE] = args.base
    if args.secondary:
        replacements[DEFAULT_SECONDARY] = args.secondary

    # 查找并处理 SVG
    svg_files = find_svg_files(svg_dir)
    modified_count = 0
    total_replacements = 0

    print("Scanning: {}".format(svg_dir))
    print("Replacements: {}".format(
        " | ".join("{} -> {}".format(k, v) for k, v in replacements.items())
    ))
    print("")

    for filepath in svg_files:
        with open(filepath, "r", encoding="utf-8") as f:
            original = f.read()

        modified = replace_colors(original, replacements)

        if modified != original:
            # 统计替换次数
            changes = 0
            for old_color in replacements:
                changes += len(re.findall(re.escape(old_color), original, re.IGNORECASE))

            rel_path = os.path.relpath(filepath, svg_dir)
            print("  [{}] {}".format(changes, rel_path))
            total_replacements += changes
            modified_count += 1

            if not args.dry_run:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(modified)

    print("")
    if args.dry_run:
        print("DRY RUN: Would modify {} files ({} color replacements)".format(
            modified_count, total_replacements
        ))
    else:
        print("Done: Modified {} files ({} color replacements)".format(
            modified_count, total_replacements
        ))


if __name__ == "__main__":
    main()
