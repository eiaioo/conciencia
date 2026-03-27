import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN DE VARIABLES
# ==========================================
if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0
if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'cli_n' not in st.session_state: st.session_state.cli_n = ""
if 'cli_w' not in st.session_state: st.session_state.cli_w = ""

# ==========================================
# 2. DISEÑO VISUAL (MODO MATE)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

C_BG = "#0E1117" if st.session_state.tema_oscuro else "#F0F2F6"
C_SEC = "#161B22" if st.session_state.tema_oscuro else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.tema_oscuro else "#1F2328"
C_BRD = "#30363D" if st.session_state.tema_oscuro else "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    div[data-testid="stExpander"], .streamlit-expanderHeader, .streamlit-expanderContent {{
        background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important;
    }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {C_BG} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important;
    }}
    div[data-testid="stNumberInput"] button {{ background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important; }}
    .stButton > button {{ background-color: {C_SEC} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important; border-radius: 8px; }}
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; font-weight: 500; }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.9, 0.1])
if c_tema.button("☀️/🌙"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 3. BASE DE DATOS TÉCNICA
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2}, "merma": 1.0, "tz": (0.025, 1), "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor", "i": ["Azúcar", "Miel", "Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8}, "merma": 0.85, "tz": (0.05, 5)},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1}, "merma": 1.0},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Chocolate": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima de Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Ruby": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar": 300, "Canela": 25}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Ruby v2.0": ["Crema Ruby"]}, "tamaños": {"Estándar": 70}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": {"Guayaba": ["Lágrima de Vainilla"]}, "tamaños": {"Estándar": 95}, "masa": "Masa Muerto Guayaba"},
    "Brownies": {"espec": {"Turín": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 4. INTERFAZ DE CAPTURA
# ==========================================

st.subheader("🥐 Comanda Técnica CONCIENCIA")

with st.container():
    c1, c2 = st.columns(2)
    st.session_state.cli_n = c1.text_input("Nombre", value=st.session_state.cli_n)
    st.session_state.cli_w = c2.text_input("WhatsApp", value=st.session_state.cli_w)

st.write("### 🍞 Agregar Panes")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,0.8])

fam_sel = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if fam_sel != "-":
    e_opts = list(ARBOL[fam_sel]["espec"].keys()) if isinstance(ARBOL[fam_sel]["espec"], dict) else ARBOL[fam_sel]["espec"]
    esp_sel = col2.selectbox("Especialidad", e_opts, key=f"e_{fk}")
    tam_sel = col3.selectbox("Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()), key=f"t_{fk}")
    can_sel = col4.number_input("Cant.", min_value=1, value=1, key=f"c_{fk}")
    
    rel_sel = "N/A"
    if fam_sel == "Rosca de reyes":
        rel_sel = st.selectbox("Relleno", ARBOL[fam_sel]["espec"][esp_sel]["rellenos"], key=f"r_{fk}")
    
    if col5.button("➕", key=f"add_btn_{fk}"):
        st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rel": rel_sel, "can": can_sel})
        st.session_state.form_key += 1
        st.rerun()

# --- NUEVA SECCIÓN: VISUALIZACIÓN DEL CARRITO ---
if st.session_state.carrito:
    st.markdown(f"#### 🛒 Revisión para: {st.session_state.cli_n}")
    
    # Creamos una lista limpia para mostrar al usuario
    df_carro = pd.DataFrame(st.session_state.carrito)
    df_carro.columns = ["Familia", "Sabor", "Tamaño", "Relleno", "Cant."]
    st.table(df_carro) # st.table es más limpio visualmente que st.dataframe
    
    cc1, cc2 = st.columns(2)
    if cc1.button("✅ FINALIZAR Y GUARDAR PEDIDO", use_container_width=True):
        if st.session_state.cli_n:
            st.session_state.comanda.append({"cliente": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()
        else: st.error("Ingresa el nombre del cliente")
    if cc2.button("🗑️ Vaciar Carrito Actual", use_container_width=True):
        st.session_state.carrito = []; st.rerun()

# ==========================================
# 5. MOTOR DE PRODUCCIÓN
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    master_inv = {}
    lotes_masa = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']].get("masa_ov", ARBOL[it['fam']]["masa"])
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cliente'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) for it in items])
            h_base = (m_batch_gr * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id}")
            c_masa, c_comp = st.columns([0.3, 0.7])
            with c_masa:
                st.info(f"Masa ({m_batch_gr:,.1f}g)")
                for k, v in m_dna['receta'].items():
                    gr = v*h_base/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c_comp:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}")

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            c1, c2 = st.columns([0.8, 0.2])
            c1.write(f"👤 **{ped['cliente']}** — WhatsApp: {ped['wa']}")
            if c2.button("❌ Borrar", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna.get("etapas", []):
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"master_{k}")

    if st.button("🗑️ LIMPIAR TODA LA PRODUCCIÓN"): st.session_state.comanda = []; st.rerun()
