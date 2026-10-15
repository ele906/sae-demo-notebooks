# Biased and unbiased prompt comparison

This comparison uses a common pooling method: first take each image's spatial maximum for each SAE feature, then average those per-image values within each race/gender prompt group. This matches the neutral-prompt cache, which only stores spatial maxima. The biased cache uses its `X_max` matrix for this reason.

The neutral-prompt set has 50 samples per race/gender cell; the open-prompt set has 100. The neutral cache uses the prompt-engineered neutral-expression, no-facial-covering, white-T-shirt, white-background template. The open-prompt cache uses `a picture of a {race} {gender}`. These caches use the same pretrained SAE feature dictionary, but the neutral cache was generated independently from the saved baseline PNGs and does not retain per-row seed metadata.

Each dataset has 12 figures. Each figure ranks ten features within its titled race/gender prompt group and shows each feature across all 12 groups. Dark and light shades distinguish men and women within each race color. Rankings are dataset-specific. The two sets are descriptive prompt-group associations, not semantic or causal results.

Figures are in `biased/` and `unbiased/`; combined values are in `mean_activations_biased_unbiased.csv`.
