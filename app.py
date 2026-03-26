import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA (SINGLE SOURCE OF TRUTH)
# ==========================================

DB_MASAS = {
    "CONCHA": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "merma": 1.0, "factor": 1.963},
    "BERLINA": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche": 22, "Sal": 1.8, "Levadura seca": 1.0, "merma": 0.85, "tz": (0.05, 5)},
    "ROL_CANELA": {"Harina de fuerza": 93, "Huevo": 30, "Leche": 5, "Levadura fresca": 1, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17, "merma": 1.0, "tz_fijo": (70, 350)},
    "ROL_RV": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7, "Vinagre": 0.3, "merma": 1.0, "tz": (0.07, 5)},
    "ROSCA": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla": 30, "Huevo": 20, "Yema": 4, "Leche": 24, "Levadura": 0.35, "Sal": 2.2, "Agua Azahar": 0.6, "merma": 1.0, "tz": (0.025, 1)},
    "MUERTO_TRAD": {"Harina": 100, "Leche": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla": 25, "Sal": 2, "Levadura": 3, "Azahar": 2, "Ralladura": 1, "merma": 1.0},
    "MUERTO_GUAYABA": {"Harina": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura": 5, "Sal": 1.8, "Polvo Guayaba": 5, "merma": 1.0, "huesos": True},
    "BROWNIE": {"Mantequilla": 330, "Azúcar Blanca": 275, "Mascabado": 120, "Chocolate": 165, "Harina": 190, "Cocoa": 75, "Sal": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez": 140, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "L_Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Choco": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Mazapan_I": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66},
    "L_Oreo": {"Harina": 100, "Azúcar Glass": 75, "Mantequilla": 100, "Oreo": 25},
    "C_Ruby": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "Mantequilla": 16, "Sal": 0.8},
    "G_Ruby": {"Choco Ruby": 80, "Azúcar Glass": 160, "Leche": 50},
    "C_Turin_Leche": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla": 20},
    "G_Turin_Costra": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche": 50, "Sal": 1, "Cabeza Conejo": 1},
    "C_Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Vainilla": 6},
    "S_Canela": {"Mantequilla": 200, "Azúcar Mascabado": 300, "Canela": 25, "Maicena": 20},
    "S_RV": {"Mantequilla": 6, "Azúcar": 6, "Cacao": 1.8, "Maicena": 0.6, "Nuez": 4, "Chocolate": 4},
    "I_FrutosRojos": {"Pasas": 4, "Arandanos": 4, "Te Earl Grey": 2, "Vainilla": 0.5},
    "I_Manzana": {"Orejón Manzana": 8, "Agua tibia": 2},
    "R_Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5}
}

# ARBOL DE DECISIÓN (PRODUCTO -> SABOR -> TAMAÑO -> RELLENO)
ARBOL = {
    "Conchas": {
        "sabores": {"Vainilla": ["L_Vainilla"], "Chocolate": ["L_Choco"], "Matcha": ["L_Matcha"], "Pinole": ["L_Pinole"], "Mazapán Intenso": ["L_Mazapan_I"], "Oreo": ["L_Oreo"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "peso_ex": {"Estándar": 30, "Mini": 10}, "masa": "CONCHA"
    },
    "Berlinas": {
        "sabores": {
            "Ruby v2.0": ["C_Ruby", "G_Ruby"], 
            "Conejo Turín": ["C_Turin_Leche", "G_Turin_Costra"],
            "Vainilla Clásica": ["C_Vainilla"]
        },
        "tamaños": {"Estándar": 60}, "masa": "BERLINA", 
        "pesos_manuales": {"Ruby v2.0": (70, {"C_Ruby": 40, "G_Ruby": 8}), "Conejo Turín": (60, {"C_Turin_Leche": 80, "G_Turin_Costra": 16})}
    },
    "Rollos": {
        "sabores": {
            "Tradicional (Canela)": ["S_Canela", "I_FrutosRojos"],
            "Manzana Canela": ["S_Canela", "I_Manzana"],
            "Red Velvet Premium": ["S_RV"]
        },
        "tamaños": {"Individual": 90}, "masa": "ROL_CANELA", "peso_ex": 15,
        "masa_override": {"Red Velvet Premium": "ROL_RV"}
    },
    "Rosca de reyes": {
        "sabores": {"Tradicional": [], "Vainilla": ["C_Vainilla"], "Chocolate": ["C_Turin_Leche"]},
        "tamaños": {"Mediana": 900, "Individual": 100}, "masa": "ROSCA", "peso_ex": 80
    },
    "Pan de muerto": {
        "sabores": {"Tradicional": ["R_Muerto"], "Guayaba": ["R_Muerto"]},
        "tamaños": {"Estándar": 85}, "masa": "MUERTO_TRAD", "peso_ex": 1,
        "masa_override": {"Guayaba": "MUERTO_GUAYABA"}
    },
    "Brownies": {
        "sabores": {"Turín Clásico": []}, "tamaños": {"Molde 12 pzas": 1}, "masa": "BROWNIE"
    }
}

# ==========================================
# 2. INTERFAZ EN CASCADA
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []

st.title("🥐 Gestión Técnica CONCIENCIA v9.0")

with st.container(border=True):
    st.subheader("Cargar Producto")
    # NIVEL 1
    p_familia = st.selectbox("1. Selecciona Familia", ["-"] + list(ARBOL.keys()))
    
    if p_familia != "-":
        # NIVEL 2
        p_sabor = st.selectbox(f"2. Selecciona Sabor de {p_familia}", ["-"] + list(ARBOL[p_familia]["sabores"].keys()))
        
        if p_sabor != "-":
            # NIVEL 3
            p_tamaño = st.selectbox("3. Selecciona Tamaño", list(ARBOL[p_familia]["tamaños"].keys()))
            
            # NIVEL 4
            p_cantidad = st.number_input("4. Cantidad de piezas", min_value=1, value=12)
            
            if st.button("➕ AGREGAR A LA COMANDA"):
                st.session_state.comanda.append({
                    "familia": p_familia, "sabor": p_sabor, "tamaño": p_tamaño, "cantidad": p_cantidad
                })
                st.rerun()

# ==========================================
# 3. HOJA DE PRODUCCIÓN (DOS COLUMNAS)
# ==========================================

if st.session_state.comanda:
    st.subheader("📋 Comanda Activa")
    st.table(pd.DataFrame(st.session_state.comanda))
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()

    t_pesado, t_almacen = st.tabs(["🥣 Detalle de Pesado", "📦 Lista de Insumos"])
    resumen_insumos = {}

    with t_pesado:
        for item in st.session_state.comanda:
            config = ARBOL[item['familia']]
            m_id = config.get("masa_override", {}).get(item['sabor'], config['masa'])
            m_dna = DB_MASAS[m_id]
            
            st.header(f"✨ {item['cantidad']}x {item['sabor']} ({item['tamaño']})")
            
            col1, col2 = st.columns(2)
            
            # --- COLUMNA 1: MASA ---
            with col1:
                st.markdown("### 📦 MASA")
                if m_dna.get("fijo"):
                    for ing, val in m_dna.items():
                        if ing not in ["merma", "fijo"]:
                            gr = val * item['cantidad']; st.write(f"• {ing}: {gr:,.1f}g")
                            resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
                else:
                    peso_u = config.get("pesos_manuales", {}).get(item['sabor'], (config['tamaños'][item['tamaño']],0))[0]
                    masa_tot = (peso_u * item['cantidad']) / m_dna['merma']
                    sum_porc = sum([v for k,v in m_dna.items() if isinstance(v, (int, float)) and k not in ["merma", "factor"]])
                    h_base = (masa_tot * 100) / sum_porc
                    
                    for ing, val in m_dna.items():
                        if isinstance(val, (int, float)) and ing not in ["merma", "factor"]:
                            gr = (val * h_base) / 100; st.write(f"• {ing}: {gr:,.1f}g")
                            resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
                    
                    if "tz" in m_dna:
                        tz_h = h_base * m_dna["tz"][0]; tz_l = tz_h * m_dna["tz"][1]
                        st.warning(f"⚡ Tangzhong: {tz_h:,.1f}g Harina | {tz_l:,.1f}g Leche")
                    if "tz_fijo" in m_dna:
                        f = h_base / 930
                        st.warning(f"⚡ Tangzhong: {70*f:,.1f}g Harina | {350*f:,.1f}g Leche")

            # --- COLUMNA 2: COMPLEMENTOS ---
            with col2:
                st.markdown("### 🎨 COMPLEMENTOS")
                subs = config["sabores"][item['sabor']]
                for sub_id in subs:
                    st.write(f"**{sub_id}**")
                    sub_receta = DB_COMPLEMENTOS[sub_id]
                    
                    # Lógica de peso de sub-receta
                    if "pesos_manuales" in config and item['sabor'] in config["pesos_manuales"]:
                        p_sub_tot = config["pesos_manuales"][item['sabor']][1].get(sub_id, 0) * item['cantidad']
                    else:
                        p_u_sub = config.get("peso_ex", {}).get(item['tamaño'], config.get("peso_ex", 0))
                        p_sub_tot = p_u_sub * item['cantidad']

                    factor = p_sub_tot / sum([v for v in sub_receta.values() if isinstance(v, (int, float))])
                    for ing, val in sub_receta.items():
                        if "Cabeza" in ing:
                            st.write(f"- {ing}: {val*item['cantidad']} pzas")
                            resumen_insumos[ing] = resumen_insumos.get(ing, 0) + (val*item['cantidad'])
                        else:
                            gr = val * factor; st.write(f"- {ing}: {gr:,.1f}g")
                            resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
                
                if m_dna.get("huesos"):
                    res = masa_tot * 0.25; st.info(f"🦴 Refuerzo Huesos: {res*0.3:,.1f}g Harina / {res*0.1:,.1f}g Yema")
                    resumen_insumos["Harina de fuerza"] = resumen_insumos.get("Harina de fuerza", 0) + (res*0.3)
                    resumen_insumos["Yemas"] = resumen_insumos.get("Yemas", 0) + (res*0.1)

            st.divider()

    with t_almacen:
        st.header("🛒 Lista Maestra de Insumos")
        df_sum = pd.DataFrame(resumen_insumos.items(), columns=["Insumo", "Cantidad Total"]).sort_values("Insumo")
        st.dataframe(df_sum, use_container_width=True)
