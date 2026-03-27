import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE UI - CONTROL TOTAL DE COLOR
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Paleta de Colores
if st.session_state.tema_oscuro:
    BG_GENERAL = "#0E1117"
    BG_TARJETAS = "#161B22"
    TEXTO = "#E6EDF3"
    INPUT_BG = "#0D1117"
    BORDER = "#30363D"
    ACCENT = "#D35400" # Naranja Conciencia
else:
    BG_GENERAL = "#FFFFFF"
    BG_TARJETAS = "#F6F8FA"
    TEXTO = "#1F2328"
    INPUT_BG = "#FFFFFF"
    BORDER = "#D0D7DE"
    ACCENT = "#E67E22"

st.markdown(f"""
    <style>
    /* Fondo principal */
    .stApp {{ background-color: {BG_GENERAL}; color: {TEXTO}; }}
    
    /* Forzar color en Selectores y Entradas de Número */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"], 
    div[data-baseweb="base-input"],
    input {{
        background-color: {INPUT_BG} !important;
        color: {TEXTO} !important;
        border-color: {BORDER} !important;
    }}

    /* Color de los iconos y texto dentro de los selectores */
    div[data-testid="stSelectbox"] svg, 
    div[data-testid="stNumberInput"] button {{
        fill: {TEXTO} !important;
        color: {TEXTO} !important;
    }}

    /* Arreglar Expanders (Barras blancas) */
    .streamlit-expanderHeader {{
        background-color: {BG_TARJETAS} !important;
        color: {TEXTO} !important;
        border-bottom: 1px solid {BORDER} !important;
    }}
    .streamlit-expanderContent {{
        background-color: {BG_TARJETAS} !important;
    }}

    /* Etiquetas de texto arriba de los inputs */
    label, .stMarkdown p {{
        color: {TEXTO} !important;
        font-weight: 600 !important;
    }}

    /* Botón "+" personalizado */
    .stButton>button {{
        width: 100%;
        background-color: {ACCENT} !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        height: 3em;
    }}

    /* Checklist en móvil */
    .stCheckbox {{ align-items: center !important; }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN DE TEMA
_, c_t2 = st.columns([0.94, 0.06])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS TÉCNICA (DNA COMPLETO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(255, 235, 156, 0.6)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(168, 230, 173, 0.6)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.6)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.6)"}],
        "merma": 1.0, "factor": 1.963
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(255, 235, 156, 0.6)"}, {"n": "2. Activación", "i": ["Levadura fresca"], "c": "rgba(168, 230, 173, 0.6)"}, {"n": "3. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": "rgba(162, 210, 255, 0.6)"}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.6)"}],
        "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"}
}

# ==========================================
# 2. INTERFAZ DE CAPTURA
# ==========================================

st.header("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=len(st.session_state.carrito_actual) == 0):
    fk_c = st.session_state.form_key
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre del Cliente", key=f"cn_{fk_c}")
    cli_w = c2.text_input("WhatsApp (10 dígitos)", key=f"cw_{fk_c}")

st.subheader("🍞 2. Carrito de Panes")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,1])

with col1:
    f_sel = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_sel_{fk}")
with col2:
    e_options = list(ARBOL[f_sel]["espec"].keys()) if f_sel != "-" else ["-"]
    e_sel = st.selectbox("Especialidad", e_options, key=f"e_sel_{fk}")
with col3:
    t_options = list(ARBOL[f_sel]["tamaños"].keys()) if f_sel != "-" else ["-"]
    t_sel = st.selectbox("Tamaño", t_options, key=f"t_sel_{fk}")
with col4:
    cant_sel = st.number_input("Cant.", min_value=1, value=1, key=f"c_sel_{fk}")

rel_sel = "N/A"
if f_sel == "Rosca de reyes" and e_sel != "-":
    rel_sel = st.selectbox("Relleno", ARBOL[f_sel]["espec"][e_sel]["rellenos"], key=f"r_sel_{fk}")

with col5:
    st.write("##") # Espaciador
    if st.button("➕"):
        if f_sel != "-" and e_sel != "-" and t_sel != "-":
            st.session_state.carrito_actual.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "rel": rel_sel, "cant": cant_sel})
            st.session_state.form_key += 1
            st.rerun()

# MOSTRAR CARRITO
if st.session_state.carrito_actual:
    st.write(f"---")
    st.markdown(f"🛒 **Pedido para:** {cli_n}")
    for p in st.session_state.carrito_actual:
        st.caption(f"• {p['cant']}x {p['fam']} {p['esp']} ({p['tam']})")
    
    cb1, cb2 = st.columns(2)
    if cb1.button("✅ FINALIZAR Y GUARDAR TODO"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []; st.session_state.form_key += 1; st.rerun()
        else: st.error("Escribe el nombre del cliente")
    if cb2.button("❌ Cancelar"): st.session_state.carrito_actual = []; st.rerun()

# ==========================================
# 3. PESTAÑAS DE TRABAJO (RESTO DE LA LÓGICA)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    master_inv = {}
    lotes_masa = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cliente'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            st.markdown(f"### 🛠️ Lote: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) for it in items])
            h_base = (m_batch_gr * 100) / sum(m_dna['receta'].values())
            c_masa, c_comp = st.columns([0.3, 0.7])
            with c_masa:
                st.info(f"**Masa ({m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
            with c_comp:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']}) — {it['cliente']}**")
                    cfg = ARBOL[it['fam']]
                    # Listar sub-recetas
                    base_espec = cfg["espec"][it['esp']]
                    lista = base_espec["fijos"].copy() if isinstance(base_espec, dict) else base_espec.copy()
                    if it.get('rel') not in ["N/A", "Sin Relleno", None]: lista.append(it['rel'])
                    for s_id in lista:
                        if s_id not in DB_COMPLEMENTOS: continue
                        p_u = cfg["p_relleno_map"][it['tam']] if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']; st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            g_s = val_s * fact; st.write(f"- {ing_s}: {g_s:,.1f}g"); master_inv[ing_s] = master_inv.get(ing_s, 0) + g_s

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            with st.container():
                c1, c2 = st.columns([0.8, 0.2])
                c1.write(f"👤 **{ped['cliente']}** — {len(ped['items'])} panes.")
                if c2.button("❌ Borrar", key=f"f_del_{i}"):
                    st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna["etapas"]:
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("📦 Lista Maestra")
        for insumo, cant in sorted(master_inv.items()):
            st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"master_{insumo}")
