import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN E INTERVENCIÓN DE ESTILOS (PRO)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'f_key' not in st.session_state: st.session_state.f_key = 0

# Definición de Colores Maestro
if st.session_state.tema == "Oscuro":
    BG, SEC, TXT, BRD, BTN = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#21262D"
    ACC, SHADOW = "#E67E22", "rgba(0,0,0,0.5)"
else:
    BG, SEC, TXT, BRD, BTN = "#F8F9FA", "#FFFFFF", "#1F2328", "#D0D7DE", "#F0F2F6"
    ACC, SHADOW = "#D35400", "rgba(0,0,0,0.1)"

st.markdown(f"""
    <style>
    /* Global */
    .stApp {{ background-color: {BG} !important; color: {TXT} !important; }}
    [data-testid="stSidebar"] {{ background-color: {SEC} !important; border-right: 1px solid {BRD} !important; }}
    
    /* Texto */
    h1, h2, h3, h4, p, span, label, li {{ color: {TXT} !important; font-family: 'Inter', sans-serif; }}

    /* Elementos de Selección y Cuadros */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {BG} !important; color: {TXT} !important; border-color: {BRD} !important;
    }}
    /* Dropdown Menus */
    div[role="listbox"], ul[role="listbox"] {{ background-color: {SEC} !important; border: 1px solid {BRD} !important; }}
    li[role="option"] {{ color: {TXT} !important; background-color: {SEC} !important; }}
    li[role="option"]:hover {{ background-color: {BRD} !important; }}

    /* Expanders (Barras de cliente) */
    div[data-testid="stExpander"], .streamlit-expanderHeader {{
        background-color: {SEC} !important; border: 1px solid {BRD} !important; border-radius: 10px !important; color: {TXT} !important;
    }}

    /* Botones */
    .stButton > button {{
        background-color: {BTN} !important; color: {TXT} !important; border: 1px solid {BRD} !important;
        border-radius: 8px; width: 100%; transition: 0.2s;
    }}
    .stButton > button:hover {{ border-color: {ACC} !important; color: {ACC} !important; }}
    
    /* Etapa Box (Opacidad 30%) */
    .etapa-box {{ 
        padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid {BRD}; 
        color: #1a1a1a !important; font-weight: 500; box-shadow: 2px 2px 5px {SHADOW};
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS TÉCNICA (DNA RESTAURADO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz_r": (0.025, 1),
        "etapas": [{"n": "Masa Principal", "i": ["Harina de fuerza", "Huevo", "Yemas", "Azúcar", "Sal fina", "Agua Azahar", "Leche entera", "Mantequilla sin sal", "Levadura fresca"], "c": "rgba(168, 230, 173, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8}, "merma": 0.85, "tz_r": (0.05, 5), "etapas": [{"n": "Lote Batido", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}]}
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "col": "rgba(255, 235, 156, 0.3)"},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "col": "rgba(162, 210, 255, 0.3)"},
    "Lágrima Matcha": {"Harina de fuerza": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "col": "rgba(168, 230, 173, 0.3)"},
    "Lágrima Mazapán": {"Harina de fuerza": 100, "Mazapán": 66, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "col": "rgba(255, 179, 140, 0.3)"},
    "Lágrima Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100, "col": "rgba(212, 163, 115, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "col": "rgba(168, 230, 173, 0.3)"},
    "Crema Ruby 50/50": {"Leche": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "col": "rgba(255, 179, 140, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "col": "rgba(200, 200, 200, 0.3)"}
}

ARBOL = {
    "Conchas": {"esp": ["Vainilla", "Chocolate", "Matcha", "Mazapán", "Pinole"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"esp": ["Tradicional"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rel_m": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"esp": ["Vainilla", "Ruby v2.0"], "tam": {"Estándar": 60}, "p_man": {"Ruby v2.0": 70}, "masa": "Masa de Berlinas"}
}

# ==========================================
# 3. NAVEGACIÓN Y CAPTURA
# ==========================================

with st.sidebar:
    st.title("👨‍🍳 MENÚ")
    pagina = st.radio("Secciones:", ["📋 Resumen Visual", "🥣 Producción Detallada", "📞 Gestión Clientes", "🛒 Súper (Total)"])
    st.divider()
    if st.button("☀️/🌙 " + st.session_state.tema):
        st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
        st.rerun()
    if st.button("🗑️ Vaciar Datos"): st.session_state.comanda = []; st.rerun()

# --- Bloque de Registro ---
with st.expander("📝 1. Datos del Cliente", expanded=not st.session_state.comanda):
    c1, c2 = st.columns(2)
    c_nom = c1.text_input("Nombre", key="input_cli")
    c_tel = c2.text_input("Celular (10 dígitos)", key="input_wa")

st.write("### 🍞 2. Carrito de Pedido")
fk = st.session_state.f_key
cc1, cc2, cc3, cc4, cc5 = st.columns([2, 2, 1.5, 1, 0.5])
f_sel = cc1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")

if f_sel != "-":
    e_sel = cc2.selectbox("Sabor", ARBOL[f_sel]["esp"], key=f"e_{fk}")
    t_sel = cc3.selectbox("Tamaño", list(ARBOL[f_sel]["tam"].keys()), key=f"t_{fk}")
    can = cc4.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    r_sel = "N/A"
    if f_sel == "Rosca de reyes":
        r_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Pastelera Vainilla"], key=f"r_{fk}")
    
    if cc5.button("➕", key=f"btn_{fk}"):
        st.session_state.carrito.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "rel": r_sel, "can": can})
        st.session_state.f_key += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Armando pedido para {c_nom}")
    if st.button("✅ FINALIZAR Y GUARDAR CLIENTE"):
        if c_nom:
            st.session_state.comanda.append({"cli": c_nom, "wa": c_tel, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PROCESAMIENTO CENTRAL
# ==========================================

if st.session_state.comanda:
    st.divider()
    inv_final = {}
    lotes_masa = {}
    lotes_comp = {} # {id_extra: gramos_totales}

    for p in st.session_state.comanda:
        for it in p['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_f = it.copy(); it_f['cliente'] = p['cli']; lotes_masa[m_id].append(it_f)
            
            # Recolectar complementos
            subs = []
            if it['fam'] == "Conchas": subs.append(f"Lágrima {it['esp']}")
            if it['fam'] == "Rosca de reyes": 
                subs.append("Decoración Rosca")
                if it['rel'] != "Sin Relleno": subs.append(it['rel'].replace("Crema Pastelera ", "Crema "))
            if it['fam'] == "Berlinas": subs.append("Crema Ruby" if "Ruby" in it['esp'] else "Crema Vainilla")
            
            for s_id in subs:
                if s_id in DB_COMPLEMENTOS:
                    p_unit = ARBOL[it['fam']].get("p_rel_m", {}).get(it['tam'], 15) if "Crema" in s_id else (ARBOL[it['fam']].get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15)
                    lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_unit * it['can'])

    # --- RENDERIZADO POR PÁGINA ---
    if pagina == "📋 Resumen Visual":
        for mid, items in lotes_masa.items():
            mdna = DB_MASAS[mid]
            mtot = sum([(ARBOL[it['fam']].get("p_man", {}).get(it['esp'], ARBOL[it['fam']]['tam'][it['tam']]) * it['can']) / mdna['merma'] for it in items])
            hb = (mtot * 100) / sum(mdna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {mid} ({mtot:,.1f}g)")
            c_l, c_r = st.columns([0.3, 0.7])
            with c_l:
                st.info("Ingredientes Masa")
                for k,v in mdna['receta'].items(): 
                    gr = v*hb/100; st.write(f"• {k}: {gr:,.1f}g"); inv_final[k] = inv_final.get(k,0)+gr
            with c_r:
                for it in items:
                    st.success(f"**{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}**")
                    sub_n = f"Lágrima {it['esp']}" if it['fam'] == "Conchas" else None
                    if sub_n and sub_n in DB_COMPLEMENTOS:
                        r_s = DB_COMPLEMENTOS[sub_n]; pt = ARBOL[it['fam']]['p_ex'][it['tam']] * it['can']
                        st.markdown(f"**{sub_n} ({pt:,.1f}g)**")
                        f_s = pt / sum(r_s.values())
                        for sk, sv in r_s.items(): 
                            if sk != 'col': st.write(f"- {sk}: {sv*f_s:,.1f}g"); inv_final[sk] = inv_final.get(sk,0)+sv*f_s

    elif pagina == "🥣 Producción Detallada":
        cl1, cl2 = st.columns(2)
        with cl1:
            st.subheader("🥣 Batidos")
            for mid, items in lotes_masa.items():
                mdna = DB_MASAS[mid]; m_bt = sum([(ARBOL[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
                hb_l = (m_bt*100)/sum(mdna['receta'].values())
                st.write(f"**{mid}**")
                for et in mdna.get("etapas", []):
                    st.markdown(f'<div class="etapa-box" style="background-color: {et["c"]};"><small>{et["n"]}</small>', unsafe_allow_html=True)
                    for ing in et['i']: st.checkbox(f"{ing}: {mdna['receta'][ing]*hb_l/100:,.1f}g", key=f"p_{mid}_{ing}_{it['can']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        with cl2:
            st.subheader("✨ Complementos")
            for sid, ptot in lotes_comp.items():
                st.write(f"**{sid} ({ptot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {DB_COMPLEMENTOS[sid].get("c","rgba(200,200,200,0.3)")};">', unsafe_allow_html=True)
                fact = ptot / sum([v for k,v in DB_COMPLEMENTOS[sid].items() if k != "col" and k != "c"])
                for sk, sv in DB_COMPLEMENTOS[sid].items():
                    if sk not in ["col","c"]: 
                        st.checkbox(f"{sk}: {sv*fact:,.1f}g", key=f"se_{sid}_{sk}"); inv_final[sk] = inv_final.get(sk,0)+sv*fact
                st.markdown('</div>', unsafe_allow_html=True)

    elif pagina == "📞 Gestión Clientes":
        for i, ped in enumerate(st.session_state.comanda):
            with st.container(border=True):
                ca, cb, cc = st.columns([0.4, 0.3, 0.3])
                ped_list = "\n".join([f"• {it['can']}x {it['esp']} ({it['tam']})" for it in ped['items']])
                ca.write(f"👤 **{ped['cli']}**"); ca.caption(ped_list)
                u = f"https://wa.me/521{ped['wa']}?text="
                cb.link_button("✅ Confirmar", u + urllib.parse.quote(f"Hola {ped['cli']}! Recibimos pedido:\n{ped_list}"))
                cc.link_button("🚀 Listo", u + urllib.parse.quote(f"Hola {ped['cli']}! Pedido listo 🥐."))
                if st.button("❌", key=f"dl_{i}"): st.session_state.comanda.pop(i); st.rerun()

    elif pagina == "🛒 Súper (Total)":
        st.header("🛒 Insumos Totales")
        # Forzar re-cálculo masivo aquí para garantizar la lista maestra
        for k, v in sorted(inv_final.items()): st.checkbox(f"{k}: **{v:,.1f}g**", key=f"mi_{k}")
