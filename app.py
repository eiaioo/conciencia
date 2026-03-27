import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN VISUAL (BLINDAJE DE COLOR)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Paleta Mate Técnica
if st.session_state.tema == "Oscuro":
    C_BG, C_SEC, C_TXT, C_BRD = "#0E1117", "#161B22", "#E6EDF3", "#30363D"
    C_ACC = "#E67E22"
else:
    C_BG, C_SEC, C_TXT, C_BRD = "#F8F9FA", "#FFFFFF", "#1F2328", "#D0D7DE"
    C_ACC = "#D35400"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    
    /* ELIMINAR BARRA BLANCA DE EXPANDERS (FUERZA BRUTA) */
    div[data-testid="stExpander"], .streamlit-expanderHeader, .streamlit-expanderContent {{
        background-color: {C_SEC} !important;
        border: 1px solid {C_BRD} !important;
        color: {C_TXT} !important;
    }}
    
    /* INPUTS Y SELECTORES OSCUROS */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
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

    /* CAJAS DE ETAPAS (OPACIDAD 30%) */
    .etapa-box {{
        padding: 15px; border-radius: 12px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.05);
        color: #1a1a1a !important; font-weight: 500;
    }}
    </style>
""", unsafe_allow_html=True)

# Botón de Cambio de Tema
_, c_t = st.columns([0.9, 0.1])
if c_t.button("☀️/🌙"):
    st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA (AUDITORÍA TOTAL)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor y Fermento", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar", "Levadura fresca"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina", "Levadura seca"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal", "Sal fina", "Levadura fresca"], "c": "rgba(168, 230, 173, 0.3)"}]},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao en polvo": 0.8, "Colorante Rojo": 0.7}, "merma": 1.0, "tz": (0.07, 5), "etapas": [{"n": "Masa RV", "i": ["Harina de fuerza", "Cacao en polvo", "Colorante Rojo"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Masa Guayaba", "i": ["Harina de fuerza", "Leche entera", "Yemas", "Polvo de Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin": 165, "Harina de fuerza": 190, "Cocoa": 75, "Sal fina": 8}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Matcha": {"Harina de fuerza": 91.5, "Matcha en polvo": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla sin sal": 100},
    "Lágrima de Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66},
    "Lágrima de Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Galleta Oreo": 25},
    "Lágrima de Pinole": {"Harina de fuerza": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30},
    "Crema Pastelera Chocolate": {"Leche entera": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Chocolate 60%": 120},
    "Crema Pastelera Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Chocolate Turin": 120},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Glaseado Ruby": {"Chocolate Ruby": 80, "Azúcar Glass": 160, "Leche entera": 50},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Turin Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2},
    "Inclusión Manzana": {"Orejón": 8, "Agua tibia": 2},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"], "Matcha": ["Lágrima de Matcha"], "Fresa": ["Lágrima de Fresa"], "Mazapán": ["Lágrima de Mazapán"], "Oreo": ["Lágrima de Oreo"], "Pinole": ["Lágrima de Pinole"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate"]}, "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Pastelera Turin"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Ruby v2.0": ["Crema Ruby 50/50", "Glaseado Ruby"], "Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "p_ber_man": {"Ruby v2.0": 70}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Canela Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"], "Manzana Canela": ["Schmear Canela", "Inclusión Manzana"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": {"Guayaba Huesos-Ref": ["Rebozado Muerto"]}, "tamaños": {"Estándar": 95}, "masa": "Masa Muerto Guayaba"},
    "Brownies": {"espec": {"Chocolate Turín": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla de Brownies"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre", key="cli_persist_n")
    cli_w = c2.text_input("WhatsApp", key="cli_persist_w")

st.write("### 🍞 2. Agregar Panes")
fk = st.session_state.form_key
col1, col2, col3, col4, col5 = st.columns([2,2,1.5,1,1])

with col1: fam_sel = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if fam_sel != "-":
    with col2: esp_sel = st.selectbox("Especialidad", list(ARBOL[fam_sel]["espec"].keys()), key=f"e_{fk}")
    with col3: tam_sel = st.selectbox("Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()), key=f"t_{fk}")
    with col4: can_sel = st.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    rel_sel = "N/A"
    if fam_sel == "Rosca de reyes":
        with col2: rel_sel = st.selectbox("Relleno", ARBOL[fam_sel]["espec"][esp_sel]["rellenos"], key=f"r_{fk}")
    
    if col5.button("➕ AGREGAR"):
        st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rel": rel_sel, "can": can_sel})
        st.session_state.form_key += 1
        st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    for p in st.session_state.carrito: st.write(f"• {p['can']}x {p['esp']} ({p['tam']})")
    if st.button("✅ GUARDAR PEDIDO FINAL"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PRODUCCIÓN (RESUMEN + DETALLE)
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}
    lotes_comp = {}

    # Agrupar datos para cálculo
    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)
            
            # Recolectar complementos
            cfg = ARBOL[it['fam']]
            lista = cfg["espec"][it['esp']]
            lista_final = lista["fijos"].copy() if isinstance(lista, dict) else lista.copy()
            if it['rel'] not in ["N/A", "Sin Relleno"]: lista_final.append(it['rel'])
            
            for s_id in lista_final:
                p_u = cfg.get("p_rell_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_tot = sum([(ARBOL[i['fam']].get("p_ber_man", {}).get(i['esp'], ARBOL[i['fam']]['tamaños'][i['tam']]) * i['can']) / m_dna['merma'] for i in items])
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
                    # Desglose de complementos por cliente
                    cfg = ARBOL[it['fam']]
                    list_s = cfg["espec"][it['esp']]
                    final_s = list_s["fijos"].copy() if isinstance(list_s, dict) else list_s.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: final_s.append(it['rel'])
                    for s_id in final_s:
                        if s_id not in DB_COMPLEMENTOS: continue
                        p_u = cfg.get("p_rell_map", {}).get(it['tam'], 15) if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_batch = p_u * it['can']
                        st.markdown(f"**{s_id} ({p_batch:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_batch / sum(s_rec.values())
                        for sk, sv in s_rec.items():
                            g_s = sv * (it['can'] if "Decoración" in s_id or "Rebozado" in s_id or "Cabeza" in sk else fact)
                            st.write(f"- {sk}: {g_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + g_s

    with t_cli:
        for i, ped in enumerate(st.session_state.comanda):
            res_txt = ", ".join([f"{it['can']} {it['esp']}" for it in ped['items']])
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{ped['cliente']}**\n\n{res_txt}")
            u_wa = f"https://wa.me/521{ped['wa']}?text="
            c2.link_button("✅ Confirmar", u_wa + urllib.parse.quote(f"Hola {ped['cliente']}! Confirmamos tu pedido de {res_txt}."))
            c3.link_button("🚀 Avisar Listo", u_wa + urllib.parse.quote(f"Hola {ped['cliente']}! Tu pedido está listo 🥐."))
            if st.button("❌ Borrar", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with t_prod:
        st.subheader("🥣 Batidos de Masa")
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']].get("p_ber_man", {}).get(it['esp'], ARBOL[it['fam']]['tamaños'][it['tam']]) * it['can']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"**{m_id} ({m_batch:,.1f}g)**")
            for etapa in m_dna.get("etapas", []):
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    st.checkbox(f"{ing}: {(m_dna['receta'][ing]*h_b/100):,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("✨ Complementos")
        for s_id, p_tot in lotes_comp.items():
            s_rec = DB_COMPLEMENTOS.get(s_id, {})
            if not s_rec: continue
            st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
            st.markdown(f'<div class="etapa-box" style="background-color: rgba(200,200,200,0.3);">', unsafe_allow_html=True)
            fact = p_tot / sum(s_rec.values())
            for sk, sv in s_rec.items():
                gr_s = sv * (1 if "Decoración" in s_id or "Rebozado" in s_id or "Cabeza" in sk else fact)
                st.checkbox(f"{sk}: {gr_s:,.1f}g", key=f"sec_{s_id}_{sk}")
            st.markdown('</div>', unsafe_allow_html=True)

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"master_{k}")
