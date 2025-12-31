import data_loader
from models import HousingInvestment, StockInvestment

def run_simulation(start_year, mortgage_years, down_payment_pct, initial_rent=None, city="National", marginal_tax_rate=0.40, move_freq_years="Never"):
    """
    Runs the simulation and returns a dictionary with results and history.
    """
    # 1. Setup Data - Regional
    house_price = data_loader.get_housing_price(start_year, city=city)
    
    # Calculate Purchase Closing Costs (LTT + Legal)
    # These are EXTRA costs. 
    # Option A: User pays them out of pocket (Initial Capital increases, Downpayment stays same)
    # Option B: User reduces Downpayment to pay them.
    # Assumption for fair comparison: 
    # - "Initial Capital" is fixed.
    # - Scenario A (House): Capital pays LTT + Downpayment.
    # - Scenario B (Stock): Capital is fully invested.
    
    # We define "Capital Available" based on the proposed House Downpayment.
    raw_down_payment = house_price * (down_payment_pct / 100.0)
    
    # Temporary placeholder to calc costs
    temp_house = HousingInvestment(start_year, house_price, raw_down_payment) 
    closing_costs = temp_house.get_closing_costs(city)
    
    # Total Initial Capital Required for Housing Path
    total_initial_capital = raw_down_payment + closing_costs
    
    # Housing Model Setup
    initial_mortgage_rate = data_loader.get_mortgage_rate(start_year) / 100.0
    
    housing_model = HousingInvestment(
        start_year=start_year,
        house_price=house_price,
        down_payment=raw_down_payment,
        interest_rate=initial_mortgage_rate, 
        amortization_years=mortgage_years
    )

    # Stock Model Setup
    # Invests the FULL capital (Downpayment + The money that would have gone to LTT)
    stock_model = StockInvestment(
        start_year=start_year,
        initial_deposit=total_initial_capital 
    )
    
    # 2. Simulation Loop
    end_year = 2024
    cumulative_inflation_index = 1.0
    
    current_rent_override = initial_rent
    
    history_data = []
    
    # TFSA Management
    # We accumulate TFSA room annually.
    # We track 'unused_tfsa_room'
    unused_tfsa_room = 0
    unused_rrsp_room = 0
    pending_tax_refund = 0
    
    total_stock_contributions = 0

    for y in range(start_year, end_year + 1):
        # Year Data
        annual_stock_return = data_loader.get_stock_return(y) / 100.0
        annual_inflation = data_loader.get_inflation_rate(y) / 100.0
        
        # House Appreciation
        current_price = data_loader.get_housing_price(y, city=city)
        next_price = data_loader.get_housing_price(y+1, city=city)
        if next_price:
             price_growth = (next_price - current_price) / current_price
        else:
            price_growth = 0.03 
        
        cumulative_inflation_index *= (1 + annual_inflation)
        
        # Add TFSA Room for this year
        # (Assuming user was 18+ and resident; simplified for 'Scenario' user)
        # Note: data_loader.get_tfsa_limit(y) returns 0 if before 2009
        annual_tfsa_limit = data_loader.get_tfsa_limit(y)
        unused_tfsa_room += annual_tfsa_limit
        unused_rrsp_room += data_loader.get_rrsp_limit(y)
        
        # Reset Annual Contribution Tracker for Refund Calc
        stock_model.annual_rrsp_contributions = 0
        
        # Determine Rent
        if initial_rent is not None:
             year_rent = current_rent_override
             current_rent_override *= (1 + annual_inflation)
        else:
             year_rent = data_loader.get_average_rent(y, city=city)

        # Monthly Loop
        for m in range(12):
            # Dynamic Monthly Price
            current_month_price = data_loader.get_monthly_housing_price(y, m+1, city)
            
            # Update Housing Model with new Market Value
            # We don't use 'annual appreciation rate' anymore for value updates, 
            # we force the value to the lookup table.
            housing_model.current_value = current_month_price
            
            # Recalculate Equity
            housing_model.equity = housing_model.current_value - housing_model.remaining_principal
            
            # Check for Mortgage Renewal (Every 5 years)
            months_elapsed = (y - start_year) * 12 + m
            if months_elapsed > 0 and months_elapsed % (5 * 12) == 0:
                new_rate_pct = data_loader.get_mortgage_rate(y)
                new_rate = new_rate_pct / 100.0
                # Remaining amortization
                remaining_years = max(0, mortgage_years - (months_elapsed / 12))
                if remaining_years > 0:
                    housing_model.update_interest_rate(new_rate, remaining_years)

            # Process Monthly Payment & Expenses
            # (Inflation passed for maintenance scaling)
            h_stat = housing_model.simulate_month(y, annual_appreciation_rate=0, annual_inflation_rate=annual_inflation)
            
            # --- Moving Scenario Logic (Friction Costs) ---
            transaction_cost_this_month = 0
            if move_freq_years != "Never":
                # Check if we move this month
                # Logic: Move exactly every X years from start
                if months_elapsed > 0 and months_elapsed % (move_freq_years * 12) == 0:
                    # SELL OLD HOUSE
                    # Costs: Agent Fees (~5%) + Legal
                    # Use existing helper (calculates commission)
                    net_proceeds = housing_model.get_net_proceeds()
                    selling_friction = housing_model.equity - net_proceeds
                    
                    # BUY NEW HOUSE (Lateral Move)
                    # Assume buying same price house (Lateral Upgrade)
                    # Costs: Land Transfer Tax (LTT) + Legal
                    buying_friction = housing_model.get_closing_costs(city)
                    
                    total_friction = selling_friction + buying_friction
                    transaction_cost_this_month = total_friction
                    
                    # Deduct from Equity (Wealth Destruction)
                    housing_model.equity -= total_friction
                    
                    # Re-Amortize? 
                    # Usually people port mortgages or start new 25y. 
                    # To isolate "Friction Cost", let's assume we keep the mortgage schedule 
                    # (Ported) but paid the fees out of equity/cash.
                    # Effectively: Equity drops, Debt stays same.
                    # Warning: If Equity < 0, they are bankrupt.
                    if housing_model.equity < 0:
                        housing_model.equity = 0 # bankrupt logic simplified
                        
            # Cash Flow
            housing_monthly_cost = h_stat['payment'] + h_stat['maintenance']
            monthly_stock_contribution = housing_monthly_cost - year_rent
            
            # Inject PROCESSED Tax Refund in March (Standard Canada timing)
            refund_this_month = 0
            if m == 2 and pending_tax_refund > 0:
                monthly_stock_contribution += pending_tax_refund
                refund_this_month = pending_tax_refund
                pending_tax_refund = 0 # Consumed
            
            total_stock_contributions += monthly_stock_contribution

            # Simulate Stocks
            # Pass available TFSA room. The model returns how much it used.
            s_stat = stock_model.simulate_month(y, annual_return_rate=annual_stock_return, 
                                                monthly_contribution=monthly_stock_contribution,
                                                tfsa_limit_room=unused_tfsa_room,
                                                rrsp_limit_room=unused_rrsp_room)
            
            # Deduct used room
            unused_tfsa_room -= s_stat.get('tfsa_used', 0)
            unused_rrsp_room -= s_stat.get('rrsp_used', 0)
            
            # Snapshot
            real_house_equity = housing_model.equity / cumulative_inflation_index
            real_stock_balance = stock_model.balance / cumulative_inflation_index
            
            current_mortgage_rate_display = housing_model.interest_rate * 100
            
            history_data.append({
                "Year": y,
                "Month": m + 1,
                "Date": f"{y}-{m+1:02d}",
                "House Price": housing_model.current_value,
                "House Equity": housing_model.equity,
                "Stock Balance": stock_model.balance,
                "Real House Equity": real_house_equity,
                "Real Stock Balance": real_stock_balance,
                "Inflation Index": cumulative_inflation_index,
                "Rent Paid (Stock Scenario)": year_rent, # Monthly Rent
                "Mortgage Rate (%)": current_mortgage_rate_display,
                "Refund Reinvested": refund_this_month,
                "Transaction Cost": transaction_cost_this_month
            })
        
        # End of Year: Calculate Tax Refund for NEXT year
        # Refund = RRSP Contributions * Marginal Tax Rate
        pending_tax_refund = stock_model.annual_rrsp_contributions * marginal_tax_rate
    
    # Final 'Net Cash' Calculation (After Taxes/Fees)
    # Housing: Net Proceeds = Equity - Agent Fees - Legal
    final_net_housing = housing_model.get_net_proceeds() 
    selling_costs = housing_model.equity - final_net_housing
    
    # Stocks: After Tax Value
    final_net_stocks = stock_model.get_after_tax_value(end_year, marginal_tax_rate)
    
    # Calculate Totals for Analysis
    total_rent_paid = sum(d['Rent Paid (Stock Scenario)'] for d in history_data)
    total_transaction_friction = sum(d['Transaction Cost'] for d in history_data)
        
    return {
        "history": history_data,
        "final_house_equity_gross": housing_model.equity,
        "final_house_net": final_net_housing,
        "final_stock_balance_gross": stock_model.balance,
        "final_stock_net": final_net_stocks,
        "initial_down_payment": raw_down_payment,
        "closing_costs_paid": closing_costs,
        "selling_costs_estimated": selling_costs,
        "total_initial_capital": total_initial_capital,
        "start_house_price": house_price,
        "inflation_index": cumulative_inflation_index,
        "total_mortgage_interest": housing_model.total_interest_paid,
        "total_maintenance": housing_model.total_maintenance_cost,
        "total_rent_paid": total_rent_paid,
        "total_stock_contributions": total_stock_contributions,
        "total_transaction_friction": total_transaction_friction
    }
