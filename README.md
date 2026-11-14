# FloodGuard AI — NASA Rainfall Trend Monitor

**NASA Space Apps Challenge 2026**  
**Challenge alignment:** “Be An Earth System Trend Detective!”

FloodGuard AI is a beginner-friendly web prototype that explores rainfall patterns using NASA POWER daily precipitation data. It helps users inspect recent rainfall, compare a recent seven-day total with historical same-month patterns, and explore long-term annual rainfall trends.

> Important: FloodGuard AI is a rainfall trend-monitoring and educational prototype. It does **not** predict floods, issue emergency alerts, or replace official warnings.

## Features

- Select a Pakistani city or enter custom coordinates.
- Retrieve daily precipitation estimates from NASA POWER.
- View daily and monthly rainfall charts.
- Calculate the latest complete seven-day rainfall total.
- Compare it with historical same-calendar-month rolling totals (median and 90th percentile).
- Explore annual rainfall totals and a linear trend with a p-value.
- View the selected monitoring point on a map.
- Download the retrieved rainfall data as CSV.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Start the app:

```bash
streamlit run app.py
```

The app opens in your browser. An internet connection is required to retrieve NASA POWER data.

## NASA data source

- NASA POWER Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
- Parameter: `PRECTOTCORR`
- Community: `AG` (Agroclimatology)
- Output: daily precipitation estimate in mm/day
- The app requests UTC daily values and leaves a short end-date buffer because the latest data may not yet be available.

## Method

1. Retrieve daily precipitation at the selected latitude and longitude.
2. Calculate rolling seven-day precipitation sums.
3. Compare the latest complete seven-day sum with historical seven-day sums from the same calendar month.
4. Label the observation as unusually wet (at or above the 90th percentile), above typical (above the median), or within/below typical.
5. Aggregate complete calendar years and fit a linear regression to annual rainfall totals. The p-value is displayed as a simple statistical indicator.

These calculations describe precipitation patterns only. Flood risk depends on many additional variables, including river discharge, drainage, soil moisture, terrain, land use and local conditions.

## Suggested next steps

- Add NASA GPM IMERG precipitation data for a more directly satellite-focused rainfall layer.
- Add watershed/river information and official local authority links.
- Validate satellite estimates against ground rain gauges.
- Add multilingual explanations and accessibility improvements.
- Deploy the app publicly and add the live demo URL to the project submission.

## Project team

Solo student project prototype. Add your name and any collaborators accurately in the official submission.

## License

MIT — see `LICENSE`.
