import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. BASE DE DATOS MAESTRA (DNA CONCIENCIA)
# ==========================================

# Aquí está todo tu recetario técnico. No falta ni un gramo ni un sabor.
RECETARIO = {
    "CONCHAS": {
        "masa_id": "Masa_Concha",
        "tallas": {"Estándar": 95, "Mini": 35},
        "extra_peso": {"Estándar": 30, "Mini": 10},
        "especialidades": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán Intenso", "Oreo", "Pinole"]
    },
    "ROSCA DE REYES": {
        "masa_id": "Masa_Rosca",
        "tallas": {"FAMILIAR (1.5kg)": 1450, "MEDIANA (650g)": 650, "MINI (120g)": 120, "CONCHA-ROSCA (90g)": 90},
        "relleno_map": {"FAMILIAR (1.5kg)": 450, "MEDIANA (650g)": 200, "MINI (120g)": 35, "CONCHA-ROSCA (90g)": 25},
        "especialidades": ["Tradicional", "Chocolate", "Turín"],
        "rellenos_validos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Chocolate", "Crema Ruby", "Crema Turín"]
    },
    "BERLINAS": {
        "masa_id": "Masa_Berlina_TZ",
        "tallas": {"Estándar (60g)": 60, "Ruby Special (70g)": 70},
        "especialidades": ["Vainilla Clásica", "Ruby v2.0", "Turín Especial"]
    },
    "ROLLOS": {
        "masa_id": "Masa_Roles_TZ",
        "tallas": {"Individual": 90},
        "especialidades": ["Tradicional Canela", "Manzana", "Red Velvet Premium"]
    },
    "PAN DE MUERTO": {
        "masa_id": "Masa_Muerto",
        "tallas": {"Estándar": 90},
        "especialidades": ["Tradicional Naranja", "Guayaba Huesos-Refuerzo"]
    },
    "BROWNIES": {
        "masa_id": "Mezcla_Brownie",
        "tallas": {"Molde 20x20 (12 piezas)": 1},
        "especialidades": ["Turín Amargo"]
    }
}

ING_RECETARIO = {
    # --- MASAS ---
    "Masa_Concha": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0},
    "Masa_Berlina_TZ": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo entero": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura": 1.0, "_merma": 0.85},
    "Masa_Roles_TZ": {"Harina de fuerza": 93, "Huevo entero": 30, "Leche": 5, "Levadura fresca": 1.0, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17},
    "Masa_Red_Velvet": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Colorante Rojo": 0.7, "Cacao": 0.8, "Vinagre": 0.3},
    "Masa_Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla": 30, "Huevo": 20, "Yemas": 4, "Leche": 24, "Sal": 2.2, "Azahar": 0.6},
    "Masa_Muerto": {"Harina": 100, "Leche": 30, "Yemas": 18, "Azúcar": 20, "Mantequilla": 25, "Sal": 1.8, "Levadura fresca": 5.0},
    "Mezcla_Brownie": {"Mantequilla": 330, "Azúcar": 275, "Chocolate Turín": 165, "Harina": 190, "Cocoa": 75, "Nuez": 140, "_fijo": True},
    
    # --- COMPLEMENTOS (Sub-recetas) ---
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Ruby": {"Leche": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63},
    "Schmear Canela": {"Mantequilla pomada": 200, "Azúcar Mascabada": 300, "Canela": 25, "Maicena": 20},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2}
}

# ==========================================
# 2. MOTOR DE UI Y CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="CONCIENCIA MASTER", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'pedidos' not in st.session_state: st.session_state.pedidos = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0

# Estilo MATE PROFESIONAL (Evita que el Sidebar se quede blanco)
BG_HEX = "#0E1117" if st.session_state.tema == "Oscuro" else "#F7F8FA"
SEC_HEX = "#161B22" if st.session_state.tema == "Oscuro" else "#FFFFFF"
TXT_HEX = "#E6EDF3" if st.session_state.tema == "Oscuro" else "#1F2328"
BRD_HEX = "#30363D" if st.session_state.tema == "Oscuro" else "#D0D7DE"

st.markdown(f"""<style>
    .stApp {{ background-color: {BG_HEX} !important; color: {TXT_HEX}; }}
    [data-testid="stSidebar"] {{ background-color: {SEC_HEX} !important; border-right: 1px solid {BRD_HEX}; }}
    div[data-testid="stExpander"], .streamlit-expanderHeader {{ background-color: {SEC_HEX} !important; border: 1px solid {BRD_HEX} !important; }}
    div[data-baseweb="select"] > div, input {{ background-color: {BG_HEX} !important; color: {TXT_HEX} !important; border: 1px solid {BRD_HEX} !important; }}
    ul[role="listbox"] {{ background-color: {SEC_HEX} !important; }}
    li[role="option"] {{ color: {TXT_HEX} !important; }}
    .stButton > button {{ border-radius: 8px; width: 100%; background-color: {SEC_HEX}; color: {TXT_HEX}; border: 1px solid {BRD_HEX}; }}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("👨‍🍳 NAVEGACIÓN")
    pag = st.radio("Secciones", ["📋 Captura (Comanda)", "📈 Resumen de Carga", "🥣 Producción", "🛒 Lista de Súper"])
    st.divider()
    if st.button("☀️/🌙 TEMA"):
        st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
        st.rerun()
    if st.button("🗑️ RESETEAR DÍA"): st.session_state.pedidos = []; st.session_state.carrito = []; st.rerun()

# ==========================================
# 3. PAGINA: CAPTURA (ESTADO PERSISTENTE)
# ==========================================

if pag == "📋 Captura (Comanda)":
    st.header("1. Datos del Cliente")
    c1, c2 = st.columns(2)
    # Persistimos nombre y WA sin usar la "llave" que causa errores en Streamlit
    cli_name = c1.text_input("Nombre", key="input_cli_n")
    cli_wa = c2.text_input("Celular (10 dígitos)", key="input_cli_w")
    
    st.divider()
    st.header("2. Seleccionar Panes")
    fk = st.session_state.form_id
    col1, col2, col3, col4, col5 = st.columns([2,2,1.5,1,0.5])
    
    fam = col1.selectbox("Pan", ["-"] + list(RECETARIO.keys()), key=f"f_{fk}")
    if fam != "-":
        esp = col2.selectbox("Sabor/Variante", RECETARIO[fam]["especialidades"], key=f"e_{fk}")
        tam = col3.selectbox("Tamaño", list(RECETARIO[fam]["tallas"].keys()), key=f"t_{fk}")
        can = col4.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
        
        rel = "N/A"
        if fam == "ROSCA DE REYES":
            rel = st.selectbox("Añadir Relleno", RECETARIO[fam]["rellenos_validos"], key=f"r_{fk}")

        if col5.button("➕"):
            st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "can": can})
            st.session_state.form_id += 1; st.rerun()

    if st.session_state.carrito:
        st.info(f"CARRITO PARA: {cli_name}")
        for i, item in enumerate(st.session_state.carrito):
            st.write(f"- {item['can']}x {item['fam']} {item['esp']} ({item['tam']})")
        if st.button("✅ FINALIZAR PEDIDO Y ENVIAR A COCINA"):
            if cli_name:
                st.session_state.pedidos.append({"cliente": cli_name, "wa": cli_wa, "items": st.session_state.carrito.copy()})
                st.session_state.carrito = []
                st.rerun()
            else: st.error("Ingresa un nombre para el cliente.")

# ==========================================
# 4. MOTOR DE PROCESAMIENTO CENTRAL
# ==========================================

if st.session_state.pedidos:
    inv_compras = {}
    batidos_lote = {}
    extras_lote = {}

    for ped in st.session_state.pedidos:
        for it in ped['items']:
            cfg = RECETARIO[it['fam']]
            # A) Agrupar Masas
            m_id = cfg["masa_id"]
            if it['esp'] == "Red Velvet Premium": m_id = "Masa_Red_Velvet"
            if m_id not in batidos_lote: batidos_lote[m_id] = []
            it_v = it.copy(); it_v['cli'] = ped['cliente']; batidos_lote[m_id].append(it_v)

            # B) Identificar Extras (Subrecetas)
            lista_subs = []
            if it['fam'] == "CONCHAS": lista_subs.append(f"Lágrima {it['esp'].replace(' Intenso','')}")
            if it['fam'] == "ROSCA DE REYES":
                lista_subs.append("Decoración Rosca Ate")
                if it['rel'] != "Sin Relleno": lista_subs.append(it['rel'].replace("Pastelera ",""))
            if it['fam'] == "BERLINAS":
                if it['esp'] == "Ruby v2.0": lista_subs.append("Crema Ruby")
                else: lista_subs.append("Crema Vainilla")
            if it['fam'] == "ROLLOS": 
                lista_subs.append("Schmear Canela")
                if it['esp'] == "Tradicional Canela": lista_subs.append("Inclusión Frutos Rojos")

            # C) Sumar gramos de extras
            for sid in lista_subs:
                if sid in ING_RECETARIO:
                    if "Crema" in sid and it['fam'] == "ROSCA DE REYES": pu = cfg["relleno_map"][it['tam']]
                    else: pu = cfg.get("extra_peso", {}).get(it['tam'], 15) if "Lágrima" in sid else 15
                    extras_lote[sid] = extras_lote.get(sid, 0) + (pu * it['can'])

    if pag == "📋 Resumen de Carga":
        for m_id, items in batidos_lote.items():
            st.header(f"Lote de Masa: {m_id}")
            m_dna = ING_RECETARIO[m_id]
            batch_tot = sum([(RECETARIO[i['fam']]['tallas'][i['tam']] * i['can']) / m_dna.get('_merma',1) for i in items])
            hb = (batch_tot * 100) / sum([v for k,v in m_dna.items() if not k.startswith('_')])
            c1, c2 = st.columns([0.4, 0.6])
            with c1:
                st.info(f"Batido Total: {batch_tot:,.1f}g")
                for k,v in m_dna.items(): 
                    if not k.startswith('_'): st.write(f"- {k}: **{v*hb/100:,.1f}g**"); inv_compras[k] = inv_compras.get(k,0)+ (v*hb/100)
            with c2:
                for it in items: st.success(f"{it['can']}x {it['esp']} — {it['cli']}")

    elif pag == "🥣 Producción":
        cl1, cl2 = st.columns(2)
        with cl1:
            st.subheader("Masas")
            for mid, items in batidos_lote.items():
                m_dna = ING_RECETARIO[mid]; batch_p = sum([(RECETARIO[i['fam']]['tallas'][i['tam']]*i['can']) for i in items])
                hb_p = (batch_p * 100) / sum([v for k,v in m_dna.items() if not k.startswith('_')])
                st.write(f"**Lote: {mid}**")
                for k,v in m_dna.items(): 
                    if not k.startswith('_'): st.checkbox(f"{k}: {v*hb_p/100:,.1f}g", key=f"p_{mid}_{k}_{it['cli']}")
        with cl2:
            st.subheader("Complementos")
            for sid, ptot in extras_lote.items():
                s_dna = ING_RECETARIO[sid]; st.write(f"**{sid} ({ptot:,.1f}g)**")
                fs = ptot / sum(s_dna.values())
                for k,v in s_dna.items(): st.checkbox(f"{k}: {v*fs:,.1f}g", key=f"s_{sid}_{k}"); inv_compras[k] = inv_compras.get(k,0)+(v*fs)

    elif pag == "📞 WhatsApp":
        for i, ped in enumerate(st.session_state.pedidos):
            with st.container(border=True):
                r = "\n".join([f"• {it['can']}x {it['esp']} ({it['tam']})" for it in ped['items']])
                st.write(f"👤 **{ped['cliente']}**"); st.caption(r)
                msg = urllib.parse.quote(f"Hola {ped['cliente']}! Tu pedido está listo:\n{r}")
                st.link_button("🚀 Avisar Listo", f"https://wa.me/521{ped['wa']}?text={msg}")
                if st.button("Borrar", key=f"d_{i}"): st.session_state.pedidos.pop(i); st.rerun()

    elif pag == "🛒 Lista de Súper":
        st.header("🛒 Insumos Totales del Día")
        # Forzar recalculo de toda la lista para que se llene siempre
        final_inv = {}
        for mid, items in batidos_lote.items():
            md = ING_RECETARIO[mid]; m_bt = sum([(RECETARIO[it['fam']]['tallas'][it['tam']] * it['can']) for it in items])
            hb_f = (m_bt*100)/sum([v for k,v in md.items() if not k.startswith('_')])
            for k,v in md.items(): 
                if not k.startswith('_'): final_inv[k] = final_inv.get(k,0)+(v*hb_f/100)
        for sid, pt in extras_lote.items():
            sd = ING_RECETARIO[sid]; fs_f = pt / sum(sd.values())
            for k,v in sd.items(): final_inv[k] = final_inv.get(k,0)+(v*fs_f)
        for k, v in sorted(final_inv.items()): st.checkbox(f"{k}: {v:,.1f}g", key=f"inv_{k}")
            
