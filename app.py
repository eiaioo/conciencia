import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. SEGURIDAD DE DATOS (AUTO-LIMPIEZA)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

# Detectamos si los datos en memoria son incompatibles y limpiamos
if 'formato_datos' not in st.session_state:
    st.session_state.clear()
    st.session_state.formato_datos = "v68.0"

# Inicializamos estados limpios
if 'pedidos' not in st.session_state: st.session_state.pedidos = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0
if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'n_persist' not in st.session_state: st.session_state.n_persist = ""
if 'w_persist' not in st.session_state: st.session_state.w_persist = ""

# ==========================================
# 2. BASE DE DATOS TÉCNICA (CERO OMISIONES)
# ==========================================

# RECETAS DE MASAS (Gramos por 100g de harina)
RECETAS_MASAS = {
    "Brioche Concha": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "_merma": 1.0},
    "Brioche Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6, "_merma": 1.0},
    "Masa Berlín (TZ)": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo entero": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0, "_merma": 0.85},
    "Masa Roles": {"Harina de fuerza": 93, "Huevo entero": 30, "Leche ajuste": 5, "Levadura fresca": 1.0, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17, "_merma": 1.0},
    "Masa Muerto": {"Harina": 100, "Leche entera": 30, "Yemas": 18, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal": 1.8, "_merma": 1.0}
}

# INGREDIENTES DE COMPLEMENTOS (Porcentaje interno o batch)
RECETAS_EXTRAS = {
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Fresa": {"Harina": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla": 100},
    "Lágrima Mazapán": {"Harina": 100, "Mazapan": 66, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Oreo": {"Harina": 100, "Oreo picada": 25, "Azúcar Glass": 75, "Mantequilla": 100},
    "Lágrima Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Ruby": {"Leche": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63},
    "Crema Turín": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Chocolate Turin": 120},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Decoración Rosca Ate": {"Ate Tiras": 50, "Higo": 20, "Cereza": 10}
}

# Árbol de Selección Completo (Jerarquía)
CATALOGO_DB = {
    "CONCHAS": {
        "sabores": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán", "Oreo", "Pinole"],
        "gramajes": {"Estándar": 95, "Mini": 35},
        "gramaje_extra": {"Estándar": 30, "Mini": 10},
        "masa_ref": "Brioche Concha"
    },
    "ROSCAS": {
        "sabores": ["Tradicional", "Turín"],
        "gramajes": {"Familiar (1.5kg)": 1450, "Mediana (650g)": 650, "Mini (120g)": 120, "Concha-Rosca (90g)": 90},
        "relleno_peso_map": {"Familiar (1.5kg)": 450, "Mediana (650g)": 200, "Mini (120g)": 35, "Concha-Rosca (90g)": 25},
        "masa_ref": "Brioche Rosca",
        "cremas_disponibles": ["Sin Relleno", "Crema Vainilla", "Crema Ruby", "Crema Turín"]
    },
    "BERLINAS": {
        "sabores": ["Ruby v2.0", "Vainilla Especial", "Turín Especial"],
        "gramajes": {"Estándar (60g)": 60, "Ruby (70g)": 70},
        "masa_ref": "Masa Berlín (TZ)"
    },
    "ROLES": {
        "sabores": ["Canela", "Manzana"],
        "gramajes": {"Individual": 90},
        "masa_ref": "Masa Roles"
    },
    "PAN MUERTO": {
        "sabores": ["Tradicional", "Guayaba"],
        "gramajes": {"Estándar": 90},
        "masa_ref": "Masa Muerto"
    }
}

# ==========================================
# 3. INTERFAZ Y ESTILO
# ==========================================

C_BG = "#0E1117" if st.session_state.tema_oscuro else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.tema_oscuro else "#1F2328"
C_SEC = "#161B22" if st.session_state.tema_oscuro else "#F8F9FA"
C_BRD = "#30363D" if st.session_state.tema_oscuro else "#DDDDDD"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label, div {{ color: {C_TXT} !important; }}
    /* Barras Blancas Off */
    div[data-testid="stExpander"], .streamlit-expanderHeader {{ background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important; }}
    /* Selectores Oscuros */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{ background-color: {C_BG} !important; border: 1px solid {C_BRD} !important; }}
    /* Cantidad Number Input Fix */
    div[data-testid="stNumberInput"] button {{ background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important; }}
    /* Botones Pro */
    .stButton > button {{ border-radius: 8px; width: 100%; background-color: {C_SEC}; color: {C_TXT}; border: 1px solid {C_BRD}; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("👨‍🍳 MENÚ MAESTRO")
    pag = st.radio("Secciones", ["🛒 Captura (Pedido)", "📊 Resumen Visual", "🥣 Producción", "📦 Lista Súper"])
    if st.button("☀️/🌙 " + ("Modo Oscuro" if st.session_state.tema_oscuro else "Modo Claro")):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro; st.rerun()
    if st.button("🗑️ VACIAR TODO"):
        st.session_state.pedidos = []; st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. LÓGICA DE CAPTURA (LALO PERSISTE)
# ==========================================

st.header(f"Conciencia — {pag}")

if pag == "🛒 Captura (Pedido)":
    with st.container():
        c1, c2 = st.columns(2)
        # Seteamos el valor de st.session_state.n_persist para que no se borre
        nombre_it = c1.text_input("Nombre Cliente", value=st.session_state.n_persist)
        st.session_state.n_persist = nombre_it # Actualizar persistencia
        wa_it = c2.text_input("WhatsApp", value=st.session_state.w_persist)
        st.session_state.w_persist = wa_it
    
    st.divider()
    fk = st.session_state.form_id
    sc1, sc2, sc3, sc4, sc5 = st.columns([2, 2, 1.5, 1, 0.5])
    fam = sc1.selectbox("Producto", ["-"] + list(CATALOGO_DB.keys()), key=f"f_{fk}")
    
    if fam != "-":
        esp = sc2.selectbox("Especialidad", CATALOGO_DB[fam]["sabores"], key=f"e_{fk}")
        tam = sc3.selectbox("Tamaño", list(CATALOGO_DB[fam]["gramajes"].keys()), key=f"t_{fk}")
        can = sc4.number_input("Cantidad", min_value=1, value=1, key=f"c_{fk}")
        
        rel = "N/A"
        if fam == "ROSCAS":
            rel = st.selectbox("Añadir Relleno", CATALOGO_DB[fam]["cremas_disponibles"], key=f"r_{fk}")
            
        sc5.write("##") # Alineación perfecta del botón ➕
        if sc5.button("➕", key=f"btn_add_{fk}"):
            st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "can": can})
            st.session_state.form_id += 1; st.rerun()

    if st.session_state.carrito:
        st.info(f"CARRITO PARA: **{st.session_state.n_persist}**")
        for i, it in enumerate(st.session_state.carrito):
            st.caption(f"{it['can']}x {it['esp']} {it['fam']} ({it['tam']})")
        if st.button("✅ GUARDAR Y ENVIAR A COCINA"):
            if st.session_state.n_persist:
                st.session_state.pedidos.append({"cliente": st.session_state.n_persist, "wa": st.session_state.w_persist, "items": st.session_state.carrito.copy()})
                st.session_state.carrito = []; st.session_state.n_persist = ""; st.session_state.w_persist = ""; st.rerun()
            else: st.error("Ingresa un nombre para cerrar el pedido.")

# ==========================================
# 5. MOTOR DE PROCESAMIENTO CENTRAL
# ==========================================

if st.session_state.pedidos:
    final_master_list = {} # Insumos compras
    dict_masa_lotes = {} # Batidos agrupados
    dict_extra_lotes = {} # Bowl de complementos

    for orden in st.session_state.pedidos:
        for it in orden['items']:
            cfg = CATALOGO_DB[it['fam']]
            # A) Agrupar Masa
            mid = cfg["masa_ref"]
            if it['esp'] == "Red Velvet Premium": mid = "Masa Red Velvet"
            if mid not in dict_masa_lotes: dict_masa_lotes[mid] = []
            it_r = it.copy(); it_r['cli'] = orden['cliente']; dict_masa_lotes[mid].append(it_r)
            
            # B) Agrupar Extras
            ext_names = []
            if it['fam'] == "CONCHAS": ext_names.append(f"Lágrima {it['esp']}")
            if it['fam'] == "ROSCAS":
                ext_names.append("Decoración Rosca Ate")
                if it['rel'] != "Sin Relleno": ext_names.append(it['rel'])
            if it['fam'] == "BERLINAS": 
                if "Ruby" in it['esp']: ext_names.append("Crema Ruby")
                elif "Turín" in it['esp']: ext_names.append("Crema Turín")
                else: ext_names.append("Crema Vainilla")
            
            for sid in ext_names:
                # Calcular peso exacto para extra
                p_u_x = 0
                if "Crema" in sid and it['fam'] == "ROSCAS": p_u_x = cfg["p_relleno_map"][it['tam']]
                elif "Lágrima" in sid: p_u_x = cfg["p_ex"][it['tam']]
                else: p_u_x = 15
                
                dict_extra_lotes[sid] = dict_extra_lotes.get(sid, 0) + (p_u_x * it['can'])

    if pag == "📋 Resumen Visual":
        for mid, items in dict_masa_lotes.items():
            st.header(f"🛠️ BATIDO: {mid}")
            mdna = RECETAS_MASAS[mid]; m_batch = sum([(CATALOGO_DB[i['fam']]['gramajes'][i['tam']] * i['can']) / mdna['_merma'] for i in items])
            hb = (m_batch*100) / sum([v for k,v in mdna['receta'].items()]); ca, cb = st.columns([0.4, 0.6])
            with ca: 
                st.write(f"Batido Total: **{m_batch:,.1f}g**")
                for k,v in mdna['receta'].items(): g = v*hb/100; st.write(f"- {k}: {g:,.1f}g"); final_master_list[k] = final_master_list.get(k,0)+g
            with cb:
                for i in items:
                    st.success(f"{i['can']}x {i['esp']} ({i['tam']}) — {i['cli']}")
                    # Desglose de lágrima en el mismo resumen
                    sn = f"Lágrima {i['esp']}" if i['fam']=="CONCHAS" else None
                    if sn and sn in RECETAS_EXTRAS:
                        sr = RECETAS_EXTRAS[sn]; ptot = CATALOGO_DB[i['fam']]['p_ex'][i['tam']] * i['can']; fs = ptot/sum(sr.values())
                        st.write(f"--- {sn} ({ptot:,.1f}g) ---")
                        for k,v in sr.items():
                            if k!='col': st.write(f"*{k}: {v*fs:,.1f}g*"); final_master_list[k] = final_master_list.get(k,0)+ (v*fs)

    elif pag == "🥣 Producción":
        cl1, cl2 = st.columns(2)
        with cl1:
            st.subheader("Masas")
            for mid, items in dict_masa_lotes.items():
                mdna = RECETAS_MASAS[mid]; mbt = sum([(CATALOGO_DB[i['fam']]['gramajes'][i['tam']]*i['can']) for i in items]); hbl = (mbt*100)/sum(mdna['receta'].values())
                st.write(f"**Lote: {mid}**")
                for et in mdna.get("etapas", [{"n": "Amasado Total", "i": list(mdna['receta'].keys()), "c":"#EEE"}]):
                    st.markdown(f'<div class="etapa-box" style="background-color: {et["c"]};">{et["n"]}</div>', unsafe_allow_html=True)
                    for k in et['i']: st.checkbox(f"{k}: {mdna['receta'][k]*hbl/100:,.1f}g", key=f"bt_{mid}_{k}_{it['cli']}")
        with cl2:
            st.subheader("Complementos (En Bowl)")
            for sid, ptot in dict_extra_lotes.items():
                if sid not in RECETAS_EXTRAS: continue
                sdna = RECETAS_EXTRAS[sid]; st.write(f"**{sid} ({ptot:,.0f}g)**")
                fs = ptot / sum(sdna.values())
                for k,v in sdna.items():
                    if k!='col': st.checkbox(f"{k}: {v*fs:,.1f}g", key=f"sd_{sid}_{k}"); final_master_list[k] = final_master_list.get(k,0)+ (v*fs)

    elif pag == "🛒 Súper":
        st.header("Lista de Insumos (Cálculo Completo)")
        for k, v in sorted(final_master_list.items()): st.checkbox(f"{k}: **{v:,.1f}g**", key=f"fs_{k}")
