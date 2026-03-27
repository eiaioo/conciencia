import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN VISUAL (MODO MATE PROFESIONAL)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'form_id' not in st.session_state: st.session_state.form_id = 0

# Colores Mate Auditados
C_BG = "#0E1117" if st.session_state.tema_oscuro else "#F0F2F6"
C_SEC = "#161B22" if st.session_state.tema_oscuro else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.tema_oscuro else "#1F2328"
C_BRD = "#30363D" if st.session_state.tema_oscuro else "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG}; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    /* Eliminar barras blancas de expanders */
    div[data-testid="stExpander"], .streamlit-expanderHeader {{
        background-color: {C_SEC} !important;
        border: 1px solid {C_BRD} !important;
        color: {C_TXT} !important;
    }}
    /* Inputs y Selectores */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {C_BG} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
    }}
    /* Etiquetas de Checklist */
    .stCheckbox label p {{ color: {C_TXT} !important; font-size: 1.1rem !important; }}
    /* Cajas de Etapas (30% Opacidad) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        color: #1a1a1a !important; font-weight: 500;
    }}
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
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor y Grasa", "i": ["Azúcar", "Miel", "Mantequilla sin sal", "Sal fina", "Agua Azahar", "Levadura fresca"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5),
        "etapas": [{"n": "Mezcla Única", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina", "Levadura seca"], "c": "rgba(162, 210, 255, 0.3)"}]},
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima de Chocolate": {"Harina": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=not st.session_state.comanda):
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre", key="cli_n_persist")
    cli_w = c2.text_input("WhatsApp", key="cli_w_persist")

with st.container():
    st.write("### 🍞 2. Seleccionar Panes")
    fk = st.session_state.form_key
    c3, c4, c5, c6 = st.columns([2,2,1.5,1])
    
    fam = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if fam != "-":
        esp = c4.selectbox("Especialidad", list(ARBOL[fam]["espec"].keys()), key=f"e_{fk}")
        tam = c5.selectbox("Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{fk}")
        can = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
        
        rel = "N/A"
        if fam == "Rosca de reyes":
            rel = st.selectbox("Relleno", ARBOL[fam]["espec"][esp]["rellenos"], key=f"r_{fk}")
        
        if st.button("➕ AGREGAR PAN", use_container_width=True):
            st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "can": can})
            st.session_state.form_key += 1
            st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    for p in st.session_state.carrito: st.write(f"• {p['can']}x {p['fam']} {p['esp']}")
    if st.button("✅ GUARDAR PEDIDO FINAL", use_container_width=True):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE CÁLCULO Y PESTAÑAS
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}

    # Procesamiento Central
    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) / m_dna['merma'] for it in items])
            h_base = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id}")
            c_m, c_c = st.columns([0.3, 0.7])
            with c_m:
                st.info(f"Masa Total: {m_batch:,.1f}g")
                for k, v in m_dna['receta'].items():
                    gr = v*h_base/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c_c:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
                    cfg = ARBOL[it['fam']]
                    # Listar subrecetas
                    lista = cfg["espec"][it['esp']]
                    lista = lista["fijos"].copy() if isinstance(lista, dict) else lista.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: lista.append(it['rel'])
                    for s_id in lista:
                        p_u = cfg.get("p_rell_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['can']; st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for sk, sv in s_rec.items():
                            g_s = sv * fact; st.write(f"- {sk}: {g_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + g_s

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            res_txt = ", ".join([f"{it['can']} {it['esp']}" for it in p['items']])
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{p['cliente']}**\n\n{res_txt}")
            wa_url = f"https://wa.me/521{p['wa']}?text="
            c2.link_button("✅ Confirmar", wa_url + urllib.parse.quote(f"Hola {p['cliente']}! Recibimos tu pedido."))
            c3.link_button("🚀 Listo", wa_url + urllib.parse.quote(f"Hola {p['cliente']}! Tu pedido de {res_txt} ya está listo 🥐."))
            if st.button("❌", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) / m_dna['merma'] for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna.get("etapas", []):
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"chk_{m_id}_{ing}_{i}_{etapa['n']}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: {v:,.1f}g", key=f"sup_{k}")
