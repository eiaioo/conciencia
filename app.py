import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema Conciencia v2.1", layout="wide")
st.title("🥐 Sistema de Producción Técnico - CONCIENCIA")

# --- BASE DE DATOS TÉCNICA ---
MASAS = {
    "Masa de Conchas": {
        "descripcion": "Masa enriquecida para conchas estándar y mini",
        "factor_panadero": 1.963, # Factor para dividir el peso total y sacar harina
        "ingredientes": {
            "Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, 
            "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2
        },
        "presentaciones": {"Estándar": 95, "Mini": 35},
        "merma": 1.0,
        "tangzhong": None
    },
    "Masa de Berlinas": {
        "descripcion": "Masa específica para fritura profunda",
        "ingredientes": {
            "Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20,
            "Huevo entero": 25, "Leche entera": 22, "Sal": 1.8, "Levadura seca": 1.0
        },
        "presentaciones": {"Pieza 60g": 60},
        "merma": 0.85, # 15% merma por corte circular
        "tangzhong": {"ratio_harina": 0.05, "relacion_liquido": 5} # 5% harina total, 1:5
    },
    "Masa Brioche (EXCLUSIVA ROSCA)": {
        "descripcion": "Base para Rosca de Reyes y derivados autorizados",
        "ingredientes": {
            "Harina de fuerza": 100, "Azúcar refinada": 25, "Miel": 3,
            "Mantequilla sin sal": 30, "Huevo entero": 20, "Yema adicional": 4,
            "Leche entera": 24, "Levadura seca": 0.35, "Sal": 2.2,
            "Ralladuras": 1.1, "Agua de azahar": 0.6
        },
        "presentaciones": {"Rosca Mediana (900g)": 900, "Pieza Individual (100g)": 100},
        "merma": 1.0,
        "tangzhong": {"ratio_harina": 0.025, "relacion_liquido": 1} # 2.5% harina total, 1:1
    },
    "Masa Roles Red Velvet": {
        "descripcion": "Masa brioche roja con Tangzhong 1:5",
        "ingredientes": {
            "Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17,
            "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura instantánea": 1.0,
            "Cacao": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3
        },
        "presentaciones": {"Rol Individual": 90},
        "merma": 1.0,
        "tangzhong": {"ratio_harina": 0.07, "relacion_liquido": 5} # 7% harina total, 1:5
    }
}

TOPPINGS_RELLENOS = {
    "Lágrima Concha Chocolate": {"unitario": 30, "mini": 10, "receta": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100}},
    "Lágrima Concha Vainilla": {"unitario": 30, "mini": 10, "receta": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100}},
    "Crema Pastelera Vainilla": {"unitario": 80, "mini": 40, "receta": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Vainilla": 6}},
    "Crema Pastelera Chocolate": {"unitario": 80, "mini": 40, "receta": {"Leche": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Chocolate 60%": 120}},
    "Schmear Roles RV": {"unitario": 15, "mini": 8, "receta": {"Mantequilla": 6, "Azúcar": 6, "Cacao": 1.8, "Maicena": 0.6, "Nuez": 4, "Chocolate": 4}},
    "Ninguno": {"unitario": 0, "mini": 0, "receta": {}}
}

# --- LÓGICA APP ---
if 'plan' not in st.session_state: st.session_state.plan = []

t1, t2, t3 = st.tabs(["📋 Plan de Producción", "🥣 Recetas de Masas", "🛒 Lista Maestra"])

with t1:
    st.subheader("Configurar producción")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        m_sel = st.selectbox("Masa", list(MASAS.keys()))
    with c2:
        t_sel = st.selectbox("Tamaño/Presentación", list(MASAS[m_sel]["presentaciones"].keys()))
    with c3:
        r_sel = st.selectbox("Relleno/Lágrima", list(TOPPINGS_RELLENOS.keys()))
    with c4:
        cant = st.number_input("Cantidad", min_value=1, value=1)
    
    if st.button("Agregar al pedido"):
        st.session_state.plan.append({"masa": m_sel, "tamaño": t_sel, "extra": r_sel, "cant": cant})

    st.write("---")
    if st.session_state.plan:
        st.table(pd.DataFrame(st.session_state.plan))
        if st.button("Borrar Plan"): st.session_state.plan = []

# --- CÁLCULOS ---
compras = {}

if st.session_state.plan:
    with t2:
        for item in st.session_state.plan:
            m_data = MASAS[item['masa']]
            st.header(f"Receta: {item['masa']}")
            st.caption(m_data['descripcion'])
            
            # Cálculo de masa
            peso_u = m_data['presentaciones'][item['tamaño']]
            masa_total = (peso_u * item['cant']) / m_data['merma']
            
            # Harina base
            sum_porc = sum(m_data['ingredientes'].values())
            h_base = (masa_total * 100) / sum_porc
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Ingredientes Masa")
                for ing, porc in m_data['ingredientes'].items():
                    peso = (porc * h_base) / 100
                    st.write(f"• {ing}: **{peso:,.1f}g**")
                    compras[ing] = compras.get(ing, 0) + peso
            
            with col_b:
                if m_data['tangzhong']:
                    st.subheader("⚡ Tangzhong")
                    tz_h = h_base * m_data['tangzhong']['ratio_harina']
                    tz_l = tz_h * m_data['tangzhong']['relacion_liquido']
                    st.warning(f"Harina: {tz_h:,.1f}g | Leche: {tz_l:,.1f}g")
                    st.info(f"Relación 1:{m_data['tangzhong']['relacion_liquido']}")
            
            # Extras
            if item['extra'] != "Ninguno":
                st.subheader(f"Extra: {item['extra']}")
                ex_data = TOPPINGS_RELLENOS[item['extra']]
                peso_ex_total = ex_data['unitario'] * item['cant']
                sum_ex = sum(ex_data['receta'].values())
                f_ex = peso_ex_total / sum_ex if sum_ex > 0 else 0
                for ing, val in ex_data['receta'].items():
                    peso = val * f_ex
                    st.write(f"• {ing}: **{peso:,.1f}g**")
                    compras[ing] = compras.get(ing, 0) + peso
            st.write("---")

    with t3:
        st.header("🛒 Lista Maestra de Insumos")
        df_c = pd.DataFrame(compras.items(), columns=["Ingrediente", "Total (g)"])
        st.dataframe(df_c.sort_values("Ingrediente"), use_container_width=True)
