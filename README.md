# SAE demo notebooks

Interactive notebooks for image generation, SAE activation inspection, SAE fine-tuning, and feature suppression.

## Notebooks

- [`generation/generate_images.ipynb`](generation/generate_images.ipynb): choose SDXL Turbo or SDXL Base, enter a prompt, and generate a seeded batch.
- [`generation/compare_models.ipynb`](generation/compare_models.ipynb): compare both models on the same prompt.
- [`sae-activation/inspect_spatial_activations.ipynb`](sae-activation/inspect_spatial_activations.ipynb): overlay one SAE unit's spatial activation on a generated image and optionally show its C2C box.
- [`sae-tuning/fine_tune_box_sae.ipynb`](sae-tuning/fine_tune_box_sae.ipynb): configure and launch the existing C2C box-supervised SAE fine-tuning script.
- [`sae-feature-suppression/suppress_features.ipynb`](sae-feature-suppression/suppress_features.ipynb): configure and launch the existing feature-ablation comparison, including no-op strengths and a random control.

## Setup

The notebooks in `generation/` use Jupyter widgets on the cluster login node to submit GPU work with `sbatch`. The SLURM job uses `torch`, `diffusers`, and `safetensors` from `/n/fs/goose/el8403/conda-envs/reno/bin/python`; set `SAE_DEMO_PYTHON` before starting Jupyter if your environment is elsewhere. Model files must be available in the shared Hugging Face cache or downloadable from the compute node. Accept the SDXL Base terms and authenticate if Hugging Face asks.

The three SAE notebooks use the experiment code, SAE package, checkpoints, labels, images, and activation caches from the companion [`ele906/debiasing`](https://github.com/ele906/debiasing) checkout. For this workspace layout, keep this repository at `/n/fs/goose/sae-demo-notebooks` beside the debiasing files in `/n/fs/goose`. If you clone elsewhere, edit the `DEBIASING_ROOT` setting near the top of each SAE notebook. Data, checkpoints, and generated images are not included in this public repository.

Run the SAE notebooks with the debiasing environment and local artifacts ready. The activation notebook uses a CUDA GPU; the tuning and suppression notebooks start their existing Python scripts in the notebook kernel when you click their run buttons, so open those notebooks from a GPU allocation. They do not automatically submit jobs to Slurm.

All notebook outputs are cleared before commit. Run output folders and local model/data artifacts are ignored by Git.
