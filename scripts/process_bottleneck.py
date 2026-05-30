import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

erp = pd.read_excel(DATA_DIR / "erp.xlsx")
web = pd.read_excel(DATA_DIR / "web.xlsx")
liaison = pd.read_excel(DATA_DIR / "liaison.xlsx")

# Harmonisation des noms de colonnes
erp.columns = erp.columns.str.strip().str.lower()
web.columns = web.columns.str.strip().str.lower()
liaison.columns = liaison.columns.str.strip().str.lower()

# Renommer id_web en sku
liaison = liaison.rename(columns={"id_web": "sku"})

# Renommer id_web en sku
liaison = liaison.rename(columns={"id_web": "sku"})

# Nettoyage ciblé
erp = erp.drop_duplicates(subset=["product_id"])
liaison = liaison.dropna(subset=["product_id", "sku"]).drop_duplicates(subset=["product_id"])
web = web.dropna(subset=["sku", "total_sales"])
web = web.sort_values("total_sales").drop_duplicates(subset=["sku"], keep="last")

# Harmoniser les clés de jointure
liaison["sku"] = liaison["sku"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
web["sku"] = web["sku"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

# Fusion
df = erp.merge(liaison, on="product_id", how="inner")
df = df.merge(web, on="sku", how="inner")

# Calcul CA
df["ca"] = df["price"] * df["total_sales"]
ca_total = df["ca"].sum()

# Z-score
mean_price = df["price"].mean()
std_price = df["price"].std()
df["z_score_price"] = (df["price"] - mean_price) / std_price
df["segment"] = df["z_score_price"].apply(lambda x: "premium" if x > 2 else "ordinaire")

vins_premium = df[df["segment"] == "premium"]
vins_ordinaires = df[df["segment"] == "ordinaire"]

rapport_ca = df[["product_id", "sku", "post_title", "price", "total_sales", "ca", "z_score_price", "segment"]]

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
            len(df),
            len(vins_premium),
            len(vins_ordinaires)
        ]
    })

    synthese.to_excel(writer, sheet_name="Synthese", index=False)

vins_premium.to_csv(OUTPUT_DIR / "vins_premium.csv", index=False)
vins_ordinaires.to_csv(OUTPUT_DIR / "vins_ordinaires.csv", index=False)

print("Pipeline terminé avec succès.")
print(f"ERP après dédoublonnage : {len(erp)} lignes")
print(f"Liaison après nettoyage : {len(liaison)} lignes")
print(f"Web produits après nettoyage : {len(web)} lignes")
print(f"Nombre de lignes fusionnées : {len(df)}")
print(f"Chiffre d'affaires total : {ca_total:.2f} €")
print(f"Nombre de vins premium : {len(vins_premium)}")
print(f"Nombre de vins ordinaires : {len(vins_ordinaires)}")