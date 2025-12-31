
import streamlit as st
import pandas as pd
import plotly.express as px
import simulation
import importlib
importlib.reload(simulation)
import models
importlib.reload(models)
import data_loader
importlib.reload(data_loader)

st.set_page_config(page_title="Housing vs Stocks Model", layout="wide")

st.title("🏡 Housing vs 📈 Stock Market: Wealth Accumulation Model")
st.markdown("Compare the historical performance of buying a home in Canada vs investing the equivalent capital in the S&P 500.")

st.sidebar.header("Simulation Parameters")

start_year = st.sidebar.slider("Start Year", 1975, 2020, 1990)
amortization = st.sidebar.selectbox("Mortgage Amortization (Years)", [15, 20, 25, 30], index=2)
down_payment_pct = st.sidebar.slider("Down Payment (%)", 5, 50, 20)

use_historical_rent = st.sidebar.checkbox("Use Historical Average Rent", value=True)
initial_rent_override = None
if not use_historical_rent:
    initial_rent_override = st.sidebar.number_input("Starting Monthly Rent ($)", value=800)

st.sidebar.markdown("---")
city = st.sidebar.selectbox("City", ["National", "Toronto", "Vancouver", "Calgary", "Montreal"], index=0)
marginal_tax = st.sidebar.slider("Marginal Tax Rate (%)", 0, 54, 40)

if st.sidebar.button("Run Simulation", type="primary"):
    # Run Simulation
    results = simulation.run_simulation(
        start_year=start_year, 
        mortgage_years=amortization, 
        down_payment_pct=down_payment_pct,
        initial_rent=initial_rent_override,
        city=city,
        marginal_tax_rate=marginal_tax/100.0
    )
    
    history_df = pd.DataFrame(results['history'])
    
    st.subheader(f"Results for {city} ({start_year}-2024)")
    
    # Starting Conditions
    st.markdown("### 🏁 Starting Conditions")
    col_start1, col_start2, col_start3 = st.columns(3)
    
    with col_start1:
        st.metric("Home Purchase Price", f"${results['start_house_price']:,.0f}")
    with col_start2:
        # Calculate mortgage amount for display
        mortgage_amt = results['start_house_price'] - results['initial_down_payment']
        st.metric("Mortgage Amount", f"${mortgage_amt:,.0f}")
    with col_start3:
        st.metric("Initial Capital (Stocks)", f"${results['total_initial_capital']:,.0f}", 
                 help=f"Includes Down Payment (${results['initial_down_payment']:,.0f}) + Closing Costs (${results['closing_costs_paid']:,.0f}) saved.")

    st.divider()

    # Final Results
    st.markdown("### 🏁 Final Outcome (After 25+ Years)")
    
    # --- VERDICT BANNER ---
    final_equity_net = results['final_house_net']
    final_stock_net = results['final_stock_net']
    diff = final_equity_net - final_stock_net
    winner = "Buying a Home" if diff > 0 else "Investing in Stocks"
    win_amount = abs(diff)
    
    st.markdown("### 🏆 The Verdict")
    if diff > 0:
        st.success(f"**{winner}** was the better financial decision by **${win_amount:,.0f}**!")
    else:
        st.info(f"**{winner}** was the better financial decision by **${win_amount:,.0f}**!")

    # --- MAIN CHART (Nominal Wealth) ---
    st.markdown("### 📈 Net Wealth Over Time")
    chart_df = history_df[['Date', 'House Equity', 'Stock Balance']].melt('Date', var_name='Asset', value_name='Value')
    fig = px.line(chart_df, x='Date', y='Value', color='Asset', markers=False) # Markers false for density
    
    # Improve Chart Styling
    fig.update_layout(xaxis_title="Year", yaxis_title="Net Worth ($)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # --- UNRECOVERABLE COSTS ("THE BURN CHART") ---
    st.markdown("### 🔥 Unrecoverable Costs (Where did the money go?)")
    st.caption("People say 'Rent is throwing money away', but Owning has its own 'Burn Rate'.")
    
    burn_data = {
        "Category": ["Rent", "Mortgage Interest", "Maintenance", "Buying Costs (LTT)", "Selling Costs (Agent)"],
        "Amount": [
            results['total_rent_paid'],
            results['total_mortgage_interest'],
            results['total_maintenance'],
            results['closing_costs_paid'],
            results['selling_costs_estimated']
        ],
        "Scenario": ["Renter", "Homeowner", "Homeowner", "Homeowner", "Homeowner"]
    }
    burn_df = pd.DataFrame(burn_data)
    
    fig_burn = px.bar(burn_df, x="Scenario", y="Amount", color="Category", 
                      title="Total Unrecoverable Costs (1990-2024)",
                      text_auto='.2s', height=400)
    fig_burn.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_burn, use_container_width=True)
    
    # Check if Buying actually "Burned" more than Renting
    total_home_burn = results['total_mortgage_interest'] + results['total_maintenance'] + results['closing_costs_paid'] + results['selling_costs_estimated']
    if total_home_burn > results['total_rent_paid']:
        st.warning(f"⚠️ **Myth Buster**: The Homeowner 'threw away' **${total_home_burn:,.0f}** on interest, maintenance, and fees, while the Renter only paid **${results['total_rent_paid']:,.0f}** in rent!")

    st.divider()

    # --- WEALTH COMPOSITION ---
    st.markdown("### 💰 Wealth Composition")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Housing Net Cash (After Fees)", f"${final_equity_net:,.0f}", 
                 delta=f"Growth: ${(final_equity_net - results['initial_down_payment']):,.0f}")
    with col2:
        st.metric("Stock Net Cash (After Tax)", f"${final_stock_net:,.0f}",
                 delta=f"Growth: ${(final_stock_net - results['total_initial_capital']):,.0f}")

    # Composition Chart
    # Stack: Initial Capital | Contributions (if any) | Growth
    
    # Stocks Breakdown
    stock_net = final_stock_net
    stock_initial = results['total_initial_capital']
    stock_added = results['total_stock_contributions']
    stock_growth = max(0, stock_net - (stock_initial + stock_added))
    
    # Housing Breakdown
    # Simplified: Initial Downpayment + Paid Principal (Forced Savings) + Growth (Appreciation)
    # Actually, simpler for comparison: Cash In vs Market Growth
    # Housing Cash In = Downpayment + Principal Payments? 
    # Let's keep Housing simple for now: Initial vs Growth, as 'Contributions' are mixed with maintenance costs in user mind.
    # Or: Initial | Principal Paid | Appreciation?
    # Let's stick to the user request: Stocks breakdown.
    
    comp_data = {
        "Asset": ["Housing", "Housing", "Housing", "Stocks", "Stocks", "Stocks"],
        "Type": ["Initial Capital", "Contributions", "Net Growth", 
                 "Initial Capital", "Contributions", "Net Growth"],
        "Amount": [
            results['initial_down_payment'], 
            0, # Housing 'Contributions' (Principal paydown) masked for now to keep simple
            max(0, final_equity_net - results['initial_down_payment']),
            stock_initial,
            stock_added,
            stock_growth
        ]
    }
    comp_df = pd.DataFrame(comp_data)
    
    fig_comp = px.bar(comp_df, x="Asset", y="Amount", color="Type", 
                      title="Net Wealth Composition (Source of Funds)", text_auto='.2s',
                      color_discrete_map={
                          "Initial Capital": "#1f77b4", # Blue
                          "Contributions": "#aec7e8",   # Light Blue
                          "Net Growth": "#2ca02c"       # Green
                      })
    st.plotly_chart(fig_comp, use_container_width=True)

    st.divider()
    
    # Charts
    tab2, tab3 = st.tabs(["Inflation Adjusted (Real)", "Raw Data"])
    
    with tab2:
        st.subheader("Net Wealth Over Time (Real / Inflation Adjusted)")
        chart_df_real = history_df[['Date', 'Real House Equity', 'Real Stock Balance']].melt('Date', var_name='Asset', value_name='Value')
        fig_real = px.line(chart_df_real, x='Date', y='Value', color='Asset', markers=False)
        st.plotly_chart(fig_real, use_container_width=True)

    with tab3:
        st.subheader("Simulation Data")
        st.dataframe(history_df.style.format({
            "House Price": "${:,.0f}",
            "House Equity": "${:,.0f}",
            "Stock Balance": "${:,.0f}",
            "Real House Equity": "${:,.0f}",
            "Real Stock Balance": "${:,.0f}",
            "Rent Paid (Stock Scenario)": "${:,.0f}",
            "Mortgage Rate (%)": "{:.2f}%"
        }))

else:
    st.info("👈 Adjust parameters in the sidebar and click 'Run Simulation' to start.")

st.markdown("---")
st.markdown("*Data Sources: Historical Canadian Housing Prices (Approx), S&P 500 Total Returns, StatsCan CPI, CMHC Rental Data.*")
