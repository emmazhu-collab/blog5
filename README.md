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
    └── tables/                 County estimates, selected examples, summary
```

The article is kept in `blog/posts/post5/` in my [website repository](https://github.com/emmazhu-collab/website). This project contains the analysis files. Running the Python code recreates the data tables and figures; it does not build the webpage.

## Sources

- [2024 ACS five-year Summary File, table B19013](https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/5YRData/acsdt5y2024-b19013.dat): median household income and its margin of error.
- [2024 cartographic county boundaries, 1:500,000](https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip): county shapes used to draw the map.
- [Census Summary File documentation](https://www.census.gov/programs-surveys/acs/data/summary-file.2024.html).

The 2024 five-year release covers 2020–2024. Income is in 2024 inflation-adjusted dollars. The summary-file fields `B19013_E001` and `B19013_M001` correspond to API variables `B19013_001E` and `B19013_001M`. Margins of error use the Census 90% confidence level.

The download script uses public Census files, so no API key is needed. Both original files are included in this project. `data/source/sources.json` records URLs and the download date.

## Replication instructions

### Get the project

On the [Blog 5 GitHub page](https://github.com/emmazhu-collab/blog5), choose **Code > Download ZIP**, then unzip the folder. Keep `code`, `data`, `requirements.txt`, and `blog5.Rproj` together. Download the full project rather than copying only the Python code. Open `blog5.Rproj` in RStudio.

The steps below are for macOS or Linux. A downloaded project does not include `.venv`; new users should complete **First-time setup** in Terminal before choosing a run method. If you already have the project and its working environment, skip setup.

### Run directly in RStudio

Open `blog5.Rproj`. Before starting Python, select **Session > Restart R**. In the **R Console** (the prompt is `>`), copy only the two lines inside this box, paste them into the R Console, and press Enter. Do not copy the backticks:

```r
library(reticulate)
use_python(file.path(getwd(), ".venv", "bin", "python"), required = TRUE)
```

These lines select this project's Python environment. If `.venv` does not exist, complete the first-time Terminal setup below first. If `reticulate` is missing, install it once with `install.packages("reticulate")` in the R Console.

Open `code/analysis.py`, select all the code with **Command+A**, and click **Run**. Run from the top so that imports and data are created before the plotting steps. The script supports this interactive mode as well as Terminal execution.

A `>>>` prompt means you are now in Python. Do not enter R functions such as `py_run_string()` there. To return to R, type `exit`. If an error occurs, check the first error: later messages such as `fig is not defined` may only be consequences of it.

The figures are saved in `results/figures/`. Open those PNG files to view them. Running the code does not automatically open a plot window.

### Run in Terminal instead

Open `blog5.Rproj` in RStudio. Select **Terminal**, next to Console. If it is not visible, use **Tools > Terminal > New Terminal**.

Copy only the commands inside each code box, paste them into Terminal, and press Enter. Do not copy the backticks or paste these commands into the R Console. You can run the whole file in Terminal, or use the RStudio Run steps above.

The commands below are for macOS or Linux. They should run from the `blog5` project folder. Type `pwd` to check the current folder and `ls` to check that it contains `code`, `data`, and `requirements.txt`. If needed, type `cd `, drag the project folder from Finder into Terminal, and press Enter.

### First-time setup

You need Python 3.13. If this project already has a working `.venv` with the required packages, skip this step. Otherwise, copy and run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Wait for installation to finish before running the analysis. An internet connection is needed to install packages. The main packages are pandas, GeoPandas, Matplotlib, and requests. `requirements.txt` lists the tested versions.

### Run the analysis

Copy this command into Terminal each time you want to recreate the results:

```sh
.venv/bin/python code/analysis.py
```

This uses the project's Python environment directly, so you do not need to activate it first. The two inputs are included in `data/source/`: `acsdt5y2024-b19013.dat` and `cb_2024_us_county_500k.zip`. With these inputs and the packages installed, the analysis works offline. No API key is needed.

The command prints the summary and saves the tables in `results/tables/` and two PNG figures in `results/figures/`. It also recreates `data/processed/`. Open the PNG files to view the figures; they do not automatically appear in RStudio's Plots panel. Expected results include 254 counties and a Texas median income of $78,476.

If either original input is missing, run this command with an internet connection, then run the analysis again:

```sh
.venv/bin/python code/download.py
```

The downloader keeps existing source files. The analysis rebuilds its outputs from the saved inputs; no results are manually copied from Console output.

### Run in JupyterLab

Complete the first-time setup above first. Then, in **Terminal**, from the Blog 5 project folder, copy and run:

```sh
.venv/bin/python -m pip install jupyterlab ipykernel
.venv/bin/python -m ipykernel install --user --name blog5 --display-name "Python (Blog5)"
.venv/bin/python -m jupyterlab
```

Install JupyterLab and register the kernel only once. On later visits, run only the last command from the project folder. If you already use Jupyter, you can open it as usual after registering the kernel and select **Python (Blog5)**.

In JupyterLab, create a notebook in the main Blog 5 folder, beside `code`, `data`, and `requirements.txt`. Choose the **Python (Blog5)** kernel. Copy this line into a **code cell** and press **Shift+Enter**:

```python
%run code/analysis.py
```

This runs the saved script and recreates the same tables and figures. You do not need to copy the full script into the notebook. If you prefer to paste all of `code/analysis.py` into one code cell, that also works when the notebook is in the main project folder. Run the cell from the beginning.

The script saves figures instead of displaying them automatically. To view one inside the notebook, run a new cell:

```python
from IPython.display import Image, display
display(Image(filename="results/figures/texas-income-map.png"))
display(Image(filename="results/figures/selected-county-incomes.png"))
```

If a package is missing, check that the selected kernel is **Python (Blog5)**. If a file cannot be found, run `%pwd` in a cell and check that the notebook is working from the main Blog 5 folder.

### If a command does not work

- `__file__ is not defined`: reopen the updated script from disk; it now supports interactive Run. Open the project before running it.
- `ModuleNotFoundError`: install the requirements with `.venv/bin/python -m pip install -r requirements.txt`. This installs them in the same environment used by the analysis.
- `No such file or directory`: check that Terminal is in the project folder. If `.venv/bin/python` is missing, complete first-time setup.
- An R error such as `unexpected symbol`: switch from Console to Terminal before pasting the command.

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

Expected checks for these inputs: 254 matched counties; state median $78,476; 41 county estimates above and 213 below it. The figure and table files are saved programmatically.

## Updating the website article

After running the analysis, use Finder to copy the files below into the matching folders in the website project. Copy the files themselves, keep their names unchanged, and replace the old copies if prompted:

| File in this project | Location in the website project |
| --- | --- |
| `results/figures/texas-income-map.png` | `blog/posts/post5/graph/texas-income-map.png` |
| `results/figures/selected-county-incomes.png` | `blog/posts/post5/graph/selected-county-incomes.png` |
| `results/tables/county-estimates.csv` | `blog/posts/post5/data/county-estimates.csv` |
| `results/tables/summary.csv` | `blog/posts/post5/data/summary.csv` |

Then open the website project and render `blog/posts/post5/index.qmd`. The article reads the saved tables for its numbers and displays the saved figures. This step is only needed to update the webpage, not to reproduce the analysis.

## Limits

A county's area is not its population size. Median household income is not an individual salary and does not measure within-county inequality. Values are adjusted over time into 2024 dollars, but not for local living costs or household size. Five-year estimates are not a single-year snapshot. The analysis describes locations and differences; it does not identify their causes or determine funding priorities.
