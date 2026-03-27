import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE UI - CONTROL TOTAL DE CSS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Paleta Auditada (Gris Carbón y Acero)
if st.session_state.tema_oscuro:
    BG, SEC, TXT, BRD, BTN = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#21262D"
    ACC = "#E67E22"
else:
    BG, SEC, TXT, BRD, BTN = "#FFFFFF", "#F0F2F6", "#262730", "#DEE2E6", "#E0E0E0"
    ACC = "#D35400"

st.markdown(f"""
    <style>
    /* 1. Reset Global */
    .stApp {{ background-color: {BG} !important; color: {TXT} !important; }}
    
    /* 2. Forzar todos los Labels (Texto de arriba de los campos) */
    [data-testid="stWidgetLabel"] p, label, .stMarkdown p {{
        color: {TXT} !important;
        font-weight: 500 !important;
    }}

    /* 3. Bloqueo de Barras Blancas en Expanders */
    div[data-testid="stExpander"] {{
        background-color: {SEC} !important;
        border: 1px solid {BRD} !important;
    }}
    .streamlit-expanderHeader {{
        background-color: {SEC} !important;
        color: {TXT} !important;
        border-bottom: 1px solid {BRD} !important;
    }}

    /* 4. Selectores y Menús Flotantes (Auditado) */
    div[data-baseweb="select"] > div {{
        background-color: {BG} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
    }}
    /* Esto quita el fondo blanco de la lista que aparece al dar click */
    div[data-baseweb="popover"] > div, ul[role="listbox"] {{
        background-color: {SEC} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
    }}
    li[role="option"] {{
        background-color: {SEC} !important;
        color: {TXT} !important;
    }}
    li[role="option"]:hover {{ background-color: {BRD} !important; }}

    /* 5. Casilla de Cantidad (Number Input) */
    div[data-testid="stNumberInput"] > div {{
        background-color: {BG} !important;
        border: 1px solid {BRD} !important;
    }}
    div[data-testid="stNumberInput"] input {{ color: {TXT} !important; }}
    div[data-testid="stNumberInput"] button {{
        background-color: {BTN} !important;
        border: none !important;
        color: {TXT} !important;
    }}

    /* 6. Botones Generales */
    .stButton>button {{
        background-color: {BTN} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
        border-radius: 8px;
    }}

    /* 7. Pestañas (Tabs) */
    button[data-baseweb="tab"] {{ color: {TXT} !important; opacity: 0.6; }}
    button[aria-selected="true"] {{ color: {ACC} !important; border-bottom-color: {ACC} !important; opacity: 1; }}

    /* 8. Estilo de Etapas */
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN TEMA
_, c_t2 = st.columns([0.94, 0.06])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS COMPLETA (Auditada)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7}, "merma": 1.0, "tz": (0.07, 5), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2}, "merma": 1.0, "tz": (0.025, 1), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Muerto Tradicional": {"receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3}, "merma": 1.0, "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Polvo Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True, "etapas": [{"n": "Batch Fijo", "i": ["Mantequilla sin sal", "Azúcar Blanca", "Chocolate Turin Amargo"], "c": "rgba(162, 210, 255, 0.3)"}]}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar": 300, "Canela": 25},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "masa_ov": {"Red Velvet": "Masa Red Velvet"}},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rel_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Pan de muerto": {"espec": {"Tradicional": []}, "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}},
    "Brownies": {"espec": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 2. CAPTURA DE PEDIDO (LÓGICA PERSISTENTE)
# ==========================================

st.subheader("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    fk_c = st.session_state.form_key
    c1, c2 = st.columns(2)
    st.session_state.cli_n = c1.text_input("Nombre", value=st.session_state.get('cli_n',''), key=f"cli_n_{fk_c}")
    st.session_state.cli_w = c2.text_input("WhatsApp", value=st.session_state.get('cli_w',''), key=f"cli_w_{fk_c}")

st.write("### 🍞 2. Carrito")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,0.8])

with col1: f_sel = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
with col2: e_sel = st.selectbox("Especialidad", list(ARBOL[f_sel]["espec"].keys()) if f_sel != "-" else ["-"], key=f"e_{fk}")
with col3: t_sel = st.selectbox("Tamaño", list(ARBOL[f_sel]["tamaños"].keys()) if f_sel != "-" else ["-"], key=f"t_{fk}")
with col4: c_sel = st.number_input("Cant.", min_value=1, value=1, key=f"c_{fk}")

r_sel = "N/A"
if f_sel == "Rosca de reyes" and e_sel != "-":
    r_sel = st.selectbox("Relleno", ARBOL[f_sel]["espec"][e_sel]["rellenos"], key=f"r_{fk}")

with col5:
    st.write("##")
    if st.button("➕"):
        if f_sel != "-" and e_sel != "-" and t_sel != "-":
            st.session_state.carrito_actual.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "rel": r_sel, "cant": c_sel})
            st.session_state.form_key += 1; st.rerun()

if st.session_state.carrito_actual:
    st.info(f"🛒 Pedido Actual: {st.session_state.cli_n}")
    if st.button("✅ FINALIZAR Y GUARDAR"):
        if st.session_state.cli_n:
            st.session_state.comanda.append({"cliente": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()

# ==========================================
# 3. LÓGICA DE PRODUCCIÓN
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
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) for it in items])
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            st.markdown(f"#### 🛠️ Lote: {m_id}")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info(f"Masa ({m_batch_gr:,.1f}g)")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['cant']}x {it['esp']} ({it['tam']}) — {it['cliente']}")
                    cfg = ARBOL[it['fam']]
                    list_subs = cfg["espec"][it['esp']]
                    if isinstance(list_subs, dict): list_subs = list_subs["fijos"].copy()
                    else: list_subs = list_subs.copy()
                    if it.get('rel') not in ["N/A", "Sin Relleno", None]: list_subs.append(it['rel'])
                    for s_id in list_subs:
                        p_u = cfg.get("p_rel_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            g_s = val_s * fact; master_inv[ing_s] = master_inv.get(ing_s, 0) + g_s

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            st.write(f"👤 **{ped['cliente']}** — {ped['wa']}")
            if st.button("❌", key=f"f_del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna["etapas"]:
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for insumo, cant in sorted(master_inv.items()):
            st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"master_{insumo}")import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE UI - CONTROL TOTAL DE CSS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Paleta Auditada (Gris Carbón y Acero)
if st.session_state.tema_oscuro:
    BG, SEC, TXT, BRD, BTN = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#21262D"
    ACC = "#E67E22"
else:
    BG, SEC, TXT, BRD, BTN = "#FFFFFF", "#F0F2F6", "#262730", "#DEE2E6", "#E0E0E0"
    ACC = "#D35400"

st.markdown(f"""
    <style>
    /* 1. Reset Global */
    .stApp {{ background-color: {BG} !important; color: {TXT} !important; }}
    
    /* 2. Forzar todos los Labels (Texto de arriba de los campos) */
    [data-testid="stWidgetLabel"] p, label, .stMarkdown p {{
        color: {TXT} !important;
        font-weight: 500 !important;
    }}

    /* 3. Bloqueo de Barras Blancas en Expanders */
    div[data-testid="stExpander"] {{
        background-color: {SEC} !important;
        border: 1px solid {BRD} !important;
    }}
    .streamlit-expanderHeader {{
        background-color: {SEC} !important;
        color: {TXT} !important;
        border-bottom: 1px solid {BRD} !important;
    }}

    /* 4. Selectores y Menús Flotantes (Auditado) */
    div[data-baseweb="select"] > div {{
        background-color: {BG} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
    }}
    /* Esto quita el fondo blanco de la lista que aparece al dar click */
    div[data-baseweb="popover"] > div, ul[role="listbox"] {{
        background-color: {SEC} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
    }}
    li[role="option"] {{
        background-color: {SEC} !important;
        color: {TXT} !important;
    }}
    li[role="option"]:hover {{ background-color: {BRD} !important; }}

    /* 5. Casilla de Cantidad (Number Input) */
    div[data-testid="stNumberInput"] > div {{
        background-color: {BG} !important;
        border: 1px solid {BRD} !important;
    }}
    div[data-testid="stNumberInput"] input {{ color: {TXT} !important; }}
    div[data-testid="stNumberInput"] button {{
        background-color: {BTN} !important;
        border: none !important;
        color: {TXT} !important;
    }}

    /* 6. Botones Generales */
    .stButton>button {{
        background-color: {BTN} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
        border-radius: 8px;
    }}

    /* 7. Pestañas (Tabs) */
    button[data-baseweb="tab"] {{ color: {TXT} !important; opacity: 0.6; }}
    button[aria-selected="true"] {{ color: {ACC} !important; border-bottom-color: {ACC} !important; opacity: 1; }}

    /* 8. Estilo de Etapas */
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN TEMA
_, c_t2 = st.columns([0.94, 0.06])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS COMPLETA (Auditada)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7}, "merma": 1.0, "tz": (0.07, 5), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2}, "merma": 1.0, "tz": (0.025, 1), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Muerto Tradicional": {"receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3}, "merma": 1.0, "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Polvo Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True, "etapas": [{"n": "Batch Fijo", "i": ["Mantequilla sin sal", "Azúcar Blanca", "Chocolate Turin Amargo"], "c": "rgba(162, 210, 255, 0.3)"}]}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar": 300, "Canela": 25},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "masa_ov": {"Red Velvet": "Masa Red Velvet"}},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rel_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Pan de muerto": {"espec": {"Tradicional": []}, "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}},
    "Brownies": {"espec": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 2. CAPTURA DE PEDIDO (LÓGICA PERSISTENTE)
# ==========================================

st.subheader("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    fk_c = st.session_state.form_key
    c1, c2 = st.columns(2)
    st.session_state.cli_n = c1.text_input("Nombre", value=st.session_state.get('cli_n',''), key=f"cli_n_{fk_c}")
    st.session_state.cli_w = c2.text_input("WhatsApp", value=st.session_state.get('cli_w',''), key=f"cli_w_{fk_c}")

st.write("### 🍞 2. Carrito")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,0.8])

with col1: f_sel = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
with col2: e_sel = st.selectbox("Especialidad", list(ARBOL[f_sel]["espec"].keys()) if f_sel != "-" else ["-"], key=f"e_{fk}")
with col3: t_sel = st.selectbox("Tamaño", list(ARBOL[f_sel]["tamaños"].keys()) if f_sel != "-" else ["-"], key=f"t_{fk}")
with col4: c_sel = st.number_input("Cant.", min_value=1, value=1, key=f"c_{fk}")

r_sel = "N/A"
if f_sel == "Rosca de reyes" and e_sel != "-":
    r_sel = st.selectbox("Relleno", ARBOL[f_sel]["espec"][e_sel]["rellenos"], key=f"r_{fk}")

with col5:
    st.write("##")
    if st.button("➕"):
        if f_sel != "-" and e_sel != "-" and t_sel != "-":
            st.session_state.carrito_actual.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "rel": r_sel, "cant": c_sel})
            st.session_state.form_key += 1; st.rerun()

if st.session_state.carrito_actual:
    st.info(f"🛒 Pedido Actual: {st.session_state.cli_n}")
    if st.button("✅ FINALIZAR Y GUARDAR"):
        if st.session_state.cli_n:
            st.session_state.comanda.append({"cliente": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()

# ==========================================
# 3. LÓGICA DE PRODUCCIÓN
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
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) for it in items])
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            st.markdown(f"#### 🛠️ Lote: {m_id}")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info(f"Masa ({m_batch_gr:,.1f}g)")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['cant']}x {it['esp']} ({it['tam']}) — {it['cliente']}")
                    cfg = ARBOL[it['fam']]
                    list_subs = cfg["espec"][it['esp']]
                    if isinstance(list_subs, dict): list_subs = list_subs["fijos"].copy()
                    else: list_subs = list_subs.copy()
                    if it.get('rel') not in ["N/A", "Sin Relleno", None]: list_subs.append(it['rel'])
                    for s_id in list_subs:
                        p_u = cfg.get("p_rel_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            g_s = val_s * fact; master_inv[ing_s] = master_inv.get(ing_s, 0) + g_s

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            st.write(f"👤 **{ped['cliente']}** — {ped['wa']}")
            if st.button("❌", key=f"f_del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna["etapas"]:
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for insumo, cant in sorted(master_inv.items()):
            st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"master_{insumo}")import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE UI - CONTROL TOTAL DE CSS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Paleta Auditada (Gris Carbón y Acero)
if st.session_state.tema_oscuro:
    BG, SEC, TXT, BRD, BTN = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#21262D"
    ACC = "#E67E22"
else:
    BG, SEC, TXT, BRD, BTN = "#FFFFFF", "#F0F2F6", "#262730", "#DEE2E6", "#E0E0E0"
    ACC = "#D35400"

st.markdown(f"""
    <style>
    /* 1. Reset Global */
    .stApp {{ background-color: {BG} !important; color: {TXT} !important; }}
    
    /* 2. Forzar todos los Labels (Texto de arriba de los campos) */
    [data-testid="stWidgetLabel"] p, label, .stMarkdown p {{
        color: {TXT} !important;
        font-weight: 500 !important;
    }}

    /* 3. Bloqueo de Barras Blancas en Expanders */
    div[data-testid="stExpander"] {{
        background-color: {SEC} !important;
        border: 1px solid {BRD} !important;
    }}
    .streamlit-expanderHeader {{
        background-color: {SEC} !important;
        color: {TXT} !important;
        border-bottom: 1px solid {BRD} !important;
    }}

    /* 4. Selectores y Menús Flotantes (Auditado) */
    div[data-baseweb="select"] > div {{
        background-color: {BG} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
    }}
    /* Esto quita el fondo blanco de la lista que aparece al dar click */
    div[data-baseweb="popover"] > div, ul[role="listbox"] {{
        background-color: {SEC} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
    }}
    li[role="option"] {{
        background-color: {SEC} !important;
        color: {TXT} !important;
    }}
    li[role="option"]:hover {{ background-color: {BRD} !important; }}

    /* 5. Casilla de Cantidad (Number Input) */
    div[data-testid="stNumberInput"] > div {{
        background-color: {BG} !important;
        border: 1px solid {BRD} !important;
    }}
    div[data-testid="stNumberInput"] input {{ color: {TXT} !important; }}
    div[data-testid="stNumberInput"] button {{
        background-color: {BTN} !important;
        border: none !important;
        color: {TXT} !important;
    }}

    /* 6. Botones Generales */
    .stButton>button {{
        background-color: {BTN} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
        border-radius: 8px;
    }}

    /* 7. Pestañas (Tabs) */
    button[data-baseweb="tab"] {{ color: {TXT} !important; opacity: 0.6; }}
    button[aria-selected="true"] {{ color: {ACC} !important; border-bottom-color: {ACC} !important; opacity: 1; }}

    /* 8. Estilo de Etapas */
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN TEMA
_, c_t2 = st.columns([0.94, 0.06])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS COMPLETA (Auditada)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7}, "merma": 1.0, "tz": (0.07, 5), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2}, "merma": 1.0, "tz": (0.025, 1), "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Muerto Tradicional": {"receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3}, "merma": 1.0, "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Única", "i": ["Harina de fuerza", "Polvo Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True, "etapas": [{"n": "Batch Fijo", "i": ["Mantequilla sin sal", "Azúcar Blanca", "Chocolate Turin Amargo"], "c": "rgba(162, 210, 255, 0.3)"}]}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar": 300, "Canela": 25},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "masa_ov": {"Red Velvet": "Masa Red Velvet"}},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rel_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Pan de muerto": {"espec": {"Tradicional": []}, "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}},
    "Brownies": {"espec": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 2. CAPTURA DE PEDIDO (LÓGICA PERSISTENTE)
# ==========================================

st.subheader("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    fk_c = st.session_state.form_key
    c1, c2 = st.columns(2)
    st.session_state.cli_n = c1.text_input("Nombre", value=st.session_state.get('cli_n',''), key=f"cli_n_{fk_c}")
    st.session_state.cli_w = c2.text_input("WhatsApp", value=st.session_state.get('cli_w',''), key=f"cli_w_{fk_c}")

st.write("### 🍞 2. Carrito")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,0.8])

with col1: f_sel = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
with col2: e_sel = st.selectbox("Especialidad", list(ARBOL[f_sel]["espec"].keys()) if f_sel != "-" else ["-"], key=f"e_{fk}")
with col3: t_sel = st.selectbox("Tamaño", list(ARBOL[f_sel]["tamaños"].keys()) if f_sel != "-" else ["-"], key=f"t_{fk}")
with col4: c_sel = st.number_input("Cant.", min_value=1, value=1, key=f"c_{fk}")

r_sel = "N/A"
if f_sel == "Rosca de reyes" and e_sel != "-":
    r_sel = st.selectbox("Relleno", ARBOL[f_sel]["espec"][e_sel]["rellenos"], key=f"r_{fk}")

with col5:
    st.write("##")
    if st.button("➕"):
        if f_sel != "-" and e_sel != "-" and t_sel != "-":
            st.session_state.carrito_actual.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "rel": r_sel, "cant": c_sel})
            st.session_state.form_key += 1; st.rerun()

if st.session_state.carrito_actual:
    st.info(f"🛒 Pedido Actual: {st.session_state.cli_n}")
    if st.button("✅ FINALIZAR Y GUARDAR"):
        if st.session_state.cli_n:
            st.session_state.comanda.append({"cliente": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()

# ==========================================
# 3. LÓGICA DE PRODUCCIÓN
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
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) for it in items])
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            st.markdown(f"#### 🛠️ Lote: {m_id}")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info(f"Masa ({m_batch_gr:,.1f}g)")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['cant']}x {it['esp']} ({it['tam']}) — {it['cliente']}")
                    cfg = ARBOL[it['fam']]
                    list_subs = cfg["espec"][it['esp']]
                    if isinstance(list_subs, dict): list_subs = list_subs["fijos"].copy()
                    else: list_subs = list_subs.copy()
                    if it.get('rel') not in ["N/A", "Sin Relleno", None]: list_subs.append(it['rel'])
                    for s_id in list_subs:
                        p_u = cfg.get("p_rel_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            g_s = val_s * fact; master_inv[ing_s] = master_inv.get(ing_s, 0) + g_s

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            st.write(f"👤 **{ped['cliente']}** — {ped['wa']}")
            if st.button("❌", key=f"f_del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna["etapas"]:
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for insumo, cant in sorted(master_inv.items()):
            st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"master_{insumo}")
