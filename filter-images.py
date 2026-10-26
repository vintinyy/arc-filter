"""Stage 2B: first-pass quality filter (blur + brightness).

Input : metadata CSV (needs an image_id column) + folder of <image_id>.jpg files
Output: CSV with one row per image: scores, kept, drop_reason

Usage:
    python filter_images.py --csv sample_metadata.csv --images sample_images --out filter_results.csv

All thresholds below are PLACEHOLDERS. Tune them against your hand labels.
"""
import argparse
import csv
import os

import cv2
import numpy as np


def blur_score(gray):
    """Variance of the Laplacian on the middle horizontal band.

    The top/bottom of an equirectangular pano are heavily stretched (sky, car roof),
    so only the middle half of the image height is scored. Higher = sharper.
    """
    h = gray.shape[0]
    band = gray[h // 4 : 3 * h // 4, :]
    return float(cv2.Laplacian(band, cv2.CV_64F).var())


def brightness_stats(gray, dark_cutoff=40, bright_cutoff=235):
    """Mean brightness plus fraction of very dark and blown-out pixels (middle band)."""
    h = gray.shape[0]
    band = gray[h // 4 : 3 * h // 4, :]
    return (
        float(band.mean()),
        float((band < dark_cutoff).mean()),
        float((band > bright_cutoff).mean()),
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--images", required=True)
    p.add_argument("--out", default="filter_results.csv")
    # Placeholder thresholds
    p.add_argument("--blur-min", type=float, default=100.0)
    p.add_argument("--brightness-min", type=float, default=50.0)
    p.add_argument("--brightness-max", type=float, default=220.0)
    p.add_argument("--pct-dark-max", type=float, default=0.5)
    p.add_argument("--pct-bright-max", type=float, default=0.3)
    args = p.parse_args()

    with open(args.csv, newline="") as f:
        image_ids = [row["image_id"] for row in csv.DictReader(f)]

    fields = ["image_id", "blur_score", "brightness_mean", "pct_dark", "pct_bright",
              "road_frac", "building_frac", "kept", "drop_reason"]

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()

        for image_id in image_ids:
            path = os.path.join(args.images, f"{image_id}.jpg")
            img = cv2.imread(path)
            if img is None:
                w.writerow({"image_id": image_id, "kept": False, "drop_reason": "unreadable"})
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = blur_score(gray)
            mean_b, pct_dark, pct_bright = brightness_stats(gray)

            reasons = []
            if blur < args.blur_min:
                reasons.append("blur")
            if mean_b < args.brightness_min or pct_dark > args.pct_dark_max:
                reasons.append("dark")
            if mean_b > args.brightness_max or pct_bright > args.pct_bright_max:
                reasons.append("overexposed")

            w.writerow({
                "image_id": image_id,
                "blur_score": round(blur, 2),
                "brightness_mean": round(mean_b, 2),
                "pct_dark": round(pct_dark, 4),
                "pct_bright": round(pct_bright, 4),
                "road_frac": "",       # TODO: segmentation model
                "building_frac": "",   # TODO: segmentation model
                "kept": not reasons,
                "drop_reason": ";".join(reasons),
            })

    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()