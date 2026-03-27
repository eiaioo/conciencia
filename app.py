import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN DE MEMORIA (ESTADOS)
# ==========================================
if 'master_comanda' not in st.session_state: st.session_state.master_comanda = []
if 'carrito_temp' not in st.session_state: st.session_state.carrito_temp = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0

st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

# Estilo Claro de Alto Contraste para Cocina
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3, h4, p, span, label { color: #000000 !important; font-weight: 500; }
    div[data-testid="stExpander"] { border: 2px solid #EEEEEE !important; border-radius: 10px; }
    .stButton > button { border-radius: 8px; font-weight: bold; background-color: #F0F2F6; border: 1px solid #CCCCCC; height: 3em; }
    .etapa-box { padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #DDD; color: #000 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS TÉCNICA MAESTRA
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1)},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5)},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_f": (70, 350)},
    "Masa Muerto": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True}
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Ruby 50/50": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Cuerpos": 100, "Leche": 50, "Cabeza de Conejo": 1},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar": 300, "Canela": 25},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5}
}

CATALOGO = {
    "Conchas": {"esp": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán", "Oreo", "Pinole"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas"},
    "Rosca de reyes": {"esp": ["Tradicional", "Chocolate", "Turín"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rel_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "m": "Masa Brioche Rosca"},
    "Berlinas": {"esp": ["Ruby v2.0", "Vainilla", "Chocolate"], "tam": {"Estándar": 60}, "m": "Masa de Berlinas", "p_man": {"Ruby v2.0": 70}},
    "Rollos": {"esp": ["Canela", "Manzana", "Red Velvet"], "tam": {"Individual": 90}, "m": "Masa Brioche Roles"},
    "Pan de muerto": {"esp": ["Tradicional", "Guayaba"], "tam": {"Estándar": 85}, "m": "Masa Muerto"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA (CERO BORRADOS)
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.container():
    col_c1, col_c2 = st.columns(2)
    # Vinculamos directamente a session_state para que no se borre al refrescar
    cli_n = col_c1.text_input("Nombre del Cliente", key="input_nombre")
    cli_w = col_c2.text_input("WhatsApp (10 dígitos)", key="input_whatsapp")

st.write("### 🍞 Seleccionar Panes")
fk = st.session_state.form_key
c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1, 0.8])

f_sel = c1.selectbox("Familia", ["-"] + list(CATALOGO.keys()), key=f"f_{fk}")
if f_sel != "-":
    e_sel = c2.selectbox("Especialidad", CATALOGO[f_sel]["esp"], key=f"e_{fk}")
    t_sel = c3.selectbox("Tamaño", list(CATALOGO[f_sel]["tam"].keys()), key=f"t_{fk}")
    c_sel = c4.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    c5.write("##")
    if c5.button("➕"):
        st.session_state.carrito_temp.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "can": c_sel})
        st.session_state.form_key += 1 # Solo resetea los selectores de pan
        st.rerun()

# VISTA DEL CARRITO ACTUAL
if st.session_state.carrito_temp:
    st.info(f"🛒 Pedido actual para: **{cli_n}**")
    for it in st.session_state.carrito_temp:
        st.write(f"- {it['can']}x {it['fam']} {it['esp']} ({it['tam']})")
    
    if st.button("✅ GUARDAR PEDIDO Y FINALIZAR CLIENTE"):
        if cli_n:
            st.session_state.master_comanda.append({
                "cliente": cli_n, "whatsapp": cli_w, "items": st.session_state.carrito_temp.copy()
            })
            st.session_state.carrito_temp = []
            st.session_state.input_nombre = "" # Aquí sí limpiamos el nombre
            st.session_state.input_whatsapp = ""
            st.rerun()
        else: st.error("Escribe el nombre del cliente")

# ==========================================
# 4. MOTOR DE RESUMEN Y PRODUCCIÓN
# ==========================================

if st.session_state.master_comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}

    # Agrupar items por Masa
    for ped in st.session_state.master_comanda:
        for it in ped['items']:
            m_id = CATALOGO[it['fam']]["m"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(CATALOGO[i['fam']].get("p_ber_man", {}).get(i['esp'], CATALOGO[i['fam']]['tam'][i['tam']]) * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
