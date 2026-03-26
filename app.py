import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA DEFINITIVA
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "merma": 1.0, "factor_panadero": 1.963
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "merma": 0.85, "tz": (0.05, 5)
    },
    "Masa Brioche Roles": {
        "receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche (ajuste)": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17},
        "merma": 1.0, "tz_fijo": (70, 350)
    },
    "Masa Red Velvet": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao en polvo": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3},
        "merma": 1.0, "tz": (0.07, 5)
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "merma": 1.0, "tz": (0.025, 1)
    },
    "Masa Muerto Tradicional": {
        "receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3, "Agua Azahar": 2, "Ralladura Naranja": 1},
        "merma": 1.0
    },
    "Masa Muerto Guayaba": {
        "receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5},
        "merma": 1.0, "huesos": True
    },
    "Mezcla Brownie": {
        "receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez Tostada": 140, "Sal escamas": 1.8},
        "merma": 1.0, "fijo": True
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Matcha": {"Harina de fuerza": 91.5, "Matcha en polvo": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla sin sal": 100},
    "Lágrima de Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66},
    "Lágrima de Pinole": {"Harina de fuerza": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Oreo": 25},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Crema Pastelera Chocolate": {"Leche entera": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Chocolate 60%": 120},
    "Crema Pastelera Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla sin sal": 20},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "Mantequilla sin sal": 16, "Sal": 0.8},
    "Glaseado Ruby": {"Chocolate Ruby": 80, "Azúcar Glass": 160, "Leche entera": 50},
    "Glaseado Turin": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche": 50, "Cabeza de Conejo": 1},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Schmear Red Velvet": {"Mantequilla sin sal": 6, "Azúcar": 6, "Cacao": 1.8, "Nuez": 4, "Chocolate amargo": 4},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2, "Vainilla": 0.5},
    "Inclusión Manzana": {"Orejón": 8, "Agua tibia": 2},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {
        "especialidad": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"], "Matcha": ["Lágrima de Matcha"], "Fresa": ["Lágrima de Fresa"], "Mazapán": ["Lágrima de Mazapán"], "Oreo": ["Lágrima de Oreo"], "Pinole": ["Lágrima de Pinole"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"
    },
    "Berlinas": {
        "especialidad": {"Vainilla": ["Crema Pastelera Vainilla"], "Ruby v2.0": ["Crema Ruby 50/50", "Glaseado Ruby"], "Turín": ["Crema Pastelera Turin", "Glaseado Turin"]},
        "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas",
        "p_berlina": {"Ruby v2.0": (70, {"Crema Ruby 50/50": 40, "Glaseado Ruby": 8}), "Turín": (60, {"Crema Pastelera Turin": 80, "Glaseado Turin": 16}), "Vainilla": (60, {"Crema Pastelera Vainilla": 80})}
    },
    "Rollos": {
        "especialidad": {"Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"], "Manzana": ["Schmear Canela", "Inclusión Manzana"], "Red Velvet": ["Schmear Red Velvet"]},
        "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "override": {"Red Velvet": "Masa Red Velvet"}
    },
    "Rosca de reyes": {
        "especialidad": {
            "Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate"]},
            "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Pastelera Turin"]}
        },
        "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90},
        "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25},
        "masa": "Masa Brioche Rosca"
    },
    "Pan de muerto": {
        "especialidad": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto"]},
        "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "override": {"Guayaba": "Masa Muerto Guayaba"}
    },
    "Brownies": {"especialidad": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 2. INTERFAZ
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0

st.title("🥐 Gestión Técnica CONCIENCIA")

with st.expander("📝 Cargar Nuevo Producto", expanded=True):
    f_id = st.session_state.form_id
    fam = st.selectbox("1. Familia", ["-"] + list(ARBOL.keys()), key=f"f_{f_id}")
    if fam != "-":
        esp = st.selectbox("2. Especialidad", ["-"] + list(ARBOL[fam]["especialidad"].keys()), key=f"e_{f_id}")
        if esp != "-":
            tam = st.selectbox("3. Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{f_id}")
            rel = "N/A"
            if fam == "Rosca de reyes":
                rel = st.selectbox("4. Relleno", ARBOL[fam]["especialidad"][esp]["rellenos"], key=f"r_{f_id}")
            cant = st.number_input("5. Cantidad", min_value=1, value=1, key=f"c_{f_id}")
            if st.button("✅ AGREGAR"):
                st.session_state.comanda.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "cant": cant})
                st.session_state.form_id += 1
                st.rerun()

# ==========================================
# 3. LÓGICA DE PRODUCCIÓN
# =====================
