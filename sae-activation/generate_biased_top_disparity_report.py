"""Generate per-feature group charts for the biased-set disparity report."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent / "mean_activations_by_race_gender_comparison"
CSV_PATH = ROOT / "mean_activations_biased_unbiased.csv"
OUTPUT = ROOT / "biased" / "top_group_disparity"
GROUPS = [
    ("black_man", "Black\nmen", "#8c1c13"),
    ("black_woman", "Black\nwomen", "#e59891"),
    ("white_man", "White\nmen", "#1f4e79"),
    ("white_woman", "White\nwomen", "#8fbce6"),
    ("east_asian_man", "East Asian\nmen", "#2a6f3e"),
    ("east_asian_woman", "East Asian\nwomen", "#9bcf9f"),
    ("middle_eastern_man", "Middle Eastern\nmen", "#a65300"),
    ("middle_eastern_woman", "Middle Eastern\nwomen", "#f2b36f"),
    ("indian_man", "Indian\nmen", "#5b3c88"),
    ("indian_woman", "Indian\nwomen", "#b7a2dc"),
    ("hispanic_man", "Hispanic\nmen", "#6f4e37"),
    ("hispanic_woman", "Hispanic\nwomen", "#c8a98d"),
]


def main():
    with CSV_PATH.open(newline="") as f:
        rows = [row for row in csv.DictReader(f) if row["dataset"] == "biased"]

    # Candidate pool is exactly the union of the biased dataset's 12 top-10 lists.
    features = sorted({int(row["feature"]) for row in rows})
    metrics = []
    for feature in features:
        row = next(row for row in rows if int(row["feature"]) == feature)
        values = np.array([float(row[f"mean_activation_{slug}"]) for slug, _, _ in GROUPS])
        peak_idx = int(values.argmax())
        other_mean = float(np.delete(values, peak_idx).mean())
        metrics.append({
            "feature": feature,
            "peak_group": GROUPS[peak_idx][1].replace("\n", " "),
            "peak": float(values[peak_idx]),
            "other_11_mean": other_mean,
            "gap": float(values[peak_idx] - other_mean),
            "values": values,
        })
    top = sorted(metrics, key=lambda item: item["gap"], reverse=True)[:10]

    OUTPUT.mkdir(parents=True, exist_ok=True)
    x = np.arange(len(GROUPS))
    for item in top:
        fig, ax = plt.subplots(figsize=(13, 6.5), constrained_layout=True)
        ax.bar(x, item["values"], color=[group[2] for group in GROUPS],
               edgecolor="white", linewidth=0.7)
        ax.set_xticks(x, [group[1] for group in GROUPS], fontsize=10)
        ax.set_ylabel("Mean per-image spatial-max activation")
        ax.set_title(f"Biased dataset — SAE feature {item['feature']}\n"
                     f"Peak: {item['peak_group']} ({item['peak']:.2f}); "
                     f"other 11 groups average {item['other_11_mean']:.2f}")
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        fig.savefig(OUTPUT / f"feature_{item['feature']}.png", dpi=180)
        plt.close(fig)

    lines = [
        "# Largest race/gender group differences in the biased dataset",
        "",
        "This report ranks features by the highest of their 12 race/gender group means minus the average of the other 11 group means. Candidate features are the union of features in the biased dataset's top-10 list for each of the 12 groups (35 unique features).",
        "",
        "Activations are means of per-image spatial maxima (`X_max`), using 100 images per group. The charts show all 12 groups for each of the ten largest gaps. Colors follow the comparison charts: race determines the hue and women use the lighter shade.",
        "",
        "| Rank | Feature | Peak group | Peak mean | Other 11 groups’ average | Difference | Chart |",
        "|---:|---:|---|---:|---:|---:|---|",
    ]
    for rank, item in enumerate(top, 1):
        feature = item["feature"]
        lines.append(
            f"| {rank} | {feature} | {item['peak_group']} | {item['peak']:.2f} "
            f"| {item['other_11_mean']:.2f} | {item['gap']:.2f} "
            f"| [feature {feature}](feature_{feature}.png) |"
        )
    lines.extend([
        "",
        "These are descriptive differences between generated prompt groups. They do not establish what a feature represents or why it activates.",
        "",
    ])
    (OUTPUT / "README.md").write_text("\n".join(lines))
    print(f"Wrote report and {len(top)} charts to {OUTPUT}")


if __name__ == "__main__":
    main()
