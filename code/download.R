# Run from the blog5 project folder. The key stays in your local .Renviron.
library(tidycensus)
library(readr)
library(dplyr)

dir.create('data/source', recursive = TRUE, showWarnings = FALSE)
if (!nzchar(Sys.getenv('CENSUS_API_KEY'))) {
  stop('Set CENSUS_API_KEY in your local .Renviron, restart R, and try again.')
}
county_income <- get_acs(geography = 'county', state = 'TX',
                         variables = 'B19013_001', year = 2024,
                         survey = 'acs5', geometry = FALSE)
state_income <- get_acs(geography = 'state', state = 'TX',
                        variables = 'B19013_001', year = 2024,
                        survey = 'acs5', geometry = FALSE)
write_csv(county_income, 'data/source/texas-county-income-2024.csv')
write_csv(state_income, 'data/source/texas-state-income-2024.csv')
boundary_url <- 'https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_500k.zip'
if (!file.exists('data/source/cb_2024_us_county_500k.zip')) {
  download.file(boundary_url, 'data/source/cb_2024_us_county_500k.zip', mode = 'wb')
}
write_csv(tibble(source = c('ACS county estimates', 'ACS state estimate', 'County boundaries'),
                 url = c('https://api.census.gov/data/2024/acs/acs5?get=NAME,B19013_001E,B19013_001M&for=county:*&in=state:48',
                         'https://api.census.gov/data/2024/acs/acs5?get=NAME,B19013_001E,B19013_001M&for=state:48', boundary_url),
                 downloaded_on = as.character(Sys.Date())), 'data/source/sources.csv')
