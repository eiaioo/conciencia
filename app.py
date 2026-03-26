import streamlit as st
import pandas as pd

st.set_page_config(page_title="Producción Conciencia v3.0", layout="wide")
st.title("🥐 Sistema de Producción Inteligente - CONCIENCIA")

# --- 1. BASES DE DATOS TÉCNICAS ---
MASAS = {
    "Conchas": {
        "ingredientes": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0},
        "tamaños": {"Estándar": 95, "Mini": 35},
        "merma": 1.0
    },
    "Pan de Muerto Tradicional": {
        "ingredientes": {"Harina panificable": 100, "Leche": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla": 25, "Sal": 2.0, "Levadura fresca": 3.0, "Agua de azahar": 2.0, "Ralladura naranja": 1.0},
        "tamaños": {"Estándar": 85},
        "merma": 1.0
    },
    "Pan de Muerto Guayaba": {
        "ingredientes": {"Harina de fuerza": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura fresca": 5.0, "Sal": 1.8, "Polvo de guayaba": 5.0},
        "tamaños": {"Estándar": 95},
        "merma": 1.0,
        "huesos_extra": {"harina": 0.075, "yema": 0.025}
    },
    "Berlinas": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo entero": 25, "Leche entera": 22, "Sal": 1.8, "Levadura seca": 1.0},
        "tangzhong": {"ratio_h": 0.05, "ratio_l": 0.25},
        "tamaños": {"Pieza 60g": 60},
        "merma": 0.85
    },
    "Roles Gourmet": {
        "ingredientes": {"Harina de fuerza": 93, "Huevo": 30, "Leche (ajuste)": 5, "Levadura fresca": 3, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17},
        "tangzhong": {"ratio_h": 0.07, "ratio_l": 0.35},
        "tamaños": {"Individual": 90},
        "merma": 1.0
    }
}

# Variantes específicas (Lágrimas, Rellenos, Inclusiones)
SABORES_CONCHA = {
    "Vainilla": {"Harina": 10, "Azúcar Glass": 10, "Mantequilla": 10},
    "Chocolate": {"Harina": 8.7, "Cacao": 1.3, "Azúcar Glass": 10, "Mantequilla": 10},
    "Matcha": {"Harina": 9.1, "Matcha": 0.9, "Azúcar Glass": 10, "Mantequilla": 10},
    "Mazapán Intenso": {"Harina": 10, "Azúcar Glass": 10, "Mantequilla": 10, "Mazapán": 6.6}
}

TIPOS_ROL = {
    "Tradicional": {"schmear": True, "incl": {"Pasas+Arandanos": 8, "Te Earl Grey": 2, "Nuez": 4}, "glaseado": "Vainilla"},
    "Manzana": {"schmear": True, "incl": {"Orejón Manzana": 8, "Nuez": 4}, "glaseado": "Vainilla"},
    "Conejo Turín": {"schmear": True, "incl": {"Nuez": 4}, "glaseado": "Turín"}
}

RELLENOS_CREMA = {
    "Sin Relleno": {},
    "Crema Vainilla": {"Leche": 50, "Yemas": 10, "Azúcar": 12, "Fécula": 4.5, "Mantequilla": 3},
    "Crema Chocolate Amargo": {"Leche": 48, "Yemas": 10, "Azúcar": 10, "Fécula": 4.5, "Chocolate 60%": 12, "Mantequilla": 3},
    "Crema Chocolate Leche Turín": {"Leche": 45, "Yemas": 10, "Azúcar": 9, "Fécula": 4.5, "Chocolate Turín": 12, "Mantequilla": 2}
}

# --- 2. LÓGICA DE SELECCIÓN ---
if 'comanda' not in st.session_state: st.session_state.comanda = []

t1, t2, t3 = st.tabs(["🛒 Nueva Orden", "🥣 Hoja de Producción", "📋 Lista de Insumos"])

with t1:
    st.subheader("Configurar Producto")
    base_sel = st.selectbox("1. Selecciona el Pan Base", list(MASAS.keys()))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        size_sel = st.selectbox("Tamaño", list(MASAS[base_sel]["tamaños"].keys()))
        cant = st.number_input("Cantidad", min_value=1, value=12)

    with col2:
        # Opciones dinámicas según la base
        variante = "N/A"
        if base_sel == "Conchas":
            variante = st.selectbox("Sabor de Lágrima", list(SABORES_CONCHA.keys()))
        elif base_sel == "Roles Gourmet":
            variante = st.selectbox("Tipo de Rollo", list(TIPOS_ROL.keys()))
        elif base_sel in ["Pan de Muerto Tradicional", "Pan de Muerto Guayaba", "Berlinas"]:
            variante = st.selectbox("Relleno de Crema", list(RELLENOS_CREMA.keys()))

    if st.button("➕ Agregar a la Producción"):
        st.session_state.comanda.append({
            "base": base_sel,
            "tamaño": size_sel,
            "variante": variante,
            "cant": cant
        })

    if st.session_state.comanda:
        st.write("---")
        st.table(pd.DataFrame(st.session_state.comanda))
        if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []

# --- 3. CÁLCULOS ---
compras = {}

if st.session_state.comanda:
    with t2:
        for item in st.session_state.comanda:
            masa_data = MASAS[item['base']]
            st.header(f"{item['base']} - {item['variante']}")
            
            # --- CÁLCULO MASA ---
            peso_u = masa_data['tamaños'][item['tamaño']]
            m_total = (peso_u * item['cant']) / masa_data['merma']
            h_total = (m_total * 100) / sum(masa_data['ingredientes'].values())
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🥣 Masa Base")
                for ing, porc in masa_data['ingredientes'].items():
                    p = (porc * h_total) / 100
                    st.write(f"• {ing}: **{p:,.1f}g**")
                    compras[ing] = compras.get(ing, 0) + p
            
            with c2:
                if 'tangzhong' in masa_data:
                    tz_h = h_total * masa_data['tangzhong']['ratio_h']
                    tz_l = h_total * masa_data['tangzhong']['ratio_l']
                    st.warning(f"⚡ Tangzhong: {tz_h:,.1f}g Harina | {tz_l:,.1f}g Leche")
                
                if 'huesos_extra' in masa_data:
                    h_ex = m_total * masa_data['huesos_extra']['harina']
                    y_ex = m_total * masa_data['huesos_extra']['yema']
                    st.info(f"🦴 Refuerzo Huesos: {h_ex:,.1f}g Harina | {y_ex:,.1f}g Yema")
                    compras["Harina de fuerza"] = compras.get("Harina de fuerza", 0) + h_ex
                    compras["Yemas"] = compras.get("Yemas", 0) + y_ex

            # --- CÁLCULO VARIANTES (LÁGRIMAS / INCLUSIONES / RELLENOS) ---
            st.subheader("✨ Complementos y Acabados")
            
            # Caso Conchas
            if item['base'] == "Conchas":
                l_receta = SABORES_CONCHA[item['variante']]
                p_l_u = 30 if item['tamaño'] == "Estándar" else 10
                for ing, val in l_receta.items():
                    p = val * (item['cant'] * p_l_u / sum(l_receta.values()))
                    st.write(f"• {ing} (Lágrima): {p:,.1f}g")
                    compras[ing] = compras.get(ing, 0) + p

            # Caso Muerto / Berlinas (Rellenos)
            if item['variante'] in RELLENOS_CREMA and item['variante'] != "Sin Relleno":
                r_receta = RELLENOS_CREMA[item['variante']]
                # 80g por pieza estándar
                for ing, val in r_receta.items():
                    p = val * (item['cant'] * 80 / sum(r_receta.values()))
                    st.write(f"• {ing} (Relleno): {p:,.1f}g")
                    compras[ing] = compras.get(ing, 0) + p

            # Caso Roles
            if item['base'] == "Roles Gourmet":
                rol_info = TIPOS_ROL[item['variante']]
                # Schmear fijo 13.4g por pieza
                st.write("**Schmear y Extras:**")
                for ing, val in {"Mantequilla":6, "Azúcar Mascabado":9, "Canela":0.75, "Maicena":0.6}.items():
                    p = val * item['cant']
                    st.write(f"- {ing}: {p:,.1f}g")
                    compras[ing] = compras.get(ing, 0) + p
                for ing, val in rol_info['incl'].items():
                    p = val * item['cant']
                    st.write(f"- {ing} (Inclusión): {p:,.1f}g")
                    compras[ing] = compras.get(ing, 0) + p
            
            st.divider()

    with t3:
        st.header("🛒 Lista Maestra de Insumos")
        df_c = pd.DataFrame(compras.items(), columns=["Ingrediente", "Total (g)"])
        st.dataframe(df_c.sort_values("Ingrediente"), use_container_width=True)
