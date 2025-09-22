import pandas as pd

# Load
df = pd.read_excel(r"/mnt/data/Measles_Dataset.xlsx", sheet_name="WEB")

# 1) Drop exact duplicates
df = df.drop_duplicates()

# 2) Trim whitespace in object columns
for c in df.select_dtypes(include="object"):
    df[c] = df[c].str.strip()

# 3) Convert numeric-like text columns
numeric_like = []
for c in numeric_like:
    df[c] = (df[c].astype(str)
                   .str.replace(r"[,%\s]", "", regex=True)
                   .replace("", None))
    df[c] = pd.to_numeric(df[c], errors="coerce")

# 4) Parse date-like columns
date_candidates = []
for c in date_candidates:
    df[c] = pd.to_datetime(df[c], errors="coerce", infer_datetime_format=True)

# 5) Optional: unify text case for categoricals (title case)
low_card_cols = ['Region', 'Country', 'ISO3', 'Year', 'Month', 'Measles \nclinical', 'Measles \nepi-linked', 'Measles \nlab-confirmed', 'Rubella \nclinical', 'Rubella \nepi-linked', 'Rubella \nlab-confirmed', 'Rubella\nTotal', 'Discarded']
for c in low_card_cols:
    if df[c].dtype == "object":
        df[c] = df[c].str.strip().str.title()

# 6) Save cleaned dataset
df.to_csv("Measles_Dataset_cleaned.csv", index=False)
print("Saved cleaned CSV -> Measles_Dataset_cleaned.csv")
