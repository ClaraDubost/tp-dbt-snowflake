import snowflake.connector
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger le .env depuis le dossier scripts/
load_dotenv('scripts/.env')

print(" Vérification des variables :")
print(f"USER: {os.getenv('DBT_SNOWFLAKE_USER')}")
print(f"ACCOUNT: {os.getenv('DBT_SNOWFLAKE_ACCOUNT')}")
print(f"WAREHOUSE: {os.getenv('DBT_SNOWFLAKE_WAREHOUSE')}")

# Configuration Snowflake
conn = snowflake.connector.connect(
    user=os.getenv('DBT_SNOWFLAKE_USER'),
    password=os.getenv('DBT_SNOWFLAKE_PASSWORD'), 
    account=os.getenv('DBT_SNOWFLAKE_ACCOUNT'),
    warehouse=os.getenv('DBT_SNOWFLAKE_WAREHOUSE'),
    database='SILVER',
    schema='RAW'
)

# Activer le warehouse explicitement
cursor = conn.cursor()
warehouse_name = os.getenv('DBT_SNOWFLAKE_WAREHOUSE')
cursor.execute(f"USE WAREHOUSE {warehouse_name}")
print(f" Warehouse {warehouse_name} activé")

# Export des données Sankey
query = "SELECT * FROM SILVER.RAW.SANKEY_DATA ORDER BY nb_transitions DESC"
df = pd.read_sql(query, conn)

# Créer le dossier data s'il n'existe pas
Path("data").mkdir(exist_ok=True)

# Export en CSV
df.to_csv('data/sankey_transitions.csv', index=False)
print(f" Données exportées : {len(df)} transitions dans data/sankey_transitions.csv")

# Fermer la connexion
cursor.close()
conn.close()

# Afficher un aperçu
print("\n Aperçu des données :")
print(df.head(10))