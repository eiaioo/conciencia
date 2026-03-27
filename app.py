import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN Y DISEÑO (MODO MATE)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'f_key' not in st.session_state: st.session_state.f_key = 0

# Paleta Mate Técnica
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
    div[data-testid="stExpander"], .streamlit-expanderHeader {{
        background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important;
    }}
    
    /* Inputs y Selectores */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {C_BG} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important;
    }}
    
    /* Sidebar Estilo */
    [data-testid="stSidebar"] {{ background-color: {C_SEC} !important; border-right: 1px solid {C_BRD}; }}
    
    /* Etapa-Box (Opacidad 30%) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #1a1a1a !important; font-weight: 500;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BARRA LATERAL (NAVEGACIÓN)
# ==========================================
with st.sidebar:
    st.title("👨‍🍳 Menú")
    pagina = st.radio("Ir a:", ["📋 Resumen Visual", "🥣 Producción", "📞 Clientes & WhatsApp", "🛒 Súper (Lista Maestra)"])
    
    st.divider()
    if st.button("☀️/🌙 Cambiar Tema"):
        st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
        st.rerun()
    
    if st.button("🗑️ Limpiar Todo el Día"):
        st.session_state.comanda = []
        st.rerun()

# ==========================================
# 3. BASE DE DATOS TÉCNICA (DNA COMPLETO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor", "i": ["Azúcar", "Miel", "Levadura", "Sal fina"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "c": "rgba(168, 230, 173, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "c": "rgba(212, 163, 115, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": ["Vainilla", "Chocolate"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": ["Tradicional"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35}, "masa": "Masa Brioche Rosca"},
}

# ==========================================
# 3. INTERFAZ DE CAPTURA (SIEMPRE VISIBLE ARRIBA)
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("📝 1. Iniciar Nuevo Pedido", expanded=not st.session_state.comanda):
    c_n, c_w = st.columns(2)
    cli_n = c_n.text_input("Nombre Cliente", key="persist_cli_n")
    cli_w = c_w.text_input("WhatsApp (10 dígitos)", key="persist_cli_w")

st.write("### 🍞 2. Agregar Panes")
fk = st.session_state.form_key
c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1, 0.8])
fam_sel = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")

if fam_sel != "-":
    esp_sel = c4.selectbox("Especialidad", ARBOL[fam_sel]["espec"], key=f"e_{fk}")
    tam_sel = c5.selectbox("Tamaño", list(ARBOL[fam_sel]["tam"].keys()), key=f"t_{fk}")
    can_sel = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    rel_sel = "Sin Relleno"
    if fam_sel == "Rosca de reyes":
        rel_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Pastelera Vainilla"], key=f"r_{fk}")
    
    if c7.button("➕"):
        st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "can": can_sel, "rel": rel_sel})
        st.session_state.form_key += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    if st.button("✅ GUARDAR PEDIDO Y CERRAR CLIENTE"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. PÁGINAS DE TRABAJO (SEGÚN SIDEBAR)
# ==========================================

if st.session_state.comanda:
    st.divider()
    master_inv = {}
    lotes_masa = {}
    lotes_comp = {}

    # Procesar datos globales
    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)
            
            # Recolectar complementos
            subs = []
            if it['fam'] == "Conchas": subs.append(f"Lágrima {it['esp']}")
            if it['fam'] == "Rosca de reyes": 
                subs.append("Decoración Rosca")
                if it['rel'] != "Sin Relleno": subs.append(it['rel'])
            
            for s_id in subs:
                if s_id in DB_COMPLEMENTOS:
                    p_u = ARBOL[it['fam']].get("p_rell_map", {}).get(it['tam'], 15) if "Crema" in s_id else (ARBOL[it['fam']].get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15)
                    lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

    # --- PÁGINA: RESUMEN ---
    if pagina == "📋 Resumen Visual":
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_tot = sum([(ARBOL[i['fam']]['tam'][i['tam']] * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_tot * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_tot:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info("Ingredientes Masa")
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
                    sub_id = f"Lágrima {it['esp']}" if it['fam'] == "Conchas" else None
                    if sub_id in DB_COMPLEMENTOS:
                        s_rec = DB_COMPLEMENTOS[sub_id]
                        p_t = ARBOL[it['fam']]['p_ex'][it['tam']] * it['can']
                        st.write(f"**{sub_id} ({p_t:,.1f}g):**")
                        f_s = p_t / sum([v for k,v in s_rec.items() if k != "c"])
                        for sk, sv in s_rec.items():
                            if sk != "c": gr_s = sv * f_s; st.write(f"- {sk}: {gr_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + gr_s

    # --- PÁGINA: CLIENTES ---
    elif pagina == "📞 Clientes & WhatsApp":
        st.header("📞 Gestión de Clientes")
        for i, p in enumerate(st.session_state.comanda):
            with st.container(border=True):
                col_a, col_b, col_c = st.columns([0.4, 0.3, 0.3])
                resumen_txt = ", ".join([f"{it['can']} {it['esp']}" for it in p['items']])
                col_a.write(f"👤 **{p['cliente']}**\n\n{resumen_txt}")
                
                u_base = f"https://wa.me/521{p['wa']}?text="
                col_b.link_button("✅ Confirmar Pedido", u_base + urllib.parse.quote(f"¡Hola {p['cliente']}! Recibimos tu pedido de {resumen_txt}. Gracias!"))
                col_c.link_button("🚀 Avisar: LISTO", u_base + urllib.parse.quote(f"¡Hola {p['cliente']}! Tu pedido de {resumen_txt} ya está listo 🥐."))
                
                if st.button("❌ Eliminar Pedido", key=f"del_{i}"):
                    st.session_state.comanda.pop(i); st.rerun()

    # --- PÁGINA: PRODUCCIÓN ---
    elif pagina == "🥣 Producción":
        cm, cc = st.columns(2)
        with cm:
            st.subheader("🥣 Batidos de Masa")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(ARBOL[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.write(f"**{m_id}**")
                for etapa in m_dna.get("etapas", []):
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        st.checkbox(f"{ing}: {m_dna['receta'][ing]*h_b/100:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}_{i}")
                    st.markdown('</div>', unsafe_allow_html=True)
        with cc:
            st.subheader("✨ Complementos")
            for s_id, p_tot in lotes_comp.items():
                s_rec = DB_COMPLEMENTOS[s_id]
                st.write(f"**{s_id} ({p_tot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {s_rec["c"]};">', unsafe_allow_html=True)
                fact = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
                for sk, sv in s_rec.items():
                    if sk != "c": st.checkbox(f"{sk}: {sv*fact:,.1f}g", key=f"sec_{s_id}_{sk}")
                st.markdown('</div>', unsafe_allow_html=True)

    # --- PÁGINA: SÚPER ---
    elif pagina == "🛒 Súper (Lista Maestra)":
        st.header("🛒 Lista Maestra de Surtido")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"sup_{k}")
