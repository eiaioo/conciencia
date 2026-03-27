import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DISEÑO (TEMA MATE)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'f_id' not in st.session_state: st.session_state.f_id = 0
if 'dark' not in st.session_state: st.session_state.dark = True

# Paleta Profesional
C_BG = "#0E1117" if st.session_state.dark else "#F0F2F6"
C_SEC = "#161B22" if st.session_state.dark else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.dark else "#1F2328"
C_BRD = "#30363D" if st.session_state.dark else "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    div[data-testid="stExpander"], .streamlit-expanderHeader {{ background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important; }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{ background-color: {C_BG} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important; }}
    div[data-testid="stNumberInput"] button {{ background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important; }}
    .stButton > button {{ background-color: {C_SEC} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important; border-radius: 8px; }}
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; font-weight: 500; }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.9, 0.1])
if c_tema.button("☀️/🌙"):
    st.session_state.dark = not st.session_state.dark
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA MAESTRA
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar", "Levadura fresca"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Roles Master", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(168, 230, 173, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Masa Guayaba", "i": ["Harina de fuerza", "Polvo de Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla": 330, "Azúcar Blanca": 275, "Mascabado": 120, "Chocolate Turin": 165, "Harina": 190}, "merma": 1.0, "fijo": True}
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
    "Crema Turin": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120},
    "Crema Ruby": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar": 300, "Canela": 25}
}

ARBOL = {
    "Conchas": {"espec": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán", "Oreo", "Pinole"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas"},
    "Rosca de reyes": {"espec": ["Tradicional", "Turín"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "m": "Masa Brioche Rosca"},
    "Berlinas": {"espec": ["Vainilla", "Ruby v2.0"], "tam": {"Estándar": 60}, "m": "Masa de Berlinas", "p_man": {"Ruby v2.0": 70}},
    "Rollos": {"espec": ["Canela"], "tam": {"Individual": 90}, "m": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": ["Guayaba"], "tam": {"Estándar": 95}, "m": "Masa Muerto Guayaba"},
    "Brownies": {"espec": ["Turín"], "tam": {"Molde 20x20": 1}, "m": "Mezcla Brownie"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=not st.session_state.comanda):
    c1, c2 = st.columns(2)
    nombre_cli = c1.text_input("Nombre", key="cli_n")
    whatsapp_cli = c2.text_input("WhatsApp", key="cli_w")

st.write("### 🍞 2. Agregar Panes")
fk = st.session_state.f_id
c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1, 0.8])

fam = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if fam != "-":
    esp = c4.selectbox("Especialidad", ARBOL[fam]["espec"], key=f"e_{fk}")
    tam = c5.selectbox("Tamaño", list(ARBOL[fam]["tam"].keys()), key=f"t_{fk}")
    can = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    rel = "N/A"
    if fam == "Rosca de reyes":
        rel = st.selectbox("Relleno", ["Sin Relleno", "Crema Vainilla", "Crema Ruby"], key=f"r_{fk}")
    
    c7.write("##")
    if c7.button("➕"):
        st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "can": can, "rel": rel})
        st.session_state.f_id += 1
        st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {nombre_cli}")
    if st.button("✅ GUARDAR PEDIDO COMPLETO"):
        if nombre_cli:
            st.session_state.comanda.append({"cli": nombre_cli, "wa": whatsapp_cli, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []
            st.rerun()

# ==========================================
# 4. MOTOR DE PRODUCCIÓN
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}
    lotes_comp = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["m"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cliente'] = ped['cli']; lotes_masa[m_id].append(it_c)
            
            # Complementos
            subs = []
            if it['fam'] == "Conchas": subs.append(f"Lágrima {it['esp']}")
            if it['fam'] == "Rosca de reyes": subs.append("Decoración Rosca"); 
            if it['rel'] != "Sin Relleno" and it['rel'] != "N/A": subs.append(it['rel'])
            
            for s_id in subs:
                if s_id in DB_COMPLEMENTOS:
                    p_u = ARBOL[it['fam']].get("p_rell_map", {}).get(it['tam'], 15) if s_id == it['rel'] else (ARBOL[it['fam']].get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15)
                    lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']].get("p_man", {}).get(it['esp'], ARBOL[it['fam']]['tam'][it['tam']]) * it['can']) / m_dna['merma'] for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            c_izq, c_der = st.columns([0.3, 0.7])
            with c_izq:
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c_der:
                for it in items: st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}")

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{p['cli']}**")
            wa_url = f"https://wa.me/521{p['wa']}?text="
            c2.link_button("✅ Confirmar", wa_url + "Pedido Recibido")
            c3.link_button("🚀 Listo", wa_url + "Tu pan esta listo!")
            if st.button("❌", key=f"d_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.write(f"### 🥣 {m_id}")
            for etapa in m_dna.get("etapas", []):
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    st.checkbox(f"{ing}: {m_dna['receta'][ing]*h_b/100:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"master_{k}")

    if st.button("🗑️ LIMPIAR TODO"): st.session_state.comanda = []; st.rerun()
