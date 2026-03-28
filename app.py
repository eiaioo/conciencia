import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="CONCIENCIA MASTER", layout="wide")

if 'pedidos' not in st.session_state: st.session_state.pedidos = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'cli_n' not in st.session_state: st.session_state.cli_n = ""
if 'cli_w' not in st.session_state: st.session_state.cli_w = ""

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3, h4, p, span, label { color: #000000 !important; font-weight: 600; }
    .stButton > button { border-radius: 10px; font-weight: bold; background-color: #F0F2F6; border: 1px solid #DDD; height: 3em; width: 100%; }
    .masa-box { padding: 15px; border-radius: 15px; border: 2px solid #000; margin-bottom: 15px; background-color: #F9F9F9; }
    .extra-box { padding: 15px; border-radius: 15px; border: 2px solid #FF9800; margin-bottom: 15px; background-color: #FFF8E1; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. NORMALIZACIÓN DE INGREDIENTES
# ==========================================
MAPA_NORMALIZACION = {
    "Mantequilla": "Mantequilla sin sal",
    "Mantequilla pomada": "Mantequilla sin sal",
    "Leche": "Leche entera",
    "Levadura": "Levadura seca",
    "Levadura fresca": "Levadura fresca",
    "Sal": "Sal fina",
    "Sal fina": "Sal fina",
    "Harina": "Harina de fuerza",
    "Harina de fuerza": "Harina de fuerza",
    "Cacao": "Cocoa",
    "Choco Turin": "Chocolate Turín",
    "Choco Turin Amargo": "Chocolate Turín"
}

def normalizar(nombre):
    return MAPA_NORMALIZACION.get(nombre, nombre)

# ==========================================
# 3. BASE DE DATOS MAESTRA
# ==========================================
DATABASE = {
    "CONCHAS": {
        "masa_id": "Brioche Concha",
        "tallas": {"Estándar": 95, "Mini": 35},
        "peso_sub_map": {"Estándar": 30, "Mini": 10},
        "espec": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán", "Oreo", "Pinole"]
    },
    "ROSCAS": {
        "masa_id": "Brioche Rosca 1:1",
        "tallas": {"FAMILIAR (1.45kg)": 1450, "MEDIANA (650g)": 650, "MINI (120g)": 120, "CONCHA-ROSCA (90g)": 90},
        "peso_relleno_map": {"FAMILIAR (1.45kg)": 450, "MEDIANA (650g)": 200, "MINI (120g)": 35, "CONCHA-ROSCA (90g)": 25},
        "espec": ["Tradicional", "Chocolate", "Turín"],
        "cremas": ["Sin Relleno", "Pastelera Vainilla", "Pastelera Chocolate", "Pastelera Turín", "Pastelera Ruby"]
    },
    "BERLINAS": {
        "masa_id": "Berlina 1:5",
        "tallas": {"Estándar": 60, "Especial Ruby": 70},
        "espec": ["Vainilla Clásica", "Ruby v2.0", "Turín Especial"]
    },
    "ROLES": {
        "masa_id": "Roles 1:5",
        "tallas": {"Individual": 90},
        "espec": ["Tradicional Canela", "Manzana Canela", "Red Velvet"]
    },
    "PAN MUERTO": {
        "masa_id": "Muerto Brioche",
        "tallas": {"Estándar": 85},
        "espec": ["Naranja Tradicional", "Guayaba Huesos-Refuerzo"]
    },
    "BROWNIES": {
        "masa_id": "Batch Brownie",
        "tallas": {"Molde 20x20": 1},
        "espec": ["Chocolate Turín Amargo"]
    }
}

INGREDIENTES = {
    # RECETA CORREGIDA: CONCHAS (Levadura Seca + Vainilla)
    "Brioche Concha": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0},
    
    "Brioche Rosca 1:1": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura seca": 0.35, "Sal fina": 2.2, "Azahar": 0.6},
    "Berlina 1:5": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche": 22, "Sal": 1.8, "Levadura": 1.0, "_merma": 0.85},
    "Roles 1:5": {"Harina de fuerza": 93, "Huevo": 30, "Leche": 5, "Levadura fresca": 1.0, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17},
    "Masa Red Velvet": {"Harina de fuerza": 93, "Huevo": 30, "Leche": 5, "Levadura fresca": 1.0, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17, "Colorante Rojo": 2, "Cocoa": 5},
    "Muerto Brioche": {"Harina": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Sal": 1.8, "Polvo Guayaba": 5, "Levadura fresca": 5.0},
    "Batch Brownie": {"Mantequilla": 330, "Azúcar": 395, "Choco Turin": 165, "Harina de fuerza": 190, "Cocoa": 75, "Nuez": 140, "Sal": 8},
    
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Matcha": {"Harina de fuerza": 95, "Matcha": 5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Fresa": {"Harina de fuerza": 95, "Fresa Polvo": 5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Mazapán": {"Harina de fuerza": 80, "Mazapán": 20, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Oreo": {"Harina de fuerza": 80, "Oreo Polvo": 20, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Pinole": {"Harina de fuerza": 80, "Pinole": 20, "Azúcar Glass": 100, "Mantequilla": 100},
    
    "Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Vainilla": 6},
    "Pastelera Chocolate": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Cocoa": 20},
    "Pastelera Turín": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Choco Turin": 50},
    "Pastelera Ruby": {"Leche": 131, "Crema 35%": 131, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Schmear Canela": {"Mantequilla pomada": 200, "Azúcar Mascabada": 300, "Canela": 25, "Maicena": 20},
    "Pasas Earl Grey": {"Pasas": 4, "Arándanos": 4, "Te Earl Grey": 2},
    "Decoración Rosca Ate": {"Ate Membrillo": 50, "Ate Guayaba": 50, "Higo": 20, "Cereza": 20}
}

# ==========================================
# 4. INTERFAZ DE CAPTURA
# ==========================================
with st.sidebar:
    st.title("👨‍🍳 MENÚ")
    pagina = st.radio("Navegar", ["📋 Captura", "📉 Resumen", "🥣 Producción", "🛒 Lista Súper"])
    if st.button("🗑️ VACIAR DÍA"): 
        st.session_state.pedidos = []; st.session_state.carrito = []; st.rerun()

if pagina == "📋 Captura":
    st.title("Captura de Pedidos")
    c1, c2 = st.columns(2)
    st.session_state.cli_n = c1.text_input("Nombre Cliente", value=st.session_state.cli_n)
    st.session_state.cli_w = c2.text_input("WhatsApp", value=st.session_state.cli_w)
    st.divider()
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    fam = col1.selectbox("Pan", ["-"] + list(DATABASE.keys()))
    if fam != "-":
        db_f = DATABASE[fam]
        esp = col2.selectbox("Variante", db_f["espec"])
        tam = col3.selectbox("Tamaño", list(db_f["tallas"].keys()))
        can = col4.number_input("Cant", min_value=1, value=1)
        rel = "N/A"
        if "cremas" in db_f: rel = st.selectbox("Añadir Relleno", db_f["cremas"])
        if st.button("➕ AÑADIR AL CARRITO"):
            st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "can": can, "rel": rel})
            st.rerun()
    if st.session_state.carrito:
        st.subheader(f"Carrito de {st.session_state.cli_n}")
        for i, p in enumerate(st.session_state.carrito):
            relleno_txt = f" - Relleno: {p['rel']}" if p['rel'] not in ["N/A", "Sin Relleno"] else ""
            st.write(f"**{p['can']}x {p['esp']} ({p['tam']})**{relleno_txt}")
        if st.button("✅ GUARDAR PEDIDO FINAL"):
            st.session_state.pedidos.append({"cli": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()

# ==========================================
# 5. MOTOR DE CÁLCULO CENTRAL
# ==========================================
lotes_masa = {}
lotes_complementos = {}
compra_dia = {}

for ped in st.session_state.pedidos:
    for it in ped['items']:
        db_it = DATABASE[it['fam']]
        mid = db_it["masa_id"]
        if it['esp'] == "Red Velvet": mid = "Masa Red Velvet"
        if mid not in lotes_masa: lotes_masa[mid] = []
        it_ref = it.copy(); it_ref['cli_ref'] = ped['cli']
        lotes_masa[mid].append(it_ref)

        subs = []
        if it['fam'] == "CONCHAS":
            lag_sabor = f"Lágrima {it['esp']}"
            subs.append(lag_sabor if lag_sabor in INGREDIENTES else "Lágrima Vainilla")
        if it['fam'] == "ROSCAS": 
            subs.append("Decoración Rosca Ate")
            if it['rel'] != "Sin Relleno": subs.append(it['rel'])
        if it['fam'] == "BERLINAS":
            if "Ruby" in it['esp']: subs.append("Pastelera Ruby")
            elif "Turín" in it['esp']: subs.append("Pastelera Turín")
            else: subs.append("Pastelera Vainilla")
        if it['fam'] == "ROLES":
            subs.append("Schmear Canela")
            if "Tradicional" in it['esp']: subs.append("Pasas Earl Grey")
        
        for sid in subs:
            if sid in INGREDIENTES:
                p_u = 15
                if "Pastelera" in sid and it['fam']=="ROSCAS": p_u = db_it["peso_relleno_map"][it['tam']]
                elif "Lágrima" in sid: p_u = db_it["peso_sub_map"][it['tam']]
                lotes_complementos[sid] = lotes_complementos.get(sid, 0) + (p_u * it['can'])

# Consolidación con Normalización
for mid, items in lotes_masa.items():
    m_dna = INGREDIENTES[mid]
    total_g = sum([(DATABASE[i['fam']]['tallas'][i['tam']] * i['can']) / m_dna.get('_merma',1) for i in items])
    hb = (total_g * 100) / sum([v for k,v in m_dna.items() if not k.startswith('_')])
    for k,v in m_dna.items():
        if not k.startswith('_'):
            nombre_norm = normalizar(k)
            compra_dia[nombre_norm] = compra_dia.get(nombre_norm, 0) + (v*hb/100)

for sid, ptot in lotes_complementos.items():
    sdna = INGREDIENTES[sid]
    fs = ptot/sum(sdna.values())
    for k,v in sdna.items():
        nombre_norm = normalizar(k)
        compra_dia[nombre_norm] = compra_dia.get(nombre_norm, 0) + (v*fs)

# ==========================================
# 6. VISTAS
# ==========================================
if pagina == "📉 Resumen":
    st.title("Resumen")
    if not lotes_masa: st.info("No hay pedidos.")
    st.subheader("BATIDOS DE MASA")
    for mid, items in lotes_masa.items():
        m_rec = INGREDIENTES[mid]
        total_g = sum([(DATABASE[i['fam']]['tallas'][i['tam']] * i['can']) / m_rec.get('_merma',1) for i in items])
        st.markdown(f"<div class='masa-box'><b>{mid}: {total_g:,.1f} g</b></div>", unsafe_allow_html=True)
    st.subheader("COMPLEMENTOS Y RELLENOS")
    for sid, ptot in lotes_complementos.items():
        st.markdown(f"<div class='extra-box'><b>{sid}: {ptot:,.1f} g</b></div>", unsafe_allow_html=True)

elif pagina == "🥣 Producción":
    st.title("Hoja de Pesado")
    colA, colB = st.columns(2)
    with colA:
        st.header("Masas")
        for mid, items in lotes_masa.items():
            m_dna = INGREDIENTES[mid]
            total_g = sum([(DATABASE[i['fam']]['tallas'][i['tam']] * i['can']) / m_dna.get('_merma',1) for i in items])
            hb = (total_g * 100) / sum([v for k,v in m_dna.items() if not k.startswith('_')])
            st.subheader(mid)
            for k,v in m_dna.items():
                if not k.startswith('_'): 
                    st.checkbox(f"{k}: {v*hb/100:,.1f} g", key=f"m_{mid}_{k}")
    with colB:
        st.header("Extras")
        for sid, ptot in lotes_complementos.items():
            sdna = INGREDIENTES[sid]
            st.subheader(sid)
            fs = ptot/sum(sdna.values())
            for k,v in sdna.items(): 
                st.checkbox(f"{k}: {v*fs:,.1f} g", key=f"s_{sid}_{k}")

elif pagina == "🛒 Lista Súper":
    st.title("Lista de Compras")
    if not compra_dia: st.info("Agrega pedidos para ver la lista.")
    for k, v in sorted(compra_dia.items()):
        st.write(f"**{k}**: {v:,.1f} g")
