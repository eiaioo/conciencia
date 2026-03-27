import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA DE DISEÑO (BLINDAJE TOTAL)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'f_key' not in st.session_state: st.session_state.f_key = 0

# Paleta Mate
if st.session_state.tema == "Oscuro":
    B_APP, B_CARD, T_MAIN, B_BRD, B_INPUT = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#1C2128"
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
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; font-weight: 500; }}
    </style>
""", unsafe_allow_html=True)

# Botón Sol/Luna
_, c_t = st.columns([0.9, 0.1])
if c_t.button("☀️/🌙"):
    st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
    st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA (RESTABLECIDA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "merma": 1.0, "factor": 1.963,
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor y Grasa", "i": ["Azúcar", "Miel", "Mantequilla sin sal", "Sal fina", "Agua Azahar", "Levadura"], "c": "rgba(165, 165, 141, 0.3)"}]
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina", "Levadura seca"], "c": "rgba(162, 210, 255, 0.3)"}]
    },
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_fijo": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "rgba(168, 230, 173, 0.3)"}]},
    "Masa Red Velvet": {"receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao en polvo": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3}, "merma": 1.0, "tz": (0.07, 5), "etapas": [{"n": "Masa RV", "i": ["Harina de fuerza", "Cacao", "Colorante Rojo"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Masa Guayaba", "i": ["Harina de fuerza", "Polvo de Guayaba"], "c": "rgba(255, 179, 140, 0.3)"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin": 165, "Harina de fuerza": 190, "Cocoa": 75, "Sal fina": 8, "Nuez": 140}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Lágrima de Matcha": {"Harina de fuerza": 91.5, "Matcha en polvo": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(168, 230, 173, 0.3)"},
    "Lágrima de Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik Fresa": 21, "Mantequilla sin sal": 100, "c": "rgba(255, 179, 140, 0.3)"},
    "Lágrima de Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66, "c": "rgba(212, 163, 115, 0.3)"},
    "Lágrima de Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Galleta Oreo": 25, "c": "rgba(165, 165, 141, 0.3)"},
    "Lágrima de Pinole": {"Harina de fuerza": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "rgba(212, 163, 115, 0.3)"},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "c": "rgba(162, 210, 255, 0.3)"},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "c": "rgba(168, 230, 173, 0.3)"},
    "Crema Especial Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla sin sal": 20, "c": "rgba(162, 210, 255, 0.3)"},
    "Glaseado Turin": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche": 50, "Cabeza de Conejo": 1, "c": "rgba(212, 163, 115, 0.3)"},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar Mascabada": 300, "Canela": 25, "c": "rgba(183, 183, 164, 0.3)"},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2, "c": "rgba(168, 230, 173, 0.3)"},
    "Inclusión Manzana": {"Orejón de Manzana": 8, "Agua tibia": 2, "c": "rgba(162, 210, 255, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "c": "rgba(212, 163, 115, 0.3)"},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5, "c": "rgba(183, 183, 164, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán", "Oreo", "Pinole"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": ["Tradicional", "Chocolate", "Turín"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": ["Ruby v2.0", "Turín", "Vainilla Clásica"], "tam": {"Estándar": 60}, "p_man": {"Ruby v2.0": 70}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": ["Tradicional (Canela)", "Manzana", "Red Velvet Premium"], "tam": {"Individual": 90}, "masa": "Masa Brioche Roles", "masa_ov": {"Red Velvet Premium": "Masa Red Velvet"}},
    "Pan de muerto": {"espec": ["Tradicional", "Guayaba Huesos-Ref"], "tam": {"Estándar": 85}, "masa": "Masa Muerto Guayaba"},
    "Brownies": {"espec": ["Chocolate Turín"], "tam": {"Molde 20x20": 1}, "masa": "Mezcla de Brownies"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.header("🥐 Comanda Técnica CONCIENCIA")

with st.container():
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre del Cliente", key="cli_name_persist")
    cli_w = c2.text_input("WhatsApp", key="cli_wa_persist")

st.write("### 🍞 Agregar Panes")
fk = st.session_state.form_key
c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1, 0.8])

f_sel = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if f_sel != "-":
    e_sel = c4.selectbox("Especialidad", ARBOL[f_sel]["espec"], key=f"e_{fk}")
    t_sel = c5.selectbox("Tamaño", list(ARBOL[f_sel]["tam"].keys()), key=f"t_{fk}")
    c_sel = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    r_sel = "N/A"
    if f_sel == "Rosca de reyes":
        r_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Especial Turin", "Crema Ruby"], key=f"r_{fk}")
    
    c7.write("##")
    if c7.button("➕"):
        st.session_state.carrito.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "can": c_sel, "rel": r_sel})
        st.session_state.form_key += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    for it in st.session_state.carrito: st.write(f"• {it['can']}x {it['esp']} ({it['tam']})")
    if st.button("✅ FINALIZAR PEDIDO COMPLETO"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PROCESAMIENTO
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}
    lotes_comp = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']].get("masa_ov", {}).get(it['esp'], ARBOL[it['fam']]["masa"])
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[m_id].append(it_c)
            
            # Identificar complementos
            subs = []
            if it['fam'] == "Conchas": subs.append(f"Lágrima {it['esp']}")
            if it['fam'] == "Rosca de reyes": subs.append("Decoración Rosca"); 
            if it['rel'] != "Sin Relleno" and it['rel'] != "N/A": subs.append(it['rel'].replace("Crema Pastelera ","Crema ").replace("Especial ",""))
            if it['esp'] == "Ruby v2.0": subs.append("Crema Ruby")
            if it['fam'] == "Rollos": 
                subs.append("Schmear Canela")
                if "Manzana" in it['esp']: subs.append("Inclusión Manzana")
                if "Tradicional" in it['esp']: subs.append("Inclusión Frutos Rojos")
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
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
                    # Desglose de complementos por cliente en el resumen
                    cfg_it = ARBOL[it['fam']]
                    # (Lógica simplificada para mostrar ingredientes de lágrima en el resumen verde)
                    s_name = f"Lágrima {it['esp']}" if it['fam'] == "Conchas" else None
                    if s_name and s_name in DB_COMPLEMENTOS:
                        st.markdown(f"**{s_name}:**")
                        s_rec = DB_COMPLEMENTOS[s_name]
                        p_t_it = cfg_it['p_ex'][it['tam']] * it['can']
                        f_s_it = p_t_it / sum([v for k,v in s_rec.items() if k != "c"])
                        for sk, sv in s_rec.items():
                            if sk != "c": st.write(f"- {sk}: {sv*f_s_it:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + (sv*f_s_it)

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            res_txt = ", ".join([f"{it['can']} {it['esp']}" for it in p['items']])
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{p['cliente']}**\n\n{res_txt}")
            u = f"https://wa.me/521{p['wa']}?text=" + urllib.parse.quote(f"Hola {p['cliente']}! Tu pedido está listo.")
            c2.link_button("✅ Confirmar", u.replace("listo.", "recibido.")); c3.link_button("🚀 Listo", u)
            if st.button("❌", key=f"d_{i}"): st.session_state.comanda.pop(i); st.rerun()

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
                        st.checkbox(f"{ing}: {m_dna['receta'][ing]*h_b/100:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        with cc:
            st.subheader("✨ Complementos")
            for s_id, p_tot in lotes_comp.items():
                s_rec = DB_COMPLEMENTOS[s_id]
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
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"master_{k}")

    if st.button("🗑️ LIMPIAR TODO"): st.session_state.comanda = []; st.rerun()
