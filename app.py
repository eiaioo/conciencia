import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE UI - AUDITORÍA AGRESIVA
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# Inicialización de estados
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0
if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True

# Paleta Profesional Mate
if st.session_state.tema_oscuro:
    BG_HEX, SEC_BG, TEXT_HEX, BORDER_HEX, BTN_HEX = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#3D4B53"
    ACCENT = "#E67E22"
else:
    BG_HEX, SEC_BG, TEXT_HEX, BORDER_HEX, BTN_HEX = "#F6F8FA", "#FFFFFF", "#24292F", "#D0D7DE", "#E0E0E0"
    ACCENT = "#D35400"

st.markdown(f"""
    <style>
    /* 1. Fondo Global y Textos */
    .stApp {{ background-color: {BG_HEX} !important; color: {TEXT_HEX} !important; }}
    label, p, span, h1, h2, h3, h4, .stMarkdown, .stText {{ color: {TEXT_HEX} !important; }}

    /* 2. ELIMINAR BARRA BLANCA (Expander) */
    div[data-testid="stExpander"] {{
        background-color: {SEC_BG} !important;
        border: 1px solid {BORDER_HEX} !important;
        border-radius: 8px !important;
    }}
    .streamlit-expanderHeader {{
        background-color: {SEC_BG} !important;
        color: {TEXT_HEX} !important;
        border-bottom: 1px solid {BORDER_HEX} !important;
    }}
    .streamlit-expanderContent {{ background-color: {SEC_BG} !important; }}

    /* 3. INPUTS Y SELECTORES (Cero fugas de blanco) */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {BG_HEX} !important; 
        color: {TEXT_HEX} !important; 
        border: 1px solid {BORDER_HEX} !important;
    }}
    
    /* 4. NUMBER INPUT (CANTIDAD) - Estilo Gris Acero */
    div[data-testid="stNumberInput"] {{
        border: 1px solid {BORDER_HEX} !important;
        border-radius: 8px;
        background-color: {BG_HEX} !important;
    }}
    div[data-testid="stNumberInput"] button {{
        background-color: {BTN_HEX} !important;
        border: none !important;
        color: {TEXT_HEX} !important;
    }}
    div[data-testid="stNumberInput"] input {{ border: none !important; }}

    /* 5. BOTONES MATE */
    .stButton>button {{
        background-color: {BTN_HEX} !important;
        color: {TEXT_HEX} !important;
        border: 1px solid {BORDER_HEX} !important;
        border-radius: 8px;
    }}
    .stButton>button:hover {{ border-color: {ACCENT} !important; color: {ACCENT} !important; }}

    /* 6. CAJAS DE ETAPAS (Opacidad 30%) */
    .etapa-box {{ 
        padding: 15px; border-radius: 12px; margin-bottom: 10px; 
        border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; 
    }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN TEMA
_, c_t2 = st.columns([0.94, 0.06])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS COMPLETA
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7}, "merma": 1.0, "tz_ratio": 0.07, "tz_liq": 5},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2}, "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1},
    "Masa Muerto Tradicional": {"receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3}, "merma": 1.0},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Mascabado": 120, "Chocolate": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar": 300, "Canela": 25},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "masa_ov": {"Red Velvet": "Masa Red Velvet"}},
    "Pan de muerto": {"espec": {"Tradicional": []}, "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}},
    "Brownies": {"espec": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 2. INTERFAZ (DATOS PERSISTENTES)
# ==========================================

st.header("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente (Persistentes)", expanded=True):
    c1, c2 = st.columns(2)
    # Estos no usan form_key para que no se borren al añadir panes
    cli_n = c1.text_input("Nombre del Cliente", value=st.session_state.get('last_cli', ''), key="cli_persist")
    cli_w = c2.text_input("WhatsApp", value=st.session_state.get('last_wa', ''), key="wa_persist")

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
            st.session_state.carrito_actual.append({
                "fam": f_sel, "esp": e_sel, "tam": tam_sel if (tam_sel := t_sel) else "Único", 
                "rel": r_sel, "cant": c_sel
            })
            # Guardamos el cliente en memoria antes de refrescar los selectores de pan
            st.session_state.last_cli = cli_n
            st.session_state.last_wa = cli_w
            st.session_state.form_key += 1
            st.rerun()

# MOSTRAR CARRITO Y FINALIZAR
if st.session_state.carrito_actual:
    st.write(f"---")
    st.markdown(f"🛒 **Pedido Actual para:** {cli_n}")
    for p in st.session_state.carrito_actual: st.caption(f"• {p['cant']}x {p['fam']} {p['esp']} ({p['tam']})")
    
    if st.button("✅ FINALIZAR Y GUARDAR PEDIDO COMPLETO", use_container_width=True):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []
            st.session_state.last_cli = "" # Ahora sí borramos los datos del cliente
            st.session_state.last_wa = ""
            st.session_state.form_key += 1
            st.rerun()
        else: st.error("Ingresa el nombre del cliente")

# ==========================================
# 3. PRODUCCIÓN (LÓGICA CONSOLIDADA)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🛒 Súper"])
    master_inv = {}
    lotes_masa = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']].get("masa_ov", ARBOL[it['fam']]["masa"])
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cliente'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            st.markdown(f"#### 🛠️ Lote: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) for it in items])
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            c_masa, c_comp = st.columns([0.3, 0.7])
            with c_masa:
                st.info(f"**Masa ({m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
            with c_comp:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']}) — {it['cliente']}**")
                    cfg = ARBOL[it['fam']]
                    lista = cfg["espec"][it['esp']]
                    lista = lista["fijos"].copy() if isinstance(lista, dict) else lista.copy()
                    if it.get('rel') not in ["N/A", "Sin Relleno", None]: lista.append(it['rel'])
                    for s_id in lista:
                        if s_id not in DB_COMPLEMENTOS: continue
                        p_u = cfg.get("p_rel_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']; st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            g_s = val_s * fact; st.write(f"- {ing_s}: {g_s:,.1f}g"); master_inv[ing_s] = master_inv.get(ing_s, 0) + g_s

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            st.write(f"👤 **{ped['cliente']}** — {ped['wa']}")
            if st.button("❌ Borrar Pedido", key=f"f_del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_sup:
        st.header("🛒 Lista Maestra")
        for insumo, cant in sorted(master_inv.items()):
            st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"master_{insumo}")
