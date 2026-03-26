import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA
# ==========================================

DB_MASAS = {
    "CONCHA": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "merma": 1.0},
    "BERLINA": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche entera": 22, "Sal": 1.8, "Levadura seca": 1.0, "merma": 0.85, "tz": (0.05, 5)},
    "ROL_CANELA": {"Harina de fuerza": 93, "Huevo": 30, "Leche": 5, "Levadura fresca": 1, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17, "merma": 1.0, "tz_fijo": (70, 350)},
    "ROL_RV": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7, "Vinagre": 0.3, "merma": 1.0, "tz": (0.07, 5)},
    "ROSCA": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla": 30, "Huevo": 20, "Yema": 4, "Leche": 24, "Levadura": 0.35, "Sal": 2.2, "Agua Azahar": 0.6, "merma": 1.0, "tz": (0.025, 1)},
    "MUERTO_TRAD": {"Harina": 100, "Leche": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla": 25, "Sal": 2, "Levadura": 3, "Azahar": 2, "Ralladura": 1, "merma": 1.0},
    "MUERTO_GUAYABA": {"Harina": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura": 5, "Sal": 1.8, "Polvo Guayaba": 5, "merma": 1.0, "huesos": True},
    "BROWNIE": {"Mantequilla": 330, "Azúcar Blanca": 275, "Mascabado": 120, "Chocolate": 165, "Harina": 190, "Cocoa": 75, "Sal": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez": 140, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "L_Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Mazapán_I": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66},
    "L_Oreo": {"Harina": 100, "Azúcar Glass": 75, "Mantequilla": 100, "Oreo": 25},
    "L_Fresa": {"Harina": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla": 100},
    "C_Ruby": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "Mantequilla": 16, "Sal": 0.8},
    "G_Ruby": {"Choco Ruby": 80, "Azúcar Glass": 160, "Leche": 50},
    "C_Turín": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla": 20},
    "G_Turín": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche": 50, "Sal": 1, "Cabeza": 1},
    "C_Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Vainilla": 6},
    "S_Canela": {"Mantequilla": 200, "Azúcar Mascabado": 300, "Canela": 25, "Maicena": 20},
    "S_RV": {"Mantequilla": 6, "Azúcar": 6, "Cacao": 1.8, "Maicena": 0.6, "Nuez": 4, "Chocolate": 4},
    "I_FrutosRojos": {"Pasas": 4, "Arandanos": 4, "Te Earl Grey": 2, "Vainilla": 0.5},
    "I_Manzana": {"Orejón Manzana": 8, "Agua tibia": 2},
    "R_Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"sabores": {"Vainilla": ["L_Vainilla"], "Chocolate": ["L_Chocolate"], "Matcha": ["L_Matcha"], "Pinole": ["L_Pinole"], "Mazapán Intenso": ["L_Mazapán_I"], "Oreo": ["L_Oreo"], "Fresa": ["L_Fresa"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "CONCHA"},
    "Berlinas": {"sabores": {"Ruby v2.0": ["C_Ruby", "G_Ruby"], "Conejo Turín": ["C_Turín", "G_Turín"], "Vainilla Clásica": ["C_Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "BERLINA", "p_manual": {"Ruby v2.0": (70, {"C_Ruby": 40, "G_Ruby": 8}), "Conejo Turín": (60, {"C_Turín": 80, "G_Turín": 16})}},
    "Rollos": {"sabores": {"Tradicional": ["S_Canela", "I_FrutosRojos"], "Manzana": ["S_Canela", "I_Manzana"], "Conejo Turín": ["S_Canela", "G_Turín"], "Red Velvet": ["S_RV"]}, "tamaños": {"Individual": 90}, "masa": "ROL_CANELA", "p_ex": 15, "override": {"Red Velvet": "ROL_RV"}},
    "Rosca de reyes": {"sabores": {"Tradicional": [], "Vainilla": ["C_Vainilla"], "Chocolate": ["C_Turín"]}, "tamaños": {"Mediana": 900, "Individual": 100}, "masa": "ROSCA", "p_ex": 80},
    "Pan de muerto": {"sabores": {"Tradicional": ["R_Muerto"], "Guayaba": ["R_Muerto"]}, "tamaños": {"Estándar": 85}, "masa": "MUERTO_TRAD", "p_ex": 1, "override": {"Guayaba": "MUERTO_GUAYABA"}},
    "Brownies": {"sabores": {"Turín Clásico": []}, "tamaños": {"Molde 12 pzas": 1}, "masa": "BROWNIE"}
}

# ==========================================
# 2. INTERFAZ
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0
if 'exp' not in st.session_state: st.session_state.exp = True

st.title("🥐 Gestión Técnica CONCIENCIA v13.0")

with st.expander("📝 Cargar Nuevo Producto", expanded=st.session_state.exp):
    f = st.selectbox("1. Familia", ["-"] + list(ARBOL.keys()), key=f"f_{st.session_state.form_id}")
    if f != "-":
        s = st.selectbox(f"2. Sabor", ["-"] + list(ARBOL[f]["sabores"].keys()), key=f"s_{st.session_state.form_id}")
        if s != "-":
            t = st.selectbox("3. Tamaño", list(ARBOL[f]["tamaños"].keys()), key=f"t_{st.session_state.form_id}")
            c = st.number_input("4. Cantidad", min_value=1, value=12, key=f"c_{st.session_state.form_id}")
            if st.button("✅ AGREGAR"):
                st.session_state.comanda.append({"fam": f, "sab": s, "tam": t, "cant": c})
                st.session_state.form_id += 1
                st.session_state.exp = False
                st.rerun()

if not st.session_state.exp:
    if st.button("➕ Agregar otro"): st.session_state.exp = True; st.rerun()

# ==========================================
# 3. LÓGICA DE AGRUPACIÓN POR MASA MADRE
# ==========================================

if st.session_state.comanda:
    st.subheader("📋 Comanda del Día")
    st.table(pd.DataFrame(st.session_state.comanda))
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.session_state.exp = True; st.rerun()

    t_hoja, t_super = st.tabs(["🥣 Hoja de Producción (Batidos)", "📦 Lista de Insumos"])
    resumen_insumos = {}

    # AGRUPAR POR MASA_ID: 
    # { "Masa_ID": [lista de items que la usan] }
    lotes_masa = {}
    for item in st.session_state.comanda:
        config = ARBOL[item['fam']]
        m_id = config.get("override", {}).get(item['sab'], config['masa'])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    with t_hoja:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            
            # 1. CALCULAR MASA TOTAL DEL BATCH (Sumando todos los tamaños y cantidades)
            masa_total_batch = 0
            for i in items:
                p_u = ARBOL[i['fam']].get("p_manual", {}).get(i['sab'], (ARBOL[i['fam']]['tamaños'][i['tam']], 0))[0]
                masa_total_batch += (p_u * i['cant']) / m_dna['merma']
            
            h_base_batch = (masa_total_batch * 100) / sum([v for k,v in m_dna.items() if isinstance(v, (int, float)) and k != "merma"])

            # 2. RENDERIZAR BLOQUE DE MASA
            st.markdown(f"## 🛠️ Lote de Masa: {m_id.replace('_',' ')}")
            
            # Mostrar resumen de división
            division_str = " | ".join([f"{i['cant']}x {i['tam']} ({i['sab']})" for i in items])
            st.caption(f"**Destino:** {division_str}")

            # Diseño de Columnas: 1 para Masa, el resto para Complementos específicos
            n_cols = 1 + len(items)
            cols = st.columns(n_cols)

            with cols[0]:
                st.info("**🥣 RECETA DEL BATIDO**")
                if m_dna.get("fijo"):
                    for ing, val in m_dna.items():
                        if ing not in ["merma", "fijo"]:
                            total = val * sum(i['cant'] for i in items)
                            st.write(f"• {ing}: **{total:,.1f}g**")
                            resumen_insumos[ing] = resumen_insumos.get(ing, 0) + total
                else:
                    for ing, porc in m_dna.items():
                        if isinstance(porc, (int, float)) and ing != "merma":
                            gr = (porc * h_base_batch) / 100
                            st.write(f"• {ing}: **{gr:,.1f}g**")
                            resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
                    
                    if "tz" in m_dna:
                        st.warning(f"⚡ TZ 1:5: {h_base_batch*m_dna['tz'][0]:,.1f}g H / {h_base_batch*m_dna['tz'][0]*m_dna['tz'][1]:,.1f}g L")
                    if "tz_fijo" in m_dna:
                        f = h_base_batch / 1000
                        st.warning(f"⚡ TZ 70/350: {m_dna['tz_fijo'][0]*f:,.1f}g H / {m_dna['tz_fijo'][1]*f:,.1f}g L")
                    if m_dna.get("huesos"):
                        res = masa_total_batch * 0.25
                        st.info(f"🦴 Refuerzo Huesos: +{res*0.3:,.1f}g Harina / +{res*0.1:,.1f}g Yema")
                        resumen_insumos["Harina Extra"] = resumen_insumos.get("Harina Extra", 0) + (res*0.3)
                        resumen_insumos["Yemas Extra"] = resumen_insumos.get("Yemas Extra", 0) + (res*0.1)

            # 3. RENDERIZAR COMPLEMENTOS (Uno por cada item de la comanda)
            for idx, item in enumerate(items):
                with cols[idx+1]:
                    st.success(f"✨ **Complementos {item['tam']}**")
                    st.write(f"Sabor: *{item['sab']}*")
                    
                    subs = ARBOL[item['fam']]["sabores"][item['sab']]
                    for sub_id in subs:
                        st.write(f"**{sub_id.replace('_',' ')}**")
                        s_rec = DB_COMPLEMENTOS[sub_id]
                        
                        # Cálculo de peso sub-receta
                        if "p_manual" in ARBOL[item['fam']] and item['sab'] in ARBOL[item['fam']]["p_manual"]:
                            p_sub_tot = ARBOL[item['fam']]["p_manual"][item['sab']][1].get(sub_id, 0) * item['cant']
                        else:
                            p_u_sub = ARBOL[item['fam']].get("p_ex", {}).get(item['tam'], ARBOL[item['fam']].get("p_ex", 0))
                            p_sub_tot = p_u_sub * item['cant']

                        factor = p_sub_tot / sum([v for v in s_rec.values() if isinstance(v, (int, float))])
                        for ing, val in s_rec.items():
                            if "Cabeza" in ing:
                                st.write(f"- {ing}: {val*item['cant']} pz")
                                resumen_insumos[ing] = resumen_insumos.get(ing, 0) + (val*item['cant'])
                            else:
                                gr = val * factor; st.write(f"- {ing}: {gr:,.1f}g")
                                resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
            st.divider()

    with t_super:
        st.header("🛒 Lista Maestra")
        df_sum = pd.DataFrame(resumen_insumos.items(), columns=["Insumo", "Cantidad Total"]).sort_values("Insumo")
        st.table(df_sum)
        
