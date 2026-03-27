import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE UI - INTERVENCIÓN PROFUNDA
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Paleta Técnica
if st.session_state.tema_oscuro:
    BG_HEX, SEC_BG, TEXT_HEX, BORDER_HEX, BTN_HEX = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#21262D"
    ACCENT = "#E67E22"
else:
    BG_HEX, SEC_BG, TEXT_HEX, BORDER_HEX, BTN_HEX = "#F6F8FA", "#FFFFFF", "#24292F", "#D0D7DE", "#F3F4F6"
    ACCENT = "#D35400"

st.markdown(f"""
    <style>
    /* Fondo Global */
    .stApp {{ background-color: {BG_HEX} !important; color: {TEXT_HEX} !important; }}
    
    /* Forzar visibilidad de textos y etiquetas */
    label, p, span, h1, h2, h3, h4, .stMarkdown {{ color: {TEXT_HEX} !important; font-weight: 500 !important; }}

    /* Eliminar Barras Blancas en Expanders */
    div[data-testid="stExpander"] {{ background-color: {SEC_BG} !important; border: 1px solid {BORDER_HEX} !important; }}
    .streamlit-expanderHeader {{ background-color: {SEC_BG} !important; color: {TEXT_HEX} !important; }}

    /* Selectores y Menús (Control total de BaseWeb) */
    div[data-baseweb="select"] > div {{ background-color: {BG_HEX} !important; color: {TEXT_HEX} !important; border-color: {BORDER_HEX} !important; }}
    div[data-baseweb="popover"], ul[role="listbox"] {{ background-color: {SEC_BG} !important; border: 1px solid {BORDER_HEX} !important; }}
    li[role="option"] {{ color: {TEXT_HEX} !important; background-color: {SEC_BG} !important; }}
    li[role="option"]:hover {{ background-color: {BORDER_HEX} !important; }}

    /* Inputs de Número y Texto */
    input, div[data-baseweb="input"] {{ background-color: {BG_HEX} !important; color: {TEXT_HEX} !important; border-color: {BORDER_HEX} !important; }}
    div[data-testid="stNumberInput"] button {{ background-color: {BTN_HEX} !important; border-color: {BORDER_HEX} !important; color: {TEXT_HEX} !important; }}

    /* Botones Mate */
    .stButton>button {{ background-color: {BTN_HEX} !important; color: {TEXT_HEX} !important; border: 1px solid {BORDER_HEX} !important; border-radius: 8px; }}
    .stButton>button:hover {{ border-color: {ACCENT} !important; color: {ACCENT} !important; }}

    /* Recuadros de Etapas (Opacidad 30%) */
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; }}
    .etapa-titulo {{ font-weight: bold; text-transform: uppercase; font-size: 0.8rem; color: rgba(0,0,0,0.6) !important; }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN TEMA
_, c_t2 = st.columns([0.94, 0.06])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS TÉCNICA (DNA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(255, 235, 156, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(168, 230, 173, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.3)"}],
        "merma": 1.0
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(255, 235, 156, 0.3)"}, {"n": "2. Fermento", "i": ["Levadura fresca"], "c": "rgba(168, 230, 173, 0.3)"}, {"n": "3. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.3)"}],
        "merma": 1.0, "tz": (0.025, 1)
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "etapas": [{"n": "1. Batido y TZ", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(255, 235, 156, 0.3)"}, {"n": "2. Estructura", "i": ["Azúcar", "Levadura seca", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.3)"}],
        "merma": 0.85, "tz": (0.05, 5)
    },
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Proceso Único", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Muerto Tradicional": {"receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3}, "merma": 1.0, "etapas": [{"n": "Proceso Único", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Proceso Único", "i": ["Harina de fuerza", "Polvo Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True, "etapas": [{"n": "Batch Fijo", "i": ["Mantequilla sin sal", "Azúcar Blanca", "Chocolate Turin Amargo"], "c": "rgba(162, 210, 255, 0.3)"}]}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar": 300, "Canela": 25},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Pan de muerto": {"espec": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto"]}, "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}},
    "Brownies": {"espec": {"Turín": []}, "tamaños": {"Molde 12 pzas": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 2. INTERFAZ
# ==========================================

st.subheader("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=len(st.session_state.carrito_actual) == 0):
    fk_c = st.session_state.form_key
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre", key=f"cn_{fk_c}")
    cli_w = c2.text_input("WhatsApp", key=f"cw_{fk_c}")

st.write("### 🍞 2. Carrito de Panes")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,0.8])

with col1: f_sel = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
with col2:
    e_opts = list(ARBOL[f_sel]["espec"].keys()) if f_sel != "-" else ["-"]
    e_sel = st.selectbox("Especialidad", e_opts, key=f"e_{fk}")
with col3:
    t_opts = list(ARBOL[f_sel]["tamaños"].keys()) if f_sel != "-" else ["-"]
    t_sel = st.selectbox("Tamaño", t_opts, key=f"t_{fk}")
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
    st.info(f"🛒 Pedido actual para {cli_n}")
    cb1, cb2 = st.columns(2)
    if cb1.button("✅ FINALIZAR Y GUARDAR"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []; st.session_state.form_key += 1; st.rerun()
    if cb2.button("❌ Cancelar"): st.session_state.carrito_actual = []; st.rerun()

# ==========================================
# 3. PRODUCCIÓN (BATCHES)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    master_inv = {}
    lotes_masa = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']].get("masa_ov", {}).get(it['esp'], ARBOL[it['fam']]['masa'])
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cliente'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            st.markdown(f"#### 🛠️ Lote: {m_id}")
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
                    base_espec = cfg["espec"][it['esp']]
                    lista = base_espec["fijos"].copy() if isinstance(base_espec, dict) else base_espec.copy()
                    if it.get('rel') not in ["N/A", "Sin Relleno", None]: lista.append(it['rel'])
                    for s_id in lista:
                        if s_id not in DB_COMPLEMENTOS: continue
                        p_u = cfg.get("p_relleno_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']; st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values()); 
                        for ing_s, val_s in s_rec.items():
                            g_s = val_s * fact; st.write(f"- {ing_s}: {g_s:,.1f}g"); master_inv[ing_s] = master_inv.get(ing_s, 0) + g_s

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            res_txt = ", ".join([f"{it['cant']} {it['esp']}" for it in ped['items']])
            st.write(f"👤 **{ped['cliente']}** — {res_txt}")
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
            if st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"master_{insumo}"): pass
