import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema Maestro Conciencia", layout="wide")
st.title("🥐 Sistema de Producción Integral - CONCIENCIA")

# --- BASE DE DATOS TÉCNICA CONSOLIDADA ---
MASAS = {
    "Masa de Conchas": {
        "ingredientes": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0},
        "presentaciones": {"Estándar (95g)": 95, "Mini (35g)": 35},
        "merma": 1.0,
        "tangzhong": None,
        "procedimiento": ["Autólisis 20 min (harina, huevo, leche)", "Levadura + Vainilla", "Azúcar en 3 tandas", "Mantequilla en bloques"]
    },
    "Pan de Muerto Tradicional": {
        "ingredientes": {"Harina panificable": 100, "Leche": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla": 25, "Sal": 2.0, "Levadura fresca": 3.0, "Agua de azahar": 2.0, "Ralladura de naranja": 1.0},
        "presentaciones": {"Pieza Tradicional (85g)": 85},
        "merma": 1.0,
        "tangzhong": None,
        "procedimiento": ["1. Mezcla inicial: Harina + leche + levadura + huevos.", "2. Amasar 5–8 min; agregar azúcar en 2 partes.", "3. Incorporar mantequilla poco a poco.", "4. Agregar sal, azahar y ralladura al final."]
    },
    "Pan de Muerto (Guayaba)": {
        "ingredientes": {"Harina de fuerza": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura fresca": 5.0, "Sal": 1.8, "Polvo de guayaba": 5.0},
        "presentaciones": {"Pieza Guayaba (95g)": 95},
        "merma": 1.0,
        "tangzhong": None,
        "huesos_reforzados": {"harina_extra_porc": 0.30, "yema_extra_porc": 0.10, "reserva_masa_porc": 0.25},
        "procedimiento": ["1. Mezcla base sin grasa.", "2. Integrar polvo de guayaba tras hidratación inicial.", "3. Mantequilla en tandas y sal al final."]
    },
    "Masa de Berlinas": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo entero": 25, "Leche entera": 22, "Sal": 1.8, "Levadura seca": 1.0},
        "presentaciones": {"Pieza 60g": 60},
        "merma": 0.85, 
        "tangzhong": {"ratio_harina": 0.05, "relacion_liquido": 5},
        "procedimiento": ["Preparar Tangzhong 1:5", "Amasar hasta 70% gluten antes de azúcar", "Fritura 172°C"]
    },
    "Masa Roles Red Velvet": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura instantánea": 1.0, "Cacao": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3},
        "presentaciones": {"Rol Individual (90g)": 90},
        "merma": 1.0,
        "tangzhong": {"ratio_harina": 0.07, "relacion_liquido": 5},
        "procedimiento": ["Tangzhong 1:5", "Colorante en fase líquida", "No buscar sobrevelo extremo"]
    },
    "Masa Brioche (EXCLUSIVA ROSCA)": {
        "ingredientes": {"Harina de fuerza": 100, "Azúcar refinada": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo entero": 20, "Yema adicional": 4, "Leche entera": 24, "Levadura seca": 0.35, "Sal": 2.2, "Ralladuras": 1.1, "Agua de azahar": 0.6},
        "presentaciones": {"Rosca Mediana (900g)": 900, "Pieza Individual (100g)": 100},
        "merma": 1.0,
        "tangzhong": {"ratio_harina": 0.025, "relacion_liquido": 1},
        "procedimiento": ["Tangzhong 1:1", "Reposo en bloque extendido 12h a 4°C"]
    },
    "Brownie (Batch 20x20)": {
        "fijo": {"Mantequilla (avellana)": 330, "Azúcar blanca": 275, "Azúcar mascabado": 120, "Chocolate amargo Turín": 165, "Harina de trigo": 190, "Cocoa alcalinizada": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez": 140, "Sal escamas": 1.8},
        "presentaciones": {"Molde 12 piezas": 1},
        "merma": 1.0,
        "procedimiento": ["Avellanar mantequilla", "Mezclar con chocolate caliente", "Añadir azúcares", "Huevos sin montar"]
    }
}

EXTRAS = {
    "Ninguno": {"unitario": 0, "receta": {}},
    # --- LÁGRIMAS DE CONCHA (Basado en harina=100) ---
    "Lágrima Vainilla (Base)": {"unitario": 30, "receta": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100}},
    "Lágrima Chocolate": {"unitario": 30, "receta": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100}},
    "Lágrima Matcha": {"unitario": 30, "receta": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100}},
    "Lágrima Fresa (Nesquik)": {"unitario": 30, "receta": {"Harina": 100, "Azúcar Glass": 79, "Nesquik Fresa": 21, "Mantequilla": 100}},
    "Lágrima Mazapán (Estándar)": {"unitario": 30, "receta": {"Harina": 100, "Azúcar Glass": 92, "Mantequilla": 83, "Mazapán": 25}},
    "Lágrima Mazapán (Intenso)": {"unitario": 30, "receta": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66}},
    "Lágrima Oreo": {"unitario": 30, "receta": {"Harina": 100, "Azúcar Glass": 75, "Mantequilla": 100, "Oreo": 25}},
    "Lágrima Pinole": {"unitario": 30, "receta": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100}},
    # --- RELLENOS Y ACABADOS ---
    "Crema Pastelera Vainilla": {"unitario": 80, "receta": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Vainilla": 6}},
    "Crema Pastelera Chocolate Amargo": {"unitario": 80, "receta": {"Leche": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Chocolate 60%": 120, "Mantequilla": 30}},
    "Crema Pastelera Choco-Leche Turín": {"unitario": 80, "receta": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Chocolate Turín": 120, "Mantequilla": 20}},
    "Glaseado Ruby": {"unitario": 8, "receta": {"Chocolate Ruby": 80, "Azúcar glass": 160, "Leche": 50}},
    "Glaseado Chocolate Turín": {"unitario": 16, "receta": {"Azúcar glass": 40, "Chocolate Turín": 20, "Leche": 12}},
    "Schmear Roles Red Velvet": {"unitario": 15, "receta": {"Mantequilla": 6, "Azúcar": 6, "Cacao": 1.8, "Maicena": 0.6, "Nuez": 4, "Chocolate": 4}},
    "Rebozado Muerto Tradicional": {"unitario": 1, "receta": {"Mantequilla (baño)": 6.5, "Azúcar (rebozo)": 12.5, "Ralladura naranja": 0.25}}
}

if 'plan' not in st.session_state: st.session_state.plan = []

t1, t2, t3 = st.tabs(["📋 Plan de Producción", "🥣 Hojas de Trabajo", "🛒 Lista Maestra"])

with t1:
    st.subheader("Configuración del Horneado")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: m_sel = st.selectbox("Masa Base", list(MASAS.keys()))
    with c2: t_sel = st.selectbox("Presentación", list(MASAS[m_sel]["presentaciones"].keys()))
    with c3: cant = st.number_input("Cantidad", min_value=1, value=1)
    with c4: r_sel = st.selectbox("Relleno / Schmear", list(EXTRAS.keys()))
    with c5: a_sel = st.selectbox("Lágrima / Acabado", list(EXTRAS.keys()))
    
    if st.button("➕ Añadir a la Lista"):
        st.session_state.plan.append({"masa": m_sel, "tamaño": t_sel, "cant": cant, "extra1": r_sel, "extra2": a_sel})

    if st.session_state.plan:
        st.write("---")
        st.table(pd.DataFrame(st.session_state.plan))
        if st.button("🗑️ Limpiar Todo"): st.session_state.plan = []

compras = {}

if st.session_state.plan:
    with t2:
        for item in st.session_state.plan:
            m = MASAS[item['masa']]
            st.header(f"Producción: {item['masa']} ({item['tamaño']})")
            
            if "fijo" in m:
                for ing, val in m['fijo'].items():
                    total = val * item['cant']
                    st.write(f"• {ing}: **{total:,.1f}g**")
                    compras[ing] = compras.get(ing, 0) + total
            else:
                peso_u = m['presentaciones'][item['tamaño']]
                masa_total = (peso_u * item['cant']) / m['merma']
                h_base = (masa_total * 100) / sum(m['ingredientes'].values())
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🥣 Masa")
                    for ing, porc in m['ingredientes'].items():
                        peso = (porc * h_base) / 100
                        st.write(f"• {ing}: **{peso:,.1f}g**")
                        compras[ing] = compras.get(ing, 0) + peso
                with col2:
                    if m['tangzhong']:
                        tz_h = h_base * m['tangzhong']['ratio_harina']
                        st.warning(f"⚡ Tangzhong: {tz_h:,.1f}g Harina | {tz_h*m['tangzhong']['relacion_liquido']:,.1f}g Leche")
                    if "huesos_reforzados" in m:
                        reserva = masa_total * 0.25
                        st.info(f"🦴 Huesos: Reforzar {reserva:,.1f}g masa con {reserva*0.3:,.1f}g harina y {reserva*0.1:,.1f}g yema.")
                        compras["Harina de fuerza"] = compras.get("Harina de fuerza", 0) + (reserva*0.3)
                        compras["Yemas"] = compras.get("Yemas", 0) + (reserva*0.1)

            # Lógica de Extras (Lágrimas automáticas por tamaño)
            for ex_name in [item['extra1'], item['extra2']]:
                if ex_name != "Ninguno":
                    ex = EXTRAS[ex_name]
                    st.subheader(f"✨ {ex_name}")
                    # Auto-ajuste de peso de lágrima
                    peso_target = ex['unitario']
                    if "Lágrima" in ex_name:
                        peso_target = 10 if "Mini" in item['tamaño'] else 30
                    
                    peso_ex_total = peso_target * item['cant']
                    if ex['receta']:
                        factor = peso_ex_total / sum(ex['receta'].values()) if "Rebozado" not in ex_name else item['cant']
                        for ing, val in ex['receta'].items():
                            p = val * factor
                            st.write(f"• {ing}: {p:,.1f}g")
                            compras[ing] = compras.get(ing, 0) + p
            st.divider()

    with t3:
        st.header("🛒 Lista Maestra")
        df_c = pd.DataFrame(compras.items(), columns=["Ingrediente", "Gramos Totales"])
        st.dataframe(df_c.sort_values("Ingrediente"), use_container_width=True)
