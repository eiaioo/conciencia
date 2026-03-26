import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema Maestro Conciencia", layout="wide")
st.title("🥐 Sistema de Producción Integral - CONCIENCIA")

# --- BASE DE DATOS TÉCNICA CONSOLIDADA (MASAS) ---
MASAS = {
    "Brioche para Roles (Master)": {
        "ingredientes": {"Harina de fuerza": 93, "Huevo": 30, "Leche (ajuste)": 5, "Levadura fresca": 3, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17},
        "presentaciones": {"Rol Estándar (90g)": 90},
        "merma": 1.0,
        "tangzhong": {"ratio_harina_total": 0.07, "relacion_liquido": 5}, # 7% harina total, relación 1:5
        "procedimiento": ["1. TZ Frío + Huevo + Secos.", "2. Autólisis pasiva 15 min.", "3. Desarrollo gluten antes de azúcar.", "4. Mantequilla en 3 tandas.", "5. DDT 24°C.", "6. Bloque 12h a 4°C."]
    },
    "Pan de Muerto Tradicional": {
        "ingredientes": {"Harina panificable": 100, "Leche": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla": 25, "Sal": 2.0, "Levadura fresca": 3.0, "Agua de azahar": 2.0, "Ralladura de naranja": 1.0},
        "presentaciones": {"Pieza Tradicional (85g)": 85},
        "merma": 1.0,
        "procedimiento": ["Mantequilla a 18-20°C", "Sal y Azahar al final", "División 70g base / 15g huesos"]
    },
    "Pan de Muerto (Guayaba)": {
        "ingredientes": {"Harina de fuerza": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura fresca": 5.0, "Sal": 1.8, "Polvo de guayaba": 5.0},
        "presentaciones": {"Pieza Guayaba (95g)": 95},
        "merma": 1.0,
        "huesos_reforzados": {"harina_extra_porc": 0.30, "yema_extra_porc": 0.10, "reserva_masa_porc": 0.25},
        "procedimiento": ["Integrar guayaba tras hidratación", "Huesos reforzados con extra harina/yema"]
    },
    "Masa de Conchas": {
        "ingredientes": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0},
        "presentaciones": {"Estándar (95g)": 95, "Mini (35g)": 35},
        "merma": 1.0,
        "procedimiento": ["Autólisis 20 min", "Levadura+Vainilla", "Azúcar en 3 tandas"]
    },
    "Masa de Berlinas": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo entero": 25, "Leche entera": 22, "Sal": 1.8, "Levadura seca": 1.0},
        "presentaciones": {"Pieza 60g": 60},
        "merma": 0.85,
        "tangzhong": {"ratio_harina_total": 0.05, "relacion_liquido": 5},
        "procedimiento": ["TZ 1:5", "Merma 15% por corte circular", "Fritura 172°C"]
    },
    "Masa Roles Red Velvet": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura instantánea": 1.0, "Cacao": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3},
        "presentaciones": {"Rol Individual (90g)": 90},
        "merma": 1.0,
        "tangzhong": {"ratio_harina_total": 0.07, "relacion_liquido": 5},
        "procedimiento": ["Colorante en líquidos", "TZ 1:5", "Cacao con harina"]
    },
    "Masa Brioche (EXCLUSIVA ROSCA)": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar refinada": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo entero": 20, "Yema adicional": 4, "Leche entera": 24, "Levadura seca": 0.35, "Sal": 2.2, "Ralladuras": 1.1, "Agua de azahar": 0.6},
        "presentaciones": {"Rosca Mediana (900g)": 900, "Pieza Individual (100g)": 100},
        "merma": 1.0,
        "tangzhong": {"ratio_harina_total": 0.025, "relacion_liquido": 1},
        "procedimiento": ["TZ 1:1", "Reposo en bloque 12h"]
    },
    "Brownie (Batch 20x20)": {
        "fijo": {"Mantequilla (avellana)": 330, "Azúcar blanca": 275, "Azúcar mascabado": 120, "Chocolate amargo Turín": 165, "Harina de trigo": 190, "Cocoa alcalinizada": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez": 140, "Sal escamas": 1.8},
        "presentaciones": {"Molde 12 piezas": 1},
        "merma": 1.0,
        "procedimiento": ["Mantequilla color avellana", "No montar huevos", "175°C por 22-26 min"]
    }
}

# --- RELLENOS, LÁGRIMAS Y ACABADOS ---
EXTRAS = {
    "Ninguno": {"unitario": 0, "receta": {}},
    "Schmear Canela (Gourmet)": {"unitario": 13.4, "receta": {"Mantequilla": 200, "Azúcar Mascabado": 300, "Canela": 25, "Maicena": 20, "Sal": 3}},
    "Schmear Roles Red Velvet": {"unitario": 15, "receta": {"Mantequilla": 6, "Azúcar": 6, "Cacao": 1.8, "Maicena": 0.6, "Nuez": 4, "Chocolate": 4}},
    "Lágrima Vainilla (Concha)": {"unitario": 30, "receta": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100}},
    "Lágrima Chocolate (Concha)": {"unitario": 30, "receta": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100}},
    "Lágrima Mazapán (Intenso)": {"unitario": 30, "receta": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66}},
    "Crema Pastelera Vainilla": {"unitario": 80, "receta": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Vainilla": 6}},
    "Inclusión: Frutos Rojos (Earl Grey)": {"unitario": 8, "receta": {"Pasas+Arándanos": 8, "Té Earl Grey": 2, "Vainilla": 0.5}},
    "Inclusión: Manzana (Orejón)": {"unitario": 8, "receta": {"Orejón Manzana": 8, "Agua tibia": 2}},
    "Inclusión: Nuez Tostada": {"unitario": 4, "receta": {"Nuez Pecana": 4}},
    "Glaseado Clásico (Vainilla)": {"unitario": 10, "receta": {"Azúcar Glass": 200, "Leche": 30, "Vainilla": 5, "Sal": 0.5}},
    "Glaseado Turín (Costra)": {"unitario": 28, "receta": {"Azúcar Glass": 36, "Chocolate Turín (Cuerpos)": 18, "Leche": 9, "Conejo Turín (Cabeza)": 1}},
    "Rebozado Muerto Tradicional": {"unitario": 1, "receta": {"Mantequilla (baño)": 6.5, "Azúcar (rebozo)": 12.5, "Ralladura naranja": 0.25}},
    "Nappage Chabacano (Brillo)": {"unitario": 5, "receta": {"Mermelada Chabacano": 150, "Jugo Naranja": 30}},
    "Doradura Real (Brillo Huevo)": {"unitario": 3, "receta": {"Huevo": 50, "Yema": 20, "Crema batir": 15, "Azúcar": 1, "Sal": 1}}
}

if 'plan' not in st.session_state: st.session_state.plan = []

tabs = st.tabs(["📋 Plan de Producción", "🥣 Hojas de Trabajo", "🛒 Lista Maestra"])

with tabs[0]:
    st.subheader("Configurar Pedido del Día")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: m_sel = st.selectbox("Masa Base", list(MASAS.keys()))
    with col2: t_sel = st.selectbox("Presentación", list(MASAS[m_sel]["presentaciones"].keys()))
    with col3: cant = st.number_input("Cantidad", min_value=1, value=1)
    with col4: r_sel = st.selectbox("Relleno/Schmear", list(EXTRAS.keys()))
    with col5: a_sel = st.selectbox("Acabado/Inclusión", list(EXTRAS.keys()))
    
    if st.button("➕ Añadir a Producción"):
        st.session_state.plan.append({"masa": m_sel, "tamaño": t_sel, "cant": cant, "extra1": r_sel, "extra2": a_sel})

    if st.session_state.plan:
        st.write("---")
        st.table(pd.DataFrame(st.session_state.plan))
        if st.button("🗑️ Limpiar Plan"): st.session_state.plan = []

compras = {}

if st.session_state.plan:
    with tabs[1]:
        for item in st.session_state.plan:
            m = MASAS[item['masa']]
            st.header(f"Receta: {item['masa']} ({item['tamaño']})")
            
            if "fijo" in m:
                for ing, val in m['fijo'].items():
                    total = val * item['cant']
                    st.write(f"• {ing}: **{total:,.1f}g**")
                    compras[ing] = compras.get(ing, 0) + total
            else:
                p_u = m['presentaciones'][item['tamaño']]
                m_total = (p_u * item['cant']) / m['merma']
                h_total = (m_total * 100) / (sum(m['ingredientes'].values()) + (7 if m['tangzhong'] else 0))
                
                col_m, col_s = st.columns(2)
                with col_m:
                    st.subheader("🥣 Masa Principal")
                    for ing, porc in m['ingredientes'].items():
                        peso = (porc * h_total) / 100
                        st.write(f"• {ing}: **{peso:,.1f}g**")
                        compras[ing] = compras.get(ing, 0) + peso
                with col_s:
                    if m['tangzhong']:
                        st.subheader("⚡ Tangzhong")
                        tz_h = h_total * m['tangzhong']['ratio_harina_total']
                        tz_l = tz_h * m['tangzhong']['relacion_liquido']
                        st.warning(f"Harina: {tz_h:,.1f}g | Leche: {tz_l:,.1f}g")
                        compras["Harina de fuerza"] = compras.get("Harina de fuerza", 0) + tz_h
                        compras["Leche entera"] = compras.get("Leche entera", 0) + tz_l
                    if "huesos_reforzados" in m:
                        reserva = m_total * 0.25
                        st.info(f"🦴 Huesos: Reforzar {reserva:,.1f}g masa con {reserva*0.3:,.1f}g harina y {reserva*0.1:,.1f}g yema.")
                        compras["Harina de fuerza"] = compras.get("Harina de fuerza", 0) + (reserva*0.3)
                        compras["Yemas"] = compras.get("Yemas", 0) + (reserva*0.1)

            for ex_name in [item['extra1'], item['extra2']]:
                if ex_name != "Ninguno":
                    ex = EXTRAS[ex_name]
                    st.subheader(f"✨ {ex_name}")
                    p_target = 10 if "Mini" in item['tamaño'] and "Lágrima" in ex_name else ex['unitario']
                    p_ex_total = p_target * item['cant']
                    if ex['receta']:
                        factor = p_ex_total / sum([v for v in ex['receta'].values() if isinstance(v, (int, float))])
                        for ing, val in ex['receta'].items():
                            p = val * factor if isinstance(val, (int, float)) else val * item['cant']
                            st.write(f"• {ing}: {p:,.1f}g" if isinstance(p, (int, float)) else f"• {ing}: {p} pzas")
                            compras[ing] = compras.get(ing, 0) + p
            st.divider()

    with tabs[2]:
        st.header("🛒 Lista Maestra de Insumos")
        df_c = pd.DataFrame(compras.items(), columns=["Ingrediente", "Total"])
        st.dataframe(df_c.sort_values("Ingrediente"), use_container_width=True)
