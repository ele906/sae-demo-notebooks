# SAE demo notebooks

Interactive notebooks for image generation, SAE activation inspection, SAE fine-tuning, and feature suppression.

## Notebooks

- [`generation/generate_images.ipynb`](generation/generate_images.ipynb): choose SDXL Turbo or SDXL Base, enter a prompt, and generate a seeded batch.
- [`generation/compare_models.ipynb`](generation/compare_models.ipynb): compare both models on the same prompt.
- [`sae-activation/inspect_spatial_activations.ipynb`](sae-activation/inspect_spatial_activations.ipynb): overlay one SAE unit's spatial activation on a generated image and optionally show its C2C box.
- [`sae-activation/mean_activations_by_race.ipynb`](sae-activation/mean_activations_by_race.ipynb): rank the top ten SAE features by mean activation within each race group on the open-prompt portrait dataset, then compare those features across race groups.
- [`sae-activation/mean_activations_by_race_gender.ipynb`](sae-activation/mean_activations_by_race_gender.ipynb): make 12 separate figures, one per race/gender prompt group, with ten feature panels and twelve category bars per figure.
- [`sae-activation/compare_biased_unbiased_mean_activations.ipynb`](sae-activation/compare_biased_unbiased_mean_activations.ipynb): generate matched comparisons for both prompt datasets, saved in separate `biased/` and `unbiased/` result folders.
- [`sae-activation/activation_tuning/feature_138_biased_dataset_alpha_sweep.ipynb`](sae-activation/activation_tuning/feature_138_biased_dataset_alpha_sweep.ipynb): intervene on feature 138 in the original biased dataset images, replaying each image's saved simple prompt and seed across 19 alpha values.
- [`sae-activation/activation_tuning/feature_3884_biased_dataset_alpha_sweep.ipynb`](sae-activation/activation_tuning/feature_3884_biased_dataset_alpha_sweep.ipynb): intervene on feature 3884 across all 12 biased race/gender groups, using 20 images per group and a symmetric 19-value alpha sweep.
- [`sae-tuning/fine_tune_box_sae.ipynb`](sae-tuning/fine_tune_box_sae.ipynb): configure and launch the existing C2C box-supervised SAE fine-tuning script.
- [`sae-feature-suppression/suppress_features.ipynb`](sae-feature-suppression/suppress_features.ipynb): configure and launch the existing feature-ablation comparison, including no-op strengths and a random control.

## Setup

The notebooks in `generation/` use Jupyter widgets on the cluster login node to submit GPU work with `sbatch`. The SLURM job uses `torch`, `diffusers`, and `safetensors` from `/n/fs/goose/el8403/conda-envs/reno/bin/python`; set `SAE_DEMO_PYTHON` before starting Jupyter if your environment is elsewhere. Model files must be available in the shared Hugging Face cache or downloadable from the compute node. Accept the SDXL Base terms and authenticate if Hugging Face asks.

The three SAE notebooks use the experiment code, SAE package, checkpoints, labels, images, and activation caches from the companion [`ele906/debiasing`](https://github.com/ele906/debiasing) checkout. For this workspace layout, keep this repository at `/n/fs/goose/sae-demo-notebooks` beside the debiasing files in `/n/fs/goose`. If you clone elsewhere, edit the `DEBIASING_ROOT` setting near the top of each SAE notebook. Data, checkpoints, and generated images are not included in this public repository.

The mean-activation notebook uses the 1,200 simple-prompt images (`a picture of a {race} {gender}`) and their cached spatial-mean activations. It pools genders within each race, ranks features on the full dataset for this descriptive chart, and compares each race's top features across all race groups. The result is descriptive prompt-group association, not evidence of semantic meaning or causation.

The race/gender mean-activation notebook keeps all 12 prompt groups separate. It ranks ten features within each group and plots each feature's mean across all 12 groups. Bar colors share a hue by race, with darker shades for men and lighter shades for women. Outputs are saved under `sae-activation/mean_activations_by_race_gender/` with a CSV of all values.

The two-dataset comparison uses the mean of per-image spatial-max activations for both sets because the neutral-prompt cache stores spatial maxima. It saves 12 figures under each of `sae-activation/mean_activations_by_race_gender_comparison/biased/` and `.../unbiased/`, plus a combined CSV. The neutral cache contains 50 examples per group; the open-prompt cache contains 100. The neutral cache was generated independently from the saved baseline PNGs.

Feature 138 tuning uses the biased dataset's saved Middle Eastern women images and their original prompts (`a picture of a middle eastern woman`) and seeds from the manifest. It runs the original plus 19 alpha values per seed and saves activation metrics, generated images, and signed coefficient overlays. The prior headscarf/no-headscarf prompt-controlled run is retained separately as an exploratory archive.

Feature 3884 tuning uses the first 20 original seeds in each of the 12 biased race/gender groups. Its alpha values are `-75, -50, -30, -20, -15, -10, -7, -5, -3, 0, 3, 5, 7, 10, 15, 20, 30, 50, 75`, with the original image shown first in each 5×4 grid. Results are organized under a separate folder for each group in `cos398/tuning_activations/feature_3884/`.

Run the SAE notebooks with the debiasing environment and local artifacts ready. The activation notebook uses a CUDA GPU; the tuning and suppression notebooks start their existing Python scripts in the notebook kernel when you click their run buttons, so open those notebooks from a GPU allocation. They do not automatically submit jobs to Slurm.

All notebook outputs are cleared before commit. Run output folders and local model/data artifacts are ignored by Git.
