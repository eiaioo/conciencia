import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN Y BLINDAJE DE DATOS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# Forzar limpieza si hay versiones antiguas para evitar el KeyError
if 'v_check' not in st.session_state:
    st.session_state.clear()
    st.session_state.v_check = "66.0"

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Estilo Claro de Alto Contraste (Cero errores de visibilidad)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3, h4, p, span, label { color: #000000 !important; font-weight: 500; }
    .stButton > button { border-radius: 8px; font-weight: bold; background-color: #F0F2F6; border: 1px solid #CCCCCC; }
    div[data-testid="stExpander"] { border: 1px solid #DDDDDD !important; border-radius: 8px; background-color: #FDFDFD; }
    .etapa-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #DDDDDD; color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS MAESTRA (AUDITADA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5)},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_f": (70, 350)},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1.0, "Cacao": 0.8, "Rojo": 0.7, "Vinagre": 0.3}, "merma": 1.0, "tz": (0.07, 5)},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1)},
    "Masa Muerto": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True},
    "Mezcla Brownie": {"receta": {"Mantequilla": 330, "Azúcar": 275, "Chocolate": 165, "Harina": 190}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Fresa": {"Harina": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla": 100},
    "Lágrima Mazapán": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66},
    "Lágrima Oreo": {"Harina": 100, "Azúcar Glass": 75, "Mantequilla": 100, "Oreo": 25},
    "Lágrima Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Chocolate": {"Leche": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Choco 60%": 120},
    "Crema Turin": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120},
    "Crema Ruby": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Glaseado Turin": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche": 50, "Cabeza": 1},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar": 300, "Canela": 25},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5}
}

CATALOGO = {
    "Conchas": {"esp": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán", "Oreo", "Pinole"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas"},
    "Rosca de reyes": {"esp": ["Tradicional", "Chocolate", "Turín"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rel_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "m": "Masa Brioche Rosca"},
    "Berlinas": {"esp": ["Vainilla", "Chocolate", "Ruby v2.0"], "tam": {"Estándar": 60}, "m": "Masa de Berlinas", "p_ber_man": {"Ruby v2.0": 70}},
    "Rollos": {"esp": ["Canela", "Manzana", "Red Velvet"], "tam": {"Individual": 90}, "m": "Masa Brioche Roles", "m_ov": {"Red Velvet": "Masa Red Velvet"}},
    "Pan de muerto": {"esp": ["Tradicional", "Guayaba"], "tam": {"Estándar": 85}, "m": "Masa Muerto"},
    "Brownies": {"esp": ["Turín"], "tam": {"Molde 20x20": 1}, "m": "Mezcla Brownie"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    c1, c2 = st.columns(2)
    cli_nombre = c1.text_input("Nombre del Cliente", key="input_cli_n")
    cli_whatsapp = c2.text_input("WhatsApp", key="input_cli_w")

st.write("### 🍞 2. Seleccionar Panes")
fk = st.session_state.form_key
c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1, 0.6])

f_sel = c3.selectbox("Familia", ["-"] + list(CATALOGO.keys()), key=f"f_{fk}")
if f_sel != "-":
    e_sel = c4.selectbox("Especialidad", CATALOGO[f_sel]["esp"], key=f"e_{fk}")
    t_sel = c5.selectbox("Tamaño", list(CATALOGO[f_sel]["tam"].keys()), key=f"t_{fk}")
    c_sel = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    c7.write("##")
    if c7.button("➕", key=f"add_{fk}"):
        st.session_state.carrito.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "can": c_sel})
        st.session_state.form_key += 1
        st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Pedido actual para: {cli_nombre}")
    for it in st.session_state.carrito:
        st.write(f"- {it['can']}x {it['fam']} {it['esp']} ({it['tam']})")
    if st.button("✅ GUARDAR PEDIDO Y FINALIZAR"):
        if cli_nombre:
            st.session_state.comanda.append({"cliente": cli_nombre, "wa": cli_whatsapp, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []
            st.rerun()

# ==========================================
# 4. MOTOR DE PRODUCCIÓN (BATCHES)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            masa_id = CATALOGO[it['fam']].get("m_ov", {}).get(it['esp'], CATALOGO[it['fam']]["m"])
            if masa_id not in lotes_masa: lotes_masa[masa_id] = []
            it_con_cli = it.copy(); it_con_cli['cliente'] = ped['cliente']; lotes_masa[masa_id].append(it_con_cli)

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            # Calculo de masa total
            m_batch = 0
            for i in items:
                p_u_m = CATALOGO[i['fam']].get("p_ber_man", {}).get(i['esp'], CATALOGO[i['fam']]['tam'][i['tam']])
                m_batch += (p_u_m * i['can']) / m_dna['merma']
            
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            col_m, col_p = st.columns([0.3, 0.7])
            with col_m:
                st.info("Ingredientes Masa")
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with col_p:
                for it in items: st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}")

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{p['cliente']}**")
            u = f"https://wa.me/521{p['wa']}?text="
            c2.link_button("✅ Confirmar", u + "Recibido")
            c3.link_button("🚀 Listo", u + "Listo!")
            if st.button("❌", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"sup_{k}")

    if st.button("🗑️ LIMPIAR TODO EL DÍA"): st.session_state.comanda = []; st.rerun()
