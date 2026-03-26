import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema Conciencia v2.3", layout="wide")
st.title("🥐 Sistema de Producción Técnico - CONCIENCIA")

# --- BASE DE DATOS TÉCNICA ---
MASAS = {
    "Pan de Muerto Tradicional": {
        "descripcion": "Brioche mexicano: Naranja + Azahar (70g base + 15g huesos)",
        "ingredientes": {
            "Harina panificable": 100, "Leche": 25, "Yemas": 24, "Claras": 16,
            "Azúcar": 20, "Mantequilla": 25, "Sal": 2.0, "Levadura fresca": 3.0,
            "Agua de azahar": 2.0, "Ralladura de naranja": 1.0
        },
        "presentaciones": {"Pieza Tradicional (85g)": 85},
        "merma": 1.0,
        "procedimiento": [
            "1. Temperar mantequilla (18–20°C).",
            "2. Activar levadura en leche tibia + pizca de azúcar.",
            "3. Mezcla inicial: Harina + leche + levadura + huevos.",
            "4. Amasar 5–8 min; agregar azúcar en 2 partes.",
            "5. Incorporar mantequilla poco a poco hasta ventana media.",
            "6. Agregar sal, azahar y ralladura al final (Refuerza gluten).",
            "7. Fermentación inicial: 1–1.5 h a 26°C.",
            "8. División: 70g para cuerpo y 15g para huesos."
        ]
    },
    "Pan de Muerto (Guayaba)": {
        "descripcion": "Masa enriquecida con polvo de guayaba y técnica de huesos reforzados",
        "ingredientes": {
            "Harina de fuerza": 100, "Leche": 30, "Yemas": 18, "Claras": 12,
            "Azúcar": 20, "Mantequilla": 25, "Levadura fresca": 5.0, "Sal": 1.8,
            "Polvo de guayaba": 5.0
        },
        "presentaciones": {"Pieza Guayaba (95g)": 95},
        "merma": 1.0,
        "procedimiento": [
            "1. Activar levadura fresca en leche.",
            "2. Mezcla: Harina + levadura activada + huevos.",
            "3. Incorporar azúcar gradualmente.",
            "4. Integrar polvo de guayaba (evita que robe agua al inicio).",
            "5. Mantequilla en tandas y sal al final.",
            "6. T° final masa: 24-26°C."
        ],
        "huesos_reforzados": {"harina_extra_porc": 0.30, "yema_extra_porc": 0.10, "reserva_masa_porc": 0.25}
    },
    "Masa de Conchas": {
        "descripcion": "Masa brioche base para conchas conciencia",
        "ingredientes": {
            "Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, 
            "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0
        },
        "presentaciones": {"Estándar (95g)": 95, "Mini (35g)": 35},
        "merma": 1.0,
        "procedimiento": ["Autólisis 20 min", "Levadura+Vainilla", "Azúcar en 3 tandas", "Mantequilla", "T° 24-26°C"]
    },
    "Masa de Berlinas": {
        "descripcion": "Masa para fritura con Tangzhong 1:5",
        "ingredientes": {
            "Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20,
            "Huevo entero": 25, "Leche entera": 22, "Sal": 1.8, "Levadura seca": 1.0
        },
        "presentaciones": {"Pieza 60g": 60},
        "merma": 0.85,
        "tangzhong": {"ratio_harina": 0.05, "relacion_liquido": 5},
        "procedimiento": ["Preparar Tangzhong 1:5", "Gluten al 70% antes de grasa", "Fritura a 172°C"]
    }
}

ACABADOS = {
    "Rebozado Tradicional (Muerto)": {"receta": {"Mantequilla (baño)": 6.5, "Azúcar (rebozado)": 12.5, "Ralladura naranja (azúcar)": 0.25}},
    "Lágrima Concha Chocolate": {"unitario": 30, "mini": 10, "receta": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100}},
    "Lágrima Concha Vainilla": {"unitario": 30, "mini": 10, "receta": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100}},
    "Ninguno": {"receta": {}}
}

# --- LÓGICA INTERFAZ ---
if 'plan' not in st.session_state: st.session_state.plan = []

t1, t2, t3 = st.tabs(["📋 Plan de Producción", "🥣 Recetas y Procesos", "🛒 Lista Maestra"])

with t1:
    st.subheader("Configurar pedido")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        m_sel = st.selectbox("Masa", list(MASAS.keys()))
    with c2:
        t_sel = st.selectbox("Tamaño", list(MASAS[m_sel]["presentaciones"].keys()))
    with c3:
        a_sel = st.selectbox("Acabado/Lágrima", list(ACABADOS.keys()))
    with c4:
        cant = st.number_input("Piezas", min_value=1, value=1)
    
    if st.button("Añadir a Producción"):
        st.session_state.plan.append({"masa": m_sel, "tamaño": t_sel, "extra": a_sel, "cant": cant})

    if st.session_state.plan:
        st.write("---")
        st.table(pd.DataFrame(st.session_state.plan))
        if st.button("Limpiar plan"): st.session_state.plan = []

# --- CÁLCULOS ---
compras = {}

if st.session_state.plan:
    with t2:
        for item in st.session_state.plan:
            m_data = MASAS[item['masa']]
            st.header(f"Producción: {item['masa']} ({item['tamaño']})")
            
            peso_u = m_data['presentaciones'][item['tamaño']]
            masa_total = (peso_u * item['cant']) / m_data['merma']
            sum_porc = sum(m_data['ingredientes'].values())
            h_base = (masa_total * 100) / sum_porc
            
            c_izq, c_der = st.columns(2)
            with c_izq:
                st.subheader("🥣 Batido Principal")
                for ing, porc in m_data['ingredientes'].items():
                    peso = (porc * h_base) / 100
                    st.write(f"• {ing}: **{peso:,.1f}g**")
                    compras[ing] = compras.get(ing, 0) + peso
            
            with c_der:
                st.subheader("📝 SOP / Puntos Críticos")
                for paso in m_data['procedimiento']:
                    st.write(paso)
                
                if "huesos_reforzados" in m_data:
                    reserva = masa_total * m_data['huesos_reforzados']['reserva_masa_porc']
                    h_ex = reserva * m_data['huesos_reforzados']['harina_extra_porc']
                    y_ex = reserva * m_data['huesos_reforzados']['yema_extra_porc']
                    st.warning(f"🦴 Huesos: Reforzar {reserva:,.1f}g de masa con {h_ex:,.1f}g harina y {y_ex:,.1f}g yema.")
                    compras["Harina de fuerza"] = compras.get("Harina de fuerza", 0) + h_ex
                    compras["Yemas"] = compras.get("Yemas", 0) + y_ex

            if item['extra'] != "Ninguno":
                st.subheader(f"✨ Acabado: {item['extra']}")
                ex_data = ACABADOS[item['extra']]
                # Lógica para rebozado o lágrima
                if "Rebozado" in item['extra']:
                    for ing, g_p in ex_data['receta'].items():
                        peso = g_p * item['cant']
                        st.write(f"• {ing}: **{peso:,.1f}g**")
                        compras[ing] = compras.get(ing, 0) + peso
                else: # Lógica para lágrima de concha
                    peso_l_total = (ex_data['unitario'] if "Estándar" in item['tamaño'] else ex_data['mini']) * item['cant']
                    factor_l = peso_l_total / sum(ex_data['receta'].values())
                    for ing, val in ex_data['receta'].items():
                        peso = val * factor_l
                        st.write(f"• {ing}: **{peso:,.1f}g**")
                        compras[ing] = compras.get(ing, 0) + peso
            st.divider()

    with t3:
        st.header("🛒 Lista Maestra de Insumos")
        df_c = pd.DataFrame(compras.items(), columns=["Ingrediente", "Total (g)"])
        st.dataframe(df_c.sort_values("Ingrediente"), use_container_width=True)
