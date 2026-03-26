import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA (NOMBRES COMPLETOS)
# ==========================================

DB_MASAS = {
    "Masa Concha": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "merma": 1.0, "factor": 1.963},
    "Masa Berlina": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche entera": 22, "Sal": 1.8, "Levadura seca": 1.0, "merma": 0.85, "tz": (0.05, 5)},
    "Masa Roles Canela": {"Harina de fuerza": 93, "Huevo": 30, "Leche (ajuste)": 5, "Levadura fresca": 1, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17, "merma": 1.0, "tz_fijo": (70, 350)},
    "Masa Roles Red Velvet": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7, "Vinagre": 0.3, "merma": 1.0, "tz": (0.07, 5)},
    "Masa Brioche Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla": 30, "Huevo": 20, "Yema": 4, "Leche": 24, "Levadura": 0.35, "Sal": 2.2, "Agua Azahar": 0.6, "merma": 1.0, "tz": (0.025, 1)},
    "Masa Pan de Muerto Tradicional": {"Harina": 100, "Leche": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla": 25, "Sal": 2, "Levadura": 3, "Azahar": 2, "Ralladura": 1, "merma": 1.0},
    "Masa Pan de Muerto Guayaba": {"Harina": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura": 5, "Sal": 1.8, "Polvo Guayaba": 5, "merma": 1.0, "huesos": True},
    "Mezcla Brownie": {"Mantequilla": 330, "Azúcar Blanca": 275, "Mascabado": 120, "Chocolate Turin Amargo": 165, "Harina": 190, "Cocoa": 75, "Sal": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez": 140, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    # LÁGRIMAS
    "Lágrima de Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima de Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima de Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima de Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima de Mazapán Intenso": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66},
    "Lágrima de Oreo": {"Harina": 100, "Azúcar Glass": 75, "Mantequilla": 100, "Oreo": 25},
    # CREMAS
    "Crema Pastelera Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Vainilla": 6},
    "Crema Pastelera Chocolate Amargo": {"Leche": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Chocolate 60%": 120, "Mantequilla": 30},
    "Crema Pastelera Especial Turín": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla": 20},
    "Crema Ruby 50/50": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "Mantequilla": 16, "Sal": 0.8},
    # ACABADOS Y DECORACIÓN
    "Glaseado de Chocolate Ruby": {"Choco Ruby": 80, "Azúcar Glass": 160, "Leche": 50},
    "Glaseado Turín Tipo Costra": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche": 50, "Cabeza de Conejo": 1},
    "Decoración Tradicional Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Decoración Nuez Fileteada": {"Nuez Fileteada": 15},
    "Schmear de Canela": {"Mantequilla": 200, "Azúcar": 300, "Canela": 25},
    "Schmear Red Velvet": {"Mantequilla": 6, "Azúcar": 6, "Cacao": 1.8, "Maicena": 0.6, "Nuez": 4, "Chocolate": 4},
    "Rebozado de Pan de Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {
        "especialidad": {
            "Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"], 
            "Matcha": ["Lágrima de Matcha"], "Mazapán Intenso": ["Lágrima de Mazapán Intenso"], 
            "Pinole": ["Lágrima de Pinole"], "Oreo": ["Lágrima de Oreo"]
        },
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa Concha"
    },
    "Rosca de reyes": {
        "especialidad": {
            "Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Tradicional Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate Amargo"]},
            "Chocolate": {"fijos": ["Lágrima de Chocolate", "Decoración Nuez Fileteada"], "rellenos": ["Sin Relleno", "Crema Pastelera Chocolate Amargo"]},
            "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turín Tipo Costra"], "rellenos": ["Sin Relleno", "Crema Pastelera Especial Turín"]}
        },
        "tamaños": {"FAMILIAR (10-12p)": 1450, "MEDIANA (6-8p)": 650, "MINI (1-2p)": 120, "CONCHA-ROSCA": 90},
        "p_relleno_map": {"FAMILIAR (10-12p)": 450, "MEDIANA (6-8p)": 200, "MINI (1-2p)": 35, "CONCHA-ROSCA": 25},
        "masa": "Masa Brioche Rosca"
    },
    "Berlinas": {
        "especialidad": {
            "Vainilla Clásica": ["Crema Pastelera Vainilla"], 
            "Ruby v2.0": ["Crema Ruby 50/50", "Glaseado de Chocolate Ruby"], 
            "Conejo Turín": ["Crema Pastelera Especial Turín", "Glaseado Turín Tipo Costra"]
        },
        "tamaños": {"Estándar": 60}, "masa": "Masa Berlina",
        "pesos_override_berlina": {"Ruby v2.0": (70, {"Crema Ruby 50/50": 40, "Glaseado de Chocolate Ruby": 8}), "Conejo Turín": (60, {"Crema Pastelera Especial Turín": 80, "Glaseado Turín Tipo Costra": 16})}
    },
    "Rollos": {
        "especialidad": {
            "Tradicional": ["Schmear de Canela"], "Manzana": ["Schmear de Canela"], 
            "Conejo Turín": ["Schmear de Canela", "Glaseado Turín Tipo Costra"], "Red Velvet": ["Schmear Red Velvet"]
        },
        "tamaños": {"Individual": 90}, "masa": "Masa Roles Canela", "p_ex": 15, "masa_override": {"Red Velvet": "Masa Roles Red Velvet"}
    },
    "Pan de muerto": {
        "especialidad": {"Tradicional": ["Rebozado de Pan de Muerto"], "Guayaba": ["Rebozado de Pan de Muerto"]},
        "tamaños": {"Estándar": 85}, "masa": "Masa Pan de Muerto Tradicional", "masa_override": {"Guayaba": "Masa Pan de Muerto Guayaba"}
    }
}

# ==========================================
# 2. LÓGICA DE INTERFAZ
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0
if 'expandido' not in st.session_state: st.session_state.expandido = True

st.title("🥐 Gestión Técnica CONCIENCIA")

with st.expander("📝 Cargar Nuevo Producto", expanded=st.session_state.expandido):
    f_id = st.session_state.form_id
    fam = st.selectbox("1. Familia de Pan", ["-"] + list(ARBOL.keys()), key=f"f_{f_id}")
    if fam != "-":
        espec = st.selectbox("2. Especialidad", ["-"] + list(ARBOL[fam]["especialidad"].keys()), key=f"e_{f_id}")
        if espec != "-":
            tam = st.selectbox("3. Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{f_id}")
            relleno = "N/A"
            if fam == "Rosca de reyes":
                relleno = st.selectbox("4. Opción de Relleno", ARBOL[fam]["especialidad"][espec]["rellenos"], key=f"r_{f_id}")
            cant = st.number_input("Cantidad", min_value=1, value=1, key=f"c_{f_id}")
            if st.button("✅ AGREGAR A LA COMANDA"):
                st.session_state.comanda.append({"familia": fam, "especialidad": espec, "tamaño": tam, "relleno": relleno, "cantidad": cant})
                st.session_state.form_id += 1
                st.session_state.expandido = False
                st.rerun()

if not st.session_state.expandido:
    if st.button("➕ Agregar otro producto"): st.session_state.expandido = True; st.rerun()

# ==========================================
# 3. LÓGICA DE CONSOLIDACIÓN
# ==========================================

if st.session_state.comanda:
    st.subheader("📋 Comanda del Día")
    st.table(pd.DataFrame(st.session_state.comanda))
    if st.button("🗑️ Vaciar todo"): st.session_state.comanda = []; st.session_state.expandido = True; st.rerun()

    t_pesado, t_super = st.tabs(["🥣 Hoja de Producción (Batidos)", "📦 Lista Maestra de Insumos"])
    resumen_insumos = {}

    lotes_masa = {}
    for item in st.session_state.comanda:
        m_id = ARBOL[item['familia']].get("masa_override", {}).get(item['especialidad'], ARBOL[item['familia']]['masa'])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    with t_pesado:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            st.markdown(f"## 🛠️ Batido: {m_id}")
            m_total_batch = 0
            for i in items:
                p_u_m = ARBOL[i['familia']].get("pesos_override_berlina", {}).get(i['especialidad'], (ARBOL[i['familia']]['tamaños'][i['tamaño']], 0))[0]
                m_total_batch += (p_u_m * i['cantidad']) / m_dna['merma']
            h_base = (m_total_batch * 100) / sum([v for k,v in m_dna.items() if isinstance(v, (int, float)) and k != "merma"])

            bloques_acabado = {}
            for i in items:
                key = (i['especialidad'], i['relleno'], i['tamaño'])
                if key not in bloques_acabado: bloques_acabado[key] = []
                bloques_acabado[key].append(i)

            cols = st.columns(1 + len(bloques_acabado))
            with cols[0]:
                st.info("**🥣 INGREDIENTES MASA**")
                for ing, porc in m_dna.items():
                    if isinstance(porc, (int, float)) and ing != "merma":
                        gr = (porc * h_base) / 100; st.write(f"• {ing}: **{gr:,.1f}g**")
                        resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
                if "tz" in m_dna: st.warning(f"⚡ TZ: {h_base*m_dna['tz'][0]:,.1f}g H / {h_base*m_dna['tz'][0]*m_dna['tz'][1]:,.1f}g L")

            for idx, ((espec, rell, tam_id), sub_items) in enumerate(bloques_acabado.items()):
                with cols[idx+1]:
                    total_pzas = sum(si['cantidad'] for si in sub_items)
                    st.success(f"✨ **{espec} {tam_id}**")
                    st.caption(f"Cant: {total_pzas}")
                    
                    fam_cfg = ARBOL[sub_items[0]['familia']]
                    # Unificar sub-recetas
                    lista_subs = []
                    if isinstance(fam_cfg["especialidad"][espec], list): lista_subs = fam_cfg["especialidad"][espec].copy()
                    else: lista_subs = fam_cfg["especialidad"][espec]["fijos"].copy()
                    
                    if rell != "N/A" and rell != "Sin Relleno": lista_subs.append(rell)

                    for s_id in lista_subs:
                        st.write(f"**{s_id}**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        # Cálculo de peso total para este sabor/tamaño
                        if fam == "Rosca de reyes" and s_id == rell: p_u_extra = fam_cfg["p_relleno_map"][tam_id]
                        elif fam == "Conchas": p_u_extra = fam_cfg["p_ex"][tam_id]
                        elif "pesos_override_berlina" in fam_cfg and espec in fam_cfg["pesos_override_berlina"]:
                            p_u_extra = fam_cfg["pesos_override_berlina"][espec][1].get(s_id, 15)
                        else: p_u_extra = 15 # Default
                        
                        factor_s = (p_u_extra * total_pzas) / sum([v for v in s_rec.values() if isinstance(v, (int, float))])
                        for ing, val in s_rec.items():
                            if "Cabeza" in ing:
                                st.write(f"- {ing}: {val*total_pzas} pz")
                                resumen_insumos[ing] = resumen_insumos.get(ing, 0) + (val*total_pzas)
                            else:
                                gr = val * (total_pzas if "Rosca" in s_id else factor_s)
                                st.write(f"- {ing}: {gr:,.1f}g")
                                resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
            st.divider()

    with t_super:
        st.header("🛒 Lista Maestra de Insumos")
        df_sum = pd.DataFrame(resumen_insumos.items(), columns=["Insumo", "Cantidad"]).sort_values("Insumo")
        st.table(df_sum)
