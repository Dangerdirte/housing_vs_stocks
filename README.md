# 🏡 Housing vs 📈 Stock Market: Wealth Accumulation Model

A sophisticated financial modeling tool comparing the historical returns of buying a home in major Canadian cities vs. renting and investing in the S&P 500.

## 🎯 Features
- **Real-World Canadian Data**: Historical housing prices for Toronto, Vancouver, Calgary, and Montreal (1975-2024).
- **Advanced Taxation Logic**:
  - **TFSA**: Automatically maximizes Tax-Free Savings Account room.
  - **RRSP**: Re-invests annual tax refunds and calculates tax on final withdrawal.
  - **Principal Residence Exemption**: Tax-free capital gains on housing.
- **Transaction Costs**:
  - Buying: Land Transfer Taxes (Municipal + Provincial) and legal fees.
  - Selling: Realtor commissions and closing costs.
- **Granular Simulation**: Monthly cash-flow analysis including mortgage renewals, maintenance inflation (CPI), and rent investing.

## 🚀 Comparison Logic
The model answers the question: *"If I didn't buy this house, and instead invested my Down Payment + Closing Costs + Monthly Difference into the market, where would I be today?"*

## 🛠️ Running Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```

## ☁️ Deployment
This app is ready for [Streamlit Community Cloud](https://streamlit.io/cloud).
1. Push this repository to GitHub.
2. Connect your repository on Streamlit Cloud.
3. Deploy!
