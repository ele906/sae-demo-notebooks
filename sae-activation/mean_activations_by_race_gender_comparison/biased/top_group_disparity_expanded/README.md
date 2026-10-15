# Largest race/gender group differences in the biased dataset

## Section 1: one group vs. the other 11


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


## Section 2: predefined many-group contrasts

This section checks seven interpretable splits across the full 5,120-feature SAE dictionary: all women vs. all men, and each race's men and women together vs. the other five races. For each split, the table shows the three features with the largest absolute difference between the two side means. Each linked chart retains all 12 group bars. Repeated features share one chart.

| Contrast | Feature | First side mean | Comparison side mean | Difference | 12-group chart |
|---|---:|---:|---:|---:|---|
| All women vs. All men | 452 | 0.81 | 44.76 | -43.94 | [feature 452](many_vs_many/feature_452.png) |
| All women vs. All men | 2611 | 36.81 | 9.81 | +27.00 | [feature 2611](many_vs_many/feature_2611.png) |
| All women vs. All men | 1664 | 20.52 | 46.57 | -26.05 | [feature 1664](many_vs_many/feature_1664.png) |
| Black men and women vs. The other five races | 527 | 53.01 | 10.59 | +42.42 | [feature 527](many_vs_many/feature_527.png) |
| Black men and women vs. The other five races | 3279 | 38.33 | 7.52 | +30.81 | [feature 3279](many_vs_many/feature_3279.png) |
| Black men and women vs. The other five races | 546 | 5.45 | 25.37 | -19.92 | [feature 546](many_vs_many/feature_546.png) |
| White men and women vs. The other five races | 669 | 0.12 | 34.92 | -34.81 | [feature 669](many_vs_many/feature_669.png) |
| White men and women vs. The other five races | 3459 | 0.00 | 16.63 | -16.63 | [feature 3459](many_vs_many/feature_3459.png) |
| White men and women vs. The other five races | 3722 | 0.27 | 16.55 | -16.28 | [feature 3722](many_vs_many/feature_3722.png) |
| East Asian men and women vs. The other five races | 1759 | 28.06 | 0.00 | +28.06 | [feature 1759](many_vs_many/feature_1759.png) |
| East Asian men and women vs. The other five races | 1563 | 35.31 | 14.69 | +20.62 | [feature 1563](many_vs_many/feature_1563.png) |
| East Asian men and women vs. The other five races | 452 | 9.09 | 25.53 | -16.44 | [feature 452](many_vs_many/feature_452.png) |
| Middle Eastern men and women vs. The other five races | 138 | 51.52 | 3.05 | +48.47 | [feature 138](many_vs_many/feature_138.png) |
| Middle Eastern men and women vs. The other five races | 669 | 57.88 | 23.37 | +34.51 | [feature 669](many_vs_many/feature_669.png) |
| Middle Eastern men and women vs. The other five races | 2486 | 35.22 | 4.83 | +30.39 | [feature 2486](many_vs_many/feature_2486.png) |
| Indian men and women vs. The other five races | 669 | 55.40 | 23.87 | +31.53 | [feature 669](many_vs_many/feature_669.png) |
| Indian men and women vs. The other five races | 3181 | 30.36 | 3.45 | +26.91 | [feature 3181](many_vs_many/feature_3181.png) |
| Indian men and women vs. The other five races | 2527 | 34.33 | 8.44 | +25.89 | [feature 2527](many_vs_many/feature_2527.png) |
| Hispanic men and women vs. The other five races | 3884 | 24.77 | 2.31 | +22.46 | [feature 3884](many_vs_many/feature_3884.png) |
| Hispanic men and women vs. The other five races | 199 | 29.23 | 6.84 | +22.39 | [feature 199](many_vs_many/feature_199.png) |
| Hispanic men and women vs. The other five races | 138 | 0.33 | 13.28 | -12.95 | [feature 138](many_vs_many/feature_138.png) |

Differences are descriptive associations in this generated prompt dataset. They do not establish what a feature represents or why it activates. The many-vs-many scan uses predefined contrasts rather than searching every possible subset of the 12 groups.
