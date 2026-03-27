import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN Y CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'master_comanda' not in st.session_state: st.session_state.master_comanda = []
if 'carrito_temp' not in st.session_state: st.session_state.carrito_temp = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0

# Estilo Claro de Alto Contraste
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3, h4, p, span, label { color: #000000 !important; font-weight: 500; }
    div[data-testid="stExpander"] { border: 2px solid #EEEEEE !important; border-radius: 10px; }
    .stButton > button { border-radius: 8px; font-weight: bold; background-color: #F0F2F6; border: 1px solid #CCCCCC; }
    /* Etapas con Opacidad 30% */
    .etapa-box { 
        padding: 15px; border-radius: 12px; margin-bottom: 10px; 
        border: 1px solid rgba(0,0,0,0.1); color: #000 !important; 
    }
    .etapa-titulo { font-weight: bold; text-transform: uppercase; font-size: 0.8rem; opacity: 0.7; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS TÉCNICA MAESTRA
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
            {"n": "2. Sabor y Grasa", "i": ["Azúcar", "Miel", "Mantequilla sin sal", "Sal fina", "Agua Azahar", "Levadura"], "c": "rgba(165, 165, 141, 0.3)"}
        ]
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8},
        "merma": 0.85, "tz": (0.05, 5),
        "etapas": [{"n": "Batido Único", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}]
    }
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "c": "rgba(255, 179, 140, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "c": "rgba(168, 230, 173, 0.3)"}
}

CATALOGO = {
    "Conchas": {"esp": ["Vainilla", "Chocolate"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas", "sub": "Lágrima "},
    "Rosca de reyes": {"esp": ["Tradicional"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35}, "m": "Masa Brioche Rosca"},
    "Berlinas": {"esp": ["Vainilla Clásica"], "tam": {"Estándar": 60}, "m": "Masa de Berlinas"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.container():
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre del Cliente", key="input_nombre")
    cli_w = c2.text_input("WhatsApp (10 dígitos)", key="input_whatsapp")

st.write("### 🍞 Seleccionar Panes")
fk = st.session_state.form_id
c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1, 0.8])

fam = c3.selectbox("Familia", ["-"] + list(CATALOGO.keys()), key=f"f_{fk}")
if fam != "-":
    esp = c4.selectbox("Especialidad", CATALOGO[fam]["esp"], key=f"e_{fk}")
    tam = c5.selectbox("Tamaño", list(CATALOGO[fam]["tam"].keys()), key=f"t_{fk}")
    can = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    rel = "N/A"
    if fam == "Rosca de reyes":
        rel = st.selectbox("Relleno", ["Sin Relleno", "Crema Pastelera Vainilla"], key=f"r_{fk}")
    
    c7.write("##")
    if c7.button("➕"):
        st.session_state.carrito_temp.append({"fam": fam, "esp": esp, "tam": tam, "can": can, "rel": rel})
        st.session_state.form_id += 1
        st.rerun()

if st.session_state.carrito_temp:
    st.info(f"🛒 Carrito para: **{cli_n}**")
    for p in st.session_state.carrito_temp:
        st.write(f"- {p['can']}x {p['fam']} {p['esp']} ({p['tam']})")
    if st.button("✅ FINALIZAR Y GUARDAR PEDIDO"):
        if cli_n:
            st.session_state.master_comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito_temp.copy()})
            st.session_state.carrito_temp = []
            st.session_state.input_nombre = ""; st.session_state.input_whatsapp = ""
            st.rerun()

# ==========================================
# 4. MOTOR DE PRODUCCIÓN Y RESÚMENES
# ==========================================

if st.session_state.master_comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}
    lotes_complementos = {} # {id_sub: gramos_totales}

    # PROCESAMIENTO INICIAL
    for ped in st.session_state.master_comanda:
        for it in ped['items']:
            # Masa
            m_id = CATALOGO[it['fam']]["m"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)
            
            # Sub-recetas (Lágrimas, Rellenos, Decoración)
            subs_actuales = []
            cfg = CATALOGO[it['fam']]
            if it['fam'] == "Conchas": subs_actuales.append(f"Lágrima {it['esp']}")
            if it['fam'] == "Rosca de reyes": 
                subs_actuales.append("Decoración Rosca")
                if it['rel'] != "Sin Relleno": subs_actuales.append(it['rel'])
            
            for s_id in subs_actuales:
                if s_id not in DB_COMPLEMENTOS: continue
                # Peso unitario
                p_u = cfg.get("p_rell_map", {}).get(it['tam'], 15) if s_id == it.get('rel') else (cfg.get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15)
                lotes_complementos[s_id] = lotes_complementos.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(CATALOGO[it['fam']]['tam'][it['tam']] * it['can']) / m_dna['merma'] for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            c_m, c_p = st.columns([0.3, 0.7])
            with c_m:
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c_p:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
                    # Desglose de lágrima en el resumen
                    sub_id = f"Lágrima {it['esp']}" if it['fam'] == "Conchas" else None
                    if sub_id in DB_COMPLEMENTOS:
                        rec_s = DB_COMPLEMENTOS[sub_id]
                        p_t = CATALOGO[it['fam']]['p_ex'][it['tam']] * it['can']
                        f_s = p_t / sum(rec_s.values())
                        st.markdown(f"**{sub_id} ({p_t:,.1f}g)**")
                        for sk, sv in rec_s.items():
                            if sk != "c": st.write(f"- {sk}: {sv*f_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + (sv*f_s)

    with t_cli:
        for i, p in enumerate(st.session_state.master_comanda):
            c_a, c_b = st.columns([0.7, 0.3])
            c_a.write(f"👤 **{p['cliente']}** — WhatsApp: {p['wa']}")
            c_b.link_button("🚀 WhatsApp", f"https://wa.me/521{p['wa']}?text=Listo")
            if st.button("❌", key=f"d_{i}"): st.session_state.master_comanda.pop(i); st.rerun()

    with t_prod:
        col_m, col_s = st.columns(2)
        with col_m:
            st.subheader("🥣 Batidos de Masa")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(CATALOGO[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
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

    if st.button("🗑️ LIMPIAR DÍA"): st.session_state.master_comanda = []; st.rerun()
