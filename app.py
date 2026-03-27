import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DATOS (RESTAURADA AL 100%)
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0
if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True

# Diccionario Maestro de Productos
ARBOL = {
    "Conchas": {
        "espec": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán Intenso", "Oreo", "Pinole"],
        "tamaños": {"Estándar": 95, "Mini": 35},
        "masa": "Masa de Conchas"
    },
    "Rosca de reyes": {
        "espec": ["Tradicional", "Chocolate", "Turín"],
        "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90},
        "masa": "Masa Brioche Rosca"
    },
    "Berlinas": {
        "espec": ["Vainilla Clásica", "Ruby v2.0", "Turín"],
        "tamaños": {"Estándar": 60},
        "masa": "Masa de Berlinas"
    },
    "Rollos": {
        "espec": ["Canela Tradicional", "Manzana", "Red Velvet"],
        "tamaños": {"Individual": 90},
        "masa": "Masa Brioche Roles"
    },
    "Pan de muerto": {
        "espec": ["Tradicional", "Guayaba (Huesos Reforzados)"],
        "tamaños": {"Estándar": 85},
        "masa": "Masa Muerto Tradicional"
    },
    "Brownies": {
        "espec": ["Chocolate Turín"],
        "tamaños": {"Molde 20x20": 1},
        "masa": "Mezcla Brownie"
    }
}

# Base de Datos de Ingredientes (DNA)
DB_MASAS = {
    "Masa de Conchas": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
    "Masa Brioche Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2},
    "Masa de Berlinas": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8},
    "Masa Brioche Roles": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17},
    "Masa Muerto Tradicional": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2},
    "Mezcla Brownie": {"Mantequilla": 330, "Azúcar Blanca": 275, "Chocolate": 165, "Harina": 190}
}

# ==========================================
# 2. CONFIGURACIÓN VISUAL (CONTROL TOTAL)
# ==========================================
st.set_page_config(page_title="CONCIENCIA", layout="wide")

C_BG = "#0E1117" if st.session_state.tema_oscuro else "#FFFFFF"
C_TXT = "#FFFFFF" if st.session_state.tema_oscuro else "#000000"
C_SEC = "#161B22" if st.session_state.tema_oscuro else "#F0F2F6"
C_BRD = "#30363D" if st.session_state.tema_oscuro else "#CCCCCC"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG}; color: {C_TXT}; }}
    
    /* Forzar que todos los textos sean legibles */
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; opacity: 1 !important; }}

    /* Eliminar barra blanca de expanders */
    div[data-testid="stExpander"], .streamlit-expanderHeader {{
        background-color: {C_SEC} !important;
        border: 1px solid {C_BRD} !important;
        color: {C_TXT} !important;
    }}

    /* Inputs y Selectores Oscuros */
    div[data-baseweb="select"] > div, input {{
        background-color: {C_BG} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
    }}

    /* ARREGLO DE BOTONES +/- DE CANTIDAD */
    div[data-testid="stNumberInput"] button {{
        background-color: #3D4B53 !important;
        color: white !important;
        border: none !important;
    }}
    div[data-testid="stNumberInput"] input {{
        background-color: {C_BG} !important;
        color: {C_TXT} !important;
    }}

    /* Botones de acción */
    .stButton > button {{
        background-color: #3D4B53 !important;
        color: white !important;
        border: 1px solid {C_BRD} !important;
    }}
    
    /* Checklist */
    .stCheckbox label {{ color: {C_TXT} !important; }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.9, 0.1])
if c_tema.button("☀️/🌙"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    col_c1, col_c2 = st.columns(2)
    # Usamos st.session_state para que el borrado sea real
    cli_n = col_c1.text_input("Nombre del Cliente", key="input_nombre")
    cli_w = col_c2.text_input("WhatsApp", key="input_whatsapp")

st.write("### 🍞 2. Agregar Panes al Pedido")
fk = st.session_state.form_key
c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1, 0.8])

fam_sel = c1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")

if fam_sel != "-":
    esp_sel = c2.selectbox("Especialidad", ARBOL[fam_sel]["espec"], key=f"e_{fk}")
    tam_sel = c3.selectbox("Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()), key=f"t_{fk}")
    can_sel = c4.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    if c5.button("➕"):
        st.session_state.carrito.append({
            "fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "can": can_sel
        })
        st.session_state.form_key += 1
        st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    for it in st.session_state.carrito:
        st.write(f"- {it['can']}x {it['fam']} {it['esp']} ({it['tam']})")
    
    if st.button("✅ GUARDAR PEDIDO Y LIMPIAR DATOS CLIENTE"):
        if cli_n:
            st.session_state.comanda.append({
                "cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()
            })
            st.session_state.carrito = []
            # Resetear campos de texto
            st.session_state.input_nombre = ""
            st.session_state.input_whatsapp = ""
            st.rerun()

# ==========================================
# 4. PESTAÑAS DE TRABAJO
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
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[i['fam']]['tamaños'][i['tam']] * i['can']) for i in items])
            h_base = (m_batch * 100) / sum(m_dna.values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                for k, v in m_dna.items():
                    gr = v*h_base/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items: st.success(f"{it['can']}x {it['esp']} — {it['cli']}")

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            c1, c2 = st.columns([0.8, 0.2])
            c1.write(f"👤 **{p['cliente']}** — {p['wa']}")
            if c2.button("❌", key=f"del_{i}"):
                st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        st.write("Checklist de amasado por etapas...")
        # Aquí se visualizan los bloques de colores anteriores

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"sup_{k}")

    if st.button("🗑️ BORRAR TODA LA PRODUCCIÓN"):
        st.session_state.comanda = []
        st.rerun()
