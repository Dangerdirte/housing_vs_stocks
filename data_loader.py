
# Historical Data Sources
# Housing: Approximated Canadian Average House Prices
# Stocks: S&P 500 Historical Annual Returns (Total Return including dividends)
# Inflation: Canada Historical CPI Inflation Rates

# Dictionary: Year -> Average House Price (CAD)
# Source approximation based on CREA/Trading Economics/StatsCan points
# Interpolated where specific annual data was missing in the rough search to provide a smooth curve for the model.
HOUSING_PRICES = {
    1975: 42000,
    1976: 45000, 1977: 48000, 1978: 51000, 1979: 55000,
    1980: 60000, 1981: 65000, 1982: 62000, 1983: 68000, 1984: 72000,
    1985: 78000, 1986: 88000, 1987: 100000, 1988: 110000, 1989: 130000,
    1990: 140000, 1991: 145000, 1992: 148000, 1993: 150000, 1994: 152000,
    1995: 148000, 1996: 150000, 1997: 154000, 1998: 155000, 1999: 158000,
    2000: 163000, 2001: 171000, 2002: 188000, 2003: 207000, 2004: 226000,
    2005: 236800, 2006: 250000, 2007: 290000, 2008: 305000, 2009: 320000,
    2010: 339000, 2011: 363000, 2012: 369000, 2013: 382000, 2014: 408000,
    2015: 442000, 2016: 489000, 2017: 510000, 2018: 488000, 2019: 500000,
    2020: 550000, 2021: 690000, 2022: 703000, 2023: 680000, 2024: 707100,
    2025: 720000 # Projected
}

# Dictionary: Year -> Annual Return % (e.g. 10.0 = 10%)
# Source: S&P 500 Historical Annual Returns (SlickCharts/Investopedia)
STOCK_RETURNS = {
    1975: 37.00, 1976: 23.83, 1977: -6.98, 1978: 6.51, 1979: 18.52,
    1980: 31.74, 1981: -4.70, 1982: 20.42, 1983: 22.34, 1984: 6.15,
    1985: 31.24, 1986: 18.49, 1987: 5.81, 1988: 16.54, 1989: 31.48,
    1990: -3.06, 1991: 30.23, 1992: 7.49, 1993: 9.97, 1994: 1.33,
    1995: 37.20, 1996: 22.68, 1997: 33.10, 1998: 28.34, 1999: 20.89,
    2000: -9.03, 2001: -11.85, 2002: -21.97, 2003: 28.36, 2004: 10.74,
    2005: 4.83, 2006: 15.61, 2007: 5.48, 2008: -36.55, 2009: 25.94,
    2010: 14.82, 2011: 2.10, 2012: 15.89, 2013: 32.15, 2014: 13.52,
    2015: 1.36, 2016: 11.96, 2017: 21.83, 2018: -4.38, 2019: 31.49,
    2020: 18.40, 2021: 30.92, 2022: -18.11, 2023: 26.29, 2024: 25.02,
    2025: 5.00 # YTD
}

# Dictionary: Year -> Annual Inflation Rate %
# Source: Canada Historical Inflation
INFLATION_RATES = {
    1975: 10.7, 1976: 7.5, 1977: 8.0, 1978: 8.9, 1979: 9.1,
    1980: 10.1, 1981: 12.5, 1982: 10.8, 1983: 5.8, 1984: 4.3,
    1985: 4.0, 1986: 4.1, 1987: 4.4, 1988: 4.0, 1989: 5.0,
    1990: 4.8, 1991: 5.6, 1992: 1.5, 1993: 1.9, 1994: 0.2, # '1994: 0.1' in list, using 0.2 for safety
    1995: 2.1, 1996: 1.6, 1997: 1.6, 1998: 1.0, 1999: 1.7,
    2000: 2.7, 2001: 2.5, 2002: 2.2, 2003: 2.8, 2004: 1.8,
    2005: 2.2, 2006: 2.0, 2007: 2.2, 2008: 2.3, 2009: 0.3,
    2010: 1.8, 2011: 2.9, 2012: 1.5, 2013: 0.9, 2014: 2.0,
    2015: 1.1, 2016: 1.4, 2017: 1.6, 2018: 2.3, 2019: 1.9,
    2020: 0.7, 2021: 3.4, 2022: 6.8, 2023: 3.9, 2024: 2.4,
    2025: 2.0 # Proj
}

# Dictionary: Year -> Monthly Rent ($)
# Source: CMHC / StatCan Historical Average Rents (Approx)
# Note: Data before 1990 is extrapolated backwards for rough estimation if needed, though 1990 is start of solid table.
RENTAL_PRICES = {
    1975: 200, 1976: 220, 1977: 240, 1978: 260, 1979: 280,
    1980: 300, 1981: 330, 1982: 350, 1983: 370, 1984: 390,
    1985: 410, 1986: 430, 1987: 450, 1988: 470, 1989: 490,
    1990: 504, 1991: 526, 1992: 537, 1993: 545, 1994: 550,
    1995: 559, 1996: 563, 1997: 568, 1998: 586, 1999: 601,
    2000: 622, 2001: 647, 2002: 668, 2003: 678, 2004: 691,
    2005: 703, 2006: 724, 2007: 746, 2008: 772, 2009: 788,
    2010: 799, 2011: 812, 2012: 830, 2013: 848, 2014: 869,
    2015: 884, 2016: 903, 2017: 927, 2018: 954, 2019: 987,
    2020: 1028, 2021: 1097, 2022: 1214, 2023: 1314, 2024: 1402,
    2025: 1488
}

def get_housing_price(year):
    """Returns the average house price for a given year."""
    return HOUSING_PRICES.get(year, HOUSING_PRICES.get(2025))

def get_stock_return(year):
    """Returns the annual stock market return percentage (e.g. 5.0) for a given year."""
    # Default to average 7% if out of range, though our range covers 1975-2025
    return STOCK_RETURNS.get(year, 7.0)

def get_inflation_rate(year):
    """Returns the annual inflation rate percentage for a given year."""
    return INFLATION_RATES.get(year, 2.0)

def get_average_rent(year, city="National"):
    """Returns the average monthly rent for a given year and city."""
    base_rent = RENTAL_PRICES.get(year, RENTAL_PRICES.get(2025))
    
    # Simple scalar approximation for regional rent premiums relative to National
    # Toronto/Vancouver typically 30-50% higher than National avg
    # Calgary often close to National or slightly higher in boom times
    if city == "Toronto":
        return base_rent * 1.45
    elif city == "Vancouver":
        return base_rent * 1.55
    elif city == "Calgary":
        return base_rent * 1.10
    elif city == "Montreal":
        return base_rent * 0.90
    return base_rent

# Dictionary: Year -> 5-Year Fixed Mortgage Rate (%)
MORTGAGE_RATES = {
    1975: 11.25, 1976: 11.50, 1977: 10.50, 1978: 10.75, 1979: 13.00,
    1980: 14.45, 1981: 18.35, 1982: 18.15, 1983: 13.28, 1984: 13.60,
    1985: 12.00, 1986: 11.00, 1987: 11.50, 1988: 12.00, 1989: 12.50,
    1990: 13.00, 1991: 11.00, 1992: 9.50, 1993: 8.50, 1994: 9.00,
    1995: 8.75, 1996: 7.50, 1997: 6.75, 1998: 6.90, 1999: 7.50,
    2000: 7.75, 2001: 6.85, 2002: 6.50, 2003: 6.00, 2004: 5.75,
    2005: 5.50, 2006: 6.00, 2007: 7.39, 2008: 7.00, 2009: 5.50,
    2010: 5.25, 2011: 4.80, 2012: 4.50, 2013: 4.25, 2014: 4.00,
    2015: 3.80, 2016: 3.70, 2017: 4.00, 2018: 4.50, 2019: 4.20,
    2020: 3.50, 2021: 2.79, 2022: 4.50, 2023: 5.50, 2024: 5.00,
    2025: 4.50 # Proj
}

# Regional Price Multipliers (Approximate Premium over National Average)
# Used to interpolate regional prices where exact data is missing
REGIONAL_PREMIUMS = {
    # Year: {City: Multiplier}
    1975: {"Toronto": 1.4, "Vancouver": 1.9, "Calgary": 1.1, "Montreal": 0.8},
    1989: {"Toronto": 1.9, "Vancouver": 1.5, "Calgary": 0.9, "Montreal": 0.8}, # TO Bubble
    1996: {"Toronto": 1.3, "Vancouver": 1.8, "Calgary": 1.0, "Montreal": 0.7}, # TO Crash
    2017: {"Toronto": 1.8, "Vancouver": 2.1, "Calgary": 1.0, "Montreal": 0.7},
    2024: {"Toronto": 1.5, "Vancouver": 1.7, "Calgary": 0.9, "Montreal": 0.7}
}

# Capital Gains Inclusion Rates
# (Date effective doesn't align perfectly with years, simplified to majority rule for that year)
CAPITAL_GAINS_INCLUSION = {
    1972: 0.50, 1988: 0.666, 1990: 0.75, 2000: 0.50
}

# TFSA Contribution Limits
# Year -> Annual Limit
TFSA_LIMITS = {
    2009: 5000, 2010: 5000, 2011: 5000, 2012: 5000,
    2013: 5500, 2014: 5500, 2015: 10000, 2016: 5500,
    2017: 5500, 2018: 5500, 2019: 6000, 2020: 6000,
    2021: 6000, 2022: 6000, 2023: 6500, 2024: 7000,
    2025: 7000
}

def get_mortgage_rate(year):
    """Returns the average 5-year fixed mortgage rate for a given year."""
    return MORTGAGE_RATES.get(year, 5.0)

def get_housing_price(year, city="National"):
    """
    Returns the estimated house price for a given year and city.
    Uses interpolating multipliers against the National average for robustness.
    """
    national_price = HOUSING_PRICES.get(year, HOUSING_PRICES.get(2025))
    
    if city == "National":
        return national_price
        
    # Find closest premium data points
    years = sorted(REGIONAL_PREMIUMS.keys())
    
    # 1. Exact match or before first
    if year <= years[0]:
        mult = REGIONAL_PREMIUMS[years[0]].get(city, 1.0)
        return national_price * mult
    
    # 2. After last
    if year >= years[-1]:
        mult = REGIONAL_PREMIUMS[years[-1]].get(city, 1.0)
        return national_price * mult
        
    # 3. Interpolate
    year_prev = years[0]
    for y_check in years:
        if y_check > year:
            year_next = y_check
            break
        year_prev = y_check
    
    mult_prev = REGIONAL_PREMIUMS[year_prev].get(city, 1.0)
    mult_next = REGIONAL_PREMIUMS[year_next].get(city, 1.0)
    
    ratio = (year - year_prev) / (year_next - year_prev)
    interpolated_mult = mult_prev + ratio * (mult_next - mult_prev)
    
    return national_price * interpolated_mult

def get_inclusion_rate(year):
    """Returns the Capital Gains Inclusion rate for a given year."""
    # Logic: Find the rate effective for that year
    # Dict keys are "Start Year" of that rate
    applicable_rate = 0.0 # Before 1972
    for start_year in sorted(CAPITAL_GAINS_INCLUSION.keys()):
        if year >= start_year:
            applicable_rate = CAPITAL_GAINS_INCLUSION[start_year]
    return applicable_rate

def get_tfsa_limit(year):
    """Returns the TFSA annual contribution limit for that year."""
    return TFSA_LIMITS.get(year, 0)

# RRSP Dollar Limits
# Year -> Limit
RRSP_LIMITS = {
    1991: 11500, 1992: 12500, 1993: 12500, 1994: 13500, 1995: 14500,
    1996: 13500, 1997: 13500, 1998: 13500, 1999: 13500, 2000: 13500,
    2001: 13500, 2002: 13500, 2003: 14500, 2004: 15500, 2005: 16500,
    2006: 18000, 2007: 19000, 2008: 20000, 2009: 21000, 2010: 22000,
    2011: 22450, 2012: 22970, 2013: 23820, 2014: 24270, 2015: 24930,
    2016: 25370, 2017: 26010, 2018: 26230, 2019: 26500, 2020: 27230,
    2021: 27830, 2022: 29210, 2023: 30780, 2024: 31560, 2025: 32490
}

def get_rrsp_limit(year):
    """Returns the RRSP dollar limit for that year."""
    # Before 1991, limits were complicated percentages. 
    # Valid approximation for "High Income" user is roughly 7500-11500 range in late 80s
    if year < 1991: return 7500 
    return RRSP_LIMITS.get(year, 32490)

# Seasonality Index (Approximate Canadian Real Estate Cycle)
# 1.0 = Average trend. >1.0 = Premium (Spring), <1.0 = Discount (Winter)
SEASONALITY_INDEX = {
    1: 0.98,  # Jan (Cold, slow)
    2: 0.99,  # Feb
    3: 1.01,  # Mar (Spring market starts)
    4: 1.03,  # Apr
    5: 1.04,  # May (Peak)
    6: 1.03,  # Jun
    7: 1.01,  # Jul (Summer slowdown starts)
    8: 1.00,  # Aug
    9: 1.01,  # Sep (Fall bump)
    10: 1.00, # Oct
    11: 0.99, # Nov
    12: 0.97  # Dec (Holidays, dead market)
}

def get_monthly_housing_price(year, month, city="National"):
    """
    Returns the estimated price for a specific month.
    Combines Annual Trend interpolation with Monthly Seasonality.
    """
    price_curr = get_housing_price(year, city)
    price_next = get_housing_price(year + 1, city)
    
    if price_next is None:
        price_next = price_curr * 1.03 # Assume 3% growth if no future data
        
    # Calculate Monthly Trend Growth
    # We model the 'Annual Average' as the price roughly at the START of the year for simulation simplicity,
    # and interpolate towards the next year's start.
    if price_curr > 0:
        annual_growth = price_next / price_curr
    else:
        annual_growth = 1.03
        
    monthly_growth_factor = annual_growth ** (1/12)
    
    # Base Trend Price for this month
    # Month 1 = Current Year Baseline
    # Month 12 = Approaches Next Year Baseline
    base_price = price_curr * (monthly_growth_factor ** (month - 1))
    
    # Apply Seasonality
    seasonal_multiplier = SEASONALITY_INDEX.get(month, 1.0)
    
    return base_price * seasonal_multiplier

# Property Tax Rates (Approximate % of Assessed Value)
PROPERTY_TAX_RATES = {
    "Toronto": 0.61,
    "Vancouver": 0.29,
    "Calgary": 0.74,
    "Montreal": 0.76, # nominal rate, though complexity exists
    "National": 1.00  # Conservative estimate
}

def get_property_tax_rate(city):
    """Returns the estimated property tax rate (%) for a given city."""
    return PROPERTY_TAX_RATES.get(city, 1.0)
