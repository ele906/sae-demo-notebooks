# Mean SAE activations by race and gender

These charts use the 1,200-image open-prompt dataset (`a picture of a {race} {gender}`), not the engineered neutral-shirt/background dataset. The pretrained SAE's spatial-mean activations are averaged over the 100 images in each of the 12 prompt groups.

There are 12 separate figures, one for each race/gender group. In each figure, the group's top ten features are ranked by its mean activation and shown in a 5×2 panel grid. Each panel contains 12 bars, one for each race/gender group, so the selected feature can be compared across groups. Men use a darker shade and women a lighter shade of the same race color.

This is a descriptive comparison of prompt-group activations. It does not establish feature meaning or causation. The rankings and displayed means use all 1,200 images.

The CSV records the selected features and all 12 group means. Figures are in `biased_top10_by_race_gender/`.
