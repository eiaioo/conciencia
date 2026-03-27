import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN DE ESTADO (SEGURIDAD TOTAL)
# ==========================================
if 'pedidos' not in st.session_state: st.session_state['pedidos'] = []
if 'carrito' not in st.session_state: st.session_state['carrito'] = []
if 'form_key' not in st.session_state: st.session_state['form_key'] = 0
if 'tema_oscuro' not in st.session_state: st.session_state['tema_oscuro'] = True

# ==========================================
# 2. ARQUITECTURA VISUAL (MATE PROFESIONAL)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

C_BG = "#0E1117" if st.session_state.tema_oscuro else "#F0F2F6"
C_SEC = "#161B22" if st.session_state.tema_oscuro else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.tema_oscuro else "#1F2328"
C_BRD = "#30363D" if st.session_state.tema_oscuro else "#D0D7DE"

st.markdown(f"""
    <style>
    /* Aplicar fondo a todo el sitio */
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    
    /* Control de textos y etiquetas */
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    
    /* ELIMINAR BARRA BLANCA DE DATOS DEL CLIENTE */
    div[data-testid="stExpander"], .streamlit-expanderHeader, summary, details {{
        background-color: {C_SEC} !important;
        border: 1px solid {C_BRD} !important;
        color: {C_TXT} !important;
    }}
    
    /* SELECTORES Y MENÚS OSCUROS (DROPDOWNS) */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input, select {{
        background-color: {C_BG} !important;
        color: {C_TXT} !important;
        border: 1px solid {C_BRD} !important;
    }}
    div[role="listbox"], ul[role="listbox"] {{
        background-color: {C_SEC} !important;
        border: 1px solid {C_BRD} !important;
    }}
    li[role="option"] {{ color: {C_TXT} !important; background-color: {C_SEC} !important; }}

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
if c_tema.button("☀️/🌙"):
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro
    st.rerun()

# ==========================================
# 3. BASE DE DATOS TÉCNICA (AUDITORÍA TOTAL)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2}, "merma": 1.0, "tz": (0.025, 1), "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor y Grasa", "i": ["Azúcar", "Miel", "Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350)},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Chocolate Turin": 165, "Harina de fuerza": 190}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima de Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "c": "rgba(255, 179, 140, 0.3)"},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1, "c": "rgba(168, 230, 173, 0.3)"},
    "Rebozado Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5, "c": "rgba(212, 163, 115, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}, "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": []}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": {"Guayaba": ["Rebozado Muerto"]}, "tamaños": {"Estándar": 95}, "masa": "Masa Muerto Guayaba"},
    "Brownies": {"espec": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 4. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=not st.session_state.pedidos):
    fk = st.session_state.form_key
    c1, c2 = st.columns(2)
    cli_nombre = c1.text_input("Nombre del Cliente", key="cli_persist_n")
    cli_wa = c2.text_input("WhatsApp (10 dígitos)", key="cli_persist_w")

st.write("### 🍞 2. Agregar Panes al Pedido")
c_fam, c_esp, c_tam, c_can = st.columns([2,2,1.5,1])
f_sel = c_fam.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")

if f_sel != "-":
    e_sel = c_esp.selectbox("Especialidad", list(ARBOL[f_sel]["espec"].keys()), key=f"e_{fk}")
    t_sel = c_tam.selectbox("Tamaño", list(ARBOL[f_sel]["tamaños"].keys()), key=f"t_{fk}")
    n_can = c_can.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    r_sel = "N/A"
    if f_sel == "Rosca de reyes":
        r_sel = st.selectbox("Relleno", ARBOL[f_sel]["espec"][e_sel]["rellenos"], key=f"r_{fk}")
    
    if st.button("➕ AÑADIR AL CARRITO"):
        st.session_state.carrito.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "rel": r_sel, "can": n_can})
        st.session_state.form_key += 1
        st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_nombre}")
    for it in st.session_state.carrito: st.write(f"- {it['can']}x {it['fam']} {it['esp']}")
    if st.button("✅ FINALIZAR Y GUARDAR PEDIDO"):
        if cli_nombre:
            st.session_state.pedidos.append({"cliente": cli_nombre, "wa": cli_wa, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()
        else: st.error("Falta nombre del cliente")

# ==========================================
# 5. MOTOR DE PRODUCCIÓN (BATCHES)
# ==========================================

if st.session_state.pedidos:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 WhatsApp", "🥣 Producción", "🛒 Súper"])
    
    m_inv = {}
    lotes_masa = {}
    lotes_comp = {}

    for p in st.session_state.pedidos:
        for it in p['items']:
            masa_id = ARBOL[it['fam']]["masa"]
            if masa_id not in lotes_masa: lotes_masa[masa_id] = []
            it_c = it.copy(); it_c['cli'] = p['cliente']; lotes_masa[masa_id].append(it_c)
            
            # Recolectar complementos
            cfg = ARBOL[it['fam']]
            subs = cfg["espec"][it['esp']]
            lista = subs["fijos"].copy() if isinstance(subs, dict) else subs.copy()
            if it['rel'] not in ["N/A", "Sin Relleno"]: lista.append(it['rel'])
            
            for s_id in lista:
                p_u = cfg.get("p_rell_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_tot = sum([(ARBOL[i['fam']]['tamaños'][i['tam']] * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_tot * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_tot:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); m_inv[k] = m_inv.get(k, 0) + gr
            with c2:
                for it in items: st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")

    with t_cli:
        for i, p in enumerate(st.session_state.pedidos):
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{p['cliente']}**")
            u = f"https://wa.me/521{p['wa']}?text="
            c2.link_button("✅ Confirmar", u + "Pedido Recibido")
            c3.link_button("🚀 Listo", u + "Tu pan esta listo!")
            if st.button("❌", key=f"d_{i}"): st.session_state.pedidos.pop(i); st.rerun()

    with t_prod:
        st.subheader("🥣 Batidos")
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['can']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"**Masa: {m_id}**")
            for etapa in m_dna.get("etapas", []):
                st.markdown(f'<div class="etapa-box" style="background-color:{etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("✨ Complementos")
        for s_id, p_tot in lotes_comp.items():
            s_rec = DB_COMPLEMENTOS.get(s_id, {})
            if not s_rec: continue
            st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
            st.markdown(f'<div class="etapa-box" style="background-color: {s_rec.get("c", "rgba(200,200,200,0.3)")};">', unsafe_allow_html=True)
            fact = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
            for sk, sv in s_rec.items():
                if sk == "c": continue
                gr_s = sv * fact
                st.checkbox(f"{sk}: {gr_s:,.1f}g", key=f"sec_{s_id}_{sk}")
                m_inv[sk] = m_inv.get(sk, 0) + gr_s
            st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(m_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"sup_{k}")

    if st.button("🗑️ LIMPIAR TODO"): st.session_state.pedidos = []; st.rerun()
