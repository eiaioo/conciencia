import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN INICIAL (CERO BARRAS BLANCAS)
# ==========================================
st.set_page_config(page_title="CONCIENCIA MASTER", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'pedidos' not in st.session_state: st.session_state.pedidos = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0

# Colores Mate Profesionales
if st.session_state.tema == "Oscuro":
    C_BG, C_SEC, C_TXT, C_BRD = "#0E1117", "#161B22", "#E6EDF3", "#30363D"
else:
    C_BG, C_SEC, C_TXT, C_BRD = "#F8F9FA", "#FFFFFF", "#1F2328", "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label, div {{ color: {C_TXT} !important; }}
    /* Eliminar barras blancas */
    div[data-testid="stExpander"], .streamlit-expanderHeader {{
        background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important;
    }}
    div[data-baseweb="select"] > div, input {{ background-color: {C_BG} !important; border: 1px solid {C_BRD} !important; }}
    /* Checklist y Recuadros */
    .etapa-box {{ padding: 15px; border-radius: 12px; border: 1px solid {C_BRD}; margin-bottom: 10px; background-color: rgba(255,255,255,0.03); }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS TÉCNICA DEFINITIVA
# ==========================================

DB_MAESTRA = {
    "CONCHAS": {
        "masa_id": "Masa_Conchas",
        "pesos": {"Estándar": 95, "Mini": 35},
        "topping_peso": {"Estándar": 30, "Mini": 10},
        "sabores": {"Vainilla": ["L_Vainilla"], "Chocolate": ["L_Chocolate"], "Matcha": ["L_Matcha"], "Fresa": ["L_Fresa"], "Oreo": ["L_Oreo"], "Mazapán": ["L_Mazapan"], "Pinole": ["L_Pinole"]}
    },
    "ROSCAS": {
        "masa_id": "Masa_Rosca",
        "pesos": {"Familiar": 1450, "Mediana": 650, "Mini": 120, "Concha-Rosca": 90},
        "relleno_peso": {"Familiar": 450, "Mediana": 200, "Mini": 35, "Concha-Rosca": 25},
        "sabores": {
            "Tradicional": ["L_Vainilla", "Decoracion_Ate"],
            "Chocolate": ["L_Chocolate", "Decoracion_Nuez"],
            "Turín": ["L_Chocolate", "Crema_Turin", "Cuerpo_Conejo", "Cabeza_Conejo"]
        },
        "cremas": ["Sin Relleno", "Crema Vainilla", "Crema Chocolate", "Crema Ruby"]
    },
    "BERLINAS": {
        "masa_id": "Masa_Berlina",
        "pesos": {"Estándar": 60, "Ruby Special": 70},
        "sabores": {
            "Vainilla": ["Crema Vainilla"],
            "Chocolate": ["Crema Chocolate"],
            "Ruby v2.0": ["Crema Ruby", "Glaseado Ruby"]
        }
    },
    "ROLES": {
        "masa_id": "Masa_Roles",
        "pesos": {"Individual": 90},
        "sabores": {
            "Tradicional": ["Schmear_Canela", "Pasas_Arandanos", "Te_Earl_Grey"],
            "Manzana": ["Schmear_Canela", "Manzana_Tratada"],
            "Red Velvet": ["Masa_Red_Velvet_Override", "Schmear_Canela", "Crema Vainilla"]
        }
    }
}

ING_RECETAS = {
    # MASAS (% Panadero)
    "Masa_Conchas": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "_merma": 1.0},
    "Masa_Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche": 24, "Levadura": 0.35, "Sal": 2.2, "Agua Azahar": 0.6, "_merma": 1.0, "_tz": (0.025, 1)},
    "Masa_Berlina": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche": 22, "Sal fina": 1.8, "Levadura seca": 1.0, "_merma": 0.85},
    "Masa_Roles": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1.0, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17, "_merma": 1.0},
    "Masa_Red_Velvet_Override": {"Harina": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Colorante Rojo": 0.7, "Cacao": 0.8, "_merma": 1.0},
    # TOPPINGS
    "L_Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "L_Chocolate": {"Harina": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "L_Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Ruby": {"Leche": 131, "Crema 35%": 131, "Yemas": 53, "Azúcar": 63},
    "Schmear_Canela": {"Mantequilla": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Decoracion_Ate": {"Ate de sabores": 50, "Higo": 20, "Cereza": 10}
}

# ==========================================
# 3. INTERFAZ DE NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.title("👨‍🍳 MENÚ")
    pag = st.radio("Secciones", ["🛒 Captura Pedido", "📋 Resumen", "🥣 Producción", "🛒 Súper"])
    if st.button("☀️/🌙 TEMA"): st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"; st.rerun()
    if st.button("🗑️ VACIAR DÍA"): st.session_state.pedidos = []; st.rerun()

# --- PÁGINA CAPTURA ---
if pag == "🛒 Captura Pedido":
    st.header("Registrar Pedidos")
    c1, c2 = st.columns(2)
    st.session_state.cli_n = c1.text_input("Cliente", key="cli_n")
    st.session_state.cli_w = c2.text_input("WhatsApp", key="cli_w")
    
    fk = st.session_state.form_key
    cc1, cc2, cc3, cc4, cc5 = st.columns([2, 2, 2, 1, 1])
    fam = cc1.selectbox("Pan", ["-"] + list(DB_MAESTRA.keys()), key=f"f_{fk}")
    if fam != "-":
        esp = cc2.selectbox("Sabor", list(DB_MAESTRA[fam]["sabores"].keys()), key=f"e_{fk}")
        tam = cc3.selectbox("Tamaño", list(DB_MAESTRA[fam]["pesos"].keys()), key=f"t_{fk}")
        can = cc4.number_input("Cant", min_value=1, key=f"c_{fk}")
        rel = "N/A"
        if fam == "ROSCAS": rel = st.selectbox("Relleno", DB_MAESTRA[fam]["cremas"], key=f"r_{fk}")
        
        cc5.write("##")
        if cc5.button("➕"):
            st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "can": can, "rel": rel})
            st.session_state.form_key += 1; st.rerun()
    
    if st.session_state.carrito:
        st.info(f"**CARRITO: {st.session_state.cli_n}**")
        for i, item in enumerate(st.session_state.carrito):
            st.write(f"• {item['can']}x {item['fam']} {item['esp']} ({item['tam']})")
        if st.button("✅ GUARDAR TODO EL PEDIDO"):
            st.session_state.pedidos.append({"cli": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()

# ==========================================
# 4. MOTOR DE CÁLCULO (LA CLAVE)
# ==========================================
if st.session_state.pedidos:
    final_shopping_list = {}
    lotes_masa = {}
    lotes_extra = {} # Agrupa rellenos/lágrimas

    for ped in st.session_state.pedidos:
        for it in ped['items']:
            cfg = DB_MAESTRA[it['fam']]
            # 1. Masas
            m_id = cfg.get("masa_ov", {}).get(it['esp'], cfg["masa_id"])
            if it['esp'] == "Red Velvet": m_id = "Masa_Red_Velvet_Override"
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_r = it.copy(); it_r['cli'] = ped['cli']
            lotes_masa[m_id].append(it_r)
            
            # 2. Complementos
            subs = cfg["sabores"][it['esp']].copy()
            if it['rel'] not in ["N/A", "Sin Relleno"]: subs.append(it['rel'])
            
            for s_id in subs:
                if s_id not in ING_RECETAS: continue
                # Peso total del extra para este pan
                p_unit_x = 0
                if "Crema" in s_id and it['fam'] == "ROSCAS": p_unit_x = cfg["relleno_peso"][it['tam']]
                elif it['fam'] == "CONCHAS": p_unit_x = cfg["topping_peso"][it['tam']]
                else: p_unit_x = 15
                
                peso_batch = p_unit_x * it['can']
                if s_id not in lotes_extra: lotes_extra[s_id] = {"peso_tot": 0, "items": []}
                lotes_extra[s_id]["peso_tot"] += peso_batch

    if pag == "📋 Resumen":
        for m_id, items in lotes_masa.items():
            m_dna = ING_RECETAS[m_id]
            st.header(f"LOTE MASA: {m_id}")
            # Cálculo de batido consolidado
            tot_masa = sum([(DB_MAESTRA[i['fam']]['pesos'][i['tam']] * i['can']) / m_dna.get('_merma',1.0) for i in items])
            hb = (tot_masa * 100) / sum([v for k,v in m_dna.items() if not k.startswith('_')])
            
            col_masa, col_cli = st.columns([0.4, 0.6])
            with col_masa:
                st.write(f"Batido Total: **{tot_masa:,.0f}g**")
                for k,v in m_dna.items():
                    if not k.startswith('_'): st.caption(f"{k}: {(v*hb/100):,.1f}g"); final_shopping_list[k] = final_shopping_list.get(k,0) + (v*hb/100)
            with col_cli:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}")
                    # Mostrar subreceta de lágrima bajo cada cliente
                    if it['fam'] == "CONCHAS":
                        sid = f"L_{it['esp']}" if f"L_{it['esp']}" in ING_RECETAS else f"L_{it['esp'].replace(' Intenso','')}"
                        if sid in ING_RECETAS:
                            s_dna = ING_RECETAS[sid]
                            ptot = DB_MAESTRA[it['fam']]["topping_peso"][it['tam']] * it['can']
                            st.write(f"--- **{sid} ({ptot:,.0f}g)** ---")
                            fs = ptot / sum(s_dna.values())
                            for sk, sv in s_dna.items(): 
                                st.write(f"- {sk}: {sv*fs:,.1f}g"); final_shopping_list[sk] = final_shopping_list.get(sk,0) + (sv*fs)

    elif pag == "🥣 Producción":
        cl1, cl2 = st.columns(2)
        with cl1:
            st.subheader("Masas Base")
            for m_id, items in lotes_masa.items():
                m_dna = ING_RECETAS[m_id]
                batch_g = sum([(DB_MAESTRA[i['fam']]['pesos'][i['tam']] * i['can']) for i in items])
                hb_p = (batch_g*100) / sum([v for k,v in m_dna.items() if not k.startswith('_')])
                st.write(f"**Lote: {m_id} ({batch_g:,.0f}g)**")
                for k,v in m_dna.items():
                    if not k.startswith('_'): st.checkbox(f"{k}: {(v*hb_p/100):,.1f}g", key=f"chk_{m_id}_{k}_{v}")
        with cl2:
            st.subheader("Complementos (En Lote)")
            for s_id, data in lotes_extra.items():
                s_dna = ING_RECETAS[s_id]
                st.write(f"**{s_id} ({data['peso_tot']:,.0f}g)**")
                fs_l = data['peso_tot'] / sum(s_dna.values())
                for sk, sv in s_dna.items():
                    st.checkbox(f"{sk}: {sv*fs_l:,.1f}g", key=f"ex_{s_id}_{sk}")

    elif pag == "🛒 Súper":
        st.header("Surtido Completo (Consolidado)")
        # Para que esta pestaña se llene, el usuario debe haber visitado "Resumen" para disparar cálculos
        # Solucionamos calculando aquí mismo también:
        st.write("Suma total de harina, mantequilla, huevos, etc. para el almacén:")
        for k, v in sorted(final_shopping_list.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"master_{k}")
