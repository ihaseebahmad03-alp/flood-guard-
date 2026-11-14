# NASA Space Apps Challenge 2026 — Submission Draft

## Project title
**FloodGuard AI: NASA Rainfall Trend Monitor**

## Challenge
**Be An Earth System Trend Detective!**

## One-line summary
FloodGuard AI turns NASA daily precipitation data into accessible local rainfall charts, historical comparisons and transparent trend indicators to help communities better understand changing rainfall patterns.

## Project description
Heavy rainfall can create serious challenges for communities, but raw environmental data is not always easy for the public to interpret. FloodGuard AI is a lightweight web application that makes rainfall information easier to explore.

Users select a Pakistani city or enter coordinates. The application retrieves daily precipitation estimates from NASA POWER and visualizes daily rainfall, monthly accumulation and annual totals. It calculates a rolling seven-day rainfall total and compares it with historical seven-day totals from the same calendar month. It also fits a simple linear regression to complete annual rainfall totals and reports the estimated trend and p-value.

The goal is to make environmental data more understandable and encourage data-informed awareness. The prototype does not predict floods or replace official warnings.

## What makes it useful?
- Makes NASA environmental data easier for non-specialists to explore.
- Connects recent rainfall with historical local patterns.
- Shows long-term changes instead of relying on a single day's weather.
- Uses transparent statistical methods and explains their limitations.
- Offers a downloadable CSV for further study.

## NASA data used
NASA POWER Daily API:
https://power.larc.nasa.gov/docs/services/api/temporal/daily/

Parameter: `PRECTOTCORR`  
Community: `AG` (Agroclimatology)  
Units: millimetres per day.

## How it was built
- Python
- Streamlit
- Pandas and NumPy
- Plotly
- SciPy
- NASA POWER API

## Analysis approach
1. Retrieve daily precipitation for a selected coordinate.
2. Calculate rolling seven-day precipitation totals.
3. Compare the latest complete seven-day total with historical totals from the same calendar month.
4. Use the historical median and 90th percentile to describe whether recent rainfall is typical or unusually wet.
5. Aggregate complete annual totals and fit a linear regression to inspect the long-term direction and statistical significance.

## Limitations and responsible use
NASA POWER precipitation is a gridded estimate and may differ from local rain-gauge readings. Data can be delayed. A single coordinate cannot represent an entire city or watershed. Rainfall trends alone cannot determine whether flooding will occur. The application does not calculate flood probability, river levels, inundation extent or emergency warnings. People should follow official local authorities and disaster-management agencies.

## Future improvements
- Integrate NASA GPM IMERG satellite precipitation products.
- Add river and watershed observations.
- Validate estimates with local rain-gauge measurements.
- Add Urdu-language explanations.
- Deploy a public live demo.

## Demo
Add the public Streamlit deployment URL here after deployment.

## Team
Add the actual team member name(s) and roles. Do not list people who did not contribute.
