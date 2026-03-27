import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DISEÑO (SISTEMA DE TEMAS)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Definición de paleta técnica basada en el estado
if st.session_state.tema_oscuro:
    C_FONDO = "#0E1117"     # Gris casi negro
    C_TARJETA = "#161B22"   # Gris oscuro sólido
    C_TEXTO = "#E6EDF3"     # Blanco hueso
    C_TEXTO_DIM = "#8B949E" # Gris para subtítulos
    C_BORDE = "#30363D"     # Borde sutil
    C_ACENTO = "#E67E22"    # Naranja Conciencia
else:
    C_FONDO = "#F6F8FA"     # Gris muy claro
    C_TARJETA = "#FFFFFF"   # Blanco puro
    C_TEXTO = "#1F2328"     # Negro elegante
    C_TEXTO_DIM = "#57606A" # Gris oscuro
    C_BORDE = "#D0D7DE"     # Borde gris claro
    C_ACENTO = "#D35400"    # Naranja quemado

# Inyección de CSS Limpio y Estructural
st.markdown(f"""
    <style>
    /* Reset de la App */
    .stApp {{ background-color: {C_FONDO}; color: {C_TEXTO}; }}
    
    /* Control de textos */
    h1, h2, h3, h4, p, span, label {{ color: {C_TEXTO} !important; }}
    
    /* Expander (Barra de datos cliente) sin blanco */
    div[data-testid="stExpander"] {{
        background-color: {C_TARJETA} !important;
        border: 1px solid {C_BORDE} !important;
        border-radius: 8px;
    }}
    .streamlit-expanderHeader {{ background-color: {C_TARJETA} !important; color: {C_TEXTO} !important; }}

    /* Inputs y Selectores Integrados */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {C_FONDO} !important;
        color: {C_TEXTO} !important;
        border: 1px solid {C_BORDE} !important;
    }}

    /* Estilo de Botones */
    .stButton > button {{
        background-color: {C_TARJETA} !important;
        color: {C_TEXTO} !important;
        border: 1px solid {C_BORDE} !important;
        transition: 0.2s;
    }}
    .stButton > button:hover {{ border-color: {C_ACENTO} !important; color: {C_ACENTO} !important; }}

    /* Cajas de Etapas (Opacidad 30%) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #1a1a1a !important; /* Texto oscuro para leer sobre el color pastel */
    }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna funcional
_, c_tema = st.columns([0.9, 0.1])
if c_tema.button("🌙" if st.session_state.tema_oscuro else "☀️"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 2. BASE DE DATOS MAESTRA (AUDITADA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5)},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350)},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao en polvo": 0.8, "Colorante Rojo": 0.7}, "merma": 1.0, "tz": (0.07, 5)},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2}, "merma": 1.0, "tz": (0.025, 1)},
    "Masa Muerto Tradicional": {"receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3}, "merma": 1.0},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5}, "merma": 1.0, "huesos": True},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Crema Pastelera Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla sin sal": 20},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "Mantequilla sin sal": 16, "Sal": 0.8},
    "Glaseado Ruby": {"Choco Ruby": 80, "Azúcar Glass": 160, "Leche entera": 50},
    "Glaseado Turin": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Berlinas": {"espec": {"Ruby v2.0": ["Crema Ruby 50/50", "Glaseado Ruby"], "Turín": ["Crema Pastelera Turin", "Glaseado Turin"], "Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas", "p_manual": {"Ruby v2.0": (70, {"Crema Ruby 50/50": 40, "Glaseado Ruby": 8}), "Turín": (60, {"Crema Pastelera Turin": 80, "Glaseado Turin": 16})}},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}, "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Pastelera Turin"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rel_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Rollos": {"espec": {"Canela Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto"]}, "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}},
    "Brownies": {"espec": {"Turín": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 3. INTERFAZ Y LÓGICA DE CARRITO
# ==========================================

with st.expander("👤 1. Datos del Cliente", expanded=True):
    col_c1, col_c2 = st.columns(2)
    cli_nombre = col_c1.text_input("Nombre del Cliente", key="persist_cli_n")
    cli_whatsapp = col_c2.text_input("WhatsApp", key="persist_cli_w")

st.write("### 🍞 2. Carrito de Panes")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,1])

with col1: fam_sel = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
with col2: esp_sel = st.selectbox("Especialidad", list(ARBOL[fam_sel]["espec"].keys()) if fam_sel != "-" else ["-"], key=f"e_{fk}")
with col3: tam_sel = st.selectbox("Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()) if fam_sel != "-" else ["-"], key=f"t_{fk}")
with col4: cant_sel = st.number_input("Cant.", min_value=1, value=1, key=f"c_{fk}")

rel_sel = "N/A"
if fam_sel == "Rosca de reyes" and esp_sel != "-":
    rel_sel = st.selectbox("Relleno", ARBOL[fam_sel]["espec"][esp_sel]["rellenos"], key=f"r_{fk}")

with col5:
    st.write("##")
    if st.button("➕"):
        if fam_sel != "-":
            st.session_state.carrito_actual.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rel": rel_sel, "cant": cant_sel})
            st.session_state.form_key += 1
            st.rerun()

if st.session_state.carrito_actual:
    st.info(f"🛒 Carrito para: **{cli_nombre}**")
    for i, p in enumerate(st.session_state.carrito_actual):
        st.caption(f"{p['cant']}x {p['fam']} {p['esp']} ({p['tam']})")
    
    if st.button("✅ FINALIZAR Y GUARDAR PEDIDO", use_container_width=True):
        if cli_nombre:
            st.session_state.comanda.append({"cliente": cli_nombre, "wa": cli_whatsapp, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []
            st.rerun()

# ==========================================
# 4. HOJA DE PRODUCCIÓN (BATCHES)
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
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch_gr = 0
            for i in items:
                p_u = ARBOL[i['fam']].get("p_manual", {}).get(i['esp'], (ARBOL[i['fam']]['tamaños'][i['tam']], 0))[0]
                m_batch_gr += (p_u * i['cant']) / m_dna['merma']
            
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            st.markdown(f"#### 🛠️ Lote: {m_id}")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info(f"Masa ({m_batch_gr:,.1f}g)")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['cant']}x {it['esp']} ({it['tam']}) — {it['cli']}")

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            with st.container():
                c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
                c1.write(f"👤 **{ped['cliente']}**")
                url_b = f"https://wa.me/521{ped['wa']}?text="
                c2.link_button("✅ Confirmar", url_b + urllib.parse.quote(f"¡Hola {ped['cliente']}! Recibimos tu pedido."))
                if st.button("❌", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            if "etapas" in m_dna:
                for etapa in m_dna["etapas"]:
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        gr = m_dna['receta'][ing]*h_b/100
                        st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                    st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for insumo, cant in sorted(master_inv.items()):
            st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"master_{insumo}")
