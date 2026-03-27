import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN VISUAL (SÓLO MODO CLARO)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Estilo limpio: Fondo blanco, texto negro, sin adornos que fallen
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3, h4, p, span, label { color: #000000 !important; }
    .stCheckbox label p { color: #000000 !important; font-size: 1.1rem !important; }
    div[data-testid="stExpander"] { border: 1px solid #DDDDDD !important; border-radius: 8px; }
    .etapa-box { 
        padding: 15px; border-radius: 10px; margin-bottom: 10px; 
        border: 1px solid #DDDDDD; color: #000000 !important; 
    }
    .stButton > button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS TÉCNICA TOTAL
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "merma": 1.0},
    "Masa de Berlinas": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0, "merma": 0.85},
    "Masa Brioche Roles": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17, "merma": 1.0},
    "Masa Red Velvet": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7, "merma": 1.0},
    "Masa Brioche Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6, "merma": 1.0},
    "Masa Muerto": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura": 5, "Sal fina": 1.8, "Polvo Guayaba": 5, "merma": 1.0},
    "Mezcla Brownie": {"Mantequilla": 330, "Azúcar Blanca": 275, "Chocolate": 165, "Harina de fuerza": 190, "merma": 1.0}
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Fresa": {"Harina": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla": 100},
    "Lágrima Mazapán": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66},
    "Lágrima Oreo": {"Harina": 100, "Azúcar Glass": 75, "Mantequilla": 100, "Oreo": 25},
    "Lágrima Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Chocolate": {"Leche": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Choco 60%": 120},
    "Crema Turin": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120},
    "Crema Ruby": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
}

CATALOGO = {
    "Conchas": {
        "espec": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán", "Oreo", "Pinole"],
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"
    },
    "Rosca de reyes": {
        "espec": ["Tradicional", "Chocolate", "Turín"],
        "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90},
        "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"
    },
    "Berlinas": {
        "espec": ["Vainilla", "Chocolate", "Ruby v2.0"],
        "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas", "p_ber_man": {"Ruby v2.0": 70}
    },
    "Rollos": {
        "espec": ["Canela", "Manzana", "Red Velvet"],
        "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "masa_ov": {"Red Velvet": "Masa Red Velvet"}
    },
    "Pan de muerto": {
        "espec": ["Tradicional", "Guayaba"],
        "tamaños": {"Estándar": 85}, "masa": "Masa Muerto"
    },
    "Brownies": {
        "espec": ["Turín"], "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"
    }
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=True):
    col_c1, col_c2 = st.columns(2)
    cli_n = col_c1.text_input("Nombre del Cliente", key="cli_name_input")
    cli_w = col_c2.text_input("WhatsApp", key="cli_wa_input")

st.write("### 🍞 2. Agregar Panes")
fk = st.session_state.form_key
c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1, 0.8])

fam_sel = c1.selectbox("Familia", ["-"] + list(CATALOGO.keys()), key=f"f_{fk}")

if fam_sel != "-":
    esp_sel = c2.selectbox("Especialidad", CATALOGO[fam_sel]["espec"], key=f"e_{fk}")
    tam_sel = c3.selectbox("Tamaño", list(CATALOGO[fam_sel]["tamaños"].keys()), key=f"t_{fk}")
    can_sel = c4.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
    
    if c5.button("➕", key=f"btn_{fk}"):
        st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "can": can_sel})
        st.session_state.form_key += 1
        st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    for it in st.session_state.carrito:
        st.write(f"- {it['can']}x {it['fam']} {it['esp']} ({it['tam']})")
    
    if st.button("✅ FINALIZAR Y GUARDAR PEDIDO COMPLETO"):
        if cli_n:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []
            st.rerun()
        else: st.error("Ingresa el nombre del cliente")

# ==========================================
# 4. HOJAS DE PRODUCCIÓN
# ==========================================

if st.session_state.comanda:
    st.divider()
    t_res, t_cli, t_prod, t_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    
    master_inv = {}
    lotes_masa = {}

    for ped in st.session_state.comanda:
        for it in ped['items']:
            masa_id = CATALOGO[it['fam']].get("masa_ov", {}).get(it['esp'], CATALOGO[it['fam']]["masa"])
            if masa_id not in lotes_masa: lotes_masa[masa_id] = []
            it_c = it.copy(); it_c['cli'] = ped['cliente']; lotes_masa[masa_id].append(it_c)

    with t_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            # Cálculo de masa batch
            m_batch = 0
            for i in items:
                p_u_m = CATALOGO[i['fam']].get("p_ber_man", {}).get(i['esp'], CATALOGO[i['fam']]['tamaños'][i['tam']])
                m_batch += (p_u_m * i['can']) / m_dna['merma']
            
            h_base = (m_batch * 100) / sum([v for k,v in m_dna['receta'].items()])
            
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info("Masa Principal")
                for k, v in m_dna['receta'].items():
                    gr = v*h_base/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")

    with t_cli:
        for i, p in enumerate(st.session_state.comanda):
            c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
            c1.write(f"👤 **{p['cliente']}**")
            u_wa = f"https://wa.me/521{p['wa']}?text="
            c2.link_button("✅ Confirmar", u_wa + "Pedido Recibido")
            c3.link_button("🚀 Listo", u_wa + "Tu pan esta listo!")
            if st.button("❌", key=f"del_{i}"):
                st.session_state.comanda.pop(i); st.rerun()

    with t_sup:
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"sup_{k}")

    if st.button("🗑️ LIMPIAR TODA LA PRODUCCIÓN"):
        st.session_state.comanda = []
        st.rerun()
