from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _pick_latest_jobs_csv(dir_path: Path) -> Path:
    candidates = list(dir_path.glob("jobs_*.csv"))
    if not candidates:
        raise FileNotFoundError(f"在目录中找不到 jobs_*.csv: {dir_path}")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def main() -> int:
    parser = argparse.ArgumentParser(description="对招聘 CSV 做城市/技能统计并输出图表。")
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=None,
        help="crawl_jobs.py 生成的 jobs_*.csv 路径；也可以传目录（会自动选最新 jobs_*.csv）；不传则默认用 recruit_analysis/output 下最新的 jobs_*.csv",
    )
    parser.add_argument("--out", default=None, help="输出目录（默认: 与 CSV 同目录）")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    default_dir = base_dir / "output"

    if args.csv_path is None:
        csv_path = _pick_latest_jobs_csv(default_dir)
    else:
        p = Path(args.csv_path).expanduser().resolve()
        if p.is_dir():
            csv_path = _pick_latest_jobs_csv(p)
        else:
            csv_path = p

    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    out_dir = Path(args.out).expanduser().resolve() if args.out else csv_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Windows 下 matplotlib 默认字体可能不含中文，设置一个常见中文字体优先（不存在则自动回退）
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    # 城市职位数 Top 10
    city_counts = (
        df["city"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
        .value_counts()
        .head(10)
    )
    city_counts.to_csv(out_dir / "city_top10.csv", encoding="utf-8-sig")

    plt.figure(figsize=(10, 5))
    city_counts.sort_values().plot(kind="barh")
    plt.title("Top 10 城市/地区职位数量")
    plt.xlabel("职位数量")
    plt.tight_layout()
    plt.savefig(out_dir / "city_top10.png", dpi=160)
    plt.close()

    # 技能标签 Top 10（来自 tags 列，用 | 分隔）
    tags = (
        df["tags"]
        .fillna("")
        .astype(str)
        .str.split("|")
        .explode()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .str.lower()
    )
    skill_counts = tags.value_counts().head(10)
    skill_counts.to_csv(out_dir / "skills_top10.csv", encoding="utf-8-sig")

    plt.figure(figsize=(10, 5))
    skill_counts.sort_values().plot(kind="barh")
    plt.title("Top 10 技能标签")
    plt.xlabel("出现次数")
    plt.tight_layout()
    plt.savefig(out_dir / "skills_top10.png", dpi=160)
    plt.close()

    print(f"输入: {csv_path}")
    print(f"输出目录: {out_dir}")
    print("已生成: city_top10.csv / skills_top10.csv / city_top10.png / skills_top10.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


