import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN DE MEMORIA (ANTI-ERRORES)
# ==========================================
if 'pedidos' not in st.session_state: st.session_state.pedidos = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'f_key' not in st.session_state: st.session_state.f_key = 0
if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'cli_n' not in st.session_state: st.session_state.cli_n = ""
if 'cli_w' not in st.session_state: st.session_state.cli_w = ""

st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

# ==========================================
# 2. DISEÑO VISUAL (MODO MATE INTEGRADO)
# ==========================================
C_BG = "#0E1117" if st.session_state.tema_oscuro else "#F6F8FA"
C_SEC = "#161B22" if st.session_state.tema_oscuro else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.tema_oscuro else "#1F2328"
C_BRD = "#30363D" if st.session_state.tema_oscuro else "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    
    /* Eliminar Barras Blancas y Fugas */
    div[data-testid="stExpander"], .streamlit-expanderHeader {{
        background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important;
    }}
    
    /* Dropdown Menus (Evitar blancos) */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{
        background-color: {C_BG} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important;
    }}
    ul[role="listbox"] {{ background-color: {C_SEC} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important; }}
    li[role="option"] {{ color: {C_TXT} !important; }}

    /* Corregir botón chueco y diseño de inputs */
    div[data-testid="stNumberInput"] button {{ background-color: {C_SEC} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important; }}
    .stButton > button {{ border-radius: 8px; font-weight: bold; background-color: {C_SEC} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important; }}

    /* Bloques de Producción (30% opacidad) */
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; font-weight: 600; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BASE DE DATOS TÉCNICA TOTAL (RESTAURADA)
# ==========================================

DB_MASAS = {
    "Masa Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, "factor": 1.963},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0},
    "Masa Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche ajuste": 5, "Levadura fresca": 1.0, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla": 17}, "merma": 1.0},
    "Masa Red Velvet": {"receta": {"Harina": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Levadura": 1.0, "Cacao": 0.8, "Color Rojo": 0.7, "Vinagre": 0.3}, "merma": 1.0},
    "Masa Pan Muerto": {"receta": {"Harina de fuerza": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura": 5.0, "Sal": 1.8, "Polvo Guayaba": 5.0}, "merma": 1.0},
    "Mezcla Brownie": {"receta": {"Mantequilla": 330, "Azúcar": 395, "Chocolate Turin": 165, "Harina de fuerza": 190, "Nuez": 140, "Sal fina": 8}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "col": "rgba(255, 235, 156, 0.3)"},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "col": "rgba(162, 210, 255, 0.3)"},
    "Lágrima Matcha": {"Harina de fuerza": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100, "col": "rgba(168, 230, 173, 0.3)"},
    "Lágrima Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla": 100, "col": "rgba(255, 179, 140, 0.3)"},
    "Lágrima Mazapán": {"Harina": 100, "Mazapan": 66, "Azúcar Glass": 100, "Mantequilla": 100, "col": "rgba(212, 163, 115, 0.3)"},
    "Lágrima Oreo": {"Harina": 100, "Oreo picada": 25, "Azúcar Glass": 75, "Mantequilla": 100, "col": "rgba(255, 235, 156, 0.3)"},
    "Lágrima Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100, "col": "rgba(212, 163, 115, 0.3)"},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "col": "#E3F2FD"},
    "Crema Ruby": {"Leche": 131, "Crema 35%": 131, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "col": "#F8BBD0"},
    "Crema Turin": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Chocolate Turin": 120, "col": "#FFF3E0"},
    "Schmear Canela": {"Mantequilla pomada": 200, "Azúcar Mascabada": 300, "Canela": 25, "Maicena": 20, "col": "#D7CCC8"},
    "Decoración Rosca Ate": {"Ate Tiras": 50, "Higo": 20, "Cereza": 10, "col": "#C8E6C9"}
}

# Árbol de Selección Completo
ARBOL = {
    "CONCHAS": {"espec": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán", "Oreo", "Pinole"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m_id": "Masa Conchas"},
    "ROSCAS": {"espec": ["Tradicional", "Turín"], "tam": {"Familiar (1.5kg)": 1450, "Mediana (650g)": 650, "Mini (120g)": 120, "Concha-Rosca": 90}, "p_rel_m": {"Familiar (1.5kg)": 450, "Mediana (650g)": 200, "Mini (120g)": 35, "Concha-Rosca": 25}, "m_id": "Masa Brioche Rosca"},
    "BERLINAS": {"espec": ["Vainilla Clásica", "Ruby v2.0"], "tam": {"Estándar": 60}, "m_id": "Masa de Berlinas", "p_m": {"Ruby v2.0": 70}},
    "ROLES": {"espec": ["Canela Tradicional", "Manzana", "Red Velvet Premium"], "tam": {"Individual": 90}, "m_id": "Masa Brioche Roles", "m_ov": {"Red Velvet Premium": "Masa Red Velvet"}},
    "PAN MUERTO": {"espec": ["Tradicional", "Guayaba"], "tam": {"Estándar": 95}, "m_id": "Masa Pan Muerto"},
    "BROWNIES": {"espec": ["Chocolate Turín"], "tam": {"Molde 20x20": 1}, "m_id": "Mezcla Brownie"}
}

# ==========================================
# 4. SIDEBAR (MENÚ DE NAVEGACIÓN)
# ==========================================
with st.sidebar:
    st.title("🥖 MENÚ")
    pagina = st.radio("Secciones", ["➕ Captura Pedido", "📋 Resumen Producción", "🥣 Hoja de Batidos", "🛒 Súper"])
    st.divider()
    if st.button("🗑️ VACIAR TODO"):
        st.session_state.pedidos = []; st.session_state.carrito = []; st.session_state.cli_n = ""; st.rerun()
    if st.button("🌙/☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro; st.rerun()

# ==========================================
# 5. PÁGINA: CAPTURA (ESTABLE)
# ==========================================
if pagina == "➕ Captura Pedido":
    st.header("Cargar Pedidos de Clientes")
    with st.container():
        c1, c2 = st.columns(2)
        st.session_state.cli_n = c1.text_input("Nombre Cliente", value=st.session_state.cli_n)
        st.session_state.cli_w = c2.text_input("WhatsApp", value=st.session_state.cli_w)

    st.write("---")
    fk = st.session_state.form_key
    # COLUMNAS PARA EVITAR BOTON CHUECO (ESPACIADOR VISUAL)
    col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1, 0.5])
    
    fam = col1.selectbox("Pan", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if fam != "-":
        esp = col2.selectbox("Sabor", ARBOL[fam]["espec"], key=f"e_{fk}")
        tam = col3.selectbox("Tamaño", list(ARBOL[fam]["tam"].keys()), key=f"t_{fk}")
        can = col4.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
        rel = "Sin Relleno"
        if fam == "ROSCAS": rel = st.selectbox("Relleno", ["Sin Relleno", "Crema Vainilla", "Crema Ruby"], key=f"r_{fk}")

        col5.write("") # Empujar hacia abajo
        col5.write("")
        if col5.button("➕", key=f"add_{fk}"):
            st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "can": can, "rel": rel})
            st.session_state.f_key += 1; st.rerun()

    if st.session_state.carrito:
        st.info(f"🛒 Carrito para: {st.session_state.cli_n}")
        for i, it in enumerate(st.session_state.carrito):
            st.write(f"• {it['can']}x {it['fam']} {it['esp']} ({it['tam']})")
        
        if st.button("✅ GUARDAR Y FINALIZAR PEDIDO"):
            if st.session_state.cli_n:
                st.session_state.pedidos.append({"cli": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito.copy()})
                st.session_state.carrito = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()

# ==========================================
# 6. MOTOR DE CÁLCULO Y VISTAS (RESUMEN / SÚPER / PRODUCCIÓN)
# ==========================================
if st.session_state.pedidos:
    # Cálculo Global previo
    final_master_inv = {}
    lotes_masa = {}
    lotes_complementos = {}

    for ped in st.session_state.pedidos:
        for it in ped['items']:
            # Agrupar Masas
            masa_id = ARBOL[it['fam']].get("m_ov", {}).get(it['esp'], ARBOL[it['fam']]["m_id"])
            if masa_id not in lotes_masa: lotes_masa[masa_id] = []
            it_cl = it.copy(); it_cl['cliente'] = ped['cli']; lotes_masa[masa_id].append(it_cl)

            # Complementos (Lágrimas / Rellenos / Decoración)
            subs_actuales = []
            if it['fam'] == "CONCHAS": subs_actuales.append(f"Lágrima {it['esp']}")
            if it['fam'] == "ROSCAS":
                subs_actuales.append("Decoración Rosca Ate")
                if it['rel'] != "Sin Relleno": subs_actuales.append(it['rel'].replace("Pastelera ", ""))
            if it['fam'] == "BERLINAS" and it['esp'] == "Ruby v2.0": subs_actuales.append("Crema Ruby")
            if it['fam'] == "ROLLOS": subs_actuales.append("Schmear Canela")
            if it['fam'] == "PAN MUERTO": subs_actuales.append("Rebozado Muerto")

            for sid in subs_actuales:
                if sid in DB_COMPLEMENTOS:
                    if "Crema" in sid and it['fam'] == "ROSCAS": pu = ARBOL[it['fam']]["p_rel_m"][it['tam']]
                    else: pu = ARBOL[it['fam']].get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in sid else 15
                    lotes_complementos[sid] = lotes_complementos.get(sid, 0) + (pu * it['can'])

    if pagina == "📋 Resumen Visual":
        for m_id, items in lotes_masa.items():
            st.header(f"🛠️ BATIDO: {m_id}")
            m_dna = DB_MASAS[m_id]; 
            batch_tot = sum([(ARBOL[it['fam']].get("p_man",{}).get(it['esp'], ARBOL[it['fam']]['tam'][it['tam']]) * it['can']) / m_dna['merma'] for it in items])
            hb = (batch_tot * 100) / sum(m_dna['receta'].values())
            c_l, c_r = st.columns([0.3, 0.7])
            with c_l:
                st.info(f"Ingredientes Masa ({batch_tot:,.1f}g)")
                for k,v in m_dna['receta'].items(): st.write(f"• {k}: {v*hb/100:,.1f}g"); final_master_inv[k] = final_master_inv.get(k,0)+ (v*hb/100)
            with c_r:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}")
                    s_id_it = f"Lágrima {it['esp']}" if it['fam'] == "CONCHAS" else None
                    if s_id_it in DB_COMPLEMENTOS:
                        s_r = DB_COMPLEMENTOS[s_id_it]; p_tot_s = ARBOL[it['fam']]['p_ex'][it['tam']] * it['can']; f_s = p_tot_s / sum(s_r.values())
                        st.markdown(f"**{s_id_it} ({p_tot_s:,.1f}g)**")
                        for sk, sv in s_r.items(): 
                            if sk != 'col' and sk != 'c': st.write(f"- {sk}: {sv*f_s:,.1f}g"); final_master_inv[sk] = final_master_inv.get(sk,0)+ (sv*f_s)

    elif pagina == "🥣 Hoja de Batidos":
        c_m, c_c = st.columns(2)
        with c_m:
            st.subheader("Batidos de Masa")
            for m_id, items in lotes_masa.items():
                md = DB_MASAS[m_id]; bt = sum([(ARBOL[it['fam']]['tam'][it['tam']]*it['can']) for it in items]); hb_m = (bt*100)/sum(md['receta'].values())
                st.write(f"**{m_id} ({bt:,.0f}g)**")
                for etapa in md.get("etapas", []):
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']: st.checkbox(f"{ing}: {md['receta'][ing]*hb_m/100:,.1f}g", key=f"bt_{m_id}_{ing}_{it['can']}")
        with c_c:
            st.subheader("Complementos")
            for sid, p_t in lotes_complementos.items():
                sr = DB_COMPLEMENTOS[sid]; st.write(f"**{sid} ({p_t:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {sr.get("c","rgba(200,200,200,0.3)")};">', unsafe_allow_html=True)
                f_sr = p_t / sum([v for k,v in sr.items() if k != 'col' and k != 'c'])
                for sk, sv in sr.items():
                    if sk not in ['col', 'c']: st.checkbox(f"{sk}: {sv*f_sr:,.1f}g", key=f"s_{sid}_{sk}"); final_master_inv[sk] = final_master_inv.get(sk,0)+sv*f_sr
                st.markdown('</div>', unsafe_allow_html=True)

    elif pagina == "🛒 Súper":
        st.header("Lista de Insumos (Recalculada)")
        # Sincronizamos compras totales recorriendo todo el arbol de nuevo
        for k, v in sorted(final_master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"mstr_{k}")
