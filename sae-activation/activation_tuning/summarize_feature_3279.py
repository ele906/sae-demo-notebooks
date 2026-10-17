"""Summarize feature 3279 metrics by biased race/gender group and alpha."""

import csv
import json
from collections import defaultdict
from pathlib import Path
import os

RUN = Path(os.environ.get("SAE_FEATURE_RUN", "run_biased_001")).expanduser().resolve()
GROUPS = [
    "black_man", "black_woman", "white_man", "white_woman",
    "east_asian_man", "east_asian_woman", "middle_eastern_man", "middle_eastern_woman",
    "indian_man", "indian_woman", "hispanic_man", "hispanic_woman",
]
FACTORS = [-120, -100, -75, -50, -30, -20, -15, -10, -7, -5, -3, 0, 3, 5, 7, 10, 15, 20, 30, 50, 75, 100, 120]
METRICS = {
    "pre_mean_activation": "mean_pre_intervention_activation",
    "mean_scaled_coefficient": "mean_scaled_coefficient",
    "mean_abs_scaled_coefficient": "mean_abs_scaled_coefficient",
    "mean_abs_intervention_coefficient_change": "mean_abs_intervention_coefficient_change",
    "post_reencoded_mean_activation": "mean_post_reencoded_feature_3279_activation",
    "post_reencoded_active_fraction": "mean_active_spatial_fraction",
    "pixel_mae_vs_original": "mean_pixel_mae_vs_original_rgb_0_255",
}


def main():
    rows = list(csv.DictReader((RUN / "metrics.csv").open(newline="")))
    buckets = defaultdict(list)
    for row in rows:
        buckets[(row["group"], int(row["alpha"]))].append(row)
    summary = []
    for group in GROUPS:
        for alpha in FACTORS:
            subset = buckets[(group, alpha)]
            out = {"feature": 3279, "group": group, "alpha": alpha, "n_images": len(subset)}
            for source, target in METRICS.items():
                out[target] = sum(float(r[source]) for r in subset) / len(subset)
            summary.append(out)
    with (RUN / "mean_metrics_by_group_alpha.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary)

    alphas = list(csv.DictReader((RUN / "mean_metrics_by_group_alpha.csv").open(newline="")))
    for group in GROUPS:
        group_dir = RUN / group
        group_dir.mkdir(exist_ok=True)
        selected = [r for r in alphas if r["group"] == group]
        display = group.replace("_", " ").title()
        lines = [
            f"# Feature 3279 — {display}", "",
            "Biased dataset; original prompt and seed replay for seeds 0–19. Values are means across 20 source images. The table reports the mean post-re-encoded activation of feature 3279, the active spatial fraction, mean RGB pixel MAE versus the original image (0–255 scale), and coefficient change magnitudes for each alpha.", "",
            "## Activation graph", "",
            f'<img src="activation_graph.png" width="380" alt="Feature 3279 graph for {display}">', "",
            "## Mean metrics by alpha", "",
            "| Alpha | Mean post-reencoded feature 3279 activation | Active spatial fraction | Mean pixel change (MAE) | Mean absolute coefficient change | Mean absolute scaled coefficient |", "|---:|---:|---:|---:|---:|---:|",
        ]
        for row in selected:
            lines.append(
                f"| {int(row['alpha']):+d} | {float(row['mean_post_reencoded_feature_3279_activation']):.3f} | "
                f"{float(row['mean_active_spatial_fraction']):.3f} | {float(row['mean_pixel_mae_vs_original_rgb_0_255']):.3f} | "
                f"{float(row['mean_abs_intervention_coefficient_change']):.3f} | {float(row['mean_abs_scaled_coefficient']):.3f} |"
            )
        lines += [
            "", "## Per-seed grids", "",
            "Each 5×4 sheet contains the original followed by the 19 alpha variants in ascending order.", "",
            "### Plain images", "",
            f'<img src="seed_sheets/{group}_seed0.jpg" width="1100" alt="{display} seed 0, original and alpha variants">', "",
            "[All 20 plain-image grids](seed_sheets/)", "",
            "### Signed coefficient overlays", "",
            f'<img src="signed_coefficient_overlays/{group}_seed0.jpg" width="1100" alt="{display} seed 0 signed coefficient overlays">', "",
            "[All 20 signed coefficient grids](signed_coefficient_overlays/)", "",
            "### Post-re-encoded activation overlays", "",
            f'<img src="post_activation_overlays/{group}_seed0.jpg" width="1100" alt="{display} seed 0 post-activation overlays">', "",
            "[All 20 post-activation grids](post_activation_overlays/)", "",
            "### Intervention-footprint overlays", "",
            "[All 20 intervention-footprint grids](intervention_footprint_overlays/)", "",
            "Zero is transparent. Negative coefficient colors progress green through blue to purple; positive colors progress yellow through orange to red. Each map tile is normalized individually for visibility. The original and alpha-zero tiles show the pre-intervention feature map so its location remains visible.", "",
        ]
        (group_dir / "README.md").write_text("\n".join(lines))

    settings = json.loads((RUN / "settings.json").read_text())
    settings["alpha_values"] = FACTORS
    settings["summary_metrics"] = "mean_metrics_by_group_alpha.csv; each row averages the 20 images in one group at one alpha"
    (RUN / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    print(f"Wrote {len(summary)} group-alpha rows and 12 group reports under {RUN}")


if __name__ == "__main__":
    main()
