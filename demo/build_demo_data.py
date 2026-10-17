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
FEATURE_ROOT = WORKSPACE / "sae-activation-tuning" / "tuning_activations"
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


def completed_sweep_runs():
    expected_groups = {slug for slug, _ in GROUPS}
    discovered = []
    for feature_dir in FEATURE_ROOT.glob("feature_*"):
        if not feature_dir.is_dir():
            continue
        try:
            feature = int(feature_dir.name.removeprefix("feature_"))
        except ValueError:
            continue
        candidates = []
        for run in feature_dir.glob("run_biased_*"):
            if not run.is_dir():
                continue
            try:
                settings = json.loads((run / "settings.json").read_text())
                groups = settings["groups"]
                alphas = [int(a) for a in settings["alpha_values"]]
                if set(groups) != expected_groups or settings.get("samples_per_group") != 20:
                    continue
                if not (run / "activation_maps.npz").is_file() or not (run / "mean_metrics_by_group_alpha.csv").is_file():
                    continue
                with (run / "mean_metrics_by_group_alpha.csv").open(newline="") as handle:
                    metric_rows = list(csv.DictReader(handle))
                if len(metric_rows) != len(GROUPS) * len(alphas):
                    continue
                if any(
                    not (run / "images" / group / "baseline" / "seed000.png").is_file()
                    or any(not (run / "images" / group / f"seed000_alpha_{alpha_slug(a)}.png").is_file()
                           for a in alphas)
                    for group in expected_groups
                ):
                    continue
                with np.load(run / "activation_maps.npz", allow_pickle=False) as maps:
                    keys = [str(key) for key in maps["map_keys"]]
                    if [int(a) for a in maps["multipliers"]] != alphas:
                        continue
                    if maps["pre_maps"].shape[0] != 240 or maps["post_reencoded_maps"].shape[:2] != (240, len(alphas)):
                        continue
                    expected_keys = {f"{group}|{seed}" for group in expected_groups for seed in range(20)}
                    if set(keys) != expected_keys:
                        continue
                candidates.append((run.stat().st_mtime, run, settings, metric_rows))
            except (OSError, KeyError, ValueError, json.JSONDecodeError):
                continue
        if candidates:
            _, run, settings, metric_rows = max(candidates, key=lambda item: item[0])
            discovered.append((feature, run, settings, metric_rows))
    priority = {3884: 0, 3279: 1}
    return sorted(discovered, key=lambda item: (priority.get(item[0], 2), item[0]))


def export_sweep():
    features = []
    for feature, run, settings, csv_rows in completed_sweep_runs():
        alphas = [int(a) for a in settings["alpha_values"]]
        by_group = {}
        for row in csv_rows:
            by_group.setdefault(row["group"], {})[int(row["alpha"])] = {
                "activation": float(row[f"mean_post_reencoded_feature_{feature}_activation"]),
                "activeFraction": float(row["mean_active_spatial_fraction"]),
                "pixelMae": float(row["mean_pixel_mae_vs_original_rgb_0_255"]),
            }

        with np.load(run / "activation_maps.npz", allow_pickle=False) as maps:
            keys = [str(key) for key in maps["map_keys"]]
            multipliers = [int(a) for a in maps["multipliers"]]
            pre_maps, post_maps = maps["pre_maps"], maps["post_reencoded_maps"]
            if multipliers != alphas:
                raise ValueError(f"Feature {feature}: map and settings alpha order differ")
            asset_root = OUT / "assets" / f"feature-{feature}"
            asset_root.mkdir(parents=True, exist_ok=True)
            feature_groups = []
            sheet_columns = None
            for group, label in GROUPS:
                cell = 256
                ntiles = len(alphas) + 1
                cols = 5 if ntiles <= 20 else 6
                sheet_columns = cols
                rows = (ntiles + cols - 1) // cols
                plain = Image.new("RGB", (cols * cell, rows * cell), "white")
                jet_sheet = Image.new("RGB", (cols * cell, rows * cell), "white")
                map_index = keys.index(f"{group}|0")
                sweep_maps = np.concatenate((pre_maps[map_index][None], post_maps[map_index]), axis=0)
                finite_sweep = sweep_maps[np.isfinite(sweep_maps)]
                shared_vmax = max(float(np.percentile(finite_sweep, 99.5)) if finite_sweep.size else 0.0, 1e-8)
                for tile_index in range(ntiles):
                    row, col = divmod(tile_index, cols)
                    if tile_index == 0:
                        source_path = run / "images" / group / "baseline" / "seed000.png"
                        values = pre_maps[map_index]
                    else:
                        alpha = alphas[tile_index - 1]
                        source_path = run / "images" / group / f"seed000_alpha_{alpha_slug(alpha)}.png"
                        values = post_maps[map_index, tile_index - 1]
                    with Image.open(source_path) as source:
                        base = source.convert("RGB").resize((cell, cell), Image.Resampling.LANCZOS)
                    plain.paste(base, (col * cell, row * cell))
                    values = np.asarray(values, dtype=np.float32)
                    normalized = np.clip(values / shared_vmax, 0, 1)
                    colors = (np.nan_to_num(__import__("matplotlib").colormaps["jet"](normalized)[..., :3]) * 255).astype(np.uint8)
                    opacity = (np.power(normalized, 0.65) * 210).clip(0, 210)
                    color_img = Image.fromarray(colors, "RGB").resize((cell, cell), Image.Resampling.NEAREST)
                    opacity_img = Image.fromarray(opacity.astype(np.uint8), "L").resize((cell, cell), Image.Resampling.NEAREST)
                    color_pixels = np.asarray(color_img, dtype=np.float32)
                    opacity_pixels = np.asarray(opacity_img, dtype=np.float32)[..., None] / 255.0
                    heat = Image.fromarray(np.uint8(np.clip(color_pixels * opacity_pixels + np.asarray(base) * (1 - opacity_pixels), 0, 255)), "RGB")
                    jet_sheet.paste(heat, (col * cell, row * cell))
                plain.save(asset_root / f"{group}-images.jpg", quality=86, optimize=True)
                jet_sheet.save(asset_root / f"{group}-jet.jpg", quality=86, optimize=True)

                rows_for_group = by_group[group]
                baseline = {
                    "activation": float(np.mean([float(row["mean_pre_intervention_activation"])
                                                 for row in csv_rows if row["group"] == group])),
                    "activeFraction": float(np.mean([np.mean(pre_maps[i] > 0)
                                                     for i, key in enumerate(keys) if key.startswith(group + "|")])),
                    "pixelMae": 0.0,
                }
                group_metrics = {str(a): rows_for_group[a] for a in alphas}
                group_metrics["original"] = baseline
                feature_groups.append({"id": group, "label": label, "metrics": group_metrics})
        features.append({"id": feature, "alphas": alphas, "groups": feature_groups,
                         "sheetColumns": sheet_columns, "sheetCell": 256})

    if not features:
        raise RuntimeError(f"No complete 12-group sweeps found under {FEATURE_ROOT}")
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
