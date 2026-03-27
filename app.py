import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DISEÑO (BLINDAJE UI)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0
if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'cli_n' not in st.session_state: st.session_state.cli_n = ""
if 'cli_w' not in st.session_state: st.session_state.cli_w = ""

# Colores Mate Profesionales
if st.session_state.tema_oscuro:
    BG_HEX, SEC_BG, TEXT_HEX, BORDER_HEX, BTN_HEX = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#3D4B53"
else:
    BG_HEX, SEC_BG, TEXT_HEX, BORDER_HEX, BTN_HEX = "#F8F9FA", "#FFFFFF", "#1F2328", "#D0D7DE", "#E0E0E0"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG_HEX} !important; color: {TEXT_HEX}; }}
    h1, h2, h3, h4, p, span, label {{ color: {TEXT_HEX} !important; }}
    
    /* Eliminar barra blanca de expanders y forzar tema */
    div[data-testid="stExpander"], .streamlit-expanderHeader, .streamlit-expanderContent {{
        background-color: {SEC_BG} !important; border: 1px solid {BORDER_HEX} !important; color: {TEXT_HEX} !important;
    }}
    
    /* Selectores y Campos de texto */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {BG_HEX} !important; color: {TEXT_HEX} !important; border: 1px solid {BORDER_HEX} !important;
    }}
    
    /* Botones de cantidad +/- */
    div[data-testid="stNumberInput"] button {{ background-color: {BTN_HEX} !important; border: none !important; color: {TEXT_HEX} !important; }}

    /* Botones de Acción */
    .stButton > button {{ background-color: {BTN_HEX} !important; color: {TEXT_HEX} !important; border: 1px solid {BORDER_HEX} !important; border-radius: 8px; }}
    
    /* Cajas de Etapas (30% opacidad) */
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; font-weight: 500; }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.92, 0.08])
if c_tema.button("☀️/🌙"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA (DNA COMPLETO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1)},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7}, "merma": 1.0, "tz": (0.07, 5)},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True},
    "Mezcla de Brownies": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Nuez Tostada": 140}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima de Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Lágrima de Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(168, 230, 173, 0.3)"},
    "Lágrima de Fresa": {"Harina": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla sin sal": 100, "c": "rgba(255, 179, 140, 0.3)"},
    "Lágrima de Mazapán Intenso": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66, "c": "rgba(212, 163, 115, 0.3)"},
    "Lágrima de Oreo": {"Harina": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Oreo": 25, "c": "rgba(165, 165, 141, 0.3)"},
    "Lágrima de Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(212, 163, 115, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "c": "rgba(162, 210, 255, 0.3)"},
    "Crema Ruby 50/50": {"Leche": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "c": "rgba(255, 179, 140, 0.3)"},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Cuerpos": 100, "Leche": 50, "Cabeza de Conejo": 1, "c": "rgba(212, 163, 115, 0.3)"},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar": 300, "Canela": 25, "c": "rgba(183, 183, 164, 0.3)"},
    "Rebozado Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5, "c": "rgba(255, 235, 156, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán Intenso", "Oreo", "Pinole"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas"},
    "Rosca de reyes": {"espec": ["Tradicional", "Chocolate", "Turín"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "m": "Masa Brioche Rosca"},
    "Berlinas": {"espec": ["Ruby v2.0", "Vainilla Clásica"], "tam": {"Estándar": 60}, "p_man": {"Ruby v2.0": 70}, "m": "Masa de Berlinas"},
    "Rollos": {"espec": ["Tradicional Canela", "Manzana", "Red Velvet"], "tam": {"Individual": 90}, "m": "Masa Brioche Roles", "m_ov": {"Red Velvet": "Masa Red Velvet"}},
    "Pan de muerto": {"espec": ["Tradicional", "Guayaba"], "tam": {"Estándar": 85}, "m": "Masa Muerto Guayaba"},
    "Brownies": {"espec": ["Chocolate Turín"], "tam": {"Molde 20x20": 1}, "m": "Mezcla de Brownies"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.subheader("🥐 Comanda Técnica CONCIENCIA")

with st.container():
    c_n, c_w = st.columns(2)
    # Persistencia real del cliente
    st.session_state.cli_n = c_n.text_input("Nombre del Cliente", value=st.session_state.cli_n)
    st.session_state.cli_w = c_w.text_input("WhatsApp", value=st.session_state.cli_w)

st.write("### 🍞 Agregar Panes al Pedido")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,1])

with col1: f_sel = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
with col2: e_sel = st.selectbox("Especialidad", ARBOL[f_sel]["espec"] if f_sel != "-" else ["-"], key=f"e_{fk}")
with col3: t_sel = st.selectbox("Tamaño", list(ARBOL[f_sel]["tam"].keys()) if f_sel != "-" else ["-"], key=f"t_{fk}")
with col4: c_sel = st.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")

# Lógica especial de Rellenos para Roscas
rel_sel = "N/A"
if f_sel == "Rosca de reyes":
    rel_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Ruby 50/50"], key=f"r_{fk}")

with col5:
    st.write("##")
    if st.button("➕"):
        if f_sel != "-":
            st.session_state.carrito.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "rel": rel_sel, "can": c_sel})
            st.session_state.form_key += 1; st.rerun()

# --- REVISIÓN DEL CARRITO ANTES DE GUARDAR ---
if st.session_state.carrito:
    st.divider()
    st.info(f"🛒 **Pedido en preparación para: {st.session_state.cli_n}**")
    for idx, p in enumerate(st.session_state.carrito):
        st.write(f"{p['can']}x {p['fam']} {p['esp']} ({p['tam']})")
    
    cb1, cb2 = st.columns(2)
    if cb1.button("✅ FINALIZAR Y GUARDAR PEDIDO"):
        if st.session_state.cli_n:
            st.session_state.comanda.append({"cliente": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()
        else: st.error("Ingresa el nombre del cliente")
    if cb2.button("🗑️ Vaciar Carrito"): st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PRODUCCIÓN (RESUMEN + DETALLE)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    master_inv = {}
    lotes_masa = {}
    lotes_comp = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']].get("m_ov", ARBOL[it['fam']]["m"])
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)
            
            # Recolectar complementos para batido consolidado
            subs = []
            if it['fam'] == "Conchas": subs.append(f"Lágrima {it['esp']}")
            if it['fam'] == "Rosca de reyes": 
                subs.append("Decoración Rosca")
                if it['rel'] != "Sin Relleno": subs.append(it['rel'].replace("Crema Pastelera ",""))
            if it['fam'] == "Rollos": subs.append("Schmear Canela")
            if it['fam'] == "Pan de muerto": subs.append("Rebozado Muerto")

            for s_id in subs:
                if s_id in DB_COMPLEMENTOS:
                    p_u = ARBOL[it['fam']].get("p_rell_map", {}).get(it['tam'], 15) if "Crema" in s_id else (ARBOL[it['fam']].get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15)
                    lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_tot = sum([(ARBOL[i['fam']].get("p_man", {}).get(i['esp'], ARBOL[i['fam']]['tam'][i['tam']]) * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_tot * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_tot:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info("Masa Principal")
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
                    # Desglose de complementos por cliente en resumen
                    cfg_it = ARBOL[it['fam']]
                    s_name = f"Lágrima {it['esp']}" if it['fam'] == "Conchas" else None
                    if s_name and s_name in DB_COMPLEMENTOS:
                        s_rec = DB_COMPLEMENTOS[s_name]
                        p_t_it = cfg_it['p_ex'][it['tam']] * it['can']
                        st.markdown(f"**{s_name} ({p_t_it:,.1f}g)**")
                        f_s = p_t_it / sum([v for k,v in s_rec.items() if k != "c"])
                        for sk, sv in s_rec.items():
                            if sk != "c":
                                g_s = sv * (it['can'] if "Decoración" in s_name else f_s)
                                st.write(f"- {sk}: {g_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + g_s

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{ped['cliente']}** — {ped['wa']}")
            url_b = f"https://wa.me/521{ped['wa']}?text="
            c2.link_button("✅ Confirmar", url_b + urllib.parse.quote(f"Hola {ped['cliente']}! Recibimos tu pedido."))
            c3.link_button("🚀 Listo", url_b + urllib.parse.quote(f"Hola {ped['cliente']}! Tu pedido está listo 🥐."))
            if st.button("❌", key=f"f_del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        cm, cc = st.columns(2)
        with cm:
            st.subheader("🥣 Batidos")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(ARBOL[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.write(f"**{m_id}**")
                for etapa in m_dna.get("etapas", []):
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        gr = m_dna['receta'][ing]*h_b/100
                        st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}_{i}")
                    st.markdown('</div>', unsafe_allow_html=True)
        with cc:
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
