# Current Implementation of Stage 2B: Quality Filter (Blur and Lighting)

## Purpose and Scope
The purpose of this script (`filter-images.py`) is to score each equirectangular panorama for blur and lighting, marking them as `keep` or `drop` so that MapSwipe volunteers receive a clean, filtered batch of images. 

* **Pipeline Position:** It takes metadata CSV files and raw panorama images (typically sourced from Stage 1/Mapillary outputs) and produces structured filtering results.
* **Current Status & Limitations:** The current version computes metrics directly on the middle band of the raw equirectangular panorama. However, the intended workflow requires processing each image through `py360convert` (reprojection into cube faces) to remove the stretching distortion near the poles. Because metrics on cube faces differ from raw panoramas, the thresholds in this document are provisional and will need to be re-tuned once `py360convert` integration is complete.

---

## Inputs and Outputs

### Inputs
* **Metadata CSV:** Must contain an `image_id` column.
* **Image Directory:** A folder containing images named `<image_id>.jpg`.

### Outputs (`filter_results.csv`)
The output CSV contains the filtering decisions and individual metric scores:
* `image_id`: Passes through unchanged from the input metadata.
* `blur_score`: Variance of the Laplacian computed on the middle band of the image.
* `mean_brightness`: Average pixel brightness of the evaluated band.
* `dark_frac`: Share of pixels below the dark cutoff (40).
* `bright_frac`: Share of pixels above the blown-out cutoff (235).
* `drop_reason`: Combined reasons for dropping an image (e.g., `blur; dark`), or left blank if kept.
* `kept`: Boolean/binary decision column (`1` for keep, `0` for drop) designated for downstream stages.

---

## Setup

1. **Python Version:** Python 3.8 or higher recommended.
2. **Virtual Environment:** Set up and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Git Bash / Windows
