import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DISEÑO (BLINDAJE VISUAL)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'f_key' not in st.session_state: st.session_state.f_key = 0

# Colores Profesionales Mate
if st.session_state.tema == "Oscuro":
    C_BG, C_SEC, C_TXT, C_BRD = "#0E1117", "#161B22", "#E6EDF3", "#30363D"
    C_ACC = "#E67E22"
else:
    C_BG, C_SEC, C_TXT, C_BRD = "#F8F9FA", "#FFFFFF", "#1F2328", "#D0D7DE"
    C_ACC = "#D35400"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    
    /* Eliminar Barras Blancas */
    div[data-testid="stExpander"], .streamlit-expanderHeader, .streamlit-expanderContent {{
        background-color: {C_SEC} !important;
        border: 1px solid {C_BRD} !important;
        color: {C_TXT} !important;
    }}
    
    /* Selectores y Campos */
    div[data-baseweb="select"] > div, input, div[data-baseweb="input"] {{
        background-color: {C_BG} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
    }}
    
    /* Botones de Cantidad */
    div[data-testid="stNumberInput"] button {{ 
        background-color: {C_SEC} !important; 
        border: 1px solid {C_BRD} !important; 
        color: {C_TXT} !important; 
    }}

    /* Botones de Acción */
    .stButton > button {{
        background-color: {C_SEC} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
        border-radius: 8px;
    }}
    .stButton > button:hover {{ border-color: {C_ACC} !important; color: {C_ACC} !important; }}

    /* Etapas (Opacidad 30%) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.1);
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
# 2. BASE DE DATOS TÉCNICA (DNA + SOP)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor y Grasa", "i": ["Azúcar", "Miel", "Mantequilla sin sal", "Sal fina", "Agua Azahar", "Levadura"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5),
        "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina", "Levadura seca"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal", "Sal fina", "Levadura fresca"], "c": "rgba(168, 230, 173, 0.3)"}]},
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima de Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "c": "rgba(255, 179, 140, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "c": "rgba(168, 230, 173, 0.3)"},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar Mascabada": 300, "Canela": 25, "c": "rgba(212, 163, 115, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.header("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    c1, c2 = st.columns(2)
    cli_nombre = c1.text_input("Nombre", key="cli_name_input")
    cli_wa = c2.text_input("WhatsApp", key="cli_wa_input")

st.write("### 🍞 2. Agregar Panes")
fk = st.session_state.f_key
c3, c4, c5, c6 = st.columns([2,2,1.5,1])

f_sel = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if f_sel != "-":
    e_sel = c4.selectbox("Especialidad", list(ARBOL[f_sel]["espec"].keys()), key=f"e_{fk}")
    t_sel = c5.selectbox("Tamaño", list(ARBOL[f_sel]["tamaños"].keys()), key=f"t_{fk}")
    c_sel = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    r_sel = "N/A"
    if f_sel == "Rosca de reyes": r_sel = st.selectbox("Relleno", ARBOL[f_sel]["espec"][e_sel]["rellenos"], key=f"r_{fk}")
    
    if st.button("➕ AÑADIR AL CARRITO"):
        st.session_state.carrito.append({"familia": f_sel, "especialidad": e_sel, "tamano": t_sel, "relleno": r_sel, "cantidad": c_sel})
        st.session_state.f_key += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_nombre}")
    for p in st.session_state.carrito: st.write(f"• {p['cantidad']}x {p['especialidad']} ({p['tamano']})")
    if st.button("✅ FINALIZAR Y GUARDAR"):
        if cli_nombre:
            st.session_state.comanda.append({"cliente": cli_nombre, "wa": cli_wa, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PROCESAMIENTO
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}
    lotes_complementos = {}

    try:
        for ped in st.session_state.comanda:
            for it in ped['items']:
                m_id = ARBOL[it['familia']]["masa"]
                if m_id not in lotes_masa: lotes_masa[m_id] = []
                it_c = it.copy(); it_c['cli'] = ped['cliente']
                lotes_masa[m_id].append(it_c)
                
                # Recolectar complementos
                cfg = ARBOL[it['familia']]
                subs = cfg["espec"][it['especialidad']]
                lista_subs = subs["fijos"].copy() if isinstance(subs, dict) else subs.copy()
                if it['relleno'] not in ["N/A", "Sin Relleno"]: lista_subs.append(it['relleno'])
                
                for s_id in lista_subs:
                    p_u = cfg.get("p_rell_map", {}).get(it['tamano'], 15) if it['familia'] == "Rosca de reyes" and s_id == it['relleno'] else (cfg.get("p_ex", {}).get(it['tamano'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                    lotes_complementos[s_id] = lotes_complementos.get(s_id, 0) + (p_u * it['cantidad'])

        with t_res:
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_tot = sum([(ARBOL[i['familia']]['tamaños'][i['tamano']] * i['cantidad']) / m_dna['merma'] for i in items])
                st.markdown(f"#### 🛠️ Lote: {m_id} ({m_tot:,.1f}g)")
                for it in items: st.success(f"{it['cantidad']}x {it['especialidad']} ({it['tamano']}) — {it['cli']}")

        with t_cli:
            for i, p in enumerate(st.session_state.comanda):
                col_a, col_b = st.columns([0.7, 0.3])
                col_a.write(f"👤 **{p['cliente']}** — WhatsApp: {p['wa']}")
                url = f"https://wa.me/521{p['wa']}?text=" + urllib.parse.quote(f"Hola {p['cliente']}! Tu pedido está listo.")
                col_b.link_button("🚀 Avisar Listo", url)
                if st.button("❌ Borrar", key=f"d_{i}"): st.session_state.comanda.pop(i); st.rerun()

        with t_prod:
            st.subheader("🥣 Batidos de Masa")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(ARBOL[it['familia']]['tamaños'][it['tamano']] * it['cantidad']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.markdown(f"**Masa: {m_id} (Total: {m_batch:,.1f}g)**")
                for etapa in m_dna.get("etapas", []):
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        peso = m_dna['receta'][ing]*h_b/100
                        st.checkbox(f"{ing}: {peso:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                        master_inv[ing] = master_inv.get(ing, 0) + peso
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.subheader("✨ Preparación de Complementos")
            for s_id, p_tot in lotes_complementos.items():
                s_rec = DB_COMPLEMENTOS.get(s_id, {})
                if not s_rec: continue
                st.markdown(f"**{s_id} (Total: {p_tot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {s_rec.get("c", "rgba(200,200,200,0.3)")};">', unsafe_allow_html=True)
                fact = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
                for sk, sv in s_rec.items():
                    if sk == "c": continue
                    peso_s = sv * fact
                    st.checkbox(f"{sk}: {peso_s:,.1f}g", key=f"s_{s_id}_{sk}")
                    master_inv[sk] = master_inv.get(sk, 0) + peso_s
                st.markdown('</div>', unsafe_allow_html=True)

        with t_sup:
            st.header("🛒 Lista Maestra")
            for k, v in sorted(master_inv.items()):
                st.checkbox(f"{k}: {v:,.1f}g", key=f"sup_{k}")

    except Exception:
        st.error("⚠️ Datos incompatibles detectados.")
        if st.button("♻️ RESETEAR TODO"): st.session_state.comanda = []; st.rerun()

    if st.button("🗑️ LIMPIAR TODO EL DÍA"): st.session_state.comanda = []; st.rerun()
