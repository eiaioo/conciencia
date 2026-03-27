import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN VISUAL (MODO MATE)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Paleta de colores de bajo contraste
if st.session_state.tema_oscuro:
    BG, SEC, TXT, BRD = "#0E1117", "#161B22", "#C9D1D9", "#30363D"
    ACC = "#E67E22" # Naranja Conciencia
else:
    BG, SEC, TXT, BRD = "#F6F8FA", "#FFFFFF", "#24292F", "#D0D7DE"
    ACC = "#D35400"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {TXT} !important; }}
    /* Eliminar barras blancas en expanders */
    div[data-testid="stExpander"], .streamlit-expanderHeader {{
        background-color: {SEC} !important;
        border: 1px solid {BRD} !important;
        color: {TXT} !important;
    }}
    /* Inputs y Selectores */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {BG} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
    }}
    /* Botones de cantidad */
    div[data-testid="stNumberInput"] button {{ background-color: {SEC} !important; color: {TXT} !important; border: 1px solid {BRD} !important; }}
    /* Botones de acción */
    .stButton > button {{ background-color: {SEC} !important; color: {TXT} !important; border: 1px solid {BRD} !important; border-radius: 8px; }}
    .stButton > button:hover {{ border-color: {ACC} !important; color: {ACC} !important; }}
    /* Etapas */
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; font-weight: 500; }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.92, 0.08])
if c_tema.button("🌙" if st.session_state.tema_oscuro else "☀️"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA COMPLETA
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7}, "merma": 1.0, "tz_ratio": 0.07, "tz_liq": 5},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Chocolate Turin": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima de Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Ruby 50/50": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Cuerpos": 100, "Leche": 50, "Cabeza de Conejo": 1},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}, "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Ruby 50/50"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Ruby v2.0": ["Crema Ruby 50/50"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas", "p_manual": {"Ruby v2.0": 70}},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": {"Guayaba": ["Rebozado Muerto"]}, "tamaños": {"Estándar": 95}, "masa": "Masa Muerto Guayaba"},
    "Brownies": {"espec": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=not st.session_state.comanda):
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre", key="cli_persist_n")
    cli_w = c2.text_input("WhatsApp", key="cli_persist_w")

with st.container():
    st.write("### 🍞 2. Carrito de Panes")
    fk = st.session_state.form_key
    col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,0.8])
    
    fam = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if fam != "-":
        esp = col2.selectbox("Especialidad", list(ARBOL[fam]["espec"].keys()), key=f"e_{fk}")
        tam = col3.selectbox("Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{fk}")
        can = col4.number_input("Cant.", min_value=1, value=1, key=f"c_{fk}")
        rel = "N/A"
        if fam == "Rosca de reyes":
            rel = st.selectbox("Relleno", ARBOL[fam]["espec"][esp]["rellenos"], key=f"r_{fk}")
        
        if col5.button("➕", key=f"add_{fk}"):
            st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "can": can})
            st.session_state.form_key += 1
            st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    for p in st.session_state.carrito: st.write(f"- {p['can']}x {p['fam']} {p['esp']}")
    if st.button("✅ FINALIZAR Y GUARDAR PEDIDO COMPLETO"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. LÓGICA DE PRODUCCIÓN (RESUMEN)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    master_inv = {}
    lotes_masa = {}

    # Limpiar datos viejos si causan error
    try:
        for ped in st.session_state.comanda:
            for it in ped['items']:
                m_id = ARBOL[it['fam']]["masa"]
                if m_id not in lotes_masa: lotes_masa[m_id] = []
                it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)

        with t_res:
            for m_id, items in lotes_masa.items():
                st.markdown(f"#### 🛠️ Lote: {m_id}")
                m_dna = DB_MASAS[m_id]
                m_tot = sum([(ARBOL[i['fam']].get("p_manual", {}).get(i['esp'], ARBOL[i['fam']]['tamaños'][i['tam']]) * i['can']) / m_dna['merma'] for i in items])
                h_b = (m_tot * 100) / sum(m_dna['receta'].values())
                
                c_m, c_c = st.columns([0.3, 0.7])
                with c_m:
                    st.info(f"Masa ({m_tot:,.1f}g)")
                    for k, v in m_dna['receta'].items():
                        gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
                with c_c:
                    for it in items:
                        st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
        
        with t_cli:
            for i, p in enumerate(st.session_state.comanda):
                c_1, c_2 = st.columns([0.8, 0.2])
                c_1.write(f"👤 **{p['cliente']}** — {p['wa']}")
                if c_2.button("❌", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    except Exception as e:
        st.warning("Se detectaron datos antiguos incompatibles. Por favor limpia la producción.")
        if st.button("♻️ RESETEAR DATOS"): st.session_state.comanda = []; st.rerun()

    if st.button("🗑️ LIMPIAR TODO EL DÍA"): st.session_state.comanda = []; st.rerun()
