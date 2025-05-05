import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("🏡 House Loan Calculator")

# User inputs
house_cost = st.number_input("House Cost (€)", min_value=10000, step=1000, value=300000)
years = st.number_input("Years to Pay", min_value=1, step=1, value=25)
annual_interest_rate = st.slider("Annual Interest Rate (%)", min_value=0.0, max_value=10.0, step=0.1, value=2.5)

# Convert to monthly
months = years * 12
monthly_interest_rate = annual_interest_rate / 100 / 12

# Monthly payment formula for amortized loans
if monthly_interest_rate > 0:
    monthly_payment = house_cost * monthly_interest_rate * (1 + monthly_interest_rate) ** months / ((1 + monthly_interest_rate) ** months - 1)
else:
    monthly_payment = house_cost / months

total_paid = monthly_payment * months
total_interest = total_paid - house_cost

# Display results
st.subheader("📊 Loan Summary")
st.write(f"**Monthly Payment:** €{monthly_payment:,.2f}")
st.write(f"**Total Paid Over {years} Years:** €{total_paid:,.2f}")
st.write(f"**Total Interest Paid:** €{total_interest:,.2f}")

# Prepare data for graph
balances = []
interests = []
principals = []
remaining = house_cost

for i in range(1, months + 1):
    if monthly_interest_rate > 0:
        interest_payment = remaining * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
    else:
        interest_payment = 0
        principal_payment = monthly_payment

    remaining -= principal_payment
    balances.append(house_cost - remaining)
    interests.append(interest_payment)
    principals.append(principal_payment)

df = pd.DataFrame({
    "Month": range(1, months + 1),
    "Principal Paid": np.cumsum(principals),
    "Interest Paid": np.cumsum(interests),
    "Remaining Balance": house_cost - np.cumsum(principals),
})

# Plot
st.subheader("📈 Payment Progress Over Time")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["Month"], df["Principal Paid"], label="Principal Paid", color="green")
ax.plot(df["Month"], df["Interest Paid"], label="Interest Paid", color="red")
ax.plot(df["Month"], df["Remaining Balance"], label="Remaining Balance", color="blue")
ax.set_xlabel("Month")
ax.set_ylabel("Amount (€)")
ax.legend()
ax.grid(True)

st.pyplot(fig)
