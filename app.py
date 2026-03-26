import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro v5.0", layout="wide")
st.title("🚀 Centro de Producción Técnico - CONCIENCIA")

# --- 1. BASE DE DATOS DE MASAS (Recetas Madre) ---
MASAS = {
    "Conchas (Base)": {
        "ingredientes": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0},
        "merma": 1.0, "factor_panadero": 1.963
    },
    "Berlina (Fritura)": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo entero": 25, "Leche entera": 22, "Sal": 1.8, "Levadura seca": 1.0},
        "merma": 0.85, "tz": {"h_total": 0.05, "ratio": 5} # Tangzhong 1:5 sobre harina total
    },
    "Rol Master Brioche": {
        "ingredientes": {"Harina de fuerza": 93, "Huevo": 30, "Leche (ajuste)": 5, "Levadura fresca": 1, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17},
        "merma": 1.0, "tz": {"h_total": 0.07, "ratio": 5} # 70g harina : 350g leche (1:5)
    },
    "Rol Red Velvet": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura instantánea": 1.0, "Cacao": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3},
        "merma": 1.0, "tz": {"h_total": 0.07, "ratio": 5}
    },
    "Muerto Tradicional": {
        "ingredientes": {"Harina": 100, "Leche": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla": 25, "Sal": 2.0, "Levadura fresca": 3.0, "Azahar": 2.0, "Ralladura Naranja": 1.0},
        "merma": 1.0
    },
    "Muerto Guayaba": {
        "ingredientes": {"Harina": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura fresca": 5.0, "Sal": 1.8, "Polvo de guayaba": 5.0},
        "merma": 1.0, "huesos_refuerzo": True # +30% h, +10% yema sobre masa huesos
    },
    "Brownie 20x20": {
        "fijo": {"Mantequilla (avellana)": 330, "Azúcar blanca": 275, "Azúcar mascabado": 120, "Choco Amargo": 165, "Harina": 190, "Cocoa": 75, "Sal": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez": 140, "Sal escamas": 1.8},
        "merma": 1.0
    }
}

# --- 2. RELLENOS, GLASEADOS Y LÁGRIMAS (Sub-Recetas) ---
SUBRECETAS = {
    # Lágrimas de Concha
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Mazapán Intenso": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66},
    "Lágrima Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Oreo": {"Harina": 100, "Azúcar Glass": 75, "Mantequilla": 100, "Oreo": 25},
    # Rellenos Pasteleros
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Sal": 1.5, "Vainilla": 6},
    "Crema Ruby 50/50": {"Leche": 131.5, "Crema 35%": 131.5, "Yema": 53, "Azúcar": 63, "Fécula": 24, "Mantequilla": 16, "Sal": 0.8},
    "Crema Choco Amargo": {"Leche": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Chocolate 60%": 120, "Mantequilla": 30},
    "Crema Choco Leche Turin": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Chocolate Turin Leche": 120, "Mantequilla": 20},
    # Glaseados y Acabados
    "Glaseado Ruby": {"Chocolate Ruby": 80, "Azúcar Glass": 160, "Leche": 50},
    "Glaseado Turin (Costra)": {"Azúcar Glass": 200, "Choco Turin (Cuerpos)": 100, "Leche Caliente": 50, "Sal": 1},
    "Glaseado Vainilla (Flat)": {"Azúcar Glass": 200, "Leche": 35, "Vainilla": 5, "Sal": 0.5},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar Mascabado": 300, "Canela": 25, "Maicena": 20, "Sal": 3},
    "Rebozado Muerto": {"Mantequilla (baño)": 80, "Azúcar (rebozo)": 150, "Ralladura": 3}
}

# --- 3. CATÁLOGO FINAL DE PRODUCTOS ---
PRODUCTOS = {
    "CONCHAS": {
        "Concha Vainilla": {"masa": "Conchas (Base)", "peso": 95, "sub": ["Lágrima Vainilla"], "peso_sub": 30},
        "Concha Matcha": {"masa": "Conchas (Base)", "peso": 95, "sub": ["Lágrima Matcha"], "peso_sub": 30},
        "Concha Mazapán Intenso": {"masa": "Conchas (Base)", "peso": 95, "sub": ["Lágrima Mazapán Intenso"], "peso_sub": 30},
        "Concha Pinole": {"masa": "Conchas (Base)", "peso": 95, "sub": ["Lágrima Pinole"], "peso_sub": 30},
        "Mini Concha (Elegir Sabor)": {"masa": "Conchas (Base)", "peso": 35, "sub": ["Lágrima Vainilla"], "peso_sub": 10},
    },
    "BERLINAS": {
        "Berlina Ruby v2.0": {"masa": "Berlina (Fritura)", "peso": 70, "sub": ["Crema Ruby 50/50", "Glaseado Ruby"], "peso_sub": 48}, # 40g crema + 8g choco
        "Berlina Turin": {"masa": "Berlina (Fritura)", "peso": 60, "sub": ["Crema Choco Leche Turin", "Glaseado Turin (Costra)"], "peso_sub": 96}, # 80g crema + 16g costra
        "Berlina Vainilla Clásica": {"masa": "Berlina (Fritura)", "peso": 60, "sub": ["Crema Vainilla"], "peso_sub": 80},
    },
    "ROLES": {
        "Rol Tradicional (Pasas/Earl Grey)": {"masa": "Rol Master Brioche", "peso": 90, "sub": ["Schmear Canela", "Glaseado Vainilla (Flat)"], "peso_sub": 23},
        "Rol Manzana": {"masa": "Rol Master Brioche", "peso": 90, "sub": ["Schmear Canela", "Glaseado Vainilla (Flat)"], "peso_sub": 23},
        "Rol Conejo Turin": {"masa": "Rol Master Brioche", "peso": 90, "sub": ["Schmear Canela", "Glaseado Turin (Costra)"], "peso_sub": 40},
        "Rol Red Velvet": {"masa": "Rol Red Velvet", "peso": 90, "sub": ["Schmear Canela", "Glaseado Vainilla (Flat)"], "peso_sub": 25},
    },
    "MUERTOS": {
        "Muerto Tradicional": {"masa": "Muerto Tradicional", "peso": 85, "sub": ["Rebozado Muerto"], "peso_sub": 1},
        "Muerto Guayaba (Huesos Reforzados)": {"masa": "Muerto Guayaba", "peso": 95, "sub": ["Rebozado Muerto"], "peso_sub": 1},
    },
    "OTROS": {
        "Brownie Batch 12 pzas": {"masa": "Brownie 20x20", "peso": 1, "sub": [], "peso_sub": 0}
    }
}

# --- 4. LÓGICA DE LA APP ---
if 'carrito' not in st.session_state: st.session_state.carrito = []

t1, t2, t3 = st.tabs(["🛒 Comanda", "🥣 Hoja de Pesado", "📦 Totales de Almacén"])

with t1:
    col_cat, col_prod, col_cant = st.columns(3)
    with col_cat: cat_sel = st.selectbox("Categoría", list(PRODUCTOS.keys()))
    with col_prod: prod_sel = st.selectbox("Producto", list(PRODUCTOS[cat_sel].keys()))
    with col_cant: cant_sel = st.number_input("Cantidad", min_value=1, value=12)
    
    if st.button("➕ Agregar a Producción"):
        st.session_state.carrito.append({"cat": cat_sel, "prod": prod_sel, "cant": cant_sel})
    
    if st.session_state.carrito:
        st.table(pd.DataFrame(st.session_state.carrito))
        if st.button("🗑️ Vaciar"): st.session_state.carrito = []

almacen = {}

if st.session_state.carrito:
    with t2:
        for item in st.session_state.carrito:
            config = PRODUCTOS[item['cat']][item['prod']]
            m_name = config['masa']
            m_data = MASAS[m_name]
            
            st.header(f"📦 {item['prod']} (Total: {item['cant']})")
            
            # --- CÁLCULO DE MASA ---
            if "fijo" in m_data: # Caso Brownie
                for ing, val in m_data['fijo'].items():
                    total = val * item['cant']
                    st.write(f"• {ing}: **{total:,.1f}g**")
                    almacen[ing] = almacen.get(ing, 0) + total
            else:
                m_total = (config['peso'] * item['cant']) / m_data['merma']
                sum_p = sum(m_data['ingredientes'].values())
                h_base = (m_total * 100) / sum_p
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("🥣 Masa Principal")
                    for ing, porc in m_data['ingredientes'].items():
                        peso = (porc * h_base) / 100
                        st.write(f"• {ing}: **{peso:,.1f}g**")
                        almacen[ing] = almacen.get(ing, 0) + peso
                
                with c2:
                    if "tz" in m_data:
                        st.subheader("⚡ Tangzhong")
                        h_tz = h_base * m_data['tz']['h_total']
                        l_tz = h_tz * m_data['tz']['ratio']
                        st.warning(f"Mezclar: {h_tz:,.1f}g Harina + {l_tz:,.1f}g Leche")
                        almacen["Harina de fuerza"] = almacen.get("Harina de fuerza", 0) + h_tz
                        almacen["Leche"] = almacen.get("Leche", 0) + l_tz
                    
                    if "huesos_refuerzo" in m_data:
                        h_ex = m_total * 0.25 * 0.30
                        y_ex = m_total * 0.25 * 0.10
                        st.info(f"🦴 Refuerzo Huesos: +{h_ex:,.1f}g Harina / +{y_ex:,.1f}g Yema")
                        almacen["Harina"] = almacen.get("Harina", 0) + h_ex
                        almacen["Yemas"] = almacen.get("Yemas", 0) + y_ex

            # --- CÁLCULO DE SUBRECETAS ---
            for sub_name in config['sub']:
                st.subheader(f"✨ {sub_name}")
                sub_rec = SUBRECETAS[sub_name]
                peso_sub_total = config['peso_sub'] * item['cant']
                factor_sub = peso_sub_total / sum(sub_rec.values())
                for ing, val in sub_rec.items():
                    p = val * factor_sub
                    st.write(f"• {ing}: {p:,.1f}g")
                    almacen[ing] = almacen.get(ing, 0) + p
            st.divider()

    with t3:
        st.header("🛒 Lista Maestra de Insumos")
        df_final = pd.DataFrame(almacen.items(), columns=["Ingrediente", "Total (g)"])
        st.dataframe(df_final.sort_values("Ingrediente"), use_container_width=True)
