import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Producción Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA (DNA CONCIENCIA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "merma": 1.0, "factor": 1.963},
    "Masa de Berlinas": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0, "merma": 0.85, "tz": (0.05, 5)},
    "Masa Brioche Roles": {"Harina de fuerza": 93, "Huevo": 30, "Leche (ajuste)": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17, "merma": 1.0, "tz_fijo": (70, 350)},
    "Masa Red Velvet": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao en polvo": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3, "merma": 1.0, "tz": (0.07, 5)},
    "Masa Brioche Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6, "merma": 1.0, "tz": (0.025, 1)},
    "Masa Muerto Tradicional": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3, "Agua Azahar": 2, "Ralladura Naranja": 1, "merma": 1.0},
    "Masa Muerto Guayaba": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5, "merma": 1.0, "huesos": True},
    "Mezcla de Brownies": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa alcalinizada": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez Tostada": 140, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    # LÁGRIMAS
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Matcha": {"Harina de fuerza": 91.5, "Matcha en polvo": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik Fresa": 21, "Mantequilla sin sal": 100},
    "Lágrima de Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66},
    "Lágrima de Pinole": {"Harina de fuerza": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Galleta Oreo": 25},
    # CREMAS
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Crema Pastelera Chocolate": {"Leche entera": 480, "Yemas": 100, "Azúcar": 100, "Fécula de Maíz": 45, "Chocolate 60%": 120, "Mantequilla sin sal": 30},
    "Crema Pastelera Especial Turín": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula de Maíz": 45, "Chocolate Turin": 120, "Mantequilla sin sal": 20},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema para batir 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula de Maíz": 24, "Mantequilla sin sal": 16, "Sal": 0.8},
    # ACABADOS
    "Glaseado Ruby": {"Chocolate Ruby": 80, "Azúcar Glass": 160, "Leche entera": 50},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Turin Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1},
    "Decoración Tradicional Rosca": {"Ate de colores": 50, "Higo en almíbar": 20, "Cereza marrasquino": 10},
    "Decoración Nuez": {"Nuez Fileteada": 15},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Schmear Red Velvet": {"Mantequilla sin sal": 6, "Azúcar": 6, "Cacao": 1.8, "Nuez": 4, "Chocolate amargo": 4},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2},
    "Inclusión Manzana": {"Orejón de Manzana": 8, "Agua tibia": 2}
}

ARBOL = {
    "Conchas": {
        "especialidad": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"], "Matcha": ["Lágrima de Matcha"], "Fresa": ["Lágrima de Fresa"], "Mazapán Intenso": ["Lágrima de Mazapán"], "Oreo": ["Lágrima de Oreo"], "Pinole": ["Lágrima de Pinole"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"
    },
    "Berlinas": {
        "especialidad": {
            "Vainilla Clásica": ["Crema Pastelera Vainilla"], 
            "Ruby v2.0": ["Crema Ruby 50/50", "Glaseado de Chocolate Ruby"], 
            "Conejo Turín": ["Crema Pastelera Especial Turín", "Glaseado Turin"]
        },
        "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas",
        "override_p": {"Ruby v2.0": (70, {"Crema Ruby 50/50": 40, "Glaseado de Chocolate Ruby": 8}), "Conejo Turín": (60, {"Crema Pastelera Especial Turín": 80, "Glaseado Turin": 16})}
    },
    "Rollos": {
        "especialidad": {
            "Tradicional Canela": ["Schmear Canela", "Inclusión Frutos Rojos"], 
            "Manzana Canela": ["Schmear Canela", "Inclusión Manzana"],
            "Red Velvet Premium": ["Schmear Red Velvet"]
        },
        "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15,
        "masa_override": {"Red Velvet Premium": "Masa Red Velvet"}
    },
    "Rosca de reyes": {
        "especialidad": {
            "Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Tradicional Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate"]},
            "Chocolate": {"fijos": ["Lágrima de Chocolate", "Decoración Nuez"], "rellenos": ["Sin Relleno", "Crema Pastelera Chocolate"]},
            "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Pastelera Especial Turín"]}
        },
        "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90},
        "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25},
        "masa": "Masa Brioche Rosca"
    },
    "Pan de muerto": {
        "especialidad": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto"]},
        "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1,
        "masa_override": {"Guayaba": "Masa Muerto Guayaba"}
    },
    "Brownies": {
        "especialidad": {"Chocolate Turín": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla de Brownies"
    }
}

# ==========================================
# 2. INTERFAZ EN CASCADA
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0
if 'expandido' not in st.session_state: st.session_state.expandido = True

st.title("🥐 Gestión de Producción CONCIENCIA v20.0")

with st.expander("📝 Cargar Nuevo Producto", expanded=st.session_state.expandido):
    f_id = st.session_state.form_id
    fam_sel = st.selectbox("1. Selecciona Familia", ["-"] + list(ARBOL.keys()), key=f"fam_{f_id}")
    
    if fam_sel != "-":
        esp_sel = st.selectbox("2. Selecciona Especialidad", ["-"] + list(ARBOL[fam_sel]["especialidad"].keys()), key=f"esp_{f_id}")
        
        if esp_sel != "-":
            tam_sel = st.selectbox("3. Selecciona Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()), key=f"tam_{f_id}")
            
            rell_sel = "N/A"
            if fam_sel == "Rosca de reyes":
                rell_sel = st.selectbox("4. Relleno Opcional", ARBOL[fam_sel]["especialidad"][esp_sel]["rellenos"], key=f"rell_{f_id}")
            
            cant_sel = st.number_input("5. Cantidad", min_value=1, value=1, key=f"cant_{f_id}")
            
            if st.button("✅ AGREGAR A LA COMANDA"):
                st.session_state.comanda.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rell": rell_sel, "cant": cant_sel})
                st.session_state.form_id += 1
                st.session_state.expandido = False
                st.rerun()

if not st.session_state.expandido:
    if st.button("➕ Agregar otro producto"):
        st.session_state.expandido = True; st.rerun()

# ==========================================
# 3. HOJA DE PRODUCCIÓN CONSOLIDADA
# ==========================================

if st.session_state.comanda:
    st.subheader("📋 Comanda Activa")
    st.table(pd.DataFrame(st.session_state.comanda))
    if st.button("🗑️ Vaciar todo"): st.session_state.comanda = []; st.session_state.expandido = True; st.rerun()

    t_rec, t_sup = st.tabs(["🥣 Hoja de Batidos", "📦 Lista Maestra"])
    resumen = {}

    lotes_masa = {}
    for i in st.session_state.comanda:
        m_id = ARBOL[i['fam']].get("masa_override", {}).get(i['esp'], ARBOL[i['fam']]['masa'])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(i)

    with t_rec:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            st.markdown(f"## 🛠️ Batido: {m_id}")
            
            m_batch_tot = 0
            for it in items:
                p_u = ARBOL[it['fam']].get("override_p", {}).get(it['esp'], (ARBOL[it['fam']]['tamaños'][it['tam']],0))[0]
                m_batch_tot += (p_u * it['cant']) / m_dna['merma']
            
            h_base =
