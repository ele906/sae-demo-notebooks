"""Build the small, static data bundle used by the GitHub Pages demo.

Run from this repository with the sibling COS398 checkout present:
    python demo/build_demo_data.py
"""

import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
COS398 = WORKSPACE / "cos398"
OUT = ROOT / "demo"
GROUPS = [
    ("black_man", "Black men"),
    ("black_woman", "Black women"),
    ("white_man", "White men"),
    ("white_woman", "White women"),
    ("east_asian_man", "East Asian men"),
    ("east_asian_woman", "East Asian women"),
    ("middle_eastern_man", "Middle Eastern men"),
    ("middle_eastern_woman", "Middle Eastern women"),
    ("indian_man", "Indian men"),
    ("indian_woman", "Indian women"),
    ("hispanic_man", "Hispanic men"),
    ("hispanic_woman", "Hispanic women"),
]
ALPHAS = [-75, -50, -30, -20, -15, -10, -7, -5, -3, 0, 3, 5, 7, 10, 15, 20, 30, 50, 75]
MANY_CONTRASTS = [
    {"id": "gender", "label": "Women vs. men", "features": [452, 2611, 1664], "side": "gender"},
    {"id": "black", "label": "Black vs. other races", "features": [527, 3279, 546], "side": "black"},
    {"id": "white", "label": "White vs. other races", "features": [669, 3459, 3722], "side": "white"},
    {"id": "east-asian", "label": "East Asian vs. other races", "features": [1759, 1563, 452], "side": "east_asian"},
    {"id": "middle-eastern", "label": "Middle Eastern vs. other races", "features": [138, 669, 2486], "side": "middle_eastern"},
    {"id": "indian", "label": "Indian vs. other races", "features": [669, 3181, 2527], "side": "indian"},
    {"id": "hispanic", "label": "Hispanic vs. other races", "features": [3884, 199, 138], "side": "hispanic"},
]


def alpha_slug(alpha):
    return f"m{abs(alpha)}" if alpha < 0 else f"p{alpha}"


def read_group_activation_data():
    # The report uses per-image spatial maxima (X_max), not the spatial means
    # in mean_activations_by_race_gender.csv. Preserve its candidate pool and
    # compute selected feature summaries from the matching activation cache.
    report_csv = ROOT / "sae-activation" / "mean_activations_by_race_gender_comparison" / "mean_activations_biased_unbiased.csv"
    with report_csv.open(newline="") as handle:
        candidates = {int(row["feature"]) for row in csv.DictReader(handle) if row["dataset"] == "biased"}
    features = candidates | {feature for contrast in MANY_CONTRASTS for feature in contrast["features"]}
    cache_path = WORKSPACE / "backprop" / "sae_features.npz"
    with np.load(cache_path, allow_pickle=False) as cache:
        activations = cache["X_max"]
        race_ids, gender_ids = cache["y_race"], cache["y_gender"]
        races, genders = cache["races"].tolist(), cache["genders"].tolist()
        lookup = {
            f"{races[ri].replace(' ', '_')}_{genders[gi]}": (ri, gi)
            for ri in range(len(races)) for gi in range(len(genders))
        }
        values = {}
        for feature in features:
            values[feature] = {}
            for slug, _ in GROUPS:
                ri, gi = lookup[slug]
                mask = (race_ids == ri) & (gender_ids == gi)
                values[feature][slug] = float(activations[mask, feature].mean())

    one_vs_many = []
    for feature, means in values.items():
        peak = max(GROUPS, key=lambda group: means[group[0]])
        other_mean = sum(means[slug] for slug, _ in GROUPS if slug != peak[0]) / (len(GROUPS) - 1)
        one_vs_many.append({"feature": feature, "group": peak[0], "gap": means[peak[0]] - other_mean})
    one_vs_many.sort(key=lambda item: item["gap"], reverse=True)
    one_vs_many = one_vs_many[:10]

    return {
        "groups": [{"id": slug, "label": label} for slug, label in GROUPS],
        "means": {str(feature): means for feature, means in values.items()},
        "oneVsMany": one_vs_many,
        "manyVsMany": MANY_CONTRASTS,
    }


def export_sweep():
    source = COS398 / "tuning_activations" / "feature_3884"
    metric_path = source / "mean_metrics_by_group_alpha.csv"
    by_group = {}
    with metric_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if int(row["alpha"]) not in ALPHAS:
                continue
            by_group.setdefault(row["group"], {})[int(row["alpha"])] = {
                "activation": float(row["mean_post_reencoded_feature_3884_activation"]),
                "activeFraction": float(row["mean_active_spatial_fraction"]),
                "pixelMae": float(row["mean_pixel_mae_vs_original_rgb_0_255"]),
            }

    sample_groups = ["hispanic_woman", "hispanic_man", "black_woman", "white_man", "white_woman"]
    asset_root = OUT / "assets" / "feature-3884"
    for group in sample_groups:
        plain_sheet = source / group / "seed_sheets" / f"{group}_seed0.jpg"
        overlay_sheet = source / group / "post_activation_overlays" / f"{group}_seed0.jpg"
        if not plain_sheet.exists() or not overlay_sheet.exists():
            continue
        group_dir = asset_root / group
        group_dir.mkdir(parents=True, exist_ok=True)
        for view, sheet_path in (("image", plain_sheet), ("overlay", overlay_sheet)):
            with Image.open(sheet_path) as sheet:
                width, height = sheet.size
                cell_w, cell_h = width // 5, height // 4
                for index, alpha in enumerate([None] + ALPHAS):
                    row, col = divmod(index, 5)
                    # The source sheets have a 30-pixel text label above each portrait.
                    crop = sheet.crop((col * cell_w, row * cell_h + 30,
                                       (col + 1) * cell_w, (row + 1) * cell_h))
                    name = "baseline" if alpha is None else alpha_slug(alpha)
                    crop.save(group_dir / f"{view}-{name}.jpg", quality=90, optimize=True)

    demo_sweep = {
        "feature": 3884,
        "alphas": ALPHAS,
        "groups": [
            {"id": slug, "label": dict(GROUPS)[slug], "metrics": by_group.get(slug, {})}
            for slug in sample_groups if slug in by_group
        ],
        "imageNote": "Portraits show seed 0; metrics are means across 20 seeds per group.",
    }
    (OUT / "data").mkdir(exist_ok=True)
    (OUT / "data" / "sweep.json").write_text(json.dumps(demo_sweep, indent=2) + "\n")


def main():
    (OUT / "data").mkdir(exist_ok=True)
    (OUT / "data" / "activations.json").write_text(
        json.dumps(read_group_activation_data(), indent=2) + "\n"
    )
    export_sweep()
    print(f"Built static demo data in {OUT}")


if __name__ == "__main__":
    main()
