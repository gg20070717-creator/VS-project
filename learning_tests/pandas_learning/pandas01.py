import pandas as pd
df = pd.read_csv(r'D:\VS project\learning_tests\pandas_learning\movies_data.csv', encoding='utf-8')
print(df.head())
print(df.info())