# Largest race/gender group differences in the biased dataset

This report ranks features by the highest of their 12 race/gender group means minus the average of the other 11 group means. Candidate features are the union of features in the biased dataset's top-10 list for each of the 12 groups (35 unique features).

Activations are means of per-image spatial maxima (`X_max`), using 100 images per group. The charts show all 12 groups for each of the ten largest gaps. Colors follow the comparison charts: race determines the hue and women use the lighter shade.

| Rank | Feature | Peak group | Peak mean | Other 11 groups’ average | Difference | Chart |
|---:|---:|---|---:|---:|---:|---|
| 1 | 3279 | Black women | 63.70 | 8.01 | 55.69 | [feature 3279](feature_3279.png) |
| 2 | 138 | Middle Eastern women | 60.54 | 6.63 | 53.91 | [feature 138](feature_138.png) |
| 3 | 452 | Middle Eastern men | 66.45 | 18.82 | 47.64 | [feature 452](feature_452.png) |
| 4 | 527 | Black women | 58.09 | 13.98 | 44.11 | [feature 527](feature_527.png) |
| 5 | 3725 | Indian women | 46.13 | 9.40 | 36.73 | [feature 3725](feature_3725.png) |
| 6 | 2486 | Middle Eastern women | 42.60 | 6.92 | 35.68 | [feature 2486](feature_2486.png) |
| 7 | 669 | Middle Eastern men | 60.82 | 26.24 | 34.58 | [feature 669](feature_669.png) |
| 8 | 2527 | Indian women | 43.78 | 9.94 | 33.85 | [feature 2527](feature_2527.png) |
| 9 | 433 | White women | 44.53 | 11.97 | 32.56 | [feature 433](feature_433.png) |
| 10 | 3181 | Indian women | 36.25 | 5.36 | 30.89 | [feature 3181](feature_3181.png) |

These are descriptive differences between generated prompt groups. They do not establish what a feature represents or why it activates.
