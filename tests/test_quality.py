import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "outputs"

rapport_path = OUTPUT_DIR / "rapport_ca.xlsx"
premium_path = OUTPUT_DIR / "vins_premium.csv"
ordinaires_path = OUTPUT_DIR / "vins_ordinaires.csv"

EXPECTED_ROWS = 714
EXPECTED_CA_TOTAL = 70568.60
EXPECTED_PREMIUM = 30
EXPECTED_ORDINAIRES = 684

rapport = pd.read_excel(rapport_path, sheet_name="CA par produit")
synthese = pd.read_excel(rapport_path, sheet_name="Synthese")
vins_premium = pd.read_csv(premium_path)
vins_ordinaires = pd.read_csv(ordinaires_path)

# 1. Présence des fichiers
assert rapport_path.exists(), "Le rapport Excel est manquant."
assert premium_path.exists(), "Le fichier vins_premium.csv est manquant."
assert ordinaires_path.exists(), "Le fichier vins_ordinaires.csv est manquant."

# 2. Absence de doublons sur product_id
assert rapport["product_id"].duplicated().sum() == 0, "Doublons détectés sur product_id."

# 3. Absence de valeurs manquantes sur les colonnes critiques
colonnes_critiques = ["product_id", "sku", "price", "total_sales", "ca", "segment"]
assert rapport[colonnes_critiques].isna().sum().sum() == 0, "Valeurs manquantes détectées."

# 4. Cohérence volumétrie
assert len(rapport) == EXPECTED_ROWS, f"Nombre de lignes incorrect : {len(rapport)} au lieu de {EXPECTED_ROWS}"

# 5. Cohérence CA total
ca_total = round(rapport["ca"].sum(), 2)
assert ca_total == EXPECTED_CA_TOTAL, f"CA total incorrect : {ca_total} au lieu de {EXPECTED_CA_TOTAL}"

# 6. Cohérence segmentation
assert len(vins_premium) == EXPECTED_PREMIUM, f"Nombre de vins premium incorrect : {len(vins_premium)}"
assert len(vins_ordinaires) == EXPECTED_ORDINAIRES, f"Nombre de vins ordinaires incorrect : {len(vins_ordinaires)}"

# 7. Cohérence z-score
assert (vins_premium["z_score_price"] > 2).all(), "Certains vins premium ont un z-score <= 2."
assert (vins_ordinaires["z_score_price"] <= 2).all(), "Certains vins ordinaires ont un z-score > 2."

print("Tous les tests qualité sont validés avec succès.") 