import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DISEÑO (BLINDAJE TOTAL)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

# Inicialización de estados con nombres definitivos
if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# --- LIMPIEZA DE DATOS INCOMPATIBLES (EVITA EL CUADRO ROJO) ---
if st.session_state.comanda:
    test_item = st.session_state.comanda[0]
    if 'items' not in test_item: # Si el formato es viejo, reseteamos
        st.session_state.comanda = []
        st.session_state.carrito = []

# Colores Mate Profesionales
if st.session_state.tema == "Oscuro":
    B_APP, B_CARD, T_MAIN, B_BRD, B_INPUT = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#1C2128"
    B_ACC = "#E67E22"
else:
    B_APP, B_CARD, T_MAIN, B_BRD, B_INPUT = "#F0F2F6", "#FFFFFF", "#1F2328", "#D0D7DE", "#FFFFFF"
    B_ACC = "#D35400"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {B_APP} !important; color: {T_MAIN} !important; }}
    h1, h2, h3, h4, p, span, label, div {{ color: {T_MAIN} !important; }}
    
    /* ELIMINAR BARRAS BLANCAS Y CABECERAS */
    div[data-testid="stExpander"], .streamlit-expanderHeader, summary, details {{
        background-color: {B_CARD} !important;
        border: 1px solid {B_BRD} !important;
        color: {T_MAIN} !important;
    }}
    
    /* INPUTS, SELECTORES Y NÚMEROS OSCUROS */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input, select {{
        background-color: {B_APP} !important;
        color: {T_MAIN} !important;
        border: 1px solid {B_BRD} !important;
    }}
    div[data-baseweb="popover"], ul[role="listbox"] {{
        background-color: {B_CARD} !important;
        border: 1px solid {B_BRD} !important;
    }}
    li[role="option"] {{ background-color: {B_CARD} !important; color: {T_MAIN} !important; }}
    li[role="option"]:hover {{ background-color: {B_BRD} !important; }}

    /* BOTONES MATE */
    .stButton > button {{
        background-color: {B_CARD} !important;
        color: {T_MAIN} !important;
        border: 1px solid {B_BRD} !important;
        border-radius: 8px;
    }}
    
    /* ETAPAS (OPACIDAD 30%) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #1a1a1a !important; font-weight: 500;
    }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_t = st.columns([0.9, 0.1])
if c_t.button("☀️/🌙"):
    st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA (DNA COMPLETO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1), "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor y Grasa", "i": ["Azúcar", "Miel", "Mantequilla sin sal", "Sal fina", "Agua Azahar", "Levadura"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Mezcla Única", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Sal fina", "Levadura seca"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(168, 230, 173, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Masa Guayaba", "i": ["Harina de fuerza", "Polvo Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Chocolate Turin": 165, "Harina de fuerza": 190, "Nuez": 140, "Sal fina": 8}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima de Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "c": "rgba(255, 179, 140, 0.3)"},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "c": "rgba(168, 230, 173, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "c": "rgba(212, 163, 115, 0.3)"},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25, "c": "rgba(183, 183, 164, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}, "Turín": {"fijos": ["Lágrima de Chocolate"], "rellenos": ["Sin Relleno", "Crema Ruby 50/50"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Ruby v2.0": ["Crema Ruby 50/50"]}, "tamaños": {"Estándar": 70}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": {"Guayaba": ["Lágrima de Vainilla"]}, "tamaños": {"Estándar": 95}, "masa": "Masa Muerto Guayaba"},
    "Brownies": {"espec": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla de Brownies"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA (CARRITO)
# ==========================================

st.header("🥐 Comanda Técnica CONCIENCIA")

with st.container():
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre del Cliente", key="cli_name_persist")
    cli_w = c2.text_input("WhatsApp (10 dígitos)", key="cli_wa_persist")

st.write("### 🍞 Agregar Panes")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,0.8])

f_sel = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if f_sel != "-":
    e_sel = col2.selectbox("Especialidad", list(ARBOL[f_sel]["espec"].keys()), key=f"e_{fk}")
    t_sel = col3.selectbox("Tamaño", list(ARBOL[f_sel]["tamaños"].keys()), key=f"t_{fk}")
    c_sel = col4.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    rel_sel = "N/A"
    if f_sel == "Rosca de reyes":
        rel_sel = st.selectbox("Relleno", ARBOL[f_sel]["espec"][e_sel]["rellenos"], key=f"r_{fk}")
    
    if col5.button("➕"):
        st.session_state.carrito.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "rel": rel_sel, "can": c_sel})
        st.session_state.form_key += 1
        st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito: {cli_n}")
    if st.button("✅ FINALIZAR PEDIDO"):
        if cli_n:
            st.session_state.pedidos.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PRODUCCIÓN (RESUMEN + DETALLE)
# ==========================================

if st.session_state.pedidos:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}
    lotes_comp = {}

    for ped in st.session_state.pedidos:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)
            
            # Recolectar complementos
            cfg = ARBOL[it['fam']]
            lista = cfg["espec"][it['esp']]
            lista_final = lista["fijos"].copy() if isinstance(lista, dict) else lista.copy()
            if it['rel'] not in ["N/A", "Sin Relleno"]: lista_final.append(it['rel'])
            
            for s_id in lista_final:
                p_u = cfg.get("p_rell_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_tot = sum([(ARBOL[i['fam']]['tamaños'][i['tam']] * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_tot * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Batido: {m_id} ({m_tot:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items: st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")

    with t_cli:
        for i, p in enumerate(st.session_state.pedidos):
            c1, c2 = st.columns([0.8, 0.2])
            c1.write(f"👤 **{p['cliente']}**")
            u = f"https://wa.me/521{p['wa']}?text=" + urllib.parse.quote("Hola! Tu pedido está listo.")
            c2.link_button("🚀 WhatsApp", u)
            if st.button("❌", key=f"d_{i}"): st.session_state.pedidos.pop(i); st.rerun()

    with t_prod:
        st.subheader("🥣 Masas")
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"**Lote: {m_id}**")
            for etapa in m_dna.get("etapas", []):
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("✨ Complementos")
        for s_id, p_tot in lotes_comp.items():
            s_rec = DB_COMPLEMENTOS.get(s_id, {})
            if not s_rec: continue
            st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
            st.markdown(f'<div class="etapa-box" style="background-color: {s_rec.get("c", "rgba(200,200,200,0.3)")};">', unsafe_allow_html=True)
            fact = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
            for sk, sv in s_rec.items():
                if sk == "c": continue
                gr_s = sv * fact
                st.checkbox(f"{sk}: {gr_s:,.1f}g", key=f"sec_{s_id}_{sk}")
                master_inv[sk] = master_inv.get(sk, 0) + gr_s
            st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: {v:,.1f}g", key=f"sup_{k}")

    if st.button("🗑️ LIMPIAR TODO"): st.session_state.pedidos = []; st.rerun()
