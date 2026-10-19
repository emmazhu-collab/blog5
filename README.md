# Blog 5: Texas County Household Income

## Question and method

Where are higher and lower household incomes located in Texas, and what does the state median hide? A county map shows the pattern. Another figure compares ten counties and their uncertainty.

This project uses R. I read county polygons with `sf`, check county IDs, merge income with the shapes, and change the coordinate system. The static map follows the DataCamp structure: `tm_shape()`, `tm_fill()`, `tm_borders()`, and `tm_text()`. Leaflet adds zooming and county popups. The comparison uses ggplot2.

The article is separate, in `blog/posts/post5/` in the [website repository](https://github.com/emmazhu-collab/website). This repository contains the analysis process.

## Folder structure

```text
blog5/
├── blog5.Rproj
├── README.md
├── code/
│   ├── download.R
│   └── analysis.R
├── data/
│   ├── source/       Saved API data, county ZIP, and source record
│   └── processed/    Joined county CSV and GeoJSON
└── results/
    ├── tables/       County estimates, selected examples, and summary
    └── figures/      Maps, HTML support files, and comparison figure
```

## Sources

- [2024 ACS five-year API](https://api.census.gov/data/2024/acs/acs5.html): variable `B19013_001`, median household income and its 90% margin of error. The release covers 2020–2024; income is in 2024 dollars.
- [2024 Census county boundaries, 1:500,000](https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip): county shapes.
- `data/source/sources.csv`: source URLs and retrieval date, without an API key.

The saved API tables are `texas-county-income-2024.csv` and `texas-state-income-2024.csv`. They contain IDs, names, estimates, and margins of error. The boundary ZIP is included. The interactive map uses the saved county shapes and does not request background tiles.

## Replication instructions

### Get the project

On GitHub, choose **Code > Download ZIP**, unzip it, and open `blog5.Rproj` in RStudio. Keep all folders together. Copying only the script without the data is not enough.

If Console shows `>>>`, select **Session > Restart R**. Use the **R Console**, with a `>` prompt. Copy only the commands inside the boxes, without backticks.

### Install missing packages once

In the R Console, install any missing packages:

```r
install.packages(c("tidyverse", "sf", "tmap", "leaflet", "htmlwidgets", "tidycensus"))
```

The code uses tmap 4. DataCamp's older examples use `palette` and `title` inside `tm_fill()`; tmap 4 uses `fill.scale` and `fill.legend`. The shape-and-layer approach is the same. Package installation needs internet access.

### Run in RStudio

With the Blog 5 project open, copy this into the R Console and press Enter:

```r
source("code/analysis.R")
```

Or open `code/analysis.R`, select all with **Command+A**, and click **Run**. Run from the beginning. The working directory must be the project folder, not `code/`; check it with `getwd()`.

The code reads saved inputs and recreates processed data, tables, and figures. No API key or internet connection is needed to calculate results. The interactive map also works offline because its shapes, values, and support files are stored locally.

Static figures appear in Plots when run interactively. The Leaflet map opens in Viewer. Run `income_leaflet` to show it again. The PNG files are saved in `results/figures/`.

In a Terminal opened in the project folder, you can instead run:

```sh
Rscript code/analysis.R
```

### Optional: Jupyter

Use an **R kernel**, not a Python kernel. If R is not available in Jupyter, run these once in the R Console:

```r
install.packages("IRkernel")
IRkernel::installspec(user = TRUE)
```

Registration requires Jupyter to be installed and on the system path. Create a notebook in the main Blog 5 folder and select the R kernel. Paste this into a code cell and press **Shift+Enter**:

```r
source("code/analysis.R")
income_leaflet
```

Run `income_map` or `comparison` in another cell to display the static figures. The generated files are the same as in RStudio.

### Optional: download again

Normal reproduction uses the included inputs. To fetch them again, store your own key as `CENSUS_API_KEY` in your local user `.Renviron` and restart R. Do not put the key in code or commit `.Renviron`. Then run:

```r
source("code/download.R")
source("code/analysis.R")
```

The download script uses `tidycensus::get_acs()` for Texas counties and the state. It updates the API CSV files and source record. It downloads the boundary ZIP only if missing. This step needs internet access and a valid Census key.

## Checks and outputs

The code checks 254 unique county IDs on each side before merging, matching IDs, valid polygons, and nonmissing estimates. It does not assign income by row order. Negative Census placeholder values are treated as missing.

| Output | Contents |
| --- | --- |
| `data/processed/texas-income-2024.csv` | 254 counties, income, margin of error, 90% interval endpoints, and difference from the state |
| `data/processed/texas-income-2024.geojson` | County data with longitude/latitude shapes |
| `results/tables/county-estimates.csv` | All counties sorted by income estimate |
| `results/tables/selected-counties.csv` | Ten selected examples |
| `results/tables/summary.csv` | State median and county counts |
| `results/figures/texas-income-map.png` | tmap map in EPSG:5070 |
| `results/figures/texas-income-interactive.html` | Leaflet map with labels and popups |
| `results/figures/texas-income-interactive_files/` | Required JavaScript and CSS; keep beside the HTML file |
| `results/figures/selected-county-incomes.png` | ggplot2 comparison with 90% confidence intervals |

Expected results: 254 counties; Texas median $78,476; 41 county estimates above and 213 below it. Counts compare estimates, not households or statistically tested differences. All outputs are saved by code.

## Update the website

In Finder, copy everything in `results/figures/` into the website's `blog/posts/post5/graph/`, including the HTML support folder. Copy `county-estimates.csv` and `summary.csv` from `results/tables/` into `blog/posts/post5/data/`. Keep filenames unchanged and replace the old copies.

Open the website project and render `blog/posts/post5/index.qmd`. It displays saved results without rerunning the analysis or calling the API. The article shows prose and figures without visible code.

## Limits

County area is not population size. Household income is not an individual salary or a measure of within-county inequality. The five-year estimates are not a snapshot of 2024 alone. They do not adjust for local living costs or household size. Small differences may reflect sampling error. The selected counties are examples, not a comparison of all urban and rural areas. These patterns do not establish causes.
