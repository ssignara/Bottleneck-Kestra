import duckdb
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
SQL_DIR = BASE_DIR / "sql"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

DB_PATH = OUTPUT_DIR / "bottleneck.duckdb"

con = duckdb.connect(DB_PATH)

# Lecture des fichiers Excel
erp = pd.read_excel(DATA_DIR / "erp.xlsx")
web = pd.read_excel(DATA_DIR / "web.xlsx")
liaison = pd.read_excel(DATA_DIR / "liaison.xlsx")

# Harmonisation colonnes
erp.columns = erp.columns.str.strip().str.lower()
web.columns = web.columns.str.strip().str.lower()
liaison.columns = liaison.columns.str.strip().str.lower()

# Chargement dans DuckDB
con.register("erp_df", erp)
con.register("web_df", web)
con.register("liaison_df", liaison)

con.execute("CREATE OR REPLACE TABLE erp_raw AS SELECT * FROM erp_df")
con.execute("CREATE OR REPLACE TABLE web_raw AS SELECT * FROM web_df")
con.execute("CREATE OR REPLACE TABLE liaison_raw AS SELECT * FROM liaison_df")

# Exécution des scripts SQL DuckDB
for sql_file in [
    "clean_erp.sql",
    "clean_liaison.sql",
    "clean_web.sql",
    "merge_data.sql",
    "calculate_revenue.sql",
]:
    query = (SQL_DIR / sql_file).read_text()
    con.execute(query)
    print(f"Script SQL exécuté : {sql_file}")

# Récupération du rapport CA
rapport_ca = con.execute("SELECT * FROM revenue_by_product").df()
ca_total = con.execute("SELECT ca_total FROM revenue_global").fetchone()[0]

# Z-score en Python
mean_price = rapport_ca["price"].mean()
std_price = rapport_ca["price"].std()

rapport_ca["z_score_price"] = (rapport_ca["price"] - mean_price) / std_price
rapport_ca["segment"] = rapport_ca["z_score_price"].apply(
    lambda x: "premium" if x > 2 else "ordinaire"
)

vins_premium = rapport_ca[rapport_ca["segment"] == "premium"]
vins_ordinaires = rapport_ca[rapport_ca["segment"] == "ordinaire"]

# Exports
with pd.ExcelWriter(OUTPUT_DIR / "rapport_ca.xlsx", engine="xlsxwriter") as writer:
    rapport_ca.to_excel(writer, sheet_name="CA par produit", index=False)

    synthese = pd.DataFrame({
        "indicateur": [
            "Chiffre d'affaires total",
            "Nombre de lignes fusionnées",
            "Nombre de vins premium",
            "Nombre de vins ordinaires"
        ],
        "valeur": [
            round(ca_total, 2),
            len(rapport_ca),
            len(vins_premium),
            len(vins_ordinaires)
        ]
    })

    synthese.to_excel(writer, sheet_name="Synthese", index=False)

vins_premium.to_csv(OUTPUT_DIR / "vins_premium.csv", index=False)
vins_ordinaires.to_csv(OUTPUT_DIR / "vins_ordinaires.csv", index=False)
rapport_ca.to_csv(OUTPUT_DIR / "rapport_ca.csv", index=False)

print("Pipeline DuckDB terminé avec succès.")
print(f"ERP après dédoublonnage : {con.execute('SELECT COUNT(*) FROM erp_clean').fetchone()[0]} lignes")
print(f"Liaison après nettoyage : {con.execute('SELECT COUNT(*) FROM liaison_clean').fetchone()[0]} lignes")
print(f"Web après dédoublonnage : {con.execute('SELECT COUNT(*) FROM web_clean').fetchone()[0]} lignes")
print(f"Nombre de lignes fusionnées : {len(rapport_ca)}")
print(f"Chiffre d'affaires total : {ca_total:.2f} €")
print(f"Nombre de vins premium : {len(vins_premium)}")
print(f"Nombre de vins ordinaires : {len(vins_ordinaires)}")

con.close()