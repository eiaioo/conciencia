import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE UI Y TEMA PROFESIONAL
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Colores para Dark y Light Mode
if st.session_state.tema_oscuro:
    bg = "#121212"
    sec_bg = "#1E1E1E"
    text = "#D1D1D1"
    accent = "#E67E22" # Naranja Conciencia
    input_bg = "#2D2D2D"
    border = "#333333"
else:
    bg = "#F8F9FA"
    sec_bg = "#FFFFFF"
    text = "#2C3E50"
    accent = "#D35400"
    input_bg = "#FFFFFF"
    border = "#DEE2E6"

st.markdown(f"""
    <style>
    /* Estabilidad General */
    .stApp {{ background-color: {bg}; color: {text}; }}
    
    /* Estilo de Contenedores y Expanders */
    div[data-testid="stExpander"], .stContainer {{
        background-color: {sec_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 10px !important;
    }}
    
    /* Estilo de Inputs (Bajo Contraste) */
    input, select, textarea, div[data-baseweb="select"], div[data-baseweb="input"] {{
        background-color: {input_bg} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}
    
    /* Arreglo para checklist en móvil */
    .stCheckbox {{ display: flex !important; align-items: center !important; margin-bottom: -10px; }}
    .stCheckbox label {{ color: {text} !important; font-size: 1.05rem !important; }}
    
    /* Botones */
    .stButton>button {{
        border-radius: 20px;
        background-color: {accent} !important;
        color: white !important;
        border: none;
    }}
    
    /* Títulos de Etapas (Pasteles suaves) */
    .etapa-box {{
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        color: #1c1c1c !important; /* Texto oscuro siempre en cajas de color */
    }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN DE TEMA (Emoji Flotante)
c_t1, c_t2 = st.columns([0.94, 0.06])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS TÉCNICA (COMPLETA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "etapas": [
            {"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(255, 235, 156, 0.6)"},
            {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(168, 230, 173, 0.6)"},
            {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.6)"},
            {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.6)"}
        ],
        "merma": 1.0, "factor": 1.963
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "etapas": [
            {"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(255, 235, 156, 0.6)"},
            {"n": "2. Activación", "i": ["Levadura fresca"], "c": "rgba(168, 230, 173, 0.6)"},
            {"n": "3. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": "rgba(162, 210, 255, 0.6)"},
            {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.6)"}
        ],
        "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "etapas": [
            {"n": "1. Batido y TZ", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(255, 235, 156, 0.6)"},
            {"n": "2. Estructura", "i": ["Azúcar", "Levadura seca", "Sal fina"], "c": "rgba(162, 210, 255, 0.6)"},
            {"n": "3. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.6)"}
        ],
        "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30},
    "Decoración Rosca": {"Ate de colores": 50, "Higo en almíbar": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"}
}

# ==========================================
# 2. INTERFAZ (UI LIMPIA)
# ==========================================

with st.expander("👤 1. Datos del Cliente", expanded=len(st.session_state.carrito_actual) == 0):
    fk_c = st.session_state.form_key
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre Cliente", key=f"cn_{fk_c}")
    cli_w = c2.text_input("WhatsApp (10 dígitos)", key=f"cw_{fk_c}")

with st.container():
    st.subheader("🍞 2. Carrito de Panes")
    fk = st.session_state.form_key
    col1, col2, col3, col4 = st.columns([2,2,1,1])
    
    fam_sel = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_sel_{fk}")
    if fam_sel != "-":
        esp_sel = col2.selectbox("Especialidad", list(ARBOL[fam_sel]["espec"].keys()), key=f"e_sel_{fk}")
        tam_sel = col3.selectbox("Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()), key=f"t_sel_{fk}")
        cant_sel = col4.number_input("Cant.", min_value=1, value=1, key=f"c_sel_{fk}")
        
        rel_sel = "N/A"
        if fam_sel == "Rosca de reyes":
            rel_sel = st.selectbox("Relleno", ARBOL[fam_sel]["espec"][esp_sel]["rellenos"], key=f"r_sel_{fk}")
        
        if st.button("➕ Añadir al Carrito"):
            st.session_state.carrito_actual.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rel": rel_sel, "cant": cant_sel})
            st.session_state.form_key += 1
            st.rerun()

if st.session_state.carrito_actual:
    st.markdown(f"**🛒 Pedido Actual:** {cli_n}")
    for p in st.session_state.carrito_actual:
        st.caption(f"• {p['cant']}x {p['fam']} {p['esp']} ({p['tam']})")
    
    cb1, cb2 = st.columns(2)
    if cb1.button("✅ FINALIZAR Y GUARDAR TODO"):
        if cli_n and cli_w:
            st.session_state.comanda.append({"cliente": cli_n, "whatsapp": cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []; st.session_state.form_key += 1; st.rerun()
        else: st.error("Faltan datos del cliente")
    if cb2.button("❌ Cancelar"): st.session_state.carrito_actual = []; st.rerun()

# ==========================================
# 3. PRODUCCIÓN (SOP & CRM)
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
            it_c = it.copy(); it_c['cliente'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            st.markdown(f"### 🛠️ Batido: {m_id}")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info(f"**Masa (Total: {m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
            with c2:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']}) — {it['cliente']}**")
                    cfg = ARBOL[it['fam']]
                    # Obtener subrecetas
                    base_espec = cfg["espec"][it['esp']]
                    lista = base_espec["fijos"].copy() if isinstance(base_espec, dict) else base_espec.copy()
                    if it.get('rel') not in ["N/A", "Sin Relleno", None]: lista.append(it['rel'])
                    for s_id in lista:
                        if s_id not in DB_COMPLEMENTOS: continue
                        p_u = cfg["p_relleno_map"][it['tam']] if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']; st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            g_s = val_s * (it['cant'] if "Decoración" in s_id or "Rebozado" in s_id else fact)
                            st.write(f"- {ing_s}: {g_s:,.1f}g"); master_inv[ing_s] = master_inv.get(ing_s, 0) + g_s

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            with st.container():
                c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
                res_txt = ", ".join([f"{it['cant']} {it['esp']}" for it in ped['items']])
                c1.write(f"👤 **{ped['cliente']}**\n\n{res_txt}")
                url_b = f"https://wa.me/521{ped['whatsapp']}?text="
                c2.link_button("✅ Confirmar", url_b + urllib.parse.quote(f"¡Hola {ped['cliente']}! Recibimos tu pedido de ({res_txt}). Gracias!"))
                c3.link_button("🚀 Avisar Listo", url_b + urllib.parse.quote(f"¡Hola {ped['cliente']}! Tu pedido de ({res_txt}) ya está listo 🥐."))
                if st.button("❌ Borrar", key=f"final_del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna["etapas"]:
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("📦 Surtido de Insumos")
        for insumo, cant in sorted(master_inv.items()):
            col1, col2 = st.columns([0.05, 0.95])
            if col1.checkbox("", key=f"master_{insumo}"): col2.markdown(f"~~{insumo}: {cant:,.1f}g~~")
            else: col2.write(f"{insumo}: {cant:,.1f}g")

    if st.button("🗑️ LIMPIAR TODA LA PRODUCCIÓN"): st.session_state.comanda = []; st.rerun()
