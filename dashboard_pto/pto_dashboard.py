# app.py
import streamlit as st

st.title("PTO vs Salary After-Tax Model")

# Baseline inputs
baseline_salary = st.number_input("Baseline salary at minimum PTO", value=272000, step=1000)
baseline_pto = st.number_input("Baseline PTO days", value=30, step=1)

# Known comparison point
known_pto = st.number_input("Known higher PTO days", value=36, step=1)
known_salary = st.number_input("Salary at known higher PTO", value=263119, step=1000)

# Tax assumptions
st.subheader("Tax Assumptions")
federal_tax = st.slider("Federal marginal tax %", 0.0, 50.0, 35.0)
state_tax = st.slider("State tax %", 0.0, 15.0, 5.75)
local_tax = st.slider("Local tax %", 0.0, 5.0, 3.2)
medicare_tax = st.slider("Medicare / payroll tax %", 0.0, 5.0, 2.35)

marginal_tax_rate = (
    federal_tax + state_tax + local_tax + medicare_tax
) / 100.0

# PTO slider
st.subheader("Model PTO")
pto_days = st.slider("Total PTO / holidays", 30, 80, 45)

# Linear PTO-to-salary tradeoff
salary_loss_per_pto_day = (baseline_salary - known_salary) / (known_pto - baseline_pto)

modeled_salary = baseline_salary - salary_loss_per_pto_day * (pto_days - baseline_pto)

# Simple after-tax marginal model
baseline_net_salary = baseline_salary * (1 - marginal_tax_rate)
modeled_net_salary = baseline_net_salary - (
    (baseline_salary - modeled_salary) * (1 - marginal_tax_rate)
)

gross_delta = modeled_salary - baseline_salary
net_delta = modeled_net_salary - baseline_net_salary

gross_delta_pct = gross_delta / baseline_salary * 100
net_delta_pct = net_delta / baseline_net_salary * 100

# Workday model
total_workdays = 260
actual_workdays = total_workdays - pto_days

gross_per_workday = modeled_salary / actual_workdays
net_per_workday = modeled_net_salary / actual_workdays

# Display
st.subheader("Results")

col1, col2, col3 = st.columns(3)

col1.metric("Modeled Gross Salary", f"${modeled_salary:,.0f}")
col2.metric("Modeled After-Tax Salary", f"${modeled_net_salary:,.0f}")
col3.metric("PTO Days", f"{pto_days}")

col4, col5, col6 = st.columns(3)

col4.metric("Gross Change vs 30 PTO", f"{gross_delta_pct:.2f}%")
col5.metric("Net Change vs 30 PTO", f"{net_delta_pct:.2f}%")
col6.metric("Marginal Tax Rate", f"{marginal_tax_rate * 100:.2f}%")

st.subheader("Effective Daily Pay")

col7, col8 = st.columns(2)

col7.metric("Gross Pay per Workday", f"${gross_per_workday:,.0f}")
col8.metric("Net Pay per Workday", f"${net_per_workday:,.0f}")

st.subheader("PTO Tradeoff")

st.write(f"Each extra PTO day reduces gross salary by approximately **${salary_loss_per_pto_day:,.0f}**.")
st.write(f"Each extra PTO day reduces after-tax salary by approximately **${salary_loss_per_pto_day * (1 - marginal_tax_rate):,.0f}**.")

# Optional chart
import pandas as pd

rows = []

for pto in range(30, 81):
    salary = baseline_salary - salary_loss_per_pto_day * (pto - baseline_pto)
    net_salary = baseline_net_salary - ((baseline_salary - salary) * (1 - marginal_tax_rate))
    workdays = total_workdays - pto

    rows.append({
        "PTO Days": pto,
        "Gross Salary": salary,
        "After-Tax Salary": net_salary,
        "Net Pay per Workday": net_salary / workdays
    })

df = pd.DataFrame(rows)

st.line_chart(
    df.set_index("PTO Days")[["Gross Salary", "After-Tax Salary"]]
)

st.line_chart(
    df.set_index("PTO Days")[["Net Pay per Workday"]]
)