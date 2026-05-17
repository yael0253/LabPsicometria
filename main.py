import pandas as pd

# Leer archivo
df = pd.read_excel("ep_20230606_1_opcion.xlsx")

# Mostrar todas las columnas en la salida
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", None)

# Mostrar primeras filas sin truncar columnas
print(df.head(20).to_string(index=False))