import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DISEÑO (BLINDAJE TOTAL)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# Inicialización de estados
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0
if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True

# Limpiar basura de versiones anteriores para evitar errores de carga
if st.session_state.comanda and 'items' not in st.session_state.comanda[0]:
    st.session_state.comanda = []

# Colores Profesionales
if st.session_state.tema_oscuro:
    BG, SEC, TXT, BRD = "#0E1117", "#161B22", "#E6EDF3", "#30363D"
    ACC = "#E67E22"
else:
    BG, SEC, TXT, BRD = "#F8F9FA", "#FFFFFF", "#1F2328", "#D0D7DE"
    ACC = "#D35400"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG} !important; color: {TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {TXT} !important; }}
    
    /* Eliminar barra blanca de Expanders */
    div[data-testid="stExpander"], .streamlit-expanderHeader, .streamlit-expanderContent, summary, details {{
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
    
    /* Botones de Cantidad */
    div[data-testid="stNumberInput"] button {{ background-color: {SEC} !important; border: 1px solid {BRD} !important; color: {TXT} !important; }}

    /* Botones de Acción */
    .stButton > button {{
        background-color: {SEC} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
        border-radius: 8px;
        width: 100%;
    }}

    /* Cajas de Etapas (Opacidad 30%) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #1a1a1a !important; font-weight: 500;
    }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.9, 0.1])
if c_tema.button("☀️/🌙"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA (DNA + CATALOGO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar", "Levadura fresca"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(168, 230, 173, 0.3)"}]},
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "c": "rgba(255, 179, 140, 0.3)"},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula de Maíz": 24, "Mantequilla sin sal": 16, "c": "rgba(168, 230, 173, 0.3)"},
    "Decoración Rosca": {"Ate de colores": 50, "Higo": 20, "Cereza": 10, "c": "rgba(212, 163, 115, 0.3)"},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25, "c": "rgba(183, 183, 164, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}, "Turín": {"fijos": ["Lágrima de Chocolate"], "rellenos": ["Sin Relleno", "Crema Ruby 50/50"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Ruby v2.0": ["Crema Ruby 50/50"], "Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "p_man": {"Ruby v2.0": 70}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Canela": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.container():
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre del Cliente", key="cli_name_persist")
    cli_w = c2.text_input("WhatsApp", key="cli_wa_persist")

st.write("### 🍞 Agregar Panes")
fk = st.session_state.form_key
c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1, 0.6])

fam_sel = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if fam_sel != "-":
    esp_sel = c4.selectbox("Especialidad", list(ARBOL[fam_sel]["espec"].keys()), key=f"e_{fk}")
    tam_sel = c5.selectbox("Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()), key=f"t_{fk}")
    can_sel = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    rel_sel = "N/A"
    if fam_sel == "Rosca de reyes":
        rel_sel = st.selectbox("Relleno", ARBOL[fam_sel]["espec"][esp_sel]["rellenos"], key=f"r_{fk}")
    
    c7.write("##") # Espaciador
    if c7.button("➕"):
        st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rel": rel_sel, "can": can_sel})
        st.session_state.form_key += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    for it in st.session_state.carrito: st.write(f"• {it['can']}x {it['fam']} {it['esp']} ({it['tam']})")
    if st.button("✅ GUARDAR PEDIDO FINAL"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PRODUCCIÓN (BATCHES)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}
    lotes_comp = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)
            
            # Recolectar complementos
            cfg = ARBOL[it['fam']]
            base_esp = cfg["espec"][it['esp']]
            lista = base_esp["fijos"].copy() if isinstance(base_esp, dict) else base_esp.copy()
            if it['rel'] not in ["N/A", "Sin Relleno"]: lista.append(it['rel'])
            
            for s_id in lista:
                if s_id not in DB_COMPLEMENTOS: continue
                p_u = cfg.get("p_rell_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[i['fam']].get("p_man", {}).get(i['esp'], ARBOL[i['fam']]['tamaños'][i['tam']]) * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_batch * 100) / sum([v for k,v in m_dna['receta'].items()])
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info("Ingredientes Masa")
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
                    # Desglose de complementos por cliente en resumen
                    cfg_it = ARBOL[it['fam']]
                    list_it = cfg_it["espec"][it['esp']]
                    l_it = list_it["fijos"].copy() if isinstance(list_it, dict) else list_it.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: l_it.append(it['rel'])
                    for s_id in l_it:
                        if s_id in DB_COMPLEMENTOS:
                            p_u_it = cfg_it.get("p_rell_map", {}).get(it['tam'], 15) if s_id == it['rel'] else (cfg_it.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg_it.get("p_ex"), dict) else cfg_it.get("p_ex", 15))
                            p_tot_it = p_u_it * it['can']
                            st.markdown(f"**{s_id} ({p_tot_it:,.1f}g)**")
                            s_rec = DB_COMPLEMENTOS[s_id]
                            fact = p_tot_it / sum([v for k,v in s_rec.items() if k != "c"])
                            for sk, sv in s_rec.items():
                                if sk != "c":
                                    g_s = sv * (it['can'] if "Decoración" in s_id else fact)
                                    st.write(f"- {sk}: {g_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + g_s

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{p['cliente']}**")
            u_wa = f"https://wa.me/521{p['wa']}?text="
            c2.link_button("✅ Confirmar", u_wa + urllib.parse.quote("Confirmado"))
            c3.link_button("🚀 Listo", u_wa + urllib.parse.quote("Listo!"))
            if st.button("❌", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        col_masa_v, col_comp_v = st.columns(2)
        with col_masa_v:
            st.subheader("🥣 Batidos")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.write(f"**{m_id}**")
                for etapa in m_dna.get("etapas", []):
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        st.checkbox(f"{ing}: {m_dna['receta'][ing]*h_b/100:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}_{i}")
                    st.markdown('</div>', unsafe_allow_html=True)
        with col_comp_v:
            st.subheader("✨ Complementos")
            for s_id, p_tot in lotes_comp.items():
                s_rec = DB_COMPLEMENTOS[s_id]
                st.write(f"**{s_id} ({p_tot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {s_rec["c"]};">', unsafe_allow_html=True)
                fact = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
                for sk, sv in s_rec.items():
                    if sk == "c": continue
                    st.checkbox(f"{sk}: {sv*fact:,.1f}g", key=f"sec_{s_id}_{sk}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"master_{k}")

    if st.button("🗑️ LIMPIAR TODO EL DÍA"): st.session_state.comanda = []; st.rerun()
