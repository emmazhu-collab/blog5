# Blog 5: Texas County Household Income

## Question and method

Where are higher and lower household incomes concentrated in Texas, and what does the state median hide? A county map shows the statewide pattern. A second figure compares ten examples and their Census margins of error.

The analysis uses Python to download official data, read it with pandas and GeoPandas, filter Texas, join on GEOID, project the boundaries, and save maps and tables. It uses a continuous dollar color scale, not income totals or population counts.

## Folder structure

```text
blog5/
├── blog5.Rproj                Open this project in RStudio
├── README.md
├── code/
│   ├── download.py
│   └── analysis.py
├── requirements.txt
├── data/
│   ├── source/                 Original Census table, county ZIP, source log
│   └── processed/              Texas income CSV and joined GeoJSON
└── results/
    ├── figures/                Map and selected-county comparison
    ├── tables/                 County estimates, selected examples, summary
    └── environment.txt          Versions used for the analysis
```

The article is kept in `blog/posts/post5/` in my [website repository](https://github.com/emmazhu-collab/website). This project contains the analysis files. Running the Python code recreates the data tables and figures; it does not build the webpage.

## Sources

- [2024 ACS five-year Summary File, table B19013](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19013.dat): median household income and its margin of error.
- [2024 cartographic county boundaries, 1:500,000](https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip): county shapes used to draw the map.
- [Census Summary File documentation](https://www.census.gov/programs-surveys/acs/data/summary-file.2024.html).

The 2024 five-year release covers 2020–2024. Income is in 2024 inflation-adjusted dollars. The summary-file fields `B19013_E001` and `B19013_M001` correspond to API variables `B19013_001E` and `B19013_001M`. Margins of error use the Census 90% confidence level.

The download script uses public Census files, so no API key is needed. Both original files are included in this project. `data/source/sources.json` records URLs and the download date.

## Replication instructions

1. Open `blog5.Rproj` in RStudio, then open the **Terminal** tab. Run the commands below from the project folder. The analysis was tested with Python 3.13. Create a separate Python environment and install the saved package versions:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   These setup commands are for macOS or Linux. You only need to install packages once. Activate the environment again when starting a new Terminal session.

2. The inputs are already in `data/source/`: `acsdt5y2024-b19013.dat` and `cb_2024_us_county_500k.zip`. If either file is missing, download it:

   ```sh
   python code/download.py
   ```

3. Run the analysis:

   ```sh
   python code/analysis.py
   ```

RStudio's Terminal can run these commands; they are Python commands, not R Console commands. The scripts resolve paths from their own location, so no machine-specific file path is needed.

With saved inputs and packages installed, step 3 works offline. The downloader reuses existing files. The analysis always rebuilds the processed data, tables, and figures. No result is copied from Console output.

## Processing and checks

The code selects summary-file county IDs matching `0500000US48` plus three county digits, and state ID `0400000US48`. The final five digits give the county GEOID. It selects boundary `STATEFP == "48"` and checks 254 unique IDs on each side before a one-to-one merge.

Income and margins of error are converted to numbers. Negative Census placeholder values and nonnumeric entries are treated as missing rather than as dollars. All 254 counties have valid estimates and margins of error in the saved data. The map uses EPSG:5070, an equal-area projection, and checks valid, nonempty geometries.

The state reference is the Census estimate for Texas, not an average of county medians. Above/below-state counts describe county point estimates, not households or statistically tested differences. The ten counties in the second figure are illustrative examples named in the article, not a random sample. Error bars are estimate minus/plus the published margin of error; no significance tests are performed.

## Generated outputs

- `data/processed/texas-income-2024.csv`: 254 counties, income, margin of error, interval endpoints, and differences from the state estimate.
- `data/processed/texas-income-2024.geojson`: the same data joined to projected county geometries.
- `results/tables/county-estimates.csv`: all county estimates sorted by income; order is not a significance ranking.
- `results/tables/selected-counties.csv`: ten named examples.
- `results/tables/summary.csv` and `summary.json`: state median and coverage counts.
- `results/figures/texas-income-map.png`: central county income map.
- `results/figures/selected-county-incomes.png`: estimates and 90% margins of error.

Expected checks for these inputs: 254 matched counties; state median $78,476; 41 county estimates above and 213 below it. The figure and table files are saved programmatically. `results/environment.txt` records Python and core package versions.

## Updating the website article

After running the analysis, copy these files into the website project:

| File in this project | Location in the website project |
| --- | --- |
| `results/figures/texas-income-map.png` | `blog/posts/post5/graph/texas-income-map.png` |
| `results/figures/selected-county-incomes.png` | `blog/posts/post5/graph/selected-county-incomes.png` |
| `results/tables/county-estimates.csv` | `blog/posts/post5/data/county-estimates.csv` |
| `results/tables/summary.csv` | `blog/posts/post5/data/summary.csv` |

Then open the website project and render `blog/posts/post5/index.qmd`. The article reads the saved tables for its numbers and displays the saved figures. This step is only needed to update the webpage, not to reproduce the analysis.

## Limits

A county's area is not its population size. Median household income is not an individual salary and does not measure within-county inequality. Values are adjusted over time into 2024 dollars, but not for local living costs or household size. Five-year estimates are not a single-year snapshot. The analysis describes locations and differences; it does not identify their causes or determine funding priorities.
