import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

st.set_page_config(page_title=“AgriBiz Senegal”, layout=“wide”, page_icon=“🌱”)
st.title(“🌱 AgriBiz Senegal - Volailles, Betail & Maraichage”)

PRIX_MARCHE = {
“Poulet de chair”: {“Dakar”: 2500, “Thies”: 2400, “Touba”: 2300, “Autre”: 2200},
“Boeuf”:           {“Dakar”: 3500, “Thies”: 3400, “Touba”: 3300, “Autre”: 3200},
“Tomates”:         {“Dakar”: 600,  “Thies”: 550,  “Touba”: 500,  “Autre”: 480},
“Oignons”:         {“Dakar”: 700,  “Thies”: 650,  “Touba”: 600,  “Autre”: 580},
}

CANAUX_FORMALISATION = {
“Registre du Commerce”:    {“Cout”: “50 000 FCFA”,  “Delai”: “72h”,       “Contact”: “Centre de Formalites”},
“Statut de Societe”:       {“Cout”: “100 000 FCFA”, “Delai”: “1 semaine”, “Contact”: “Greffe du Tribunal”},
“Agrement Ministere”:      {“Cout”: “Gratuit”,      “Delai”: “1 mois”,    “Contact”: “Ministere Agriculture”},
“Carte Agro-Entrepreneur”: {“Cout”: “15 000 FCFA”,  “Delai”: “48h”,       “Contact”: “Chambre d’Agriculture”},
}

RENDEMENT_SECTEUR  = {“Volailles”: 0.40, “Betail”: 0.35, “Maraichage”: 0.45}
ALLOCATION_CAPITAL = {“Volailles”: 0.33, “Betail”: 0.34, “Maraichage”: 0.33}

@st.cache_data
def generate_budget_reference():
return pd.DataFrame({
“Activite”:               [“Volailles”, “Betail”, “Maraichage”],
“Investissement Initial”:  [400000, 600000, 500000],
“Cout Mensuel”:            [350000, 250000, 300000],
“Revenu Mensuel”:          [650000, 500000, 700000],
“Marge Nette”:             [300000, 250000, 400000],
})

def fmt(n):
return “{:,.0f}”.format(n).replace(”,”, “ “) + “ FCFA”

def calculate_profitability(investment, monthly_costs, monthly_revenue):
net_margin = monthly_revenue - monthly_costs
roi        = (net_margin / investment * 100) if investment > 0 else 0
break_even = (investment / net_margin)       if net_margin > 0 else float(“inf”)
return net_margin, roi, break_even

def compute_revenue(capital, sectors):
if not sectors:
return 0.0
n = len(sectors)
total = 0.0
for s in sectors:
alloc  = capital * ALLOCATION_CAPITAL[s] if n > 1 else capital
total += alloc * RENDEMENT_SECTEUR[s]
return total

with st.sidebar:
st.header(“Configuration”)
capital = st.number_input(“Capital Initial (FCFA)”, min_value=0, value=1000000, step=50000)
region  = st.selectbox(“Region”, [“Dakar”, “Thies”, “Touba”, “Autre”])
st.subheader(“Secteurs”)
poultry   = st.checkbox(“Volailles”,  value=True)
livestock = st.checkbox(“Betail”,     value=True)
gardening = st.checkbox(“Maraichage”, value=True)
st.subheader(“Budget Mensuel (FCFA)”)
feed_cost      = st.number_input(“Alimentation Animale”, value=250000, step=10000)
seed_cost      = st.number_input(“Semences / Plants”,    value=150000, step=10000)
labor_cost     = st.number_input(“Main d’oeuvre”,        value=300000, step=10000)
equipment_cost = st.number_input(“Equipement”,           value=100000, step=10000)
other_cost     = st.number_input(“Autres Depenses”,      value=200000, step=10000)

active_sectors = (
([“Volailles”]  if poultry   else []) +
([“Betail”]     if livestock else []) +
([“Maraichage”] if gardening else [])
)

total_monthly_cost    = feed_cost + seed_cost + labor_cost + equipment_cost + other_cost
total_monthly_revenue = compute_revenue(capital, active_sectors)
net_margin, roi, break_even = calculate_profitability(capital, total_monthly_cost, total_monthly_revenue)

st.header(“Tableau de Bord Financier”)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(“Capital Initial”,    fmt(capital))
col2.metric(“Couts Mensuels”,     fmt(total_monthly_cost))
col3.metric(“Revenus Estimes”,    fmt(total_monthly_revenue))
col4.metric(“Marge Nette”,        fmt(net_margin), delta=”{:.1f}% ROI”.format(roi))
col5.metric(“Retour sur Invest.”, “{:.1f} mois”.format(break_even) if break_even != float(“inf”) else “inf”)

st.header(“Prix du Marche - “ + region)
prix_df = pd.DataFrame(
{produit: prix[region] for produit, prix in PRIX_MARCHE.items()},
index=[“Prix (FCFA)”]
).T.reset_index().rename(columns={“index”: “Produit”})
st.dataframe(prix_df, use_container_width=True, hide_index=True)

st.header(“Referentiel Budget 1 Million FCFA”)
budget_ref = generate_budget_reference()
st.dataframe(budget_ref, use_container_width=True)

fig, ax = plt.subplots(figsize=(8, 4))
width = 0.22
x = np.arange(len(budget_ref))
ax.bar(x - width, budget_ref[“Investissement Initial”], width, label=“Investissement”, color=”#2d6a4f”)
ax.bar(x,         budget_ref[“Cout Mensuel”],           width, label=“Cout Mensuel”,   color=”#e76f51”)
ax.bar(x + width, budget_ref[“Revenu Mensuel”],         width, label=“Revenu Mensuel”, color=”#457b9d”)
ax.set_xticks(x)
ax.set_xticklabels(budget_ref[“Activite”])
ax.set_ylabel(“Montant (FCFA)”)
ax.set_title(“Comparaison par secteur”)
ax.legend()
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.header(“Opportunites Sectorielles”)
c1, c2 = st.columns(2)
with c1:
st.subheader(“Volailles et Betail”)
st.markdown(”- Production de viande : +15%/an\n- Oeufs biologiques : prime 30-50%\n- Lait et derives\n- Engrais organique”)
with c2:
st.subheader(“Maraichage”)
st.markdown(”- Legumes locaux\n- Plantes medicinales\n- Hydroponique : rendement 3x\n- Transformation : sechage, jus”)

st.header(“Formalisation”)
st.dataframe(
pd.DataFrame(CANAUX_FORMALISATION).T.reset_index().rename(columns={“index”: “Formalite”}),
use_container_width=True, hide_index=True
)
st.markdown(“1. Immatriculation Registre du Commerce\n2. Declaration Ministere Agriculture\n3. Numero NINEA\n4. Chambre d’Agriculture\n5. Certification ISRA\n6. Financements FONGIP / BNDE”)

st.header(“Plan Investissement”)
st.dataframe(pd.DataFrame({
“Poste”:    [“Volailles”, “Betail”, “Maraichage”, “Infrastructure”, “Formation”],
“Montant”:  [“300 000 FCFA”, “350 000 FCFA”, “200 000 FCFA”, “100 000 FCFA”, “50 000 FCFA”],
“Priorite”: [“Elevee”, “Moyenne”, “Elevee”, “Moyenne”, “Faible”],
}), use_container_width=True, hide_index=True)

st.header(“Conseils Personnalises”)
if capital < 500000:
st.warning(“Commencez par une seule activite specialisee.”)
elif capital <= 2000000:
st.success(“Combinez 2 activites complementaires.”)
else:
st.info(“Developpez une ferme integree avec transformation.”)

if not active_sectors:
st.warning(“Aucun secteur selectionne.”)
elif net_margin < 0:
st.error(“Marge nette negative. Reduisez les couts ou augmentez le capital.”)
else:
st.success(“Rentabilite positive ! Retour en {:.1f} mois.”.format(break_even))

st.markdown(”—”)
st.caption(“AgriBiz Senegal v2.0 | Ministere Agriculture - FONGIP - BNDE”)
