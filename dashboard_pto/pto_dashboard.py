# app.py
import streamlit as st

def federal_tax_2026(income):
    brackets = [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (609350, 0.35),
        (float("inf"), 0.37),
    ]
    tax = 0
    previous_limit = 0
    for limit, rate in brackets:
        if income > limit:
            tax += (limit - previous_limit) * rate
            previous_limit = limit
        else:
            tax += (income - previous_limit) * rate
            break
    return tax
def maryland_tax(income):
    return income * 0.0575
def county_tax(income):
    return income * 0.032

def payroll_tax(income):
    social_security_cap = 176100
    social_security = min(income, social_security_cap) * 0.062
    medicare = income * 0.0145
    additional_medicare = 0
    if income > 200000:
        additional_medicare = (income - 200000) * 0.009
    return social_security + medicare + additional_medicare

def total_tax(income):
    fed = federal_tax_2026(income)
    state = maryland_tax(income)
    county = county_tax(income)
    payroll = payroll_tax(income)
    return fed + state + county + payroll

st.title("PTO vs Salary After-Tax Model")

# Baseline inputs
baseline_salary = st.number_input("Baseline salary at minimum PTO", value=272000, step=1000)
baseline_pto = st.number_input("Baseline PTO days", value=30, step=1)

# Known comparison point
known_pto = st.number_input("Known higher PTO days", value=36, step=1)
known_salary = st.number_input("Salary at known higher PTO", value=263119, step=1000)


# PTO slider
st.subheader("Model PTO")
pto_days = st.slider("Total PTO / holidays", 30, 100, 45)

# Linear PTO-to-salary tradeoff
salary_loss_per_pto_day = (baseline_salary - known_salary) / (known_pto - baseline_pto)

modeled_salary = baseline_salary - salary_loss_per_pto_day * (pto_days - baseline_pto)


# Simple after-tax marginal model
baseline_net_salary = baseline_salary   - total_tax(baseline_salary)
modeled_net_salary  = modeled_salary    - total_tax(modeled_salary)

gross_delta = modeled_salary - baseline_salary
net_delta = modeled_net_salary - baseline_net_salary

gross_delta_pct = gross_delta / baseline_salary * 100
net_delta_pct = net_delta / baseline_net_salary * 100

# Workday model
total_workdays = 260
actual_workdays = total_workdays - pto_days
gross_per_workday = modeled_salary / actual_workdays
net_per_workday = modeled_net_salary / actual_workdays

effective_tax_rate = ( total_tax(modeled_salary)/ modeled_salary ) * 100

baseline_extra_day_net = (
    salary_loss_per_pto_day
    - (
        total_tax(baseline_salary)
        - total_tax(
            baseline_salary - salary_loss_per_pto_day
        )
    )
)

# Display
st.subheader("Results")

col1, col2, col3 = st.columns(3)

col1.metric("Modeled Gross Salary", f"${modeled_salary:,.0f}")
col2.metric("Modeled After-Tax Salary", f"${modeled_net_salary:,.0f}")
col3.metric("PTO Days", f"{pto_days}")

col4, col5, col6 = st.columns(3)

col4.metric("Gross Change vs 30 PTO", f"{gross_delta_pct:.2f}%")
col5.metric("Net Change vs 30 PTO", f"{net_delta_pct:.2f}%")
col6.metric("Effective Tax Rate", f"{effective_tax_rate:.2f}%")
st.subheader("Effective Daily Pay")

col7, col8 = st.columns(2)

col7.metric("Gross Pay per Workday", f"${gross_per_workday:,.0f}")
col8.metric("Net Pay per Workday", f"${net_per_workday:,.0f}")

st.subheader("PTO Tradeoff")

st.write(
    f"Each extra PTO day reduces gross salary by approximately"
    f"**${salary_loss_per_pto_day:,.0f}**."
)

st.write(
    f"Each extra PTO day reduces after-tax salary by approximately "
    f"**${baseline_extra_day_net:,.0f}**."
)

# Optional chart
import pandas as pd

rows = []

for pto in range(30, 81):
    salary = baseline_salary - salary_loss_per_pto_day * (pto - baseline_pto)
    net_salary = salary - total_tax(salary)
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