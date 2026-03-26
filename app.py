import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema Maestro Conciencia v4.0", layout="wide")
st.title("🥐 Producción Integral - CONCIENCIA")

# --- 1. BASE DE DATOS TÉCNICA (MASAS) ---
MASAS = {
    "Conchas": {
        "ingredientes": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0},
        "tamaños": {"Estándar": 95, "Mini": 35}, "merma": 1.0
    },
    "Pan de Muerto Tradicional": {
        "ingredientes": {"Harina panificable": 100, "Leche": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla": 25, "Sal": 2.0, "Levadura fresca": 3.0, "Agua de azahar": 2.0, "Ralladura naranja": 1.0},
        "tamaños": {"Estándar": 85}, "merma": 1.0
    },
    "Pan de Muerto Guayaba": {
        "ingredientes": {"Harina de fuerza": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura fresca": 5.0, "Sal": 1.8, "Polvo de guayaba": 5.0},
        "tamaños": {"Estándar": 95}, "merma": 1.0, "huesos_extra": {"harina": 0.075, "yema": 0.025}
    },
    "Berlinas": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche": 22, "Sal": 1.8, "Levadura seca": 1.0},
        "tangzhong": {"ratio_h": 0.05, "ratio_l": 0.25}, "tamaños": {"Pieza 60g": 60}, "merma": 0.85
    },
    "Roles Gourmet (Canela)": {
        "ingredientes": {"Harina de fuerza": 93, "Huevo": 30, "Leche (ajuste)": 5, "Levadura fresca": 3, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17},
        "tangzhong": {"ratio_h": 0.07, "ratio_l": 0.35}, "tamaños": {"Individual": 90}, "merma": 1.0
    },
    "Roles Red Velvet": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura instantánea": 1.0, "Cacao": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3},
        "tangzhong": {"ratio_h": 0.07, "ratio_l": 0.35}, "tamaños": {"Individual": 90}, "merma": 1.0
    },
    "Brownies": {
        "fijo": {"Mantequilla": 330, "Azúcar blanca": 275, "Azúcar mascabado": 120, "Chocolate amargo": 165, "Harina": 190, "Cocoa": 75, "Sal": 8, "Claras": 160, "Yemas": 95, "Nuez": 140},
        "tamaños": {"Molde 20x20": 1}, "merma": 1.0
    }
}

# --- 2. VARIANTES DINÁMICAS ---
SABORES_CONCHA = {"Vainilla": {"Harina": 10, "Azúcar Glass": 10, "Mantequilla": 10}, "Chocolate": {"Harina": 8.7, "Cacao": 1.3, "Azúcar Glass": 10, "Mantequilla": 10}, "Matcha": {"Harina": 9.1, "Matcha": 0.9, "Azúcar Glass": 10, "Mantequilla": 10}, "Mazapán Intenso": {"Harina": 10, "Azúcar Glass": 10, "Mantequilla": 10, "Mazapán": 6.6}}
SABORES_ROL = {"Tradicional": {"incl": {"Pasas": 4, "Arándanos": 4, "Nuez": 4}}, "Manzana": {"incl": {"Orejón Manzana": 8, "Nuez": 4}}, "Conejo Turín": {"incl": {"Nuez": 4, "Chocolate Turín": 16}}}
RELLENOS_CREMA = {"Sin Relleno": {}, "Pastelera Vainilla": {"Leche": 50, "Yemas": 10, "Azúcar": 12, "Fécula": 4.5, "Mantequilla": 3}, "Pastelera Chocolate": {"Leche": 48, "Yemas": 10, "Azúcar": 10, "Fécula": 4.5, "Chocolate 60%": 12}}

# --- 3. LÓGICA DE INTERFAZ ---
if 'comanda' not in st.session_state: st.session_state.comanda = []

t1, t2, t3 = st.tabs(["🛒 Cargar Comanda", "🥣 Hojas de Trabajo", "📋 Lista de Súper"])

with t1:
    st.subheader("Configurar pedido")
    base_sel = st.selectbox("1. Selecciona el Pan", list(MASAS.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        size_sel = st.selectbox("Tamaño", list(MASAS[base_sel]["tamaños"].keys()))
        cant = st.number_input("Cantidad de piezas / moldes", min_value=1, value=12)

    with col2:
        variante = "Única"
        if base_sel == "Conchas":
            variante = st.selectbox("Sabor Lágrima", list(SABORES_CONCHA.keys()))
        elif base_sel == "Roles Gourmet (Canela)":
            variante = st.selectbox("Sabor de Relleno", list(SABORES_ROL.keys()))
        elif base_sel in ["Pan de Muerto Tradicional", "Pan de Muerto Guayaba", "Berlinas"]:
            variante = st.selectbox("Crema Pastelera", list(RELLENOS_CREMA.keys()))
        elif base_sel == "Roles Red Velvet":
            st.info("Incluye Schmear Red Velvet y Glaseado Blanco")

    if st.button("➕ Añadir a Producción"):
        st.session_state.comanda.append({"base": base_sel, "tamaño": size_sel, "variante": variante, "cant": cant})

    if st.session_state.comanda:
        st.write("---")
        st.table(pd.DataFrame(st.session_state.comanda))
        if st.button("🗑️ Limpiar todo"): st.session_state.comanda = []

# --- 4. CÁLCULOS TÉCNICOS ---
insumos = {}

if st.session_state.comanda:
    with t2:
        for item in st.session_state.comanda:
            masa = MASAS[item['base']]
            st.header(f"{item['base']} - {item['variante']}")
            
            # --- CÁLCULO MASA ---
            if "fijo" in masa: # Caso Brownies
                st.subheader("Batch Fijo")
                for ing, val in masa['fijo'].items():
                    p = val * item['cant']
                    st.write(f"• {ing}: **{p:,.1f}g**")
                    insumos[ing] = insumos.get(ing, 0) + p
            else:
                p_u = masa['tamaños'][item['tamaño']]
                m_total = (p_u * item['cant']) / masa['merma']
                h_total = (m_total * 100) / sum(masa['ingredientes'].values())
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("🥣 Batido")
                    for ing, porc in masa['ingredientes'].items():
                        p = (porc * h_total) / 100
                        st.write(f"• {ing}: **{p:,.1f}g**")
                        insumos[ing] = insumos.get(ing, 0) + p
                with c2:
                    if 'tangzhong' in masa:
                        tz_h = h_total * masa['tangzhong']['ratio_h']
                        tz_l = h_total * masa['tangzhong']['ratio_l']
                        st.warning(f"⚡ Tangzhong: {tz_h:,.1f}g Harina | {tz_l:,.1f}g Leche")
                        insumos["Harina de fuerza"] = insumos.get("Harina de fuerza", 0) + tz_h
                        insumos["Leche"] = insumos.get("Leche", 0) + tz_l
                    if 'huesos_extra' in masa:
                        h_ex = m_total * masa['huesos_extra']['harina']
                        y_ex = m_total * masa['huesos_extra']['yema']
                        st.info(f"🦴 Refuerzo Huesos: {h_ex:,.1f}g Harina | {y_ex:,.1f}g Yema")
                        insumos["Harina de fuerza"] = insumos.get("Harina de fuerza", 0) + h_ex
                        insumos["Yemas"] = insumos.get("Yemas", 0) + y_ex

            # --- CÁLCULO COMPLEMENTOS ---
            st.subheader("✨ Complementos")
            if item['base'] == "Conchas":
                rec = SABORES_CONCHA[item['variante']]
                peso_l = 30 if item['tamaño'] == "Estándar" else 10
                for ing, val in rec.items():
                    p = (val * item['cant'] * peso_l) / sum(rec.values())
                    st.write(f"• {ing} (Lágrima): {p:,.1f}g")
                    insumos[ing] = insumos.get(ing, 0) + p

            if item['base'] == "Roles Gourmet (Canela)":
                for ing, val in {"Mantequilla":6, "Azúcar Mascabado":9, "Canela":0.75, "Maicena":0.6}.items():
                    p = val * item['cant']
                    st.write(f"• {ing} (Schmear): {p:,.1f}g")
                    insumos[ing] = insumos.get(ing, 0) + p
                for ing, val in SABORES_ROL[item['variante']]['incl'].items():
                    p
