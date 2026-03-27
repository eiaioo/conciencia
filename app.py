import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN VISUAL (MODO MATE TOTAL)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

C_BG = "#0E1117" if st.session_state.tema_oscuro else "#F0F2F6"
C_SEC = "#161B22" if st.session_state.tema_oscuro else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.tema_oscuro else "#1F2328"
C_BRD = "#30363D" if st.session_state.tema_oscuro else "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    
    /* Eliminar barra blanca de expanders y cabeceras */
    div[data-testid="stExpander"], .streamlit-expanderHeader, .streamlit-expanderContent {{
        background-color: {C_SEC} !important;
        border: 1px solid {C_BRD} !important;
        color: {C_TXT} !important;
    }}
    
    /* Inputs, Selectores y Number Inputs */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {C_BG} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
    }}
    div[data-testid="stNumberInput"] button {{ background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important; }}

    /* Botones de acción */
    .stButton > button {{
        background-color: {C_SEC} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
        border-radius: 8px;
    }}
    .stButton > button:hover {{ border-color: #E67E22 !important; color: #E67E22 !important; }}

    /* Recuadros de Producción (Etapas) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #1a1a1a !important; font-weight: 500;
    }}
    .etapa-titulo {{ font-weight: bold; text-transform: uppercase; font-size: 0.8rem; color: rgba(0,0,0,0.6) !important; margin-bottom: 5px; }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.9, 0.1])
if c_tema.button("🌙" if st.session_state.tema_oscuro else "☀️"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor y Grasa", "i": ["Azúcar", "Miel", "Mantequilla sin sal", "Levadura", "Sal fina", "Agua Azahar"], "c": "rgba(107, 112, 92, 0.3)"}]},
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "col": "rgba(168, 230, 173, 0.3)"},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "col": "rgba(162, 210, 255, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "col": "rgba(255, 179, 140, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "col": "rgba(212, 163, 115, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.header("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre", key="cli_n_persist")
    cli_w = c2.text_input("WhatsApp", key="cli_w_persist")

st.write("### 🍞 2. Agregar Panes")
fk = st.session_state.form_key
c3, c4, c5, c6 = st.columns([2,2,1.5,1])
fam = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if fam != "-":
    esp = c4.selectbox("Especialidad", list(ARBOL[fam]["espec"].keys()), key=f"e_{fk}")
    tam = c5.selectbox("Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{fk}")
    can = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    rel = "N/A"
    if fam == "Rosca de reyes": rel = st.selectbox("Relleno", ARBOL[fam]["espec"][esp]["rellenos"], key=f"r_{fk}")
    
    if st.button("➕ AÑADIR PAN"):
        st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "can": can})
        st.session_state.form_key += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    if st.button("✅ GUARDAR PEDIDO FINAL"):
        if cli_n:
            st.session_state.comanda.append({"cli": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PRODUCCIÓN (BATCHES)
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}
    lotes_complementos = {} # {id_extra: gramos_totales}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cli']; lotes_masa[m_id].append(it_c)
            
            # Recolectar complementos para el batch de producción
            cfg = ARBOL[it['fam']]
            subs = cfg["espec"][it['esp']]
            lista_subs = subs["fijos"].copy() if isinstance(subs, dict) else subs.copy()
            if it['rel'] not in ["N/A", "Sin Relleno"]: lista_subs.append(it['rel'])
            
            for s_id in lista_subs:
                p_u = cfg.get("p_rell_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                lotes_complementos[s_id] = lotes_complementos.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            for it in items: st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
            st.divider()

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            res_txt = ", ".join([f"{it['can']} {it['esp']}" for it in p['items']])
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{p['cli']}**\n\n{res_txt}")
            u_wa = f"https://wa.me/521{p['wa']}?text="
            c2.link_button("✅ Confirmar", u_wa + urllib.parse.quote("Confirmado!"))
            c3.link_button("🚀 Listo", u_wa + urllib.parse.quote("Listo!"))
            if st.button("❌", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        st.subheader("🥣 Batidos de Masa")
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"**Lote: {m_id} ({m_batch:,.1f}g)**")
            for etapa in m_dna.get("etapas", []):
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                    master_inv[ing] = master_inv.get(ing, 0) + gr
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("✨ Preparación de Complementos")
        for s_id, p_tot in lotes_complementos.items():
            s_rec = DB_COMPLEMENTOS[s_id]
            st.markdown(f"**{s_id} (Total a preparar: {p_tot:,.1f}g)**")
            st.markdown(f'<div class="etapa-box" style="background-color: {s_rec["col"]};">', unsafe_allow_html=True)
            fact = p_tot / sum([v for k,v in s_rec.items() if k != "col"])
            for sk, sv in s_rec.items():
                if sk == "col": continue
                gr_s = sv * fact
                st.checkbox(f"{sk}: {gr_s:,.1f}g", key=f"sec_{s_id}_{sk}")
                master_inv[sk] = master_inv.get(sk, 0) + gr_s
            st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"master_{k}")
