"""Pull ~50 panoramas from Mapillary for a bounding box and save metadata + images.

Usage:
    export MAPILLARY_TOKEN="MLY|29096634703287067|99cd9bb2cec249f80b459b860e25d612"
    python pull-medan-sample.py
"""
import csv
import os
import requests

TOKEN = os.environ["MAPILLARY_TOKEN"]

# bbox = min_lon, min_lat, max_lon, max_lat (central Medan as a starting guess).
# Mapillary rejects large boxes, so keep it small (~0.01 degrees per side).
# Open mapillary.com/app, find benjidad's coverage in Medan, and adjust.
BBOX = "98.669,3.589,98.671,3.591"
LIMIT = 30
OUT_DIR = "sample_images"

FIELDS = ",".join([
    "id", "sequence", "geometry", "captured_at", "compass_angle",
    "computed_compass_angle", "is_pano", "thumb_2048_url",
])

os.makedirs(OUT_DIR, exist_ok=True)

resp = requests.get(
    "https://graph.mapillary.com/images",
    headers={"Authorization": f"OAuth {TOKEN}"},
    params={"bbox": BBOX, "is_pano": "true", "fields": FIELDS, "limit": LIMIT},
    timeout=30,
)
#resp.raise_for_status()

if not resp.ok:
    print(resp.status_code, resp.text)
    resp.raise_for_status()

images = resp.json().get("data", [])
print(f"Got {len(images)} images")

with open("sample_metadata.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["image_id", "sequence_id", "lat", "lon", "captured_at",
                "compass_angle", "computed_compass_angle", "is_pano", "image_url"])
    for img in images:
        lon, lat = img["geometry"]["coordinates"]
        url = img.get("thumb_2048_url")
        w.writerow([img["id"], img.get("sequence"), lat, lon,
                    img.get("captured_at"), img.get("compass_angle"),
                    img.get("computed_compass_angle"), img.get("is_pano"), url])
        if url:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            with open(os.path.join(OUT_DIR, f"{img['id']}.jpg"), "wb") as out:
                out.write(r.content)

print(f"Saved sample_metadata.csv and images in ./{OUT_DIR}/")