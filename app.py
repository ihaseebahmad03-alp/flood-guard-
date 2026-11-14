import datetime as dt
import requests
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.stats import linregress

st.set_page_config(
    page_title="FloodGuard AI | NASA Rainfall Monitor",
    page_icon="🌧️",
    layout="wide",
)

# --------------------------- Design ---------------------------
st.markdown("""
<style>
    .stApp {background: linear-gradient(180deg, #071629 0%, #0b1f36 48%, #071629 100%);}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    .hero {
        padding: 1.5rem 1.7rem; border: 1px solid #214d70; border-radius: 18px;
        background: linear-gradient(115deg, #102f4b, #123e5c 60%, #0b2944);
        margin-bottom: 1rem;
    }
    .hero h1 {color:#f4f9ff; margin:0; font-size:2.45rem;}
    .hero p {color:#c5d9e9; margin:.45rem 0 0 0; font-size:1.05rem;}
    .small-note {color:#b9cad8; font-size:.88rem;}
    .risk {
        padding: 1rem 1.2rem; border-radius: 13px; border: 1px solid #315879;
        background:#102b43;
    }
    div[data-testid="stMetric"] {
        background:#102b43; border:1px solid #244967; padding:12px 14px;
        border-radius:13px;
    }
    h2, h3 {color:#e7f3ff;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🌧️ FloodGuard AI</h1>
  <p>NASA Rainfall Trend Monitor · Understand rainfall patterns before they become a bigger concern.</p>
</div>
""", unsafe_allow_html=True)

st.caption("A NASA-data-powered educational prototype for rainfall trend and anomaly monitoring. It does not predict floods or replace official warnings.")

# --------------------------- Location ---------------------------
LOCATIONS = {
    "Faisalabad, Pakistan": (31.4504, 73.1350),
    "Lahore, Pakistan": (31.5204, 74.3587),
    "Islamabad, Pakistan": (33.6844, 73.0479),
    "Karachi, Pakistan": (24.8607, 67.0011),
    "Multan, Pakistan": (30.1575, 71.5249),
    "Peshawar, Pakistan": (34.0151, 71.5249),
    "Quetta, Pakistan": (30.1798, 66.9750),
}

with st.sidebar:
    st.header("📍 Monitoring area")
    place = st.selectbox("Choose a location", list(LOCATIONS.keys()))
    default_lat, default_lon = LOCATIONS[place]
    custom = st.checkbox("Enter custom coordinates")
    if custom:
        latitude = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=float(default_lat), step=0.01, format="%.4f")
        longitude = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=float(default_lon), step=0.01, format="%.4f")
        location_label = "Custom location"
    else:
        latitude, longitude = default_lat, default_lon
        location_label = place
    years = st.selectbox("Historical comparison period", [5, 8, 10, 15], index=2)
    st.markdown("---")
    st.markdown("**Data source**")
    st.markdown("[NASA POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)")
    st.caption("Daily precipitation estimate (PRECTOTCORR), mm/day. Data availability can lag.")

# NASA POWER daily endpoint. Community AG provides corrected precipitation.
@st.cache_data(ttl=3600, show_spinner=False)
def get_nasa_rainfall(lat, lon, start_date, end_date):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "PRECTOTCORR",
        "community": "AG",
        "longitude": float(lon),
        "latitude": float(lat),
        "start": start_date,
        "end": end_date,
        "format": "JSON",
        "time-standard": "UTC",
    }
    response = requests.get(url, params=params, timeout=90)
    response.raise_for_status()
    payload = response.json()
    values = payload["properties"]["parameter"]["PRECTOTCORR"]
    frame = pd.DataFrame(
        [(pd.to_datetime(k, format="%Y%m%d"), float(v)) for k, v in values.items()],
        columns=["date", "rain_mm"]
    )
    frame = frame.sort_values("date").reset_index(drop=True)
    frame.loc[frame["rain_mm"] < 0, "rain_mm"] = np.nan
    return frame.dropna(subset=["rain_mm"])

today = dt.date.today()
end = today - dt.timedelta(days=3)  # allow time for satellite/reanalysis products to be published
start = dt.date(end.year - years, 1, 1)

st.subheader(f"Rainfall overview — {location_label}")
with st.spinner("Connecting to NASA POWER and loading historical rainfall data..."):
    try:
        df = get_nasa_rainfall(latitude, longitude, start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
    except Exception as exc:
        st.error("NASA POWER data could not be loaded right now.")
        st.write("Check your internet connection and try again. The NASA service may also be temporarily unavailable.")
        st.caption(f"Technical detail: {type(exc).__name__}: {exc}")
        st.stop()

if df.empty or len(df) < 30:
    st.warning("Not enough valid rainfall observations were returned for this location and period.")
    st.stop()

df["rolling_7d"] = df["rain_mm"].rolling(7, min_periods=7).sum()
last_date = df["date"].max()
recent = df.tail(7)
recent_7d = float(recent["rain_mm"].sum()) if len(recent) == 7 else np.nan

# Compare the latest 7-day total with historical rolling 7-day totals from the same calendar month.
history = df[(df["date"] < last_date - pd.Timedelta(days=7)) & (df["date"].dt.month == last_date.month)]
history_7d = history["rolling_7d"].dropna()
if len(history_7d) >= 20 and np.isfinite(recent_7d):
    p90 = float(history_7d.quantile(0.90))
    p50 = float(history_7d.quantile(0.50))
    if recent_7d >= p90:
        status = "Unusually wet"
        status_color = "#f59e0b"
        interpretation = "The latest 7-day rainfall total is at or above the historical 90th percentile for this calendar month."
    elif recent_7d >= p50:
        status = "Above typical"
        status_color = "#38bdf8"
        interpretation = "The latest 7-day rainfall total is above the historical median for this calendar month."
    else:
        status = "Within / below typical"
        status_color = "#34d399"
        interpretation = "The latest 7-day rainfall total is below the historical median for this calendar month."
else:
    p90, p50 = np.nan, np.nan
    status = "Insufficient comparison data"
    status_color = "#94a3b8"
    interpretation = "More historical observations are needed to calculate a reliable same-month comparison."

annual = df.assign(year=df["date"].dt.year).groupby("year", as_index=False)["rain_mm"].sum()
annual = annual[annual["year"] < last_date.year]  # exclude incomplete current year from long-term trend
if len(annual) >= 4:
    fit = linregress(annual["year"].astype(float), annual["rain_mm"].astype(float))
    slope = float(fit.slope)
    p_value = float(fit.pvalue)
    if p_value < 0.05:
        trend_text = "Increasing" if slope > 0 else "Decreasing"
        confidence_text = "Statistically significant at the 5% level"
    else:
        trend_text = "No clear linear trend"
        confidence_text = "Trend is not statistically significant at the 5% level"
else:
    slope, p_value = np.nan, np.nan
    trend_text, confidence_text = "Not enough annual data", "At least four complete years are needed"

# --------------------------- KPIs ---------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Latest 7-day rainfall", f"{recent_7d:.1f} mm" if np.isfinite(recent_7d) else "N/A")
m2.metric("Historical same-month 90th percentile", f"{p90:.1f} mm" if np.isfinite(p90) else "N/A")
m3.metric("Long-term annual trend", trend_text)
m4.metric("Latest available observation", last_date.strftime("%d %b %Y"))

st.markdown(
    f'<div class="risk"><b style="color:{status_color};font-size:1.15rem;">● {status}</b>'
    f'<div style="color:#d3e2ee;margin-top:.35rem;">{interpretation}</div></div>',
    unsafe_allow_html=True
)

# --------------------------- Charts ---------------------------
left, right = st.columns(2)
with left:
    st.subheader("Daily rainfall")
    daily_plot = df.tail(365)
    fig = px.area(daily_plot, x="date", y="rain_mm", title="Daily precipitation (last 12 months)",
                  labels={"date": "Date", "rain_mm": "Rainfall (mm/day)"})
    fig.update_traces(line_color="#38bdf8", fillcolor="rgba(56,189,248,0.22)")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=45,b=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Monthly rainfall pattern")
    monthly = df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False)["rain_mm"].sum()
    fig2 = px.bar(monthly.tail(36), x="month", y="rain_mm", title="Monthly accumulated precipitation",
                  labels={"month": "Month", "rain_mm": "Rainfall (mm/month)"})
    fig2.update_traces(marker_color="#2dd4bf")
    fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=45,b=10))
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Long-term rainfall trend")
if len(annual):
    trend_fig = px.scatter(annual, x="year", y="rain_mm", trendline="ols",
                           labels={"year":"Year","rain_mm":"Annual rainfall (mm)"},
                           title="Annual rainfall totals (complete calendar years)")
    trend_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=45,b=10))
    st.plotly_chart(trend_fig, use_container_width=True)
    st.write(f"Estimated change: **{slope:+.2f} mm/year** · p-value: **{p_value:.4f}** · {confidence_text}.")
else:
    st.info("Annual trend will appear when enough complete calendar years are available.")

# --------------------------- Map and interpretation ---------------------------
st.subheader("Monitoring point")
st.map(pd.DataFrame({"lat":[latitude], "lon":[longitude]}), zoom=6)
st.caption(f"Selected point: {latitude:.4f}° latitude, {longitude:.4f}° longitude.")

with st.expander("How should I interpret these results?"):
    st.markdown("""
    - **Unusually wet:** the recent 7-day total is in the highest 10% of historical 7-day totals observed in the same calendar month.
    - **Above typical:** the recent total is above the historical median for that month.
    - **Long-term trend:** a straight-line trend is fitted to complete annual rainfall totals. A p-value below 0.05 is treated as statistically significant in this prototype.
    - These are statistical indicators, not flood forecasts. Flooding also depends on river levels, drainage, soil saturation, terrain, land use, reservoirs and local observations.
    """)

with st.expander("Data, method and limitations"):
    st.markdown("""
    **Data:** NASA POWER Daily API, parameter `PRECTOTCORR`, community `AG`. Precipitation is reported in mm/day. NASA POWER provides analysis-ready meteorological data; it is not a substitute for a local rain gauge.

    **Method:** retrieve daily precipitation for the selected coordinate; calculate rolling 7-day totals; compare the latest complete 7-day total with historical rolling totals from the same calendar month; aggregate complete years and fit a linear regression to annual totals.

    **Limitations:** data may be delayed; gridded estimates may differ from ground measurements; a point does not represent an entire city or watershed; this prototype does not model river discharge, drainage capacity, inundation extent or flood probability.
    """)

csv = df[["date", "rain_mm"]].to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download rainfall data (CSV)", data=csv,
                   file_name="floodguard_nasa_rainfall.csv", mime="text/csv")

st.markdown("---")
st.markdown("**FloodGuard AI** · Built for NASA Space Apps Challenge 2026")
st.caption("Independent student prototype. Not affiliated with or endorsed by NASA. In an emergency, follow local authorities and official disaster-management alerts.")
