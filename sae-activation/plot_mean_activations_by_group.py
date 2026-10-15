"""Plot top mean-activation SAE features for each race/gender prompt group."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


NOTEBOOK_ROOT = Path(__file__).resolve().parents[1]
ROOT = NOTEBOOK_ROOT.parent  # Companion debiasing checkout.
ACTIVATIONS = ROOT / "backprop" / "sae_features.npz"
MANIFEST = ROOT / "backprop" / "manifest.csv"
OUT = Path(__file__).resolve().parent
TOP_K = 10

RACE_COLORS = {
    "black": ("#8c1c13", "#e59891"),
    "white": ("#1f4e79", "#8fbce6"),
    "east asian": ("#2a6f3e", "#9bcf9f"),
    "middle eastern": ("#a65300", "#f2b36f"),
    "indian": ("#5b3c88", "#b7a2dc"),
    "hispanic": ("#6f4e37", "#c8a98d"),
}


def main():
    with MANIFEST.open(newline="") as f:
        prompts = {row["prompt"] for row in csv.DictReader(f)}
    if not prompts or any("t-shirt" in p or "neutral white background" in p for p in prompts):
        raise ValueError("Manifest is not the open-prompt dataset")
    if not all(p.startswith("a picture of a ") for p in prompts):
        raise ValueError(f"Unexpected prompt set: {sorted(prompts)[:3]}")

    with np.load(ACTIVATIONS, allow_pickle=False) as data:
        values = data["X_mean"].astype(np.float64)
        race_ids, gender_ids = data["y_race"], data["y_gender"]
        races, genders = data["races"].tolist(), data["genders"].tolist()

    if values.shape != (1200, 5120) or not np.isfinite(values).all():
        raise ValueError(f"Unexpected activation matrix: {values.shape}")
    groups = [(ri, gi, f"{races[ri]}_{genders[gi]}", f"{races[ri].title()} {genders[gi].title()}")
              for ri in range(len(races)) for gi in range(len(genders))]
    counts = [int(((race_ids == ri) & (gender_ids == gi)).sum()) for ri, gi, _, _ in groups]
    if counts != [100] * 12:
        raise ValueError(f"Expected 100 examples in each of 12 race/gender groups; got {counts}")

    means = np.stack([values[(race_ids == ri) & (gender_ids == gi)].mean(axis=0)
                      for ri, gi, _, _ in groups])
    top_features = [np.argsort(row)[-TOP_K:][::-1] for row in means]
    out_dir = OUT / "mean_activations_by_race_gender"
    out_dir.mkdir(exist_ok=True)

    csv_path = OUT / "mean_activations_by_race_gender.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ranking_group", "rank", "feature", "mean_activation_on_ranking_group"]
                        + [f"mean_activation_{slug}" for _, _, slug, _ in groups])
        for i, (_, _, group_slug, _) in enumerate(groups):
            for rank, feature in enumerate(top_features[i], 1):
                writer.writerow([group_slug, rank, int(feature), float(means[i, feature])]
                                + [float(means[j, feature]) for j in range(len(groups))])

    x = np.arange(len(groups))
    colors = [RACE_COLORS[races[ri]][0 if genders[gi] == "man" else 1]
              for ri, gi, _, _ in groups]
    labels = [f"{races[ri].title()}\n{genders[gi].title()}" for ri, gi, _, _ in groups]
    for target_idx, (_, _, group_slug, group_name) in enumerate(groups):
        fig, axes = plt.subplots(2, 5, figsize=(22, 10), constrained_layout=True)
        for rank, ax in enumerate(axes.flat):
            feature = top_features[target_idx][rank]
            bars = ax.bar(x, means[:, feature], color=colors, edgecolor="white", linewidth=0.5)
            ax.set_title(f"Rank {rank + 1}: feature {feature}")
            ax.set_xticks(x, labels, rotation=55, ha="right", fontsize=8)
            ax.set_ylabel("Mean spatial activation")
            ax.grid(axis="y", alpha=0.25)
            ax.set_axisbelow(True)
        fig.suptitle(f"Top 10 features for {group_name} prompts\n"
                     "Each panel compares one feature across all 12 race/gender groups",
                     fontsize=16)
        fig.savefig(out_dir / f"{group_slug}.png", dpi=180, bbox_inches="tight")
        plt.close(fig)

    readme = [
        "# Mean SAE activations by race and gender",
        "",
        "These charts use the 1,200-image open-prompt dataset (`a picture of a {race} {gender}`), not the engineered neutral-shirt/background dataset. The pretrained SAE's spatial-mean activations are averaged over the 100 images in each of the 12 prompt groups.",
        "",
        "There are 12 separate figures, one for each race/gender group. In each figure, the group's top ten features are ranked by its mean activation and shown in a 5×2 panel grid. Each panel contains 12 bars, one for each race/gender group, so the selected feature can be compared across groups. Men use a darker shade and women a lighter shade of the same race color.",
        "",
        "This is a descriptive comparison of prompt-group activations. It does not establish feature meaning or causation. The rankings and displayed means use all 1,200 images.",
        "",
        "The CSV records the selected features and all 12 group means. Figures are in `biased_top10_by_race_gender/`.",
    ]
    (OUT / "README_by_race_gender.md").write_text("\n".join(readme) + "\n")
    print(f"Wrote 12 figures to {out_dir}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
