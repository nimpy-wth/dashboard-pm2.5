import pandas as pd
df = pd.read_csv('hatyai.csv')

# Identify columns with 100% null values
null_counts = df.isnull().sum()
columns_to_drop = null_counts[null_counts == df.shape[0]].index

# Drop the identified columns
df.drop(columns_to_drop, axis=1, inplace=True)

# Impute missing values with the mean of each column
df['TEMP'].replace(to_replace=0, method='ffill', inplace=True) 
df.fillna(df.mean().round(2), inplace=True) 

# Save to a new file without the index
df.to_csv('cleaned_data.csv', index=False)