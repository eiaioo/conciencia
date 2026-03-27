import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN VISUAL (BLINDAJE TOTAL)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'f_key' not in st.session_state: st.session_state.f_key = 0

# Paleta Mate
if st.session_state.tema == "Oscuro":
    B_APP, B_CARD, T_MAIN, B_BRD, B_INPUT = "#0E1117", "#161B22", "#FFFFFF", "#30363D", "#1C2128"
    B_ACC = "#E67E22"
else:
    B_APP, B_CARD, T_MAIN, B_BRD, B_INPUT = "#F0F2F6", "#FFFFFF", "#1F2328", "#D0D7DE", "#FFFFFF"
    B_ACC = "#D35400"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {B_APP} !important; color: {T_MAIN} !important; }}
    h1, h2, h3, h4, p, span, label, div {{ color: {T_MAIN} !important; }}
    div[data-testid="stExpander"], .streamlit-expanderHeader {{ background-color: {B_CARD} !important; border: 1px solid {B_BRD} !important; color: {T_MAIN} !important; }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input, select {{ background-color: {B_APP} !important; color: {T_MAIN} !important; border: 1px solid {B_BRD} !important; }}
    div[role="listbox"], ul[role="listbox"] {{ background-color: {B_CARD} !important; border: 1px solid {B_BRD} !important; }}
    li[role="option"] {{ color: {T_MAIN} !important; background-color: {B_CARD} !important; }}
    li[role="option"]:hover {{ background-color: {B_BRD} !important; }}
    div[data-testid="stNumberInput"] button {{ background-color: {B_BRD} !important; color: {T_MAIN} !important; border: none; }}
    .stButton > button {{ background-color: {B_CARD} !important; color: {T_MAIN} !important; border: 1px solid {B_BRD} !important; border-radius: 8px; }}
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; font-weight: 600; }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_t = st.columns([0.9, 0.1])
if c_t.button("☀️/🌙"):
    st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA (DNA COMPLETO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor y Grasa", "i": ["Azúcar", "Miel", "Mantequilla sin sal", "Sal fina", "Agua Azahar", "Levadura"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(168, 230, 173, 0.3)"}]},
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Lágrima Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100, "c": "rgba(168, 230, 173, 0.3)"},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "c": "rgba(255, 179, 140, 0.3)"},
    "Crema Ruby": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "c": "rgba(255, 179, 140, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "c": "rgba(212, 163, 115, 0.3)"},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar Mascabada": 300, "Canela": 25, "c": "rgba(183, 183, 164, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima Vainilla"], "Chocolate": ["Lágrima Chocolate"], "Matcha": ["Lágrima Matcha"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Vainilla"]}}, "tamaños": {"FAM": 1450, "MED": 650, "MINI": 120}, "p_rell_map": {"FAM": 450, "MED": 200, "MINI": 35}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Ruby v2.0": ["Crema Ruby"]}, "tamaños": {"Estándar": 70}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.header("🥐 Comanda Técnica CONCIENCIA")

with st.container():
    c1, c2 = st.columns(2)
    cli_nombre = c1.text_input("Nombre", key=f"cli_name_input_{st.session_state.form_key}")
    cli_wa = c2.text_input("WhatsApp", key=f"cli_wa_input_{st.session_state.form_key}")

st.write("### 🍞 Agregar Panes")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,1.5,1,1])

fam_sel = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"fam_{fk}")
if fam_sel != "-":
    esp_sel = col2.selectbox("Especialidad", list(ARBOL[fam_sel]["espec"].keys()), key=f"esp_{fk}")
    tam_sel = col3.selectbox("Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()), key=f"tam_{fk}")
    can_sel = col4.number_input("Cant", min_value=1, value=1, key=f"cant_{fk}")
    
    rel_sel = "Sin Relleno"
    if fam_sel == "Rosca de reyes":
        rel_sel = st.selectbox("Relleno", ARBOL[fam_sel]["espec"][esp_sel]["rellenos"], key=f"rel_{fk}")

    if col5.button("➕ AGREGAR"):
        st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rel": rel_sel, "can": can_sel})
        st.session_state.form_key += 1
        st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_nombre}")
    if st.button("✅ GUARDAR PEDIDO FINAL"):
        if cli_nombre:
            st.session_state.comanda.append({"cli": cli_nombre, "wa": cli_wa, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []
            st.rerun()

# ==========================================
# 4. MOTOR DE PROCESAMIENTO (LA MAGIA)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}
    lotes_complementos = {} # {id_extra: gramos_totales}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cliente'] = ped['cli']; lotes_masa[m_id].append(it_c)
            
            # Recolectar complementos para el batch
            cfg = ARBOL[it['fam']]
            espec_data = cfg["espec"][it['esp']]
            lista_subs = espec_data["fijos"].copy() if isinstance(espec_data, dict) else espec_data.copy()
            if it['rel'] != "Sin Relleno" and it['rel'] != "N/A": lista_subs.append(it['rel'])
            
            for s_id in lista_subs:
                # Peso unitario según tabla
                if it['fam'] == "Rosca de reyes" and s_id == it['rel']:
                    p_u = cfg["p_rell_map"][it['tam']]
                else:
                    p_u = cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15)
                
                lotes_complementos[s_id] = lotes_complementos.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[i['fam']]['tamaños'][i['tam']] * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info("Masa Principal")
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}")
                    # MOSTRAR SUB-RECETAS EN EL RESUMEN
                    cfg_it = ARBOL[it['fam']]
                    espec_it = cfg_it["espec"][it['esp']]
                    l_it = espec_it["fijos"].copy() if isinstance(espec_it, dict) else espec_it.copy()
                    if it['rel'] != "Sin Relleno": l_it.append(it['rel'])
                    for s_id in l_it:
                        if s_id in DB_COMPLEMENTOS:
                            p_u_it = cfg_it.get("p_rell_map", {}).get(it['tam'], 15) if s_id == it['rel'] else (cfg_it.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg_it.get("p_ex"), dict) else cfg_it.get("p_ex", 15))
                            p_tot = p_u_it * it['can']
                            st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                            s_rec = DB_COMPLEMENTOS[s_id]
                            f_s = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
                            for sk, sv in s_rec.items():
                                if sk != "c": st.write(f"- {sk}: {sv*f_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + (sv*f_s)

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            st.write(f"👤 **{p['cli']}** — WA: {p['wa']}")
            if st.button("❌ Borrar", key=f"d_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        col_m, col_s = st.columns(2)
        with col_m:
            st.subheader("🥣 Masas")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.write(f"**{m_id}**")
                for etapa in m_dna.get("etapas", []):
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        st.checkbox(f"{ing}: {m_dna['receta'][ing]*h_b/100:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        with col_s:
            st.subheader("✨ Complementos")
            for s_id, p_tot in lotes_complementos.items():
                s_rec = DB_COMPLEMENTOS.get(s_id, {})
                if not s_rec: continue
                st.write(f"**{s_id} ({p_tot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {s_rec.get("c", "rgba(200,200,200,0.3)")};">', unsafe_allow_html=True)
                fact = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
                for sk, sv in s_rec.items():
                    if sk == "c": continue
                    st.checkbox(f"{sk}: {sv*fact:,.1f}g", key=f"sec_{s_id}_{sk}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: {v:,.1f}g", key=f"m_{k}")

    if st.button("🗑️ LIMPIAR TODO"): st.session_state.comanda = []; st.rerun()
