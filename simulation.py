
import data_loader
from models import HousingInvestment, StockInvestment

def run_simulation(start_year, mortgage_years, down_payment_pct, initial_rent=None, city="National", marginal_tax_rate=0.40):
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
            current_month_index = (y - start_year) * 12 + m
            
            # Renewal Logic
            if current_month_index > 0 and current_month_index % 60 == 0:
                new_rate = data_loader.get_mortgage_rate(y) / 100.0
                months_passed = current_month_index
                remaining_months = (mortgage_years * 12) - months_passed
                if remaining_months > 0:
                    remaining_years = remaining_months / 12.0
                    housing_model.update_interest_rate(new_rate, remaining_years)
            
            h_stat = housing_model.simulate_month(y, annual_appreciation_rate=price_growth)
            
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
                "Refund Reinvested": refund_this_month
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
        "total_stock_contributions": total_stock_contributions
    }
