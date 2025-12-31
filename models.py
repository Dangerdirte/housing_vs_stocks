
import math

class InvestmentSimulation:
    def __init__(self, start_year, initial_deposit, monthly_contribution=0):
        self.start_year = start_year
        self.initial_deposit = initial_deposit
        self.monthly_contribution = monthly_contribution
        self.history = []  # List of dicts with yearly status

class HousingInvestment:
    def __init__(self, start_year, house_price, down_payment, interest_rate=0.05, amortization_years=25, property_tax_rate=0.006, monthly_insurance=100):
        self.start_year = start_year
        self.purchase_price = house_price
        self.down_payment = down_payment
        self.loan_amount = house_price - down_payment
        self.interest_rate = interest_rate
        self.amortization_years = amortization_years
        
        self.current_value = house_price
        self.remaining_principal = self.loan_amount
        self.equity = down_payment
        self.total_interest_paid = 0
        self.total_maintenance_cost = 0
        
        # Maintenance Logic Change:
        # Instead of % of CURRENT value (which inflates with housing bubble),
        # we start with % of PURCHASE value, and inflate with General Inflation (CPI).
        # This represents labor/materials cost.
        initial_maintenance_rate = 0.01 # 1% rule
        self.monthly_maintenance_cost = (house_price * initial_maintenance_rate) / 12
        
        # New Costs (Tax & Insurance)
        self.property_tax_rate = property_tax_rate
        self.monthly_insurance = monthly_insurance
        
        self.total_property_tax = 0
        self.total_insurance = 0
        
        self.monthly_payment = 0
        self.calculate_monthly_payment()

    def calculate_monthly_payment(self):
        if self.remaining_principal <= 0:
            self.monthly_payment = 0
            return 0
            
        if self.interest_rate == 0:
            self.monthly_payment = self.remaining_principal / (self.amortization_years * 12)
        else:
            r = self.interest_rate / 12
            # Remaining amortization months calculation would be complex if we tracked "months remaining".
            # Simplified: We assume standard amortization schedule initially, then re-amortize on renewal?
            # Actually, standard Canadian mortgages: payment is calculated to pay off by end of original amortization.
            # Upon renewal, we re-calculate payment based on REMAINING amortization period and NEW rate.
            # We need to track 'months_elapsed' to know remaining amortization.
            # However, for simplicity in this function, we assume 'amortization_years' passed in is the REMAINING years.
            # We'll need a way to track remaining years properly.
            pass
            
            n = self.amortization_years * 12
            self.monthly_payment = self.remaining_principal * (r * (1 + r)**n) / ((1 + r)**n - 1)
            
    def update_interest_rate(self, new_rate, remaining_amortization_years):
        """Updates the interest rate and recalculates the monthly payment based on remaining amortization."""
        self.interest_rate = new_rate
        self.amortization_years = remaining_amortization_years
        self.calculate_monthly_payment()

    def simulate_month(self, year, annual_appreciation_rate=0.03, annual_inflation_rate=0.02):
        # Appreciation
        monthly_appreciation = (1 + annual_appreciation_rate)**(1/12) - 1
        self.current_value *= (1 + monthly_appreciation)

        # Mortgage Payment
        interest_payment = self.remaining_principal * (self.interest_rate / 12)
        principal_payment = self.monthly_payment - interest_payment
        
        if self.remaining_principal > 0:
            self.remaining_principal -= principal_payment
            if self.remaining_principal < 0:
                self.remaining_principal = 0
            self.total_interest_paid += interest_payment
        
        # Equity Update
        self.equity = self.current_value - self.remaining_principal

        # Maintenance Inflation
        # We assume maintenance cost increases by inflation
        monthly_inflation = (1 + annual_inflation_rate)**(1/12) - 1
        self.monthly_maintenance_cost *= (1 + monthly_inflation)
        
        self.total_maintenance_cost += self.monthly_maintenance_cost
        
        # Taxes & Insurance
        # Property Tax is usually based on Assessed Value (often lags Market Value, but let's use Market for simplicity/conservatism)
        monthly_tax = (self.current_value * self.property_tax_rate) / 12
        self.total_property_tax += monthly_tax
        
        # Insurance (Inflates)
        self.monthly_insurance *= (1 + monthly_inflation)
        self.total_insurance += self.monthly_insurance
        
        return {
            "year": year,
            "equity": self.equity,
            "value": self.current_value,
            "maintenance": self.monthly_maintenance_cost,
            "property_tax": monthly_tax,
            "insurance": self.monthly_insurance,
            "payment": self.monthly_payment
        }

    def get_closing_costs(self, city):
        """Calculates Land Transfer Tax and other closing costs on PURCHASE."""
        # Simplified LTT Logic
        price = self.purchase_price
        ltt = 0
        
        # Ontario/Toronto LTT (Approximate Rule)
        # 0.5% first 55k, 1.0% to 250k, 1.5% to 400k, 2.0% to 2M, 2.5% over 2M
        # This is surprisingly complex to exact match history, using rough brackets
        def calc_ontario_ltt(val):
            ex = 0
            if val > 2000000: ex += (val - 2000000) * 0.025; val = 2000000
            if val > 400000: ex += (val - 400000) * 0.02; val = 400000
            if val > 250000: ex += (val - 250000) * 0.015; val = 250000
            if val > 55000: ex += (val - 55000) * 0.01; val = 55000
            ex += val * 0.005
            return ex
            
        if city == "Toronto":
            # Double tax (City + Prov)
            ltt = calc_ontario_ltt(price) * 2
        elif city in ["National", "Calgary", "Vancouver", "Montreal"]:
             # Using Ontario scalar as a "High avg" proxy or simplified
             # Vancouver PTT is different (1% on first 200k, 2% to 2M, 3% > 2M)
             # Calgary has no LTT (Just small title fees)
             if city == "Calgary":
                 ltt = 500 # Nominal
             elif city == "Vancouver":
                 v_ltt = 0
                 val = price
                 if val > 3000000: v_ltt += (val - 3000000) * 0.05; val = 3000000 # recent higher tiers? ignore for history
                 if val > 2000000: v_ltt += (val - 2000000) * 0.03; val = 2000000
                 if val > 200000: v_ltt += (val - 200000) * 0.02; val = 200000
                 v_ltt += val * 0.01
                 ltt = v_ltt
             else:
                 # Default "Avg" LTT
                 ltt = price * 0.015 
        
        legal_fees = 1500 # approx
        return ltt + legal_fees

    def get_net_proceeds(self):
        """Calculates net cash after selling (Agent fees)."""
        # Commission: 5% + HST (13%) -> 5.65% approx
        agent_commission_rate = 0.05
        sales_tax = 0.13 # Using Ontario HST as baseline
        total_fees = self.current_value * agent_commission_rate * (1 + sales_tax)
        
        return self.equity - total_fees

class StockInvestment:
    def __init__(self, start_year, initial_deposit):
        self.start_year = start_year
        # Accounts
        self.tfsa_balance = 0
        self.rrsp_balance = 0
        self.taxable_balance = 0
        self.taxable_book_cost = 0 
        
        import data_loader
        # Initial deposit strategy: Max TFSA (unlikely at start unless recent year), then RRSP, then Taxable?
        # Simplified: All initial capital goes to Taxable to start (mimics generic "Savings"). 
        # Or RRSP? If RRSP, we get a massive refund year 1.
        # Let's assume Taxable for consistency with previous.
        self.taxable_balance = initial_deposit
        self.taxable_book_cost = initial_deposit
        self.total_dividends = 0
        self.annual_rrsp_contributions = 0 # Track for refund calc
        
        # Friction Cost Tracking
        self.total_fees_paid = 0
        self.total_tax_drag_cost = 0
    
    def simulate_month(self, year, annual_return_rate, monthly_contribution=0, tfsa_limit_room=0, rrsp_limit_room=0, mer_fee_rate=0.0, tax_drag_rate=0.0):
        # Calculates Monthly Return Factor
        
        # Effective Returns for different account types
        # MER applies to ALL (Management fees)
        # Tax Drag applies ONLY to Taxable (Dividends taxed annually)
        
        rate_registered = annual_return_rate - mer_fee_rate
        rate_taxable = annual_return_rate - mer_fee_rate - tax_drag_rate
        
        monthly_return_reg = (1 + rate_registered)**(1/12) - 1
        monthly_return_tax = (1 + rate_taxable)**(1/12) - 1
        
        # Calculate Costs (Approximation for reporting)
        # We estimate the dollar value "lost" this month to fees/drag
        # Cost = Balance * (AnnualRate / 12)
        total_balance = self.tfsa_balance + self.rrsp_balance + self.taxable_balance
        monthly_mer_cost = total_balance * (mer_fee_rate / 12)
        monthly_drag_cost = self.taxable_balance * (tax_drag_rate / 12)
        
        self.total_fees_paid += monthly_mer_cost
        self.total_tax_drag_cost += monthly_drag_cost
        
        # 1. Growth
        # 1. Growth
        self.tfsa_balance *= (1 + monthly_return_reg)
        self.rrsp_balance *= (1 + monthly_return_reg)
        self.taxable_balance *= (1 + monthly_return_tax)
        
        # 2. Contributions
        used_tfsa = 0
        used_rrsp = 0
        
        if monthly_contribution > 0:
            remaining_contribution = monthly_contribution
            
            # Priority 1: TFSA
            if tfsa_limit_room > 0:
                amount = min(remaining_contribution, tfsa_limit_room)
                self.tfsa_balance += amount
                used_tfsa = amount
                remaining_contribution -= amount
                tfsa_limit_room -= amount # Decrement local var for correctness in checks
            
            # Priority 2: RRSP
            if remaining_contribution > 0 and rrsp_limit_room > 0:
                amount = min(remaining_contribution, rrsp_limit_room)
                self.rrsp_balance += amount
                used_rrsp = amount
                self.annual_rrsp_contributions += amount 
                remaining_contribution -= amount
            
            # Priority 3: Taxable
            if remaining_contribution > 0:
                self.taxable_balance += remaining_contribution
                self.taxable_book_cost += remaining_contribution
        
        return {
            "year": year,
            "balance": self.balance,
            "tfsa_used": used_tfsa,
            "rrsp_used": used_rrsp
        }

    @property
    def balance(self):
        return self.tfsa_balance + self.taxable_balance + self.rrsp_balance

    def get_after_tax_value(self, year, marginal_tax_rate=0.4):
        """Calculates liquidation value after Capital Gains and Income Tax."""
        import data_loader
        
        # TFSA is tax free
        tfsa_val = self.tfsa_balance
        
        # RRSP is 100% Taxable Income on withdrawal
        rrsp_val_net = self.rrsp_balance * (1 - marginal_tax_rate)
        
        # Taxable Account
        gain = self.taxable_balance - self.taxable_book_cost
        if gain < 0: gain = 0 
        
        inclusion_rate = data_loader.get_inclusion_rate(year)
        taxable_gain = gain * inclusion_rate
        tax_owed = taxable_gain * marginal_tax_rate
        taxable_net = self.taxable_balance - tax_owed
        
        return tfsa_val + rrsp_val_net + taxable_net
