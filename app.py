import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DATOS (NÚCLEO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, "etapas": [{"n": "Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1), "etapas": [{"n": "Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "Sabor y Grasa", "i": ["Azúcar", "Miel", "Mantequilla sin sal", "Sal fina", "Agua Azahar", "Levadura fresca"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina", "Levadura seca"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal", "Sal fina", "Levadura fresca"], "c": "rgba(168, 230, 173, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Masa Guayaba", "i": ["Harina de fuerza", "Leche entera", "Yemas", "Claras", "Azúcar", "Mantequilla sin sal", "Sal fina", "Levadura fresca", "Polvo de Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30},
    "Crema Pastelera Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla sin sal": 20},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "Mantequilla": 16},
    "Glaseado Turin": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}, "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Pastelera Turin"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120}, "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"], "Ruby v2.0": ["Crema Ruby 50/50"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas", "p_manual": {"Ruby v2.0": 70}},
    "Pan de muerto": {"espec": {"Guayaba": ["Rebozado Muerto"]}, "tamaños": {"Estándar": 95}, "masa": "Masa Muerto Guayaba"}
}

# ==========================================
# 2. CONFIGURACIÓN VISUAL (ESTILO MATE)
# ==========================================
st.set_page_config(page_title="CONCIENCIA", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'carrito' not in st.session_state: st.session_state.carrito = []

# CSS para forzar el tema y evitar barras blancas
BG = "#0E1117" if st.session_state.tema_oscuro else "#F8F9FA"
SEC = "#161B22" if st.session_state.tema_oscuro else "#FFFFFF"
TXT = "#E6EDF3" if st.session_state.tema_oscuro else "#1F2328"
BRD = "#30363D" if st.session_state.tema_oscuro else "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TXT}; }}
    div[data-testid="stExpander"], .streamlit-expanderHeader {{ background-color: {SEC} !important; border: 1px solid {BRD} !important; color: {TXT} !important; }}
    div[data-baseweb="select"] > div, input {{ background-color: {BG} !important; color: {TXT} !important; border: 1px solid {BRD} !important; }}
    .etapa-box {{ padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; font-weight: 500; }}
    </style>
""", unsafe_allow_html=True)

# Botón de Cambio de Tema
_, c_t = st.columns([0.9, 0.1])
if c_t.button("🌙" if st.session_state.tema_oscuro else "☀️"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 Datos del Cliente y Pedido", expanded=not st.session_state.comanda):
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre Cliente")
    cli_w = c2.text_input("WhatsApp")
    
    st.divider()
    
    c3, c4, c5, c6 = st.columns([2,2,1,1])
    fam = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()))
    if fam != "-":
        esp = c4.selectbox("Especialidad", list(ARBOL[fam]["espec"].keys()))
        tam = c5.selectbox("Tamaño", list(ARBOL[fam]["tamaños"].keys()))
        can = c6.number_input("Cant", min_value=1, value=1)
        rel = "N/A"
        if fam == "Rosca de reyes":
            rel = st.selectbox("Relleno", ARBOL[fam]["espec"][esp]["rellenos"])
        
        if st.button("➕ Añadir al Carrito"):
            st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "can": can})
            st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    for i, p in enumerate(st.session_state.carrito):
        st.write(f"{p['can']}x {p['fam']} {p['esp']} ({p['tam']})")
    
    if st.button("✅ GUARDAR PEDIDO FINAL"):
        st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
        st.session_state.carrito = []
        st.rerun()

# ==========================================
# 4. PESTAÑAS DE TRABAJO (PRODUCCIÓN & CLIENTES)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}

    # Consolidar para producción
    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            st.markdown(f"#### 🛠️ Lote: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_tot = sum([(ARBOL[it['fam']].get("p_manual", {}).get(it['esp'], ARBOL[it['fam']]['tamaños'][it['tam']]) * it['can']) / m_dna['merma'] for it in items])
            h_b = (m_tot * 100) / sum(m_dna['receta'].values())
            
            col_m, col_c = st.columns([0.3, 0.7])
            with col_m:
                st.info(f"Masa Total: {m_tot:,.1f}g")
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with col_c:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            res_txt = ", ".join([f"{it['can']} {it['esp']}" for it in ped['items']])
            c1.write(f"👤 **{ped['cliente']}**")
            msg = urllib.parse.quote(f"¡Hola {ped['cliente']}! Tu pedido de {res_txt} ya está listo 🥐.")
            c2.link_button("✅ Confirmar", f"https://wa.me/521{ped['wa']}?text=Recibido")
            c3.link_button("🚀 Listo", f"https://wa.me/521{ped['wa']}?text={msg}")
            if st.button("❌ Borrar", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna.get("etapas", []):
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    st.checkbox(f"{ing}: {(m_dna['receta'][ing]*h_b/100):,.1f}g", key=f"chk_{m_id}_{ing}_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: {v:,.1f}g", key=f"sup_{k}")

    if st.button("🗑️ LIMPIAR TODO EL DÍA"): st.session_state.comanda = []; st.rerun()
