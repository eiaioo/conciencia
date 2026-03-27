import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE UI - AUDITORÍA AGRESIVA DE COLOR
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Paleta de Colores Auditada
if st.session_state.tema_oscuro:
    BG_HEX = "#0E1117"
    SEC_BG = "#161B22"
    TEXT_HEX = "#C9D1D9"
    BORDER_HEX = "#30363D"
    BTN_HEX = "#21262D"
    ACCENT = "#E67E22"
    INPUT_FOCUS = "#1F6FEB"
else:
    BG_HEX = "#F6F8FA"
    SEC_BG = "#FFFFFF"
    TEXT_HEX = "#24292F"
    BORDER_HEX = "#D0D7DE"
    BTN_HEX = "#F3F4F6"
    ACCENT = "#D35400"
    INPUT_FOCUS = "#0969DA"

# Inyección de CSS para control total de componentes
st.markdown(f"""
    <style>
    /* 1. Fondo Global y Texto */
    .stApp {{ background-color: {BG_HEX}; color: {TEXT_HEX}; }}
    
    /* 2. Selectores y Dropdowns (Eliminar fondos blancos y bordes) */
    div[data-baseweb="select"] > div {{
        background-color: {SEC_BG} !important;
        color: {TEXT_HEX} !important;
        border: 1px solid {BORDER_HEX} !important;
    }}
    /* Lista que se despliega (Dropdown list) */
    ul[role="listbox"] {{
        background-color: {SEC_BG} !important;
        border: 1px solid {BORDER_HEX} !important;
    }}
    li[role="option"] {{
        background-color: {SEC_BG} !important;
        color: {TEXT_HEX} !important;
    }}
    li[role="option"]:hover {{
        background-color: {BORDER_HEX} !important;
    }}

    /* 3. Inputs de Número y Texto */
    div[data-baseweb="input"], input {{
        background-color: {SEC_BG} !important;
        color: {TEXT_HEX} !important;
        border-color: {BORDER_HEX} !important;
    }}
    div[data-testid="stNumberInput"] button {{
        background-color: {BTN_HEX} !important;
        color: {TEXT_HEX} !important;
        border: 1px solid {BORDER_HEX} !important;
    }}

    /* 4. Cabeceras de Pedido (Expanders) */
    div[data-testid="stExpander"] {{
        background-color: {SEC_BG} !important;
        border: 1px solid {BORDER_HEX} !important;
    }}
    div[data-testid="stExpander"] summary {{ color: {TEXT_HEX} !important; }}

    /* 5. Tabs (Pestañas) */
    button[data-baseweb="tab"] {{ color: {TEXT_HEX} !important; }}
    button[aria-selected="true"] {{ border-bottom-color: {ACCENT} !important; color: {ACCENT} !important; }}

    /* 6. Botones Principales */
    .stButton>button {{
        background-color: {BTN_HEX} !important;
        color: {TEXT_HEX} !important;
        border: 1px solid {BORDER_HEX} !important;
        border-radius: 6px;
    }}
    .stButton>button:hover {{ border-color: {ACCENT} !important; color: {ACCENT} !important; }}

    /* 7. Checklist */
    .stCheckbox label {{ color: {TEXT_HEX} !important; }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN DE TEMA
_, c_t2 = st.columns([0.94, 0.06])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS TÉCNICA (INTEGRAL)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "merma": 1.0, "SOP": ["Autólisis 20m", "Desarrollo", "Mantequilla final"]},
    "Masa de Berlinas": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0, "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5, "SOP": ["TZ 1:5 frío", "Fritura 172°C"]},
    "Masa Brioche Roles": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17, "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350, "SOP": ["TZ 1:5 frío", "DDT 24°C"]},
    "Masa Red Velvet": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao": 0.8, "Rojo": 0.7, "merma": 1.0, "tz_ratio": 0.07, "tz_liq": 5, "SOP": ["Colorante en líquidos"]},
    "Masa Brioche Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1, "SOP": ["TZ 1:1", "Bloque 12h"]},
    "Masa Muerto Tradicional": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3, "merma": 1.0, "SOP": ["Naranja y Azahar al final"]},
    "Masa Muerto Guayaba": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5, "merma": 1.0, "huesos_refuerzo": True, "SOP": ["Polvo Guayaba post-hidratación"]},
    "Mezcla Brownie": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "fijo": True, "SOP": ["Brown Butter", "No montar huevos"]}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "Mantequilla sin sal": 16},
    "Crema Especial Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla sin sal": 20},
    "Glaseado Ruby": {"Choco Ruby": 80, "Azúcar Glass": 160, "Leche entera": 50},
    "Glaseado Turin": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche": 50, "Cabeza de Conejo": 1},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar": 300, "Canela": 25},
    "Schmear Red Velvet": {"Mantequilla sin sal": 6, "Azúcar": 6, "Cacao": 1.8, "Nuez": 4, "Choco amargo": 4},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2},
    "Inclusión Manzana": {"Orejón de Manzana": 8, "Agua tibia": 2},
    "Decoración Tradicional Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Berlinas": {"espec": {"Ruby v2.0": ["Crema Ruby 50/50", "Glaseado Ruby"], "Turín": ["Crema Especial Turin", "Glaseado Turin"], "Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas", "p_ber": {"Ruby v2.0": (70, {"Crema Ruby": 40, "Glaseado Ruby": 8}), "Turín": (60, {"Crema Turin": 80, "Glaseado Turin": 16}), "Vainilla": (60, {"Crema Vainilla": 80})}},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"], "Manzana": ["Schmear Canela", "Inclusión Manzana"], "Red Velvet": ["Schmear Red Velvet"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "masa_ov": {"Red Velvet": "Masa Red Velvet"}},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Tradicional Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate"]}, "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Especial Turin"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rel_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Pan de muerto": {"espec": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto"]}, "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}},
    "Brownies": {"espec": {"Turín": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla de Brownies"}
}

# ==========================================
# 2. CAPTURA
# ==========================================

st.subheader("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=len(st.session_state.carrito_actual) == 0):
    fk_c = st.session_state.form_key
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre", key=f"cn_{fk_c}")
    cli_w = c2.text_input("WhatsApp", key=f"cw_{fk_c}")

st.write("### 🍞 2. Carrito")
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
    st.info(f"🛒 Carrito: {cli_n}")
    cb1, cb2 = st.columns(2)
    if cb1.button("✅ GUARDAR PEDIDO"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []; st.session_state.form_key += 1; st.rerun()
    if cb2.button("❌ Cancelar"): st.session_state.carrito_actual = []; st.rerun()

# ==========================================
# 3. PRODUCCIÓN (BATCHES)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🛒 Lista Maestra"])
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
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            
            c_masa, c_comp = st.columns([0.3, 0.7])
            with c_masa:
                st.info(f"**Masa ({m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
                if "tz_ratio" in m_dna:
                    th = h_base*m_dna['tz_ratio']; master_inv["Harina de fuerza"] = master_inv.get("Harina de fuerza",0)+th; master_inv["Leche entera"] = master_inv.get("Leche entera",0)+th*m_dna['tz_liq']
            with c_comp:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']}) — {it['cliente']}**")
                    cfg = ARBOL[it['fam']]
                    list_subs = []
                    base_espec = cfg["espec"][it['esp']]
                    if isinstance(base_espec, dict): list_subs = base_espec["fijos"].copy()
                    else: list_subs = base_espec.copy()
                    if it.get('rel') not in ["N/A", "Sin Relleno", None]: list_subs.append(it['rel'])
                    for s_id in list_subs:
                        if s_id not in DB_COMPLEMENTOS: continue
                        p_u = cfg.get("p_rel_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']
                        st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            g_s = val_s * fact; st.write(f"- {ing_s}: {g_s:,.1f}g"); master_inv[ing_s] = master_inv.get(ing_s, 0) + g_s
            st.divider()

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            res_txt = ", ".join([f"{it['cant']} {it['esp']}" for it in ped['items']])
            st.write(f"👤 **{ped['cliente']}** — {res_txt}")
            if st.button("❌", key=f"f_del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_sup:
        st.header("🛒 Lista Maestra")
        for insumo, cant in sorted(master_inv.items()):
            st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"master_{insumo}")
