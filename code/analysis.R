# Open blog5.Rproj, then run this whole script from the project folder.
library(tidyverse)
library(sf)
library(tmap)
library(leaflet)
library(htmlwidgets)

dir.create('data/processed', recursive = TRUE, showWarnings = FALSE)
dir.create('results/tables', recursive = TRUE, showWarnings = FALSE)
dir.create('results/figures', recursive = TRUE, showWarnings = FALSE)

# Read saved API data. Downloading is a separate, optional step.
income <- read_csv('data/source/texas-county-income-2024.csv',
                   col_types = cols(GEOID = col_character()))
state <- read_csv('data/source/texas-state-income-2024.csv',
                  col_types = cols(GEOID = col_character()))
state_income <- state$estimate[1]
state_moe <- state$moe[1]

# Read the shapefile and select Texas. sf reads the same polygon data
# used in the course; st_transform puts it in the required coordinates.
shape_folder <- tempfile('county-shapes-')
unzip('data/source/cb_2024_us_county_500k.zip', exdir = shape_folder)
counties <- st_read(file.path(shape_folder, 'cb_2024_us_county_500k.shp'), quiet = TRUE)
texas <- counties |> filter(STATEFP == '48') |> select(GEOID, NAME)
stopifnot(nrow(texas) == 254, nrow(income) == 254,
          !any(duplicated(texas$GEOID)), !any(duplicated(income$GEOID)),
          all(texas$GEOID %in% income$GEOID), all(income$GEOID %in% texas$GEOID))
income <- income |> transmute(GEOID, income = if_else(estimate < 0, NA_real_, estimate),
                              moe = if_else(moe < 0, NA_real_, moe))
texas <- merge(texas, income, by = 'GEOID')
texas <- st_transform(texas, 5070)
stopifnot(all(st_is_valid(texas)), !any(st_is_empty(texas)),
          !anyNA(texas$income), !anyNA(texas$moe))
texas <- texas |> mutate(lower90 = income - moe, upper90 = income + moe,
                        difference_from_state = income - state_income,
                        moe_percent = 100 * moe / income)
county_table <- st_drop_geometry(texas)
write_csv(arrange(county_table, GEOID), 'data/processed/texas-income-2024.csv')
# GeoJSON uses longitude and latitude so it can be used in web maps.
st_write(st_transform(texas, 4326), 'data/processed/texas-income-2024.geojson',
         delete_dsn = TRUE, quiet = TRUE)
write_csv(arrange(county_table, desc(income)), 'results/tables/county-estimates.csv')
summary <- tibble(counties = nrow(texas), valid_estimates = sum(!is.na(texas$income)),
                  missing_moe = sum(is.na(texas$moe)), state_income, state_moe,
                  above_state = sum(texas$income > state_income),
                  below_state = sum(texas$income < state_income),
                  at_least_100000 = sum(texas$income >= 100000))
write_csv(summary, 'results/tables/summary.csv')
selected <- county_table |>
  filter(NAME %in% c('Collin', 'Denton', 'Dallas', 'Fort Bend', 'Harris',
                    'Williamson', 'Travis', 'Hidalgo', 'Cameron', 'Starr')) |>
  arrange(income)
write_csv(selected, 'results/tables/selected-counties.csv')

# DataCamp structure: tm_shape + fill + borders + text + credits.
# tmap 4 uses fill.scale and fill.legend for the palette and legend.
tmap_mode('plot')
labels <- texas |> filter(NAME %in% c('Collin', 'Travis', 'Fort Bend', 'Starr', 'Hidalgo'))
income_map <- tm_shape(texas) +
  tm_fill(fill = 'income', fill.scale = tm_scale_continuous(values = 'brewer.yl_gn_bu'),
          fill.legend = tm_legend(title = 'Median household income\n(2024 dollars)')) +
  tm_borders(col = 'white', lwd = 0.5) +
  tm_shape(labels) + tm_text('NAME', size = 0.65, bgcol = 'white', bgcol_alpha = 0.8) +
  tm_title('Household income varies across Texas counties') +
  tm_credits('Source: 2020-2024 ACS, B19013; 2024 Census county boundaries.\n254 counties. County area is not population size. EPSG:5070.',
             position = c('left', 'bottom'), size = 0.55)
tmap_save(income_map, 'results/figures/texas-income-map.png', width = 10, height = 9, units = 'in', dpi = 200)

# Leaflet uses longitude/latitude. The colors have the same continuous scale.
texas_web <- st_transform(texas, 4326)
pal <- colorNumeric('YlGnBu', domain = texas_web$income)
texas_web$popup <- paste0('<b>', texas_web$NAME, ' County</b><br>Median household income: ',
                          scales::dollar(texas_web$income, accuracy = 1),
                          '<br>90% margin of error: ±', scales::dollar(texas_web$moe, accuracy = 1),
                          '<br>2020-2024 ACS; 2024 dollars')
income_leaflet <- leaflet(texas_web) |>
  addPolygons(fillColor = ~pal(income), fillOpacity = 1, color = 'white', weight = 1,
              popup = ~popup, label = ~paste0(NAME, ': ', scales::dollar(income, accuracy = 1)),
              highlightOptions = highlightOptions(weight = 3, color = '#333333', bringToFront = TRUE)) |>
  addLegend(pal = pal, values = ~income, title = 'Median household income<br>(2024 dollars)',
            position = 'bottomright', opacity = 1) |>
  addControl('Source: U.S. Census Bureau, 2020-2024 ACS, B19013.<br>County area is not population size.', position = 'bottomleft')
saveWidget(income_leaflet, 'results/figures/texas-income-interactive.html',
           selfcontained = FALSE, libdir = 'texas-income-interactive_files')

# Ten selected examples; error bars are estimate +/- the published margin of error.
comparison <- ggplot(selected, aes(x = income, y = reorder(NAME, income))) +
  annotate('rect', xmin = state_income - state_moe, xmax = state_income + state_moe,
           ymin = -Inf, ymax = Inf, fill = '#b65c2e', alpha = 0.12) +
  geom_vline(xintercept = state_income, linetype = 'dashed', color = '#b65c2e') +
  geom_errorbar(aes(xmin = lower90, xmax = upper90), orientation = 'y', width = 0.15, color = '#7598a6') +
  geom_point(color = '#286789', size = 3) +
  scale_x_continuous(labels = scales::label_dollar(scale = 0.001, suffix = 'k'), limits = c(0, 135000)) +
  labs(title = 'Nearby counties can have different income levels',
       subtitle = paste('Dashed line: Texas median', scales::dollar(state_income, accuracy = 1)),
       x = 'Median household income (2024 dollars)', y = NULL,
       caption = 'Ten selected counties, not all counties. Bars show 90% confidence intervals.\nSource: 2020-2024 ACS, B19013. Shading shows the state margin of error.') +
  theme_minimal(base_size = 13)
ggsave('results/figures/selected-county-incomes.png', comparison, width = 9, height = 6.4, dpi = 200)
print(summary)
if (interactive()) {
  print(income_map)
  print(comparison)
  print(income_leaflet)
}
