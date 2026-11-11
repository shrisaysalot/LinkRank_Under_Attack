import urllib.request
import os
from pathlib import Path

def download_gdrive(file_id, dest_path):
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    print(f"Downloading {file_id} to {dest_path}...")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            if len(content) < 1000 and b"<!DOCTYPE html>" in content:
                print("Warning: Received HTML instead of binary. File might require confirm token or cookie.")
                return False
            with open(dest_path, "wb") as f:
                f.write(content)
        print(f"Successfully downloaded {dest_path.name}: {len(content)} bytes")
        return True
    except Exception as e:
        print(f"Failed to download {file_id}: {e}")
        return False

raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

hnames_ok = download_gdrive("1WIz_A1g3LjBG0gppjP5SHTth8gHVkpbz", raw_dir / "uk-2006-05.hostnames.txt.gz")
hgraph_ok = download_gdrive("1-Liy-fgvS6HVeFbeSg7V55nxr4gVem6t", raw_dir / "uk-2006-05.hostgraph.txt.gz")

