"""Generate a batch from a JSON config. Intended to run as a SLURM job."""

import argparse
import json
from pathlib import Path

from generation_utils import generate_batch, load_pipeline


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="JSON job config written by the notebook")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    pipe = load_pipeline(config["model_name"])
    images, run_dir, settings = generate_batch(
        pipe=pipe,
        model_name=config["model_name"],
        prompt=config["prompt"],
        count=int(config["count"]),
        seed=int(config["seed"]),
        steps=int(config["steps"]),
        guidance=float(config["guidance"]),
        output_root=config["output_root"],
        run_name=config["run_name"],
    )
    print(json.dumps({"output_dir": str(run_dir), "images": len(images), "settings": settings}, indent=2))


if __name__ == "__main__":
    main()
