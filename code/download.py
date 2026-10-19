"""Download the two public Census input files once; no API key is needed."""
from pathlib import Path
import datetime
import json
import requests

# Terminal runs use the script location; RStudio Run uses the project folder.
ROOT = Path(__file__).resolve().parents[1] if '__file__' in globals() else Path.cwd()
if ROOT.name == 'code':
    ROOT = ROOT.parent

RAW = ROOT / 'data' / 'source'
RAW.mkdir(parents=True, exist_ok=True)
urls = {
 'acsdt5y2024-b19013.dat': 'https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19013.dat',
 'cb_2024_us_county_500k.zip': 'https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip'
}
for name, url in urls.items():
    path = RAW / name
    if not path.exists():
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        path.write_bytes(response.content)
manifest = RAW / 'sources.json'
if not manifest.exists():
    manifest.write_text(json.dumps({'downloaded_on': str(datetime.date.today()), 'urls': urls}, indent=2))
print('Official source files ready. Existing downloads were reused.')
