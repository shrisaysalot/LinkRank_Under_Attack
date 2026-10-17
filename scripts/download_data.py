"""Download SNAP and WEBSPAM-UK2006 datasets to data/raw/."""
import sys
import os
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import gzip
import tarfile
import shutil
import urllib.request

from src.config import RAW_DATA_DIR

URLS = {
    "wiki-Vote": "https://snap.stanford.edu/data/wiki-Vote.txt.gz",
    "web-Stanford": "https://snap.stanford.edu/data/web-Stanford.txt.gz",
    "web-NotreDame": "https://snap.stanford.edu/data/web-NotreDame.txt.gz",
    "webspam-uk2006-2.0": "https://chato.cl/webspam/datasets/uk2006/webspam-uk2006-2.0.tar.gz"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}


def download_file(url: str, dest_path: Path, max_retries: int = 3) -> bool:
    """Download a file with browser headers and retry logic."""
    if dest_path.exists() and dest_path.stat().st_size > 0:
        print(f"[SKIP] {dest_path.name} already exists ({dest_path.stat().st_size / 1e6:.2f} MB).")
        return True

    print(f"[DOWNLOADING] {url} -> {dest_path}...")
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as response, open(dest_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
            print(f"[SUCCESS] Downloaded {dest_path.name} ({dest_path.stat().st_size / 1e6:.2f} MB).")
            return True
        except Exception as e:
            print(f"[WARNING] Attempt {attempt} failed for {url}: {e}")
            if dest_path.exists():
                dest_path.unlink()

    print(f"[FAILED] Could not download {url} after {max_retries} attempts.")
    return False


def extract_webspam():
    tar_path = RAW_DATA_DIR / "webspam-uk2006-2.0.tar.gz"
    extract_dir = RAW_DATA_DIR / "webspam-uk2006"
    if tar_path.exists() and not extract_dir.exists():
        print(f"[EXTRACTING] {tar_path} -> {extract_dir}...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=RAW_DATA_DIR)
        print("[SUCCESS] Extracted WEBSPAM-UK2006 archive.")


def main():
    print("=== Downloading Datasets for LinkRank Under Attack ===")
    results = {}
    for name, url in URLS.items():
        ext = ".tar.gz" if url.endswith(".tar.gz") else (".txt.gz" if url.endswith(".txt.gz") else Path(url).suffix)
        target_file = RAW_DATA_DIR / f"{name}{ext}"
        success = download_file(url, target_file)
        results[name] = success

    extract_webspam()

    print("\nDownload Summary:")
    for name, ok in results.items():
        status = "OK" if ok else "FAILED/UNAVAILABLE"
        print(f" - {name}: {status}")


if __name__ == "__main__":
    main()
