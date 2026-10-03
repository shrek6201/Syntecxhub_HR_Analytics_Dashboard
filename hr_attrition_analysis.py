# %%
import pandas as pd
import numpy as np

df = pd.read_csv("data/Cleaned_HR_Data_Analysis.csv")
print(df.shape)
pd.set_option("display.max_columns", 15)
df.head()

# %%
# Quick data quality check
print("Nulls:\n", df.isna().sum()[df.isna().sum() > 0])
print("\nDuplicate EmpIDs:", df.duplicated(subset=["EmpID"]).sum())
print("\nAttrition value counts:\n", df["Attrition"].value_counts())

# %%
# Drop duplicate EmpIDs, keeping the first occurrence
before = len(df)
df = df.drop_duplicates(subset=["EmpID"], keep="first").reset_index(drop=True)
print(f"Dropped {before - len(df)} duplicate rows. New shape: {df.shape}")

# %%
# YearsWithCurrManager nulls: plausibly employees with 0 years under their
# current manager (new hire / new manager), recorded as blank instead of 0
df["YearsWithCurrManager"] = df["YearsWithCurrManager"].fillna(0).astype(int)
print(df["YearsWithCurrManager"].isna().sum(), "nulls remaining")

# %%
# Sanity check: does YearsWithCurrManager=0 actually line up with low tenure?
# (confirms the fillna assumption was reasonable rather than just hiding a problem)
df[df["YearsWithCurrManager"] == 0][["YearsAtCompany", "YearsInCurrentRole"]].describe()

# %%
# Numeric attrition flag for correlation/aggregation work
df["AttritionFlag"] = (df["Attrition"] == "Yes").astype(int)

# %%
# Correlation of numeric features against attrition
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
corr_with_attrition = df[numeric_cols].corr()["AttritionFlag"].sort_values()
print(corr_with_attrition)

# %%
# Drop constant columns. They carry zero analytical value and clutter the model
constant_cols = ["EmployeeCount", "StandardHours", "Over18"]
df = df.drop(columns=constant_cols)
print(df.shape)

# %%
import matplotlib.pyplot as plt
import seaborn as sns

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
corr_matrix = df[numeric_cols].corr()

plt.figure(figsize=(14, 10))
sns.heatmap(corr_matrix, cmap="coolwarm", center=0, annot=False)
plt.title("Correlation Matrix - HR Attrition Dataset")
plt.tight_layout()
plt.savefig("correlation_heatmap.png", dpi=150)
plt.show()

# %%
# Categorical drivers (these often matter more than numeric correlation for attrition)
for col in ["OverTime", "JobRole", "Department", "MaritalStatus", "BusinessTravel"]:
    print(f"--- Attrition rate by {col} ---")
    print(df.groupby(col)["AttritionFlag"].mean().sort_values(ascending=False).round(3))
    print()

# %%
print(df["BusinessTravel"].value_counts())

# %%
# Fix the inconsistent category label
df["BusinessTravel"] = df["BusinessTravel"].replace("TravelRarely", "Travel_Rarely")
print(df["BusinessTravel"].value_counts())

# %%
# Re-check now that it's merged
print(df.groupby("BusinessTravel")["AttritionFlag"].mean().round(3))

# %%
# Scan all categorical columns for similar label inconsistencies
cat_cols = df.select_dtypes(include="object").columns.tolist()
for col in cat_cols:
    print(f"--- {col} ({df[col].nunique()} unique) ---")
    print(df[col].unique())
    print()

# %%
df.to_csv("hr_attrition_cleaned.csv", index=False)
print("Exported:", df.shape)

# %%
# Quick final summary for the README later
print("Attrition rate:", df["AttritionFlag"].mean().round(3))
print("\nTop numeric correlates with attrition:")
print(df[numeric_cols].corr()["AttritionFlag"].abs().sort_values(ascending=False).head(6))
