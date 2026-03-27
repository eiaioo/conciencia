import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN DE VARIABLES (SEGURIDAD)
# ==========================================
if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0
if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'cli_n' not in st.session_state: st.session_state.cli_n = ""
if 'cli_w' not in st.session_state: st.session_state.cli_w = ""

# ==========================================
# 2. DISEÑO VISUAL (MODO MATE)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

C_BG = "#0E1117" if st.session_state.tema_oscuro else "#F0F2F6"
C_SEC = "#161B22" if st.session_state.tema_oscuro else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.tema_oscuro else "#1F2328"
C_BRD = "#30363D" if st.session_state.tema_oscuro else "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    
    /* Eliminar barras blancas */
    div[data-testid="stExpander"], .streamlit-expanderHeader, .streamlit-expanderContent {{
        background-color: {C_SEC} !important;
        border: 1px solid {C_BRD} !important;
        color: {C_TXT} !important;
    }}
    
    /* Inputs y Selectores */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {C_BG} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
    }}
    
    /* Botones de cantidad +/- */
    div[data-testid="stNumberInput"] button {{ background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important; }}

    /* Botones de Acción */
    .stButton > button {{ background-color: {C_SEC} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important; border-radius: 8px; }}
    .stButton > button:hover {{ border-color: #E67E22 !important; color: #E67E22 !important; }}

    /* Etapas de Producción (30% opacidad) */
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; font-weight: 500; }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.9, 0.1])
if c_tema.button("🌙" if st.session_state.tema_oscuro else "☀️"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 3. BASE DE DATOS TÉCNICA (DNA COMPLETO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar", "Levadura"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina", "Levadura seca"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(168, 230, 173, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Masa Muerto", "i": ["Harina de fuerza", "Leche entera", "Azúcar", "Polvo Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Chocolate Turin": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Lágrima Matcha": {"Harina de fuerza": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(168, 230, 173, 0.3)"},
    "Lágrima Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla sin sal": 100, "c": "rgba(255, 179, 140, 0.3)"},
    "Lágrima Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66, "c": "rgba(212, 163, 115, 0.3)"},
    "Crema Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "c": "rgba(255, 179, 140, 0.3)"},
    "Crema Ruby": {"Leche entera": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "c": "rgba(168, 230, 173, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "c": "rgba(212, 163, 115, 0.3)"},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar": 300, "Canela": 25, "c": "rgba(183, 183, 164, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán", "Oreo", "Pinole"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas"},
    "Rosca de reyes": {"espec": ["Tradicional", "Chocolate", "Turín"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "m": "Masa Brioche Rosca"},
    "Berlinas": {"espec": ["Vainilla", "Ruby v2.0"], "tam": {"Estándar": 60}, "m": "Masa de Berlinas", "p_man": {"Ruby v2.0": 70}},
    "Rollos": {"espec": ["Canela", "Manzana", "Red Velvet"], "tam": {"Individual": 90}, "m": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": ["Guayaba Huesos-Ref"], "tam": {"Estándar": 95}, "m": "Masa Muerto Guayaba"},
    "Brownies": {"espec": ["Chocolate Turin"], "tam": {"Molde 20x20": 1}, "m": "Mezcla Brownie"}
}

# ==========================================
# 4. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.container():
    c1, c2 = st.columns(2)
    # Persistencia real: el valor se guarda en session_state directamente
    st.session_state.cli_n = c1.text_input("Nombre Cliente", value=st.session_state.cli_n)
    st.session_state.cli_w = c2.text_input("WhatsApp", value=st.session_state.cli_w)

st.write("### 🍞 Agregar Panes")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,2,1.5,0.8])
fam_sel = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")

if fam_sel != "-":
    esp_sel = col2.selectbox("Especialidad", ARBOL[fam_sel]["espec"], key=f"e_{fk}")
    tam_sel = col3.selectbox("Tamaño", list(ARBOL[fam_sel]["tam"].keys()), key=f"t_{fk}")
    can_sel = col4.number_input("Cant.", min_value=1, value=1, key=f"c_{fk}")
    rel_sel = "N/A"
    if fam_sel == "Rosca de reyes": rel_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Vainilla", "Crema Ruby"], key=f"r_{fk}")
    
    if col5.button("➕"):
        st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rel": rel_sel, "can": can_sel})
        st.session_state.form_key += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {st.session_state.cli_n}")
    if st.button("✅ FINALIZAR Y GUARDAR PEDIDO"):
        if st.session_state.cli_n:
            st.session_state.comanda.append({"cliente": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()

# ==========================================
# 5. MOTOR DE PRODUCCIÓN (RESUMEN + DETALLE)
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
            
            # Recolectar complementos para el batch
            subs = []
            if it['fam'] == "Conchas": subs.append(f"Lágrima {it['esp']}")
            if it['fam'] == "Rosca de reyes": 
                subs.append("Decoración Rosca")
                if it['rel'] != "Sin Relleno": subs.append(it['rel'])
            if it['fam'] == "Berlinas" and it['esp'] == "Ruby v2.0": subs.append("Crema Ruby")
            if it['fam'] == "Rollos": subs.append("Schmear Canela")
            
            for s_id in subs:
                if s_id in DB_COMPLEMENTOS:
                    p_u = ARBOL[it['fam']].get("p_rell_map", {}).get(it['tam'], 15) if "Crema" in s_id else (ARBOL[it['fam']].get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15)
                    lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[i['fam']].get("p_man", {}).get(i['esp'], ARBOL[i['fam']]['tam'][i['tam']]) * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            c_izq, c_der = st.columns([0.3, 0.7])
            with c_izq:
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c_der:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
                    # Desglose de ingredientes de lágrimas/rellenos por cliente
                    cfg_it = ARBOL[it['fam']]
                    s_name = f"Lágrima {it['esp']}" if it['fam'] == "Conchas" else None
                    if s_name and s_name in DB_COMPLEMENTOS:
                        s_rec = DB_COMPLEMENTOS[s_name]
                        p_t = cfg_it['p_ex'][it['tam']] * it['can']
                        f_s = p_t / sum([v for k,v in s_rec.items() if k != "c"])
                        st.markdown(f"**{s_name} ({p_t:,.1f}g):**")
                        for sk, sv in s_rec.items():
                            if sk != "c": st.write(f"- {sk}: {sv*f_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + (sv*f_s)

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            c_a, c_b, c_c = st.columns([0.4, 0.3, 0.3])
            c_a.write(f"👤 **{p['cliente']}**")
            u = f"https://wa.me/521{p['wa']}?text="
            c_b.link_button("✅ Confirmar", u + "Recibido")
            c_c.link_button("🚀 Listo", u + "Listo!")
            if st.button("❌", key=f"d_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        col_m, col_s = st.columns(2)
        with col_m:
            st.subheader("🥣 Batidos")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(ARBOL[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.write(f"**Lote: {m_id}**")
                for etapa in m_dna.get("etapas", []):
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        st.checkbox(f"{ing}: {m_dna['receta'][ing]*h_b/100:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        with col_s:
            st.subheader("✨ Complementos")
            for s_id, p_tot in lotes_comp.items():
                s_rec = DB_COMPLEMENTOS[s_id]
                st.write(f"**{s_id} ({p_tot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {s_rec["c"]};">', unsafe_allow_html=True)
                f_s = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
                for sk, sv in s_rec.items():
                    if sk == "c": continue
                    st.checkbox(f"{sk}: {sv*f_s:,.1f}g", key=f"sec_{s_id}_{sk}")
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"master_{k}")

    if st.button("🗑️ LIMPIAR TODO EL DÍA"): st.session_state.comanda = []; st.rerun()
