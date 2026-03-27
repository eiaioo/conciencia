import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DATOS Y ESTADO
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'f_key' not in st.session_state: st.session_state.f_key = 0

# Paleta Mate Técnica (Auditada para evitar textos invisibles)
if st.session_state.tema == "Oscuro":
    C_BG, C_SEC, C_TXT, C_BRD, C_INP = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#1C2128"
    C_ACC = "#E67E22"
else:
    C_BG, C_SEC, C_TXT, C_BRD, C_INP = "#F8F9FA", "#FFFFFF", "#1F2328", "#D0D7DE", "#FFFFFF"
    C_ACC = "#D35400"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label, div {{ color: {C_TXT} !important; }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{ background-color: {C_SEC} !important; border-right: 1px solid {C_BRD}; }}
    
    /* Eliminar barra blanca de expanders */
    div[data-testid="stExpander"], .streamlit-expanderHeader, .streamlit-expanderContent {{
        background-color: {C_SEC} !important;
        border: 1px solid {C_BRD} !important;
        color: {C_TXT} !important;
    }}

    /* Inputs y Selectores */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input, select {{
        background-color: {C_BG} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
    }}
    
    /* Botones Mate */
    .stButton > button {{
        background-color: {C_SEC} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
        border-radius: 8px;
    }}
    .stButton > button:hover {{ border-color: {C_ACC} !important; color: {C_ACC} !important; }}

    /* Etapas de producción (Opacidad 30%) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #1a1a1a !important; font-weight: 600;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS TÉCNICA (RESTABLECIDA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar", "Levadura"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_f": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(168, 230, 173, 0.3)"}]},
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "c": "rgba(255, 179, 140, 0.3)"},
    "Crema Ruby 50/50": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "c": "rgba(168, 230, 173, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "c": "rgba(212, 163, 115, 0.3)"},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar": 300, "Canela": 25, "c": "rgba(183, 183, 164, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": ["Vainilla", "Chocolate"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas"},
    "Rosca de reyes": {"espec": ["Tradicional", "Turín"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "m": "Masa Brioche Rosca"},
    "Berlinas": {"espec": ["Ruby v2.0", "Vainilla Clásica"], "tam": {"Estándar": 60}, "m": "Masa de Berlinas", "p_man": {"Ruby v2.0": 70}},
    "Rollos": {"espec": ["Tradicional"], "tam": {"Individual": 90}, "m": "Masa Brioche Roles"},
}

# ==========================================
# 3. NAVEGACIÓN Y CAPTURA
# =
