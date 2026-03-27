import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN Y CONFIGURACIÓN VISUAL
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Colores Mate Profesionales
C_BG = "#0E1117" if st.session_state.tema_oscuro else "#F0F2F6"
C_SEC = "#161B22" if st.session_state.tema_oscuro else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.tema_oscuro else "#1F2328"
C_BRD = "#30363D" if st.session_state.tema_oscuro else "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    div[data-testid="stExpander"], .streamlit-expanderHeader {{
        background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important;
    }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {C_BG} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important;
    }}
    /* Botones Mate */
    .stButton > button {{ background-color: {C_SEC} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important; border-radius: 8px; }}
    /* Etapas (Opacidad 30%) */
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); color: #1a1a1a !important; font-weight: 500; }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.9, 0.1])
if c_tema.button("🌙" if st.session_state.tema_oscuro else "☀️"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA (AUDITORÍA TOTAL)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor y Fermento", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar", "Levadura fresca"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Batch Berlinas", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina", "Levadura seca"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal", "Sal fina", "Levadura fresca"], "c": "rgba(168, 230, 173, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Batch Muerto", "i": ["Harina de fuerza", "Leche entera", "Azúcar", "Mantequilla sin sal", "Polvo de Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla de Brownies": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Chocolate Turin": 165, "Harina de fuerza": 190, "Sal fina": 8, "Nuez Tostada": 140}, "merma": 1.0, "fijo": True, "etapas": [{"n": "Batch Brownie", "i": ["Mantequilla sin sal", "Azúcar Blanca", "Chocolate Turin", "Nuez Tostada"], "c": "rgba(162, 210, 255, 0.3)"}]}
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Lágrima Matcha": {"Harina de fuerza": 91.5, "Matcha en polvo": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(168, 230, 173, 0.3)"},
    "Lágrima Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66, "c": "rgba(255, 179, 140, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "c": "rgba(162, 210, 255, 0.3)"},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula de Maíz": 24, "c": "rgba(255, 179, 140, 0.3)"},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Turin Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1, "c": "rgba(212, 163, 115, 0.3)"},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25, "c": "rgba(212, 163, 115, 0.3)"},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5, "c": "rgba(183, 183, 164, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": ["Vainilla", "Chocolate", "Matcha", "Mazapán"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas"},
    "Rosca de reyes": {"espec": ["Tradicional", "Turín"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35}, "m": "Masa Brioche Rosca"},
    "Berlinas": {"espec": ["Vainilla", "Ruby v2.0"], "tam": {"Estándar": 60}, "m": "Masa de Berlinas", "p_man": {"Ruby v2.0": 70}},
    "Rollos": {"espec": ["Canela Tradicional"], "tam": {"Individual": 90}, "m": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": ["Guayaba Huesos-Ref"], "tam": {"Estándar": 95}, "m": "Masa Muerto Guayaba"},
    "Brownies": {"espec": ["Chocolate"], "tam": {"Molde 20x20": 1}, "m": "Mezcla Brownie"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.container():
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre del Cliente", key="input_cli_n")
    cli_w = c2.text_input("WhatsApp", key="input_cli_w")

st.write("### 🍞 Agregar Panes")
fk = st.session_state.form_key
c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1, 0.8])

fam_sel = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if fam_sel != "-":
    esp_sel = c4.selectbox("Especialidad", ARBOL[fam_sel]["espec"], key=f"e_{fk}")
    tam_sel = c5.selectbox("Tamaño", list(ARBOL[fam_sel]["tam"].keys()), key=f"t_{fk}")
    can_sel = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    rel_sel = "N/A"
    if fam_sel == "Rosca de reyes":
        rel_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Ruby"], key=f"r_{fk}")
    
    c7.write("##")
    if c7.button("➕"):
        st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "can": can_sel, "rel": rel_sel})
        st.session_state.form_key += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    if st.button("✅ FINALIZAR Y GUARDAR PEDIDO"):
        if cli_n:
            st.session_state.comanda.append({"cli": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE CÁLCULO TOTAL (LA SOLUCIÓN)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}
    lotes_comp = {} # Aquí agruparemos los ingredientes de las lágrimas/rellenos

    for ped in st.session_state.comanda:
        for it in ped['items']:
            # 1. Agrupar Masas
            m_id = ARBOL[it['fam']]["m"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cliente'] = ped['cli']; lotes_masa[m_id].append(it_c)
            
            # 2. Identificar Complementos (Lágrimas/Rellenos)
            subs = []
            if it['fam'] == "Conchas": subs.append(f"Lágrima {it['esp']}")
            if it['fam'] == "Rosca de reyes": 
                subs.append("Decoración Rosca")
                if it['rel'] != "Sin Relleno": subs.append(it['rel'].replace("Pastelera ", ""))
            if it['fam'] == "Berlinas" and it['esp'] == "Ruby v2.0": subs.append("Crema Ruby")
            if it['fam'] == "Rollos": subs.append("Schmear Canela")
            if it['fam'] == "Pan de muerto": subs.append("Rebozado Muerto")

            # 3. Calcular peso total de cada complemento y guardarlo
            for s_id in subs:
                if s_id not in DB_COMPLEMENTOS: continue
                # Peso unitario según tabla de ingeniería
                p_u = ARBOL[it['fam']].get("p_rell_map", {}).get(it['tam'], 15) if s_id in ["Crema Vainilla", "Crema Ruby"] else (ARBOL[it['fam']].get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15)
                lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[i['fam']].get("p_man", {}).get(i['esp'], ARBOL[i['fam']]['tam'][i['tam']]) * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_batch * 100) / sum([v for k,v in m_dna['receta'].items()])
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.write("**Masa Principal**")
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}")

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            st.write(f"👤 **{p['cli']}** — {p['wa']}")
            if st.button("❌ Borrar", key=f"d_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        col_m, col_s = st.columns(2)
        with col_m:
            st.subheader("🥣 Batidos de Masa")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(ARBOL[it['fam']].get("p_man", {}).get(it['esp'], ARBOL[it['fam']]['tam'][it['tam']]) * it['can']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.write(f"**Lote: {m_id}**")
                for etapa in m_dna["etapas"]:
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        gr = m_dna['receta'][ing]*h_b/100
                        st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                    st.markdown('</div>', unsafe_allow_html=True)

        with col_s:
            st.subheader("✨ Complementos (Lágrimas y Rellenos)")
            for s_id, p_tot in lotes_complementos.items():
                s_rec = DB_COMPLEMENTOS[s_id]
                st.write(f"**{s_id} (Total: {p_tot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {s_rec["c"]};">', unsafe_allow_html=True)
                # Cálculo de ingredientes de la lágrima/relleno
                total_porc = sum([v for k,v in s_rec.items() if k != "c"])
                fact = p_tot / total_porc
                for sk, sv in s_rec.items():
                    if sk == "c": continue
                    gr_s = sv * fact
                    st.checkbox(f"{sk}: {gr_s:,.1f}g", key=f"sec_{s_id}_{sk}")
                    master_inv[sk] = master_inv.get(sk, 0) + gr_s
                st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"master_{k}")

    if st.button("🗑️ LIMPIAR TODO"): st.session_state.comanda = []; st.rerun()
