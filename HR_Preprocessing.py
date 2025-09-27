
import pandas as pd
import numpy as np

# ---------------------------------------
# Load dataset
df = pd.read_csv('HR.csv', sep=';')

# ---------------------------------------
# Convert date columns to datetime (invalid entries become NaT)
df['Hiredate'] = pd.to_datetime(df['Hiredate'], dayfirst=True, errors='coerce')
df['Termdate'] = pd.to_datetime(df['Termdate'], dayfirst=True, errors='coerce')
df['Birthdate'] = pd.to_datetime(df['Birthdate'], dayfirst=True, errors='coerce')

# ---------------------------------------
# Fill missing TermDate with today (for active employees)
today = pd.to_datetime('today')
df['Termdate'] = df['Termdate'].fillna(today)

# ---------------------------------------
# Create Attrition and IsActive columns
# Attrition: 1 = employee left, 0 = still active
df['Attrition'] = df['Termdate'].apply(lambda x: 0 if x==today else 1)
df['Attrition Flag'] = df['Attrition'].apply(lambda x: 'Yes' if x == 1 else 'No')

# IsActive flag: 1 = active, 0 = left
df['IsActive'] = df['Attrition'].apply(lambda x: 1 if x==0 else 0)

# ---------------------------------------
# Tenure in years/months
df['Tenure Years'] = ((df['Termdate'] - df['Hiredate']).dt.days / 365).round(1)
# Convert Tenure from years to months
df['Tenure Months'] = (df['Tenure Years'] * 12).round(1)

# Tenure Bands
bins = [0, 12, 36, 60, 1000]  # months: 0-12, 13-36, 37-60, 61+
labels = ['0-1 yr', '1-3 yrs', '3-5 yrs', '5+ yrs']
df['Tenure Band'] = pd.cut(df['Tenure Months'], bins=bins, labels=labels, include_lowest=True)

# ---------------------------------------
# Age
df['Age'] = (today - df['Birthdate']).dt.days // 365

# ---------------------------------------
# Handle categorical columns automatically
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
for col in categorical_cols:
    df[col] = df[col].fillna('Unknown')

# ---------------------------------------
# Handle numeric columns automatically
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
for col in numeric_cols:
    df[col] = df[col].fillna(df[col].mean())

# ---------------------------------------
# Performance Rating as ordered categorical (if exists)
performance_order = ['Needs Improvement', 'Satisfactory', 'Good', 'Excellent']
if 'Performance Rating' in df.columns:
    df['Performance Rating'] = pd.Categorical(df['Performance Rating'],
                                              categories=performance_order,
                                              ordered=True)

# ---------------------------------------
# Salary Bands
if 'Salary' in df.columns:
    df['SalaryBand'] = pd.cut(df['Salary'],
                              bins=[0, 50000, 100000, float('inf')],
                              labels=['Low', 'Medium', 'High'])

# ---------------------------------------
# Convert date columns to day/month/year format for Tableau
for col in ['Hiredate', 'Termdate', 'Birthdate']:
    df[col] = df[col].dt.strftime('%d/%m/%Y')

# ---------------------------------------
# Save cleaned & enhanced dataset
df.to_csv('HR_Final.csv', index=False)
print("Dataset fully cleaned, TermDate filled, Attrition & IsActive correct, Tenure accurate, ready for Tableau!")
