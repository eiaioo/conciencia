import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DISEÑO (TEMA MATE)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Colores de bajo contraste auditados
if st.session_state.tema_oscuro:
    BG, SEC, TXT, BRD = "#0E1117", "#161B22", "#E6EDF3", "#30363D"
    ACC = "#E67E22"
else:
    BG, SEC, TXT, BRD = "#F8F9FA", "#FFFFFF", "#1F2328", "#D0D7DE"
    ACC = "#D35400"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {TXT} !important; }}
    
    /* Eliminar Barras Blancas y Fugas */
    div[data-testid="stExpander"], .streamlit-expanderHeader {{
        background-color: {SEC} !important;
        border: 1px solid {BRD} !important;
        color: {TXT} !important;
    }}
    
    /* Inputs y Selectores Oscuros */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {BG} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
    }}
    
    /* Botones de Cantidad (Number Input) */
    div[data-testid="stNumberInput"] button {{
        background-color: {SEC} !important;
        border: 1px solid {BRD} !important;
        color: {TXT} !important;
    }}

    /* Botones de Acción */
    .stButton > button {{
        background-color: {SEC} !important;
        color: {TXT} !important;
        border: 1px solid {BRD} !important;
        border-radius: 8px;
    }}
    .stButton > button:hover {{ border-color: {ACC} !important; color: {ACC} !important; }}

    /* Etapas de Producción (Opacidad 30%) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #1a1a1a !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.92, 0.08])
if c_tema.button("🌙" if st.session_state.tema_oscuro else "☀️"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA (RESTABLECIDA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1), "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5)},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350)},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7}, "merma": 1.0, "tz": (0.07, 5)},
    "Masa Muerto Tradicional": {"receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3}, "merma": 1.0},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Matcha": {"Harina de fuerza": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla sin sal": 100},
    "Lágrima de Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66},
    "Lágrima de Pinole": {"Harina de fuerza": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Oreo": 25},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Crema Pastelera Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla sin sal": 20},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "Mantequilla sin sal": 16, "Sal": 0.8},
    "Glaseado Ruby": {"Choco Ruby": 80, "Azúcar Glass": 160, "Leche entera": 50},
    "Glaseado Turin": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche entera": 50, "Cabeza Conejo": 1},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar": 300, "Canela": 25},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"], "Matcha": ["Lágrima de Matcha"], "Fresa": ["Lágrima de Fresa"], "Mazapán": ["Lágrima de Mazapán"], "Oreo": ["Lágrima de Oreo"], "Pinole": ["Lágrima de Pinole"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}, "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Pastelera Turin"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rel_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"], "Ruby v2.0": ["Crema Ruby 50/50", "Glaseado Ruby"], "Turín": ["Crema Pastelera Turin", "Glaseado Turin"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas", "p_ber": {"Ruby v2.0": (70, {"Crema Ruby 50/50": 40, "Glaseado Ruby": 8}), "Turín": (60, {"Crema Especial Turin": 80, "Glaseado Turin": 16}), "Vainilla": (60, {"Crema Pastelera Vainilla": 80})}},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "masa_ov": {"Red Velvet": "Masa Red Velvet"}},
    "Pan de muerto": {"espec": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto"]}, "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}},
    "Brownies": {"espec": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 3. INTERFAZ Y LÓGICA DE CAPTURA
# ==========================================

st.subheader("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre del Cliente", key="persist_cli_n")
    cli_w = c2.text_input("WhatsApp", key="persist_cli_w")

st.write("### 🍞 2. Carrito de Panes")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,0.8])

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
    st.info(f"🛒 Carrito para: **{cli_n}**")
    for i, p in enumerate(st.session_state.carrito_actual):
        st.caption(f"{p['cant']}x {p['fam']} {p['esp']} ({p['tam']})")
    
    if st.button("✅ FINALIZAR Y GUARDAR PEDIDO COMPLETO"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []
            st.rerun()

# ==========================================
# 4. LÓGICA DE PRODUCCIÓN (RESUMEN + LISTA)
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
            st.markdown(f"#### 🛠️ Lote: {m_id}")
            
            # Calcular Masa Total del Batch
            m_batch_gr = 0
            for i in items:
                p_u_m = ARBOL[i['fam']].get("p_ber", {}).get(i['esp'], (ARBOL[i['fam']]['tamaños'][i['tam']],0))[0]
                m_batch_gr += (p_u_m * i['cant']) / m_dna['merma']
            
            sum_porc = sum([v for k,v in m_dna['receta'].items()])
            h_base = (m_batch_gr * 100) / sum_porc

            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info(f"Masa ({m_batch_gr:,.1f}g)")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['cant']}x {it['esp']} ({it['tam']}) — {it['cli']}")
                    # Desglose de complementos por cliente
                    cfg = ARBOL[it['fam']]
                    list_subs = []
                    base_esp = cfg["espec"][it['esp']]
                    if isinstance(base_esp, dict): list_subs = base_esp["fijos"].copy()
                    else: list_subs = base_esp.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: list_subs.append(it['rel'])
                    
                    for s_id in list_subs:
                        if s_id not in DB_COMPLEMENTOS: continue
                        s_rec = DB_COMPLEMENTOS[s_id]
                        if it['fam'] == "Rosca de reyes" and s_id == it['rel']: p_u_ex = cfg["p_relleno_map"][it['tam']]
                        elif it['fam'] == "Conchas": p_u_ex = cfg["p_ex"][it['tam']]
                        elif "p_ber" in cfg and it['esp'] in cfg["p_ber"]: p_u_ex = cfg["p_ber"][it['esp']][1].get(s_id, 15)
                        else: p_u_ex = 15
                        
                        p_sub_tot = p_u_ex * it['cant']
                        st.markdown(f"**{s_id} ({p_sub_tot:,.1f}g)**")
                        fact = p_sub_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            g_s = val_s * fact; st.write(f"- {ing_s}: {g_s:,.1f}g"); master_inv[ing_s] = master_inv.get(ing_s, 0) + g_s

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            st.write(f"👤 **{ped['cliente']}** — {ped['wa']}")
            if st.button("❌ Borrar", key=f"f_del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_sup:
        st.header("🛒 Lista Maestra")
        for insumo, cant in sorted(master_inv.items()):
            st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"master_{insumo}")
