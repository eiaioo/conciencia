import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN Y CONFIGURACIÓN VISUAL
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'f_key' not in st.session_state: st.session_state.f_key = 0

# Paleta Mate
if st.session_state.tema == "Oscuro":
    C_BG, C_SEC, C_TXT, C_BRD = "#0E1117", "#161B22", "#E6EDF3", "#30363D"
else:
    C_BG, C_SEC, C_TXT, C_BRD = "#F8F9FA", "#FFFFFF", "#1F2328", "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label, .stMarkdown {{ color: {C_TXT} !important; }}
    div[data-testid="stExpander"], .streamlit-expanderHeader {{ background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{ background-color: {C_BG} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important; }}
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid {C_BRD}; color: #000 !important; font-weight: 500; }}
    ul[role="listbox"] {{ background-color: {C_SEC} !important; color: {C_TXT} !important; }}
    </style>
""", unsafe_allow_html=True)

# Botón de Cambio de Tema en la barra lateral
with st.sidebar:
    st.title("👨‍🍳 MENÚ")
    pagina = st.radio("Navegar:", ["📋 Resumen Visual", "🥣 Producción", "📞 WhatsApp Clientes", "🛒 Súper (Insumos Totales)"])
    st.divider()
    if st.button("☀️/🌙 Cambiar Tema"):
        st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
        st.rerun()
    if st.button("🗑️ Vaciar Todo el Día"):
        st.session_state.comanda = []; st.rerun()

# ==========================================
# 2. BASE DE DATOS TÉCNICA (AUDITORÍA TOTAL)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "merma": 1.0, 
        "pasos": [{"n": "Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6, "merma": 1.0, "tz": (0.025, 1),
        "pasos": [{"n": "Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "Final", "i": ["Azúcar", "Miel", "Levadura", "Sal fina", "Agua Azahar", "Mantequilla sin sal"], "c": "rgba(165, 165, 141, 0.3)"}]},
    "Masa Berlinas": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura": 1.0, "merma": 0.85, "tz": (0.05, 5)},
    "Masa Roles Master": {"Harina de fuerza": 93, "Huevo": 30, "Leche ajuste": 5, "Levadura fresca": 1.0, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla": 17, "merma": 1.0, "tz": (70, 350)},
    "Masa Red Velvet": {"Harina": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Levadura": 1.0, "Cacao": 0.8, "Color Rojo": 0.7, "Vinagre": 0.3, "merma": 1.0},
    "Masa Pan Muerto": {"Harina de fuerza": 100, "Azúcar": 20, "Mantequilla": 25, "Huevo entero": 30, "Yemas": 24, "Leche entera": 30, "Levadura": 3.0, "merma": 1.0, "huesos": True},
    "Masa Brownie": {"Mantequilla sin sal": 330, "Azúcar": 395, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "fijo": True, "merma": 1.0}
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Oreo": {"Harina": 100, "Galleta Oreo": 25, "Azúcar Glass": 75, "Mantequilla sin sal": 100},
    "Lágrima Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Fresa": {"Harina": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla sin sal": 100},
    "Lágrima Mazapán": {"Harina": 100, "Mazapán": 66, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Ruby": {"Leche entera": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Crema Turin": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla": 20},
    "Decoración Rosca": {"Ate Colores": 50, "Higo Almíbar": 20, "Cereza Marrasquino": 10},
    "Schmear Roles": {"Mantequilla pomada": 200, "Azúcar Mascabada": 300, "Canela Polvo": 25, "Maicena": 20}
}

ARBOL = {
    "Conchas": {"esp": ["Vainilla", "Chocolate", "Matcha", "Oreo", "Pinole", "Fresa", "Mazapán Intenso"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"esp": ["Tradicional", "Chocolate", "Línea Turín"], "tam": {"Familiar": 1450, "Mediana": 650, "Mini": 120, "Concha-Rosca": 90}, "p_rel_map": {"Familiar": 450, "Mediana": 200, "Mini": 35, "Concha-Rosca": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"esp": ["Vainilla Clásica", "Ruby v2.0", "Turín"], "tam": {"Estándar": 60}, "p_man": {"Ruby v2.0": 70}, "masa": "Masa Berlinas"},
    "Rollos": {"esp": ["Canela Tradicional", "Manzana", "Red Velvet Premium"], "tam": {"Individual": 90}, "masa": "Masa Roles Master", "m_ov": {"Red Velvet Premium": "Masa Red Velvet"}},
    "Pan de muerto": {"esp": ["Tradicional (Naranja)", "Guayaba (Huesos-Ref)"], "tam": {"Estándar": 90}, "masa": "Masa Pan Muerto"},
    "Brownies": {"esp": ["Turín Clásico"], "tam": {"Molde 20x20": 1}, "masa": "Masa Brownie"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA (ESTADO PERSISTENTE)
# ==========================================

st.header("🛒 Registro de Comanda")
with st.container():
    c_n, c_w = st.columns(2)
    cli_n = c_n.text_input("Nombre Cliente", key="input_cli_n")
    cli_w = c_w.text_input("WhatsApp (10 dígitos)", key="input_cli_w")

fk = st.session_state.f_key
c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1, 0.5])
fam_sel = c3.selectbox("Familia de Pan", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
if fam_sel != "-":
    esp_sel = c4.selectbox("Sabor / Especialidad", ARBOL[fam_sel]["esp"], key=f"e_{fk}")
    tam_sel = c5.selectbox("Tamaño", list(ARBOL[fam_sel]["tam"].keys()), key=f"t_{fk}")
    can_sel = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    r_sel = "N/A"
    if fam_sel == "Rosca de reyes": 
        r_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Vainilla", "Crema Ruby"], key=f"r_{fk}")

    if col7 := c7.button("➕"):
        st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "can": can_sel, "rel": r_sel})
        st.session_state.f_key += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"Pedido en Carrito para {cli_n}:")
    for it in st.session_state.carrito: st.write(f"- {it['can']}x {it['esp']} ({it['tam']})")
    if st.button("✅ FINALIZAR Y GUARDAR TODO EL PEDIDO"):
        if cli_n:
            st.session_state.comanda.append({"cli": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PROCESAMIENTO CENTRAL
# ==========================================

if st.session_state.comanda:
    master_inv = {}
    lotes_masa = {}
    lotes_comp = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = ARBOL[it['fam']].get("m_ov", {}).get(it['esp'], ARBOL[it['fam']]["masa"])
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cli']; lotes_masa[m_id].append(it_c)
            
            # Recolectar complementos
            cfg = ARBOL[it['fam']]
            subs = []
            if it['fam'] == "Conchas": subs.append(f"Lágrima {it['esp'] if 'Intenso' not in it['esp'] else 'Mazapán'}")
            if it['fam'] == "Rosca de reyes": 
                subs.append("Decoración Rosca")
                if it['rel'] != "Sin Relleno": subs.append(it['rel'])
            if it['fam'] == "Berlinas" and it['esp'] == "Ruby v2.0": subs.append("Crema Ruby")
            if it['fam'] == "Rollos": subs.append("Schmear Roles")
            if it['fam'] == "Pan de muerto": subs.append("Rebozado Muerto")

            for s_id in subs:
                if s_id in DB_COMPLEMENTOS:
                    # Cálculo de peso basado en ingeniería
                    if it['fam'] == "Rosca de reyes" and s_id == it['rel']: p_unit = cfg["p_rell_map"][it['tam']]
                    else: p_unit = cfg.get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15
                    lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_unit * it['can'])

    # --- RENDER DE PAGINAS (SIDEBAR NAVIGATION) ---
    st.divider()
    
    if pagina == "📋 Resumen Visual":
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch_tot = sum([(ARBOL[it['fam']].get("p_man", {}).get(it['esp'], ARBOL[it['fam']]['tam'][it['tam']]) * it['can']) / m_dna['merma'] for it in items])
            h_base = (m_batch_tot * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch_tot:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info("Masa Principal")
                for k, v in m_dna['receta'].items():
                    gr = v*h_base/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")

    elif pagina == "🥣 Producción":
        col_masa_v, col_comp_v = st.columns(2)
        with col_masa_v:
            st.subheader("🥣 Batidos de Masa")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(ARBOL[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.write(f"**Lote: {m_id} ({m_batch:,.1f}g)**")
                for etapa in m_dna.get("etapas", [{"n": "Proceso", "i": list(m_dna['receta'].keys()), "c": "rgba(200,200,200,0.3)"}]):
                    st.markdown(f'<div class="etapa-box" style="background-color:{etapa["c"]};"><div style="color:rgba(0,0,0,0.6);font-weight:bold">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        peso = m_dna['receta'][ing]*h_b/100
                        st.checkbox(f"{ing}: {peso:,.1f}g", key=f"p_{m_id}_{ing}_{it['cli']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        with col_comp_v:
            st.subheader("✨ Complementos")
            for s_id, p_tot in lotes_comp.items():
                s_rec = DB_COMPLEMENTOS[s_id]
                st.write(f"**{s_id} ({p_tot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color:{s_rec["c"]};">', unsafe_allow_html=True)
                factor = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
                for sk, sv in s_rec.items():
                    if sk == "c": continue
                    peso_s = sv * factor
                    st.checkbox(f"{sk}: {peso_s:,.1f}g", key=f"s_{s_id}_{sk}")
                    master_inv[sk] = master_inv.get(sk, 0) + peso_s
                st.markdown('</div>', unsafe_allow_html=True)

    elif pagina == "📞 Clientes & WhatsApp":
        for i, ped in enumerate(st.session_state.comanda):
            with st.container(border=True):
                ca, cb, cc = st.columns([0.4, 0.3, 0.3])
                ped_list = "\n".join([f"- {it['can']}x {it['esp']} ({it['tam']})" for it in ped['items']])
                ca.write(f"👤 **{ped['cliente']}**\n\n{ped_list}")
                url = f"https://wa.me/521{ped['wa']}?text="
                cb.link_button("✅ Confirmar", url + urllib.parse.quote(f"Hola {ped['cliente']}! Recibimos tu pedido:\n{ped_list}"))
                cc.link_button("🚀 Avisar Listo", url + urllib.parse.quote(f"Hola {ped['cliente']}! Tu pedido de CONCIENCIA ya está listo!"))
                if st.button("❌ Borrar Pedido", key=f"del_p_{i}"): st.session_state.comanda.pop(i); st.rerun()

    elif pagina == "🛒 Súper (Lista Maestra)":
        st.header("📦 Surtido de Insumos")
        # Aseguramos suma de todos los batidos y complementos en la lista final
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"inv_{k}")
