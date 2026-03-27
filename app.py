import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN DE ESTADO (PROTECCIÓN TOTAL)
# ==========================================
if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0
if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True

# ==========================================
# 2. CONFIGURACIÓN VISUAL Y CSS AGRESIVO
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

C_BG = "#0E1117" if st.session_state.tema_oscuro else "#F0F2F6"
C_SEC = "#161B22" if st.session_state.tema_oscuro else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.tema_oscuro else "#1F2328"
C_BRD = "#30363D" if st.session_state.tema_oscuro else "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT} !important; }}
    h1, h2, h3, h4, p, span, label, div {{ color: {C_TXT} !important; }}
    
    /* ELIMINAR BARRAS BLANCAS DE EXPANDERS Y CABECERAS */
    div[data-testid="stExpander"], .streamlit-expanderHeader, .streamlit-expanderContent, details, summary {{
        background-color: {C_SEC} !important;
        border: 1px solid {C_BRD} !important;
        color: {C_TXT} !important;
    }}
    
    /* INPUTS Y SELECTORES OSCUROS */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input, select {{
        background-color: {C_BG} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
    }}

    /* BOTONES MATE */
    .stButton > button {{
        background-color: {C_SEC} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
        border-radius: 8px;
    }}
    
    /* ETAPAS (OPACIDAD 30%) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #1a1a1a !important; font-weight: 500;
    }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_tema = st.columns([0.9, 0.1])
if c_tema.button("🌙" if st.session_state.tema_oscuro else "☀️"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 3. BASE DE DATOS MAESTRA (DNA CONCIENCIA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "merma": 1.0, "factor": 1.963,
        "etapas": [
            {"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"},
            {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"},
            {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"},
            {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}
        ]
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "merma": 1.0, "tz": (0.025, 1),
        "etapas": [
            {"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"},
            {"n": "2. Sabor y Grasa", "i": ["Azúcar", "Miel", "Mantequilla sin sal", "Sal fina", "Agua Azahar"], "c": "rgba(107, 112, 92, 0.3)"}
        ]
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina", "Levadura seca"], "c": "rgba(162, 210, 255, 0.3)"}]
    },
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal", "Sal fina", "Levadura fresca"], "c": "rgba(168, 230, 173, 0.3)"}]},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7}, "merma": 1.0, "tz": (0.07, 5), "etapas": [{"n": "Masa Red Velvet", "i": ["Harina de fuerza", "Cacao", "Colorante Rojo"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Masa Guayaba", "i": ["Harina de fuerza", "Polvo de Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin": 165, "Harina de fuerza": 190, "Cocoa": 75, "Sal fina": 8, "Nuez": 140}, "merma": 1.0, "fijo": True, "etapas": [{"n": "Batch Fijo", "i": ["Mantequilla sin sal", "Chocolate Turin", "Nuez"], "c": "rgba(162, 210, 255, 0.3)"}]}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}, "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Ruby 50/50"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Ruby v2.0": ["Crema Ruby 50/50"]}, "tamaños": {"Estándar": 70}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": {"Guayaba": ["Rebozado Muerto"]}, "tamaños": {"Estándar": 95}, "masa": "Masa Muerto Guayaba"},
    "Brownies": {"espec": {"Turín": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 4. INTERFAZ Y LÓGICA DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre", key="cli_persist_n")
    cli_w = c2.text_input("WhatsApp", key="cli_persist_w")

st.write("### 🍞 2. Agregar Panes al Carrito")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,1.5,1,0.5])

fam_sel = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if fam_sel != "-":
    esp_sel = col2.selectbox("Especialidad", list(ARBOL[fam_sel]["espec"].keys()), key=f"e_{fk}")
    tam_sel = col3.selectbox("Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()), key=f"t_{fk}")
    can_sel = col4.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    rel_sel = "N/A"
    if fam_sel == "Rosca de reyes":
        rel_sel = st.selectbox("Relleno", ARBOL[fam_sel]["espec"][esp_sel]["rellenos"], key=f"r_{fk}")

    if col5.button("➕", key=f"add_{fk}"):
        st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rel": rel_sel, "can": can_sel})
        st.session_state.form_key += 1
        st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Pedido Actual para: {cli_n}")
    if st.button("✅ GUARDAR PEDIDO FINAL"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 5. MOTOR DE PRODUCCIÓN (BATCHES)
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[i['fam']]['tamaños'][i['tam']] * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            
            st.markdown(f"#### 🛠️ Lote: {m_id}")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info(f"Masa ({m_batch:,.1f}g)")
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
                    # Desglose de complementos
                    cfg = ARBOL[it['fam']]
                    lista_subs = cfg["espec"][it['esp']]
                    lista = lista_subs["fijos"].copy() if isinstance(lista_subs, dict) else lista_subs.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: lista.append(it['rel'])
                    for s_id in lista:
                        p_u = cfg.get("p_rell_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['can']; st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for sk, sv in s_rec.items():
                            g_s = sv * fact; st.write(f"- {sk}: {g_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + g_s

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{p['cliente']}**")
            u = f"https://wa.me/521{p['wa']}?text="
            c2.link_button("✅ Confirmar", u + "Recibido")
            c3.link_button("🚀 Listo", u + "Listo")
            if st.button("❌", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            if "etapas" in m_dna:
                for etapa in m_dna["etapas"]:
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        st.checkbox(f"{ing}: {(m_dna['receta'][ing]*h_b/100):,.1f}g", key=f"chk_{m_id}_{ing}_{i}_{etapa['n']}")
                    st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: {v:,.1f}g", key=f"sup_{k}")

    if st.button("🗑️ LIMPIAR TODO"): st.session_state.comanda = []; st.rerun()
