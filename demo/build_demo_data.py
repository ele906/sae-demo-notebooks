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
    features = []
    for feature in (3884, 3279):
        run = WORKSPACE / "sae-activation-tuning" / "tuning_activations" / f"feature_{feature}" / "run_biased_001"
        source = COS398 / "tuning_activations" / f"feature_{feature}"
        settings = json.loads((run / "settings.json").read_text())
        alphas = [int(a) for a in settings["alpha_values"]]
        metric_path = run / "mean_metrics_by_group_alpha.csv"
        by_group = {}
        with metric_path.open(newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
            for row in csv_rows:
                if int(row["alpha"]) in alphas:
                    by_group.setdefault(row["group"], {})[int(row["alpha"])] = {
                        "activation": float(row[f"mean_post_reencoded_feature_{feature}_activation"]),
                        "activeFraction": float(row["mean_active_spatial_fraction"]),
                        "pixelMae": float(row["mean_pixel_mae_vs_original_rgb_0_255"]),
                    }

        maps_path = run / "activation_maps.npz"
        with np.load(maps_path, allow_pickle=False) as maps:
            keys = [str(key) for key in maps["map_keys"]]
            multipliers = [int(a) for a in maps["multipliers"]]
            pre_maps, post_maps = maps["pre_maps"], maps["post_reencoded_maps"]
            assert multipliers == alphas, f"Feature {feature}: map and settings alpha order differ"
            asset_root = OUT / "assets" / f"feature-{feature}"
            asset_root.mkdir(parents=True, exist_ok=True)
            for group, label in GROUPS:
                sheet_path = source / group / "seed_sheets" / f"{group}_seed0.jpg"
                if not sheet_path.exists():
                    raise FileNotFoundError(sheet_path)
                with Image.open(sheet_path) as sheet:
                    cell, top = 384, 30
                    cols = sheet.width // cell
                    ntiles = len(alphas) + 1
                    rows = (ntiles + cols - 1) // cols
                    plain = Image.new("RGB", (cols * cell, rows * cell), "white")
                    jet_sheet = Image.new("RGB", (cols * cell, rows * cell), "white")
                    map_index = keys.index(f"{group}|0")
                    for tile_index in range(ntiles):
                        row, col = divmod(tile_index, cols)
                        x0, y0 = col * cell, row * (cell + top)
                        base = sheet.crop((x0, y0 + top, x0 + cell, y0 + top + cell)).convert("RGB")
                        plain.paste(base, (col * cell, row * cell))
                        values = pre_maps[map_index] if tile_index == 0 else post_maps[map_index, tile_index - 1]
                        if tile_index > 0 and alphas[tile_index - 1] == 0:
                            values = pre_maps[map_index]
                        values = np.asarray(values, dtype=np.float32)
                        finite = values[np.isfinite(values)]
                        vmax = max(float(np.percentile(finite, 99.5)) if finite.size else 0.0, 1e-8)
                        normalized = np.clip(values / vmax, 0, 1)
                        colors = (np.nan_to_num(__import__("matplotlib").colormaps["jet"](normalized)[..., :3]) * 255).astype(np.uint8)
                        opacity = (np.power(normalized, 0.65) * 210).clip(0, 210)
                        color_img = Image.fromarray(colors, "RGB").resize((cell, cell), Image.Resampling.NEAREST)
                        opacity_img = Image.fromarray(opacity.astype(np.uint8), "L").resize((cell, cell), Image.Resampling.NEAREST)
                        color_pixels = np.asarray(color_img, dtype=np.float32)
                        opacity_pixels = np.asarray(opacity_img, dtype=np.float32)[..., None] / 255.0
                        heat = Image.fromarray(np.uint8(np.clip(color_pixels * opacity_pixels + np.asarray(base) * (1 - opacity_pixels), 0, 255)), "RGB")
                        jet_sheet.paste(heat, (col * cell, row * cell))
                    asset_dir = asset_root
                    plain.save(asset_dir / f"{group}-images.jpg", quality=86, optimize=True)
                    jet_sheet.save(asset_dir / f"{group}-jet.jpg", quality=86, optimize=True)

                rows_for_group = by_group.get(group, {})
                # Alpha 1 is the no-op coefficient multiplier, so use it as the
                # closest saved intervention to the original image when present.
                baseline = {
                    "activation": float(np.mean([float(row["mean_pre_intervention_activation"])
                                                 for row in csv_rows if row["group"] == group])),
                    "activeFraction": float(np.mean([np.mean(pre_maps[i] > 0)
                                                     for i, key in enumerate(keys) if key.startswith(group + "|")])),
                    "pixelMae": 0.0,
                }
                group_metrics = {str(a): rows_for_group.get(a, {}) for a in alphas}
                group_metrics["original"] = baseline
                if group == GROUPS[0][0]:
                    feature_groups = []
                feature_groups.append({"id": group, "label": label, "metrics": group_metrics})
        features.append({"id": feature, "alphas": alphas, "groups": feature_groups})

    demo_sweep = {"features": features,
                  "imageNote": "Portraits show seed 0; metrics are means across 20 seeds per group."}
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
