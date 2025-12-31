
import sys
import data_loader
from models import HousingInvestment, StockInvestment

def main():
    print("--- Housing vs Stock Market Wealth Model (Canada) ---")
    
    try:
        start_year = int(input("Enter the year you want to simulate buying a house (1975-2024): "))
        if start_year < 1975 or start_year > 2024:
            print("Year must be between 1975 and 2024.")
            return
    except ValueError:
        print("Invalid input.")
        return

    # Get House Price for that year
    house_price = data_loader.get_housing_price(start_year)
    print(f"\nAverage House Price in {start_year}: ${house_price:,.2f}")

    try:
        mortgage_years = int(input("Enter mortgage length in years (e.g. 25): "))
        down_payment_pct = float(input("Enter down payment percentage (e.g. 20 for 20%): "))
    except ValueError:
        print("Invalid input.")
        return

    down_payment = house_price * (down_payment_pct / 100)
    print(f"\nRequired Deposit: ${down_payment:,.2f}")
    
    # Rent Estimation
    print("\nNote: Stock Market comparison assumes the investor pays the average Canadian rent each year.")
    
    housing_model = HousingInvestment(
        start_year=start_year,
        house_price=house_price,
        down_payment=down_payment,
        interest_rate=0.05, 
        amortization_years=mortgage_years
    )

    stock_model = StockInvestment(
        start_year=start_year,
        initial_deposit=down_payment 
    )

    # Simulation Loop
    current_year = start_year
    end_year = 2024 # Stop at present day data
    
    print("\nSimulating...")
    
    cumulative_inflation_index = 1.0
    
    housing_history = []
    stock_history = []
    
    for y in range(start_year, end_year + 1):
        # Get data for this year
        annual_stock_return = data_loader.get_stock_return(y) / 100.0
        annual_inflation = data_loader.get_inflation_rate(y) / 100.0
        
        # Calculate House Appreciation for this specific year
        current_price = data_loader.get_housing_price(y)
        next_price = data_loader.get_housing_price(y+1)
        if next_price:
             price_growth = (next_price - current_price) / current_price
        else:
            price_growth = 0.03 
        
        # Update Inflation Index
        cumulative_inflation_index *= (1 + annual_inflation)
        
        # Get Average Rent for this year
        current_rent = data_loader.get_average_rent(y)

        for m in range(12):
            # Simulate Housing
            h_stat = housing_model.simulate_month(y, annual_appreciation_rate=price_growth)
            
            # Calculate the "Opportunity Cost" / Stock Contribution
            # Housing Outflow = Mortgage Payment + Maintenance
            housing_monthly_cost = h_stat['payment'] + h_stat['maintenance']
            
            # Stock Scenario Outflow = Rent
            # Investable Amount = Housing_Outflow - Rent
            # If Housing is cheaper than Rent, this could be negative (withdraw from stocks to pay premium rent?), 
            # but usually Housing Cost > Rent initially.
            monthly_stock_contribution = housing_monthly_cost - current_rent
            
            # Simulate Stocks
            s_stat = stock_model.simulate_month(y, annual_return_rate=annual_stock_return, monthly_contribution=monthly_stock_contribution)
            
    
    # Final Results
    final_house_equity = housing_model.equity
    final_stock_balance = stock_model.balance
    
    # Real (Inflation Adjusted) Values
    real_house_equity = final_house_equity / cumulative_inflation_index
    real_stock_balance = final_stock_balance / cumulative_inflation_index
    
    print("\n--- RESULTS by END of 2024 ---")
    print(f"Scenario started in {start_year}.")
    print(f"Initial Capital: ${down_payment:,.2f}")
    
    print("\n[OPTION 1: BUY HOUSE]")
    print(f"Final Current Value:    ${housing_model.current_value:,.2f}")
    print(f"Remaining Mortgage:     ${housing_model.remaining_principal:,.2f}")
    print(f"Final Net Worth:        ${final_house_equity:,.2f}")
    print(f"Total Interest Paid:    ${housing_model.total_interest_paid:,.2f}")
    print(f"Total Maintenance:      ${housing_model.total_maintenance_cost:,.2f}")
    
    print("\n[OPTION 2: INVEST IN STOCKS]")
    print(f"(Invested Downpayment + Difference between Mortgage/Maintenace and Rent)")
    print(f"Final Net Worth:        ${final_stock_balance:,.2f}")
    
    print("\n--- INFLATION ADJUSTED (REAL WEALTH) ---")
    print(f"Inflation Factor:       {cumulative_inflation_index:.2f}x")
    print(f"Real House Equity:      ${real_house_equity:,.2f} (in {start_year} dollars)")
    print(f"Real Stock Value:       ${real_stock_balance:,.2f} (in {start_year} dollars)")
    
    diff = final_house_equity - final_stock_balance
    if diff > 0:
        print(f"\nWINNER: HOUSING (by ${diff:,.2f})")
    else:
        print(f"\nWINNER: STOCKS (by ${-diff:,.2f})")

if __name__ == "__main__":
    main()
