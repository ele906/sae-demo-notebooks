# SAE Explorer

A static, browser-only companion to the SAE notebooks. The page contains two views:

- A feature 3884 dose-response sweep with saved SDXL Turbo images, post-intervention activation overlays, and group-mean activation metrics.
- One-vs-many and predefined many-vs-many activation comparisons across the 12 race/gender prompt groups.

The slider selects one of the 19 saved alpha settings. It does not run SDXL in the browser. The portrait is seed 0; the displayed metrics are means across 20 seeds. The activation comparison values are means of spatial-max activations over 100 generated images per group. See the COS398 report for the source tables and caveats.

## Build the static data bundle

From this repository's root, with the sibling `cos398` checkout available:

```bash
python demo/build_demo_data.py
```

The script reads the committed group-activation CSV and the selected COS398 sweep results, then writes the JSON and small portrait assets consumed by `index.html`.

## Preview locally

```bash
python -m http.server 8000
```

Open `http://localhost:8000/demo/`.

To host it with GitHub Pages, set the `sae-demo-notebooks` repository's Pages source to **GitHub Actions**. The included workflow deploys this folder after changes land on `main`; the site will be available at `https://ele906.github.io/sae-demo-notebooks/`.

## Data and interpretation

Feature IDs are dictionary indices, not semantic labels. Group differences are descriptive associations in this generated prompt dataset. They do not establish feature meaning, identity, or causation. Intervention effects vary by group, prompt, seed, and alpha.
