"""Compare mean per-image spatial-max SAE activations in two prompt datasets."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


NOTEBOOK_ROOT = Path(__file__).resolve().parents[1]
DEBIASING_ROOT = NOTEBOOK_ROOT.parent
OUTPUT_ROOT = NOTEBOOK_ROOT / "sae-activation" / "mean_activations_by_race_gender_comparison"
TOP_K = 10

RACE_COLORS = {
    "black": ("#8c1c13", "#e59891"),
    "white": ("#1f4e79", "#8fbce6"),
    "east asian": ("#2a6f3e", "#9bcf9f"),
    "middle eastern": ("#a65300", "#f2b36f"),
    "indian": ("#5b3c88", "#b7a2dc"),
    "hispanic": ("#6f4e37", "#c8a98d"),
}


def load_set(name, path, matrix_key):
    with np.load(path, allow_pickle=False) as data:
        values = data[matrix_key].astype(np.float64)
        race_ids, gender_ids = data["y_race"], data["y_gender"]
        races, genders = data["races"].tolist(), data["genders"].tolist()
    if values.shape[1] != 5120 or not np.isfinite(values).all():
        raise ValueError(f"Unexpected {name} activations: {values.shape}")
    groups = [(ri, gi, f"{races[ri].replace(' ', '_')}_{genders[gi]}",
               f"{races[ri].title()} {genders[gi].title()}")
              for ri in range(len(races)) for gi in range(len(genders))]
    counts = [int(((race_ids == ri) & (gender_ids == gi)).sum()) for ri, gi, _, _ in groups]
    expected = 100 if name == "biased" else 50
    if len(groups) != 12 or counts != [expected] * 12:
        raise ValueError(f"{name} has missing race/gender groups: {counts}")
    means = np.stack([values[(race_ids == ri) & (gender_ids == gi)].mean(axis=0)
                      for ri, gi, _, _ in groups])
    return races, genders, groups, means, counts


def main():
    datasets = {
        "biased": load_set("biased", DEBIASING_ROOT / "backprop" / "sae_features.npz", "X_max"),
        # This 600-row neutral-prompt cache contains spatial maxima (50 per cell).
        "unbiased": load_set("unbiased", DEBIASING_ROOT / "race_classifier" / "race_classify_features.npz", "X"),
    }
    biased_meta, unbiased_meta = datasets["biased"], datasets["unbiased"]
    if biased_meta[0] != unbiased_meta[0] or biased_meta[1] != unbiased_meta[1]:
        raise ValueError("The two activation caches use different category orderings")
    races, genders = biased_meta[0], biased_meta[1]
    groups = biased_meta[2]
    for name, (_, _, other_groups, _, _) in datasets.items():
        if [g[2] for g in groups] != [g[2] for g in other_groups]:
            raise ValueError(f"Category order differs for {name}")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    x = np.arange(len(groups))
    colors = [RACE_COLORS[races[ri]][0 if genders[gi] == "man" else 1]
              for ri, gi, _, _ in groups]
    labels = [f"{races[ri].title()}\n{genders[gi].title()}" for ri, gi, _, _ in groups]

    for dataset_name, (_, _, dataset_groups, means, counts) in datasets.items():
        top_features = [np.argsort(row)[-TOP_K:][::-1] for row in means]
        dataset_dir = OUTPUT_ROOT / dataset_name
        dataset_dir.mkdir(exist_ok=True)
        for target_idx, (_, _, group_slug, group_name) in enumerate(dataset_groups):
            for rank, feature in enumerate(top_features[target_idx], 1):
                rows.append([dataset_name, group_slug, rank, int(feature),
                             float(means[target_idx, feature]), counts[target_idx]]
                            + [float(means[j, feature]) for j in range(len(groups))])

            fig, axes = plt.subplots(2, 5, figsize=(22, 10), constrained_layout=True)
            for rank, ax in enumerate(axes.flat):
                feature = top_features[target_idx][rank]
                ax.bar(x, means[:, feature], color=colors, edgecolor="white", linewidth=0.5)
                ax.set_title(f"Rank {rank + 1}: feature {feature}")
                ax.set_xticks(x, labels, rotation=55, ha="right", fontsize=8)
                ax.set_ylabel("Mean of per-image spatial-max activation")
                ax.grid(axis="y", alpha=0.25)
                ax.set_axisbelow(True)
            fig.suptitle(f"{dataset_name.title()} prompt set: top 10 for {group_name}\n"
                         "Each panel compares the feature across all 12 race/gender groups",
                         fontsize=16)
            fig.savefig(dataset_dir / f"{group_slug}.png", dpi=180, bbox_inches="tight")
            plt.close(fig)

    csv_path = OUTPUT_ROOT / "mean_activations_biased_unbiased.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["dataset", "ranking_group", "rank", "feature",
                         "mean_activation_on_ranking_group", "images_in_ranking_group"]
                        + [f"mean_activation_{slug}" for _, _, slug, _ in groups])
        writer.writerows(rows)

    note = [
        "# Biased and unbiased prompt comparison",
        "",
        "This comparison uses a common pooling method: first take each image's spatial maximum for each SAE feature, then average those per-image values within each race/gender prompt group. This matches the neutral-prompt cache, which only stores spatial maxima. The biased cache uses its `X_max` matrix for this reason.",
        "",
        "The neutral-prompt set has 50 samples per race/gender cell; the open-prompt set has 100. The neutral cache uses the prompt-engineered neutral-expression, no-facial-covering, white-T-shirt, white-background template. The open-prompt cache uses `a picture of a {race} {gender}`. These caches use the same pretrained SAE feature dictionary, but the neutral cache was generated independently from the saved baseline PNGs and does not retain per-row seed metadata.",
        "",
        "Each dataset has 12 figures. Each figure ranks ten features within its titled race/gender prompt group and shows each feature across all 12 groups. Dark and light shades distinguish men and women within each race color. Rankings are dataset-specific. The two sets are descriptive prompt-group associations, not semantic or causal results.",
        "",
        "Figures are in `biased/` and `unbiased/`; combined values are in `mean_activations_biased_unbiased.csv`.",
    ]
    (OUTPUT_ROOT / "README.md").write_text("\n".join(note) + "\n")
    print(f"Generated {sum(len(meta[2]) for meta in datasets.values())} figures in {OUTPUT_ROOT}")
    for name, meta in datasets.items():
        print(f"{name}: {sum(meta[4])} cached samples; {meta[4]} per group")


if __name__ == "__main__":
    main()
