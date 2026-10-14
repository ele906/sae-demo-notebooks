# SAE demo notebooks

Interactive notebooks for image generation, SAE activation inspection, SAE fine-tuning, and feature suppression.

## Notebooks

- [`generation/generate_images.ipynb`](generation/generate_images.ipynb): choose SDXL Turbo or SDXL Base, enter a prompt, and generate a seeded batch.
- [`generation/compare_models.ipynb`](generation/compare_models.ipynb): compare both models on the same prompt.
- [`sae-activation/inspect_spatial_activations.ipynb`](sae-activation/inspect_spatial_activations.ipynb): overlay one SAE unit's spatial activation on a generated image and optionally show its C2C box.
- [`sae-tuning/fine_tune_box_sae.ipynb`](sae-tuning/fine_tune_box_sae.ipynb): configure and launch the existing C2C box-supervised SAE fine-tuning script.
- [`sae-feature-suppression/suppress_features.ipynb`](sae-feature-suppression/suppress_features.ipynb): configure and launch the existing feature-ablation comparison, including no-op strengths and a random control.

## Setup

The notebooks in `generation/` work independently with a CUDA GPU, `torch`, `diffusers`, `safetensors`, `ipywidgets`, and Jupyter. First use downloads the selected Hugging Face model; accept the SDXL Base terms and sign in if Hugging Face asks.

The three SAE notebooks use the experiment code, SAE package, checkpoints, labels, images, and activation caches from the companion [`ele906/debiasing`](https://github.com/ele906/debiasing) checkout. For this workspace layout, keep this repository at `/n/fs/goose/sae-demo-notebooks` beside the debiasing files in `/n/fs/goose`. If you clone elsewhere, edit the `DEBIASING_ROOT` setting near the top of each SAE notebook. Data, checkpoints, and generated images are not included in this public repository.

Run the SAE notebooks on a CUDA GPU node with the debiasing environment and local artifacts ready. The tuning and suppression notebooks start their existing Python scripts only when you click their run buttons. They do not automatically submit jobs to Slurm.

All notebook outputs are cleared before commit. Run output folders and local model/data artifacts are ignored by Git.
