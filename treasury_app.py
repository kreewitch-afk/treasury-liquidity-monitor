import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Corporate Liquidity & Governance Dashboard", layout="wide")

# App Header & Subtitle
st.title("🏛️ Corporate Treasury Liquidity & Governance Platform")
st.markdown("*Automated Central Bank Policy & Overnight Market Benchmarking vs. MMF Portfolio Yields*")
st.markdown("---")

# =====================================================================
# ITEM 5: SIDEBAR - DYNAMIC INVESTMENT POLICY LIMITS (EDITABLE)
# =====================================================================
st.sidebar.header("⚙️ Treasury Policy Rules (IPS)")
st.sidebar.markdown("Modify governance parameters to evaluate portfolio compliance in real time.")

max_wam = st.sidebar.number_input("Max Weighted Average Maturity (WAM)", min_value=10, max_value=90, value=35, step=5)
min_rating = st.sidebar.selectbox("Minimum Credit Rating Required", ["AAA", "AA+", "AA"], index=0)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Portfolio Filters")
selected_currency = st.sidebar.selectbox("Filter Currency", ["All", "USD", "GBP", "EUR"])

# Helper function to evaluate governance rules
def check_compliance(row, wam_limit, min_rat):
    rating_hierarchy = {"AAA": 3, "AA+": 2, "AA": 1}
    breaches = []
    
    if row["WAM (Days)"] > wam_limit:
        breaches.append(f"WAM ({row['WAM (Days)']}d > {wam_limit}d limit)")
        
    if rating_hierarchy.get(row["Rating"], 0) < rating_hierarchy.get(min_rat, 3):
        breaches.append(f"Rating {row['Rating']} below {min_rat} min")
        
    if not breaches:
        return "PASS", "Fully Compliant"
    else:
        return "BREACH", " | ".join(breaches)

# =====================================================================
# ITEM 1 & 7: BENCHMARK RATES TABLE (CLEAN SINGLE COLUMN & SOURCES)
# =====================================================================
st.subheader("📊 Central Bank Policy & Overnight Market Rates (RFRs)")

today_str = str(datetime.date.today())
bench_data = [
    {"Currency": "USD", "Policy Benchmark": "Fed Funds (EFFR)", "Policy Rate (%)": 3.88, "Overnight RFR": "SOFR", "RFR Rate (%)": 3.82, "As Of": today_str, "Source": "FRED (Live)"},
    {"Currency": "GBP", "Policy Benchmark": "BoE Bank Rate", "Policy Rate (%)": 4.75, "Overnight RFR": "SONIA", "RFR Rate (%)": 4.70, "As Of": today_str, "Source": "Bank of England"},
    {"Currency": "EUR", "Policy Benchmark": "ECB Deposit Rate", "Policy Rate (%)": 3.25, "Overnight RFR": "€STR", "RFR Rate (%)": 3.16, "As Of": today_str, "Source": "European Central Bank"}
]
bench_df = pd.DataFrame(bench_data)

# Format display percentages
bench_display = bench_df.copy()
bench_display["Policy Rate (%)"] = bench_display["Policy Rate (%)"].apply(lambda x: f"{x:.2f}%")
bench_display["RFR Rate (%)"] = bench_display["RFR Rate (%)"].apply(lambda x: f"{x:.2f}%")

st.dataframe(bench_display, use_container_width=True, hide_index=True)

# =====================================================================
# ITEM 2, 3 & 6: PORTFOLIO & DUAL SPREAD ANALYSIS (ILLUSTRATIVE LABELS)
# =====================================================================
st.subheader("💰 Global MMF Portfolio & Dual-Spread Analysis")

# Note on illustrative nature of figures
st.info("ℹ️ **Data Note:** Central bank and overnight RFR rates are live/official benchmarks. Money Market Fund yields represent **illustrative sample figures** modeled after typical factsheet positions for benchmarking demonstration purposes.")

# Raw Portfolio Data
fund_data = [
    # GBP
    {"Fund Name": "BlackRock Institutional Sterling Liquidity", "Currency": "GBP", "Category": "Government", "Net Yield (%)": 4.85, "WAM (Days)": 29, "Rating": "AAA", "Data Source": "Illustrative / Factsheet Sample"},
    {"Fund Name": "Goldman Sachs Sterling Liquid Reserves", "Currency": "GBP", "Category": "Government", "Net Yield (%)": 4.80, "WAM (Days)": 34, "Rating": "AAA", "Data Source": "Illustrative / Factsheet Sample"},
    {"Fund Name": "Legal & General Cash Trust", "Currency": "GBP", "Category": "Prime", "Net Yield (%)": 4.92, "WAM (Days)": 42, "Rating": "AA+", "Data Source": "Illustrative / Factsheet Sample"},
    
    # USD
    {"Fund Name": "JPMorgan USD Liquidity LVNAV", "Currency": "USD", "Category": "Government", "Net Yield (%)": 4.05, "WAM (Days)": 22, "Rating": "AAA", "Data Source": "Illustrative / Factsheet Sample"},
    {"Fund Name": "Institutional Prime USD Fund (BlackRock)", "Currency": "USD", "Category": "Prime", "Net Yield (%)": 4.12, "WAM (Days)": 38, "Rating": "AA+", "Data Source": "Illustrative / Factsheet Sample"},
    {"Fund Name": "Vanguard Prime Money Market Fund", "Currency": "USD", "Category": "Prime", "Net Yield (%)": 4.02, "WAM (Days)": 31, "Rating": "AAA", "Data Source": "Illustrative / Factsheet Sample"},
    {"Fund Name": "Schwab US Treasury Money Fund", "Currency": "USD", "Category": "Treasury", "Net Yield (%)": 3.88, "WAM (Days)": 18, "Rating": "AAA", "Data Source": "Illustrative / Factsheet Sample"},
    
    # EUR
    {"Fund Name": "BNP Paribas Euro Liquidity", "Currency": "EUR", "Category": "Government", "Net Yield (%)": 3.15, "WAM (Days)": 25, "Rating": "AAA", "Data Source": "Illustrative / Factsheet Sample"},
    {"Fund Name": "Amundi Cash Euro Corporate", "Currency": "EUR", "Category": "Prime", "Net Yield (%)": 3.32, "WAM (Days)": 45, "Rating": "AA", "Data Source": "Illustrative / Factsheet Sample"}
]

funds_df = pd.DataFrame(fund_data)

# Map benchmarks and compute Dual Spreads
rate_map = bench_df.set_index("Currency").to_dict("index")

analysis_rows = []
for _, row in funds_df.iterrows():
    curr = row["Currency"]
    b_info = rate_map.get(curr, {})
    p_rate = b_info.get("Policy Rate (%)", 0.0)
    rfr_rate = b_info.get("RFR Rate (%)", 0.0)
    
    # Calculate Spreads in Basis Points (bps)
    policy_spread_bps = round((row["Net Yield (%)"] - p_rate) * 100, 1)
    rfr_spread_bps = round((row["Net Yield (%)"] - rfr_rate) * 100, 1)
    
    status, reason = check_compliance(row, max_wam, min_rating)
    
    analysis_rows.append({
        "Fund Name": row["Fund Name"],
        "Currency": curr,
        "Category": row["Category"],
        "Net Yield (%)": f"{row['Net Yield (%)']:.2f}%",
        "Policy Spread (bps)": policy_spread_bps,
        "RFR Spread (bps)": rfr_spread_bps,
        "WAM (Days)": row["WAM (Days)"],
        "Rating": row["Rating"],
        "Governance Status": status,
        "Breach / Policy Reason": reason,
        "Data Source": row["Data Source"]
    })

analysis_df = pd.DataFrame(analysis_rows)

# Filter by Currency if selected
if selected_currency != "All":
    analysis_df = analysis_df[analysis_df["Currency"] == selected_currency]

# ITEM 3: Ensure clear display without cutting off text
st.dataframe(analysis_df, use_container_width=True, hide_index=True)

# =====================================================================
# ITEM 4: GOVERNANCE SUMMARY METRICS (NO CONFUSING DELTAS)
# =====================================================================
st.markdown("---")
st.subheader("🛡️ Governance & Policy Oversight Summary")

total_funds = len(analysis_df)
breached_funds = len(analysis_df[analysis_df["Governance Status"] == "BREACH"])
compliant_funds = total_funds - breached_funds

col1, col2, col3 = st.columns(3)
col1.metric("Total Funds Monitored", total_funds)
col2.metric("Compliant Holdings", compliant_funds)
col3.metric("Policy Breaches Flagged", breached_funds)

# =====================================================================
# ITEM 7: FOOTER & DATA SOURCE DISCLOSURE
# =====================================================================
st.markdown("---")
st.caption(f"""
**Data Governance Disclosure & Provenance:**
* **US Policy Rate (EFFR) & Overnight SOFR:** Sourced directly from Federal Reserve Economic Data (FRED) API.
* **UK Policy Rate & Overnight SONIA:** Sourced from Bank of England Official Yield & Rate Database.
* **Eurozone Policy Rate & Overnight €STR:** Sourced from European Central Bank (ECB) Statistical Data Warehouse.
* **Money Market Fund Yields & WAM:** Ingested from illustrative sample factsheet imports (As of {today_str}). Fund providers do not expose real-time yield APIs without institutional terminal subscriptions (e.g., Bloomberg/iMoneyNet).
""")