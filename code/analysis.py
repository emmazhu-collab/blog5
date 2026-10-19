"""Read saved Census data, join county boundaries, and save tables and figures."""
from pathlib import Path
import json
import sys
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import patheffects

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'source'
PROCESSED = ROOT / 'data' / 'processed'
TABLES = ROOT / 'results' / 'tables'
FIGURES = ROOT / 'results' / 'figures'
for path in [PROCESSED, TABLES, FIGURES]:
    path.mkdir(parents=True, exist_ok=True)

# B19013_E001 / M001 are the summary-file names for API variables
# B19013_001E / 001M: median household income estimate and 90% margin of error.
source = pd.read_csv(RAW / 'acsdt5y2024-b19013.dat', sep='|', dtype=str)
income = source.loc[source['GEO_ID'].str.fullmatch(r'0500000US48\d{3}')].copy()
income['GEOID'] = income['GEO_ID'].str[-5:]
income['income'] = pd.to_numeric(income['B19013_E001'], errors='coerce')
income['moe'] = pd.to_numeric(income['B19013_M001'], errors='coerce')
# Census suppression / annotation values must not be treated as dollar amounts.
income.loc[income['income'] < 0, 'income'] = float('nan')
income.loc[income['moe'] < 0, 'moe'] = float('nan')
state = source.loc[source['GEO_ID'].eq('0400000US48')].iloc[0]
state_income = float(state['B19013_E001'])
state_moe = float(state['B19013_M001'])
assert len(income) == 254 and income['GEOID'].is_unique

counties = gpd.read_file(RAW / 'cb_2024_us_county_500k.zip')
texas = counties.loc[counties['STATEFP'].eq('48'), ['GEOID', 'NAME', 'geometry']].copy()
assert len(texas) == 254 and texas['GEOID'].is_unique
assert set(texas['GEOID']) == set(income['GEOID'])
texas = texas.merge(income[['GEOID', 'income', 'moe']], on='GEOID', how='left', validate='one_to_one')
texas = texas.to_crs('EPSG:5070')
assert texas.geometry.is_valid.all() and not texas.geometry.is_empty.any()
texas['lower90'] = texas['income'] - texas['moe']
texas['upper90'] = texas['income'] + texas['moe']
texas['difference_from_state'] = texas['income'] - state_income
texas['moe_percent'] = 100 * texas['moe'] / texas['income']
texas.drop(columns='geometry').sort_values('GEOID').to_csv(PROCESSED / 'texas-income-2024.csv', index=False)
texas.to_file(PROCESSED / 'texas-income-2024.geojson', driver='GeoJSON')
summary = {'counties': len(texas), 'valid_estimates': int(texas['income'].notna().sum()),
           'missing_moe': int(texas['moe'].isna().sum()),
           'state_income': state_income, 'state_moe': state_moe,
           'above_state': int((texas['income'] > state_income).sum()),
           'below_state': int((texas['income'] < state_income).sum()),
           'at_least_100000': int((texas['income'] >= 100000).sum())}
(TABLES / 'summary.json').write_text(json.dumps(summary, indent=2))
pd.DataFrame([summary]).to_csv(TABLES / 'summary.csv', index=False)
texas.drop(columns='geometry').sort_values('income', ascending=False).to_csv(TABLES / 'county-estimates.csv', index=False)

# Illustrative counties named in the article, not a random sample or metro classification.
selected_names = ['Collin', 'Denton', 'Dallas', 'Fort Bend', 'Harris', 'Williamson', 'Travis',
                  'Hidalgo', 'Cameron', 'Starr']
selected = texas.loc[texas['NAME'].isin(selected_names)].sort_values('income').copy()
assert len(selected) == len(selected_names)
selected.drop(columns='geometry').to_csv(TABLES / 'selected-counties.csv', index=False)

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.spines.top': False,
                     'axes.spines.right': False})
fig, ax = plt.subplots(figsize=(10, 9))
texas.plot(column='income', cmap='YlGnBu', edgecolor='white', linewidth=0.25,
           legend=True, legend_kwds={'label': 'Median household income (2024 dollars)',
           'shrink': 0.62, 'format': FuncFormatter(lambda x, pos: f'${x/1000:,.0f}k')},
           missing_kwds={'color': '#d8d8d8', 'label': 'No estimate'}, ax=ax)
# County labels locate the examples discussed in the article.
labels = ['Collin', 'Fort Bend', 'Travis', 'Hidalgo', 'Starr']
offsets = {'Collin': (15, 15), 'Fort Bend': (22, -3), 'Travis': (-55, 2),
           'Hidalgo': (30, -12), 'Starr': (-40, -10)}
for _, row in texas.loc[texas['NAME'].isin(labels)].iterrows():
    point = row.geometry.representative_point()
    label = ax.annotate(row['NAME'], xy=(point.x, point.y), xytext=offsets[row['NAME']],
                       textcoords='offset points', fontsize=9, color='#222222',
                       arrowprops={'arrowstyle': '-', 'color': '#444444', 'lw': 0.7})
    label.set_path_effects([patheffects.withStroke(linewidth=2.5, foreground='white')])
ax.set_title('Household income varies across Texas counties', fontsize=17, loc='left', pad=16)
ax.set_axis_off()
fig.text(0.08, 0.075, '2020–2024 ACS five-year estimates • 254 counties\nSource: U.S. Census Bureau, B19013 and 2024 county boundaries (1:500,000).\nCounty area is not population size. Albers equal-area projection (EPSG:5070).', fontsize=9)
fig.subplots_adjust(left=0.04, right=0.96, bottom=0.14, top=0.93)
fig.savefig(FIGURES / 'texas-income-map.png', dpi=200)
plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 6.4))
y = range(len(selected))
ax.errorbar(selected['income'], y, xerr=selected['moe'], fmt='o', color='#286789',
            ecolor='#7598a6', capsize=3, markersize=6)
ax.set_yticks(list(y), selected['NAME'] + ' County')
ax.axvspan(state_income-state_moe, state_income+state_moe, color='#b65c2e', alpha=0.12)
ax.axvline(state_income, color='#b65c2e', linestyle='--', label=f'Texas median: ${state_income:,.0f}')
ax.set_xlim(0, max(selected['upper90']) * 1.08)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'${x/1000:,.0f}k'))
ax.set_xlabel('Median household income (2024 dollars)')
ax.set_title('Nearby counties can have different income levels', loc='left', fontsize=16, pad=18)
ax.grid(axis='x', alpha=0.2)
ax.legend(loc='lower right', frameon=False)
fig.text(0.08, 0.025, 'Selected examples, not all counties. Bars show Census 90% margins of error.\nSource: 2020–2024 ACS, B19013. Shading shows the state margin of error.', fontsize=9)
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(FIGURES / 'selected-county-incomes.png', dpi=200)
plt.close(fig)
(ROOT / 'results' / 'environment.txt').write_text(f'Python {sys.version.split()[0]}\npandas {pd.__version__}\ngeopandas {gpd.__version__}\nmatplotlib {matplotlib.__version__}\n')
print(json.dumps(summary, indent=2))
print(texas[['NAME', 'income', 'moe']].sort_values('income', ascending=False).head(12).to_string(index=False))
print(selected[['NAME', 'income', 'moe']].to_string(index=False))
