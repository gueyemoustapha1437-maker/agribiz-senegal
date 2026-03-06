import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ─────────────────────────────────────────────

# Configuration de la page

# ─────────────────────────────────────────────

st.set_page_config(page_title=“AgriBiz Sénégal”, layout=“wide”, page_icon=“🌱”)
st.title(“🌱 AgriBiz Sénégal - Volailles, Bétail & Maraîchage”)

# ─────────────────────────────────────────────

# Données de référence

# ─────────────────────────────────────────────

PRIX_MARCHE = {
“Poulet de chair”: {“Dakar”: 2500, “Thiès”: 2400, “Touba”: 2300, “Autre”: 2200},
“Bœuf”:            {“Dakar”: 3500, “Thiès”: 3400, “Touba”: 3300, “Autre”: 3200},
“Tomates”:         {“Dakar”: 600,  “Thiès”: 550,  “Touba”: 500,  “Autre”: 480},
“Oignons”:         {“Dakar”: 700,  “Thiès”: 650,  “Touba”: 600,  “Autre”: 580},
}

CANAUX_FORMALISATION = {
“Registre du Commerce”:    {“Coût”: “50 000 FCFA”,  “Délai”: “72h”,      “Contact”: “Centre de Formalités des Entreprises”},
“Statut de Société”:       {“Coût”: “100 000 FCFA”, “Délai”: “1 semaine”,“Contact”: “Greffe du Tribunal”},
“Agrément Ministère”:      {“Coût”: “Gratuit”,      “Délai”: “1 mois”,   “Contact”: “Ministère de l’Agriculture”},
“Carte d’Agro-Entrepreneur”:{“Coût”: “15 000 FCFA”, “Délai”: “48h”,      “Contact”: “Chambre d’Agriculture”},
}

# Taux de rendement mensuel par secteur (% du capital investi)

RENDEMENT_SECTEUR = {
“Volailles”:   0.40,   # 40 % du capital alloué
“Bétail”:      0.35,
“Maraîchage”:  0.45,
}

# Répartition du capital par secteur si plusieurs activités

ALLOCATION_CAPITAL = {
“Volailles”:   0.33,
“Bétail”:      0.34,
“Maraîchage”:  0.33,
}

# ─────────────────────────────────────────────

# Référentiel budget 1 million FCFA (mis en cache)

# ─────────────────────────────────────────────

@st.cache_data
def generate_budget_reference() -> pd.DataFrame:
data = {
“Activité”:              [“Volailles”, “Bétail”, “Maraîchage”],
“Investissement Initial”: [400_000,    600_000,  500_000],
“Coût Mensuel”:          [350_000,    250_000,  300_000],
“Revenu Mensuel”:        [650_000,    500_000,  700_000],
“Marge Nette”:           [300_000,    250_000,  400_000],
}
return pd.DataFrame(data)

# ─────────────────────────────────────────────

# Fonctions utilitaires

# ─────────────────────────────────────────────

def fmt(n: float) -> str:
“”“Formate un nombre en FCFA avec espace comme séparateur de milliers.”””
return f”{n:,.0f}”.replace(”,”, “ “) + “ FCFA”

def calculate_profitability(investment: float, monthly_costs: float, monthly_revenue: float):
net_margin  = monthly_revenue - monthly_costs
roi         = (net_margin / investment * 100) if investment > 0 else 0
break_even  = (investment / net_margin)       if net_margin > 0 else float(“inf”)
return net_margin, roi, break_even

def compute_revenue(capital: float, sectors: list[str]) -> float:
“”“Calcule un revenu mensuel estimé proportionnel au capital et aux secteurs actifs.”””
if not sectors:
return 0.0
n = len(sectors)
total = 0.0
for s in sectors:
alloc  = capital * ALLOCATION_CAPITAL[s] if n > 1 else capital
total += alloc * RENDEMENT_SECTEUR[s]
return total

# ─────────────────────────────────────────────

# Sidebar – Configuration

# ─────────────────────────────────────────────

with st.sidebar:
st.header(“📝 Configuration de l’Entreprise”)
capital = st.number_input(“Capital Initial (FCFA)”, min_value=0, value=1_000_000, step=50_000)
region  = st.selectbox(“Région”, [“Dakar”, “Thiès”, “Touba”, “Autre”])

```
st.subheader("Secteurs d'Activité")
poultry   = st.checkbox("Volailles",   value=True)
livestock = st.checkbox("Bétail",      value=True)
gardening = st.checkbox("Maraîchage",  value=True)

st.subheader("Budget Mensuel (FCFA)")
feed_cost      = st.number_input("Alimentation Animale", value=250_000, step=10_000)
seed_cost      = st.number_input("Semences / Plants",    value=150_000, step=10_000)
labor_cost     = st.number_input("Main d'œuvre",         value=300_000, step=10_000)
equipment_cost = st.number_input("Équipement",           value=100_000, step=10_000)
other_cost     = st.number_input("Autres Dépenses",      value=200_000, step=10_000)
```

# ─────────────────────────────────────────────

# Calculs principaux

# ─────────────────────────────────────────────

active_sectors = (
([“Volailles”]  if poultry   else []) +
([“Bétail”]     if livestock else []) +
([“Maraîchage”] if gardening else [])
)

total_monthly_cost    = feed_cost + seed_cost + labor_cost + equipment_cost + other_cost
total_monthly_revenue = compute_revenue(capital, active_sectors)

net_margin, roi, break_even = calculate_profitability(
capital, total_monthly_cost, total_monthly_revenue
)

# ─────────────────────────────────────────────

# TABLEAU DE BORD FINANCIER

# ─────────────────────────────────────────────

st.header(“📊 Tableau de Bord Financier”)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(“Capital Initial”,     fmt(capital))
col2.metric(“Coûts Mensuels”,      fmt(total_monthly_cost))
col3.metric(“Revenus Estimés”,     fmt(total_monthly_revenue))
col4.metric(“Marge Nette”,         fmt(net_margin),
delta=f”{roi:.1f} % ROI”,
delta_color=“normal” if net_margin >= 0 else “inverse”)
col5.metric(“Retour sur Invest.”,
f”{break_even:.1f} mois” if break_even != float(“inf”) else “∞”,
help=“Nombre de mois pour récupérer le capital initial”)

# ─────────────────────────────────────────────

# PRIX DU MARCHÉ PAR RÉGION

# ─────────────────────────────────────────────

st.header(f”💹 Prix du Marché – {region}”)
prix_df = pd.DataFrame(
{produit: prix[region] for produit, prix in PRIX_MARCHE.items()},
index=[“Prix (FCFA/kg ou unité)”]
).T.reset_index().rename(columns={“index”: “Produit”})
st.dataframe(prix_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────

# RÉFÉRENTIEL BUDGET 1 MILLION

# ─────────────────────────────────────────────

st.header(“💰 Référentiel Budget 1 Million FCFA”)
budget_ref = generate_budget_reference()

st.dataframe(
budget_ref.style.format({
“Investissement Initial”: lambda x: f”{x:,.0f}”.replace(”,”, “ “) + “ FCFA”,
“Coût Mensuel”:           lambda x: f”{x:,.0f}”.replace(”,”, “ “) + “ FCFA”,
“Revenu Mensuel”:         lambda x: f”{x:,.0f}”.replace(”,”, “ “) + “ FCFA”,
“Marge Nette”:            lambda x: f”{x:,.0f}”.replace(”,”, “ “) + “ FCFA”,
}),
use_container_width=True,
)

# Graphique comparatif

fig, ax = plt.subplots(figsize=(8, 4))
width = 0.22
x     = np.arange(len(budget_ref))
ax.bar(x - width,     budget_ref[“Investissement Initial”], width, label=“Investissement”, color=”#2d6a4f”)
ax.bar(x,             budget_ref[“Coût Mensuel”],           width, label=“Coût Mensuel”,   color=”#e76f51”)
ax.bar(x + width,     budget_ref[“Revenu Mensuel”],         width, label=“Revenu Mensuel”, color=”#457b9d”)
ax.set_xticks(x)
ax.set_xticklabels(budget_ref[“Activité”])
ax.set_ylabel(“Montant (FCFA)”)
ax.set_title(“Comparaison par secteur d’activité”)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f”{int(v):,}”.replace(”,”, “ “)))
ax.legend()
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

# ─────────────────────────────────────────────

# OPPORTUNITÉS SECTORIELLES

# ─────────────────────────────────────────────

st.header(“🚀 Opportunités Sectorielles”)
opp_col1, opp_col2 = st.columns(2)

with opp_col1:
st.subheader(“Volailles & Bétail”)
st.markdown(”””

- 🌡️ **Production de viande** : demande en hausse de +15 %/an
- 🥚 **Œufs biologiques** : prime de prix de 30–50 %
- 🥛 **Lait et dérivés** : marché en croissance urbaine
- 🧪 **Engrais organique** : valorisation des déchets animaux
  “””)

with opp_col2:
st.subheader(“Maraîchage”)
st.markdown(”””

- 🍅 **Légumes locaux** : tomate, oignon, aubergine
- 🌿 **Plantes médicinales** : marché d’exportation
- 🥬 **Agriculture hydroponique** : rendement 3× supérieur
- 🥫 **Transformation** : séchage, conserves, jus
  “””)

# ─────────────────────────────────────────────

# FORMALISATION DE L’ENTREPRISE

# ─────────────────────────────────────────────

st.header(“📝 Formalisation de l’Entreprise”)
st.subheader(“Canaux de Formalisation”)
formalisation_df = (
pd.DataFrame(CANAUX_FORMALISATION)
.T
.reset_index()
.rename(columns={“index”: “Formalité”})
)
st.dataframe(formalisation_df, use_container_width=True, hide_index=True)

st.subheader(“Étapes Clés”)
st.markdown(”””

1. **Immatriculation** au Registre du Commerce (CFE)
1. **Déclaration d’activité** au Ministère de l’Agriculture
1. **Obtention du numéro NINEA**
1. **Adhésion** à la Chambre d’Agriculture
1. **Certification sanitaire** (ISRA)
1. **Accès aux financements** (FONGIP, BNDE)
   “””)

# ─────────────────────────────────────────────

# PLAN D’INVESTISSEMENT

# ─────────────────────────────────────────────

st.header(“💼 Plan d’Investissement Recommandé”)
investment_data = {
“Poste”:          [“Élevage Volailles”, “Élevage Bétail”, “Maraîchage”, “Infrastructure”, “Formation”],
“Montant (FCFA)”: [300_000, 350_000, 200_000, 100_000, 50_000],
“Priorité”:       [“Élevée”, “Moyenne”, “Élevée”, “Moyenne”, “Faible”],
}
investment_df = pd.DataFrame(investment_data)
investment_df[“Montant (FCFA)”] = investment_df[“Montant (FCFA)”].apply(
lambda x: f”{x:,}”.replace(”,”, “ “)
)
st.dataframe(investment_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────

# CONSEILS PERSONNALISÉS

# ─────────────────────────────────────────────

st.header(“💡 Conseils Personnalisés”)

if capital < 500_000:
st.warning(“🔔 Commencez par une seule activité spécialisée (ex : poules pondeuses ou maraîchage sur petite surface).”)
elif capital <= 2_000_000:
st.success(“🌟 Combinez 2 activités complémentaires (ex : élevage + maraîchage avec recyclage des déchets).”)
else:
st.info(“🚀 Vous pouvez développer une ferme intégrée avec transformation des produits.”)

if not active_sectors:
st.warning(“⚠️ Aucun secteur d’activité sélectionné. Cochez au moins un secteur dans la barre latérale.”)
elif net_margin < 0:
st.error(
f”⚠️ Marge nette négative ({fmt(net_margin)}). “
“Réduisez vos coûts mensuels ou augmentez le capital investi.”
)
else:
st.success(
f”✅ Rentabilité positive ! Retour sur investissement estimé en **{break_even:.1f} mois**.”
)

# ─────────────────────────────────────────────

# Footer

# ─────────────────────────────────────────────

st.markdown(”—”)
st.caption(“AgriBiz Sénégal v2.0 | Ministère de l’Agriculture • Chambre d’Agriculture • FONGIP”)
