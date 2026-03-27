import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE UI - INTERVENCIÓN RADICAL
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Paleta de Colores Blindada
if st.session_state.tema_oscuro:
    BG_HEX = "#0B0E11"       # Casi negro
    SEC_BG = "#15191E"       # Gris oscuro
    TEXT_HEX = "#E6EDF3"     # Blanco hueso (Alta visibilidad)
    BORDER_HEX = "#30363D"   # Borde gris oscuro
    BTN_BG = "#21262D"       # Botón mate
    ACCENT = "#D35400"       # Naranja mate
else:
    BG_HEX = "#FFFFFF"; SEC_BG = "#F6F8FA"; TEXT_HEX = "#24292F"; BORDER_HEX = "#D0D7DE"; BTN_BG = "#F3F4F6"; ACCENT = "#E67E22"

st.markdown(f"""
    <style>
    /* 1. Reset Global del App */
    .stApp {{ background-color: {BG_HEX} !important; color: {TEXT_HEX} !important; }}
    
    /* 2. Forzar todos los textos a ser visibles */
    h1, h2, h3, h4, p, span, label, li {{ color: {TEXT_HEX} !important; }}

    /* 3. Limpieza Total de Expanders (Barra de Cliente) */
    div[data-testid="stExpander"] {{
        background-color: {SEC_BG} !important;
        border: 1px solid {BORDER_HEX} !important;
    }}
    div[data-testid="stExpander"] summary {{
        background-color: {SEC_BG} !important;
        color: {TEXT_HEX} !important;
    }}
    div[data-testid="stExpander"] svg {{ fill: {TEXT_HEX} !important; }}

    /* 4. Selectores y Menús Desplegables (Blindados) */
    div[data-baseweb="select"] > div {{
        background-color: {SEC_BG} !important;
        color: {TEXT_HEX} !important;
        border: 1px solid {BORDER_HEX} !important;
    }}
    /* Menú que flota al abrir el select */
    div[role="listbox"], ul[role="listbox"] {{
        background-color: {SEC_BG} !important;
        border: 1px solid {BORDER_HEX} !important;
    }}
    li[role="option"] {{ color: {TEXT_HEX} !important; background-color: {SEC_BG} !important; }}
    li[role="option"]:hover {{ background-color: {BORDER_HEX} !important; }}

    /* 5. Inputs de Número y Texto */
    input[type="text"], input[type="number"], div[data-baseweb="input"] {{
        background-color: {SEC_BG} !important;
        color: {TEXT_HEX} !important;
        border: 1px solid {BORDER_HEX} !important;
    }}
    div[data-testid="stNumberInput"] button {{
        background-color: {BTN_BG} !important;
        color: {TEXT_HEX} !important;
        border: 1px solid {BORDER_HEX} !important;
    }}

    /* 6. Botones (Estilo Mate) */
    .stButton > button {{
        background-color: {BTN_BG} !important;
        color: {TEXT_HEX} !important;
        border: 1px solid {BORDER_HEX} !important;
        border-radius: 8px !important;
    }}
    .stButton > button:hover {{ border-color: {ACCENT} !important; color: {ACCENT} !important; }}

    /* 7. Tabs (Pestañas) */
    button[data-baseweb="tab"] {{ color: {TEXT_HEX} !important; }}
    button[aria-selected="true"] {{ border-bottom-color: {ACCENT} !important; color: {ACCENT} !important; }}

    /* 8. Etapas (Recuadros suaves 30%) */
    .etapa-box {{
        padding: 15px; border-radius: 10px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        color: #1a1a1a !important; /* Texto oscuro sobre fondo pastel */
    }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN TEMA
_, c_t2 = st.columns([0.94, 0.06])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS TÉCNICA (DNA COMPLETO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "etapas": [
            {"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"},
            {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"},
            {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(165, 165, 141, 0.3)"},
            {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}
        ],
        "merma": 1.0, "factor": 1.963
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "etapas": [
            {"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"},
            {"n": "2. Fermento", "i": ["Levadura fresca"], "c": "rgba(183, 183, 164, 0.3)"},
            {"n": "3. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": "rgba(165, 165, 141, 0.3)"},
            {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}
        ],
        "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "etapas": [{"n": "1. Batido y TZ", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}],
        "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5
    },
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350, "etapas": [{"n": "Proceso Único", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7}, "merma": 1.0, "tz_ratio": 0.07, "tz_liq": 5, "etapas": [{"n": "Proceso Único", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Muerto Tradicional": {"receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3}, "merma": 1.0, "etapas": [{"n": "Proceso Único", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True, "etapas": [{"n": "Batido Fijo", "i": ["Mantequilla sin sal", "Azúcar Blanca", "Chocolate Turin Amargo"], "c": "rgba(165, 165, 141, 0.3)"}]}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120}, "p_rel_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35}, "masa": "Masa Brioche Rosca"},
    "Pan de muerto": {"espec": {"Tradicional": []}, "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradi
