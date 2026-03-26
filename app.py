import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA
# ==========================================

DB_MASAS = {
    "CONCHA": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "merma": 1.0, "factor": 1.963},
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
    "C_Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Vainilla": 6},
    "C_Choco_Amargo": {"Leche": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Chocolate 60%": 120, "Mantequilla": 30},
    "C_Turín": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla": 20},
    "G_Turín_Costra": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche": 50, "Cabeza": 1},
    "D_Tradicional_Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "D_Nuez_Fileteada": {"Nuez Fileteada": 15},
    "S_Canela": {"Mantequilla": 200, "Azúcar": 300, "Canela": 25},
    "I_FrutosRojos": {"Pasas": 4, "Arandanos": 4, "Te Earl Grey": 2},
    "I_Manzana": {"Orejón": 8, "Agua tibia": 2},
    "R_Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {
        "especialidad": {"Vainilla": ["L_Vainilla"], "Chocolate": ["L_Chocolate"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "CONCHA"
    },
    "Rosca de reyes": {
        "especialidad": {
            "Tradicional": {"fijos": ["L_Vainilla", "D_Tradicional_Rosca"], "rellenos": ["Sin Relleno", "C_Vainilla", "C_Choco_Amargo"]},
            "Chocolate": {"fijos": ["L_Chocolate", "D_Nuez_Fileteada"], "rellenos": ["Sin Relleno", "C_Choco_Amargo"]},
            "Turín": {"fijos": ["L_Chocolate", "G_Turín_Costra"], "rellenos": ["Sin Relleno", "C_Turín"]}
        },
        "tamaños": {
            "FAMILIAR (10-12p)": 1450,
            "MEDIANA (6-8p)": 650,
            "MINI (1-2p)": 120,
            "CONCHA-ROSCA": 90
        },
        "p_relleno_map": {
            "FAMILIAR (10-12p)": 450,
            "MEDIANA (6-8p)": 200,
            "MINI (1-2p)": 35,
            "CONCHA-ROSCA": 25
        },
        "masa": "ROSCA"
    },
    "Berlinas": {
        "especialidad": {"Vainilla Clásica": ["C_Vainilla"], "Ruby v2.0": ["C_Ruby", "G_Ruby"]},
        "tamaños": {"Estándar": 60}, "masa": "BERLINA"
    },
    "Rollos": {
        "especialidad": {"Tradicional": ["S_Canela", "I_FrutosRojos"], "Manzana": ["S_Canela", "I_Manzana"]},
        "tamaños": {"Individual": 90}, "masa": "ROL_CANELA", "p_ex": 15
    },
    "Pan de muerto": {
        "especialidad": {"Tradicional": ["R_Muerto"], "Guayaba": ["R_Muerto"]},
        "tamaños": {"Estándar": 85}, "masa": "MUERTO_TRAD", "masa_override": {"Guayaba": "MUERTO_GUAYABA"}
    }
}

# ==========================================
# 2. INTERFAZ EN CASCADA
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0
if 'expandido' not in st.session_state: st.session_state.expandido = True

st.title("🥐 Gestión Técnica CONCIENCIA")

with st.expander("📝 Cargar Nuevo Producto", expanded=st.session_state.expandido):
    f_id = st.session_state.form_id
    fam = st.selectbox("1. Selecciona Familia", ["-"] + list(ARBOL.keys()), key=f"f_{f_id}")
    
    if fam != "-":
        espec = st.selectbox("2. Selecciona Especialidad", ["-"] + list(ARBOL[fam]["especialidad"].keys()), key=f"e_{f_id}")
        if espec != "-":
            tam = st.selectbox("3. Selecciona Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{f_id}")
            
            relleno = "N/A"
            if fam == "Rosca de reyes":
                relleno = st.selectbox("4. Selecciona Relleno", ARBOL[fam]["especialidad"][espec]["rellenos"], key=f"r_{f_id}")
            
            cant = st.number_input("Cantidad", min_value=1, value=1, key=f"c_{f_id}")
            
            if st.button("✅ AGREGAR A LA COMANDA"):
                st.session_state.comanda.append({"familia": fam, "especialidad": espec, "tamaño": tam, "relleno": relleno, "cantidad": cant})
                st.session_state.form_id += 1
                st.session_state.expandido = False
                st.rerun()

if not st.session_state.expandido:
    if st.button("➕ Agregar otro producto"): st.session_state.expandido = True; st.rerun()

# ==========================================
# 3. LÓGICA DE CONSOLIDACIÓN Y PESADO
# ==========================================

if st.session_state.comanda:
    st.subheader("📋 Comanda del Día")
    st.table(pd.DataFrame(st.session_state.comanda))
    if st.button("🗑️ Vaciar todo"): st.session_state.comanda = []; st.session_state.expandido = True; st.rerun()

    t_pesado, t_super = st.tabs(["🥣 Hoja de Producción", "📦 Lista de Insumos"])
    resumen_insumos = {}

    lotes_masa = {}
    for item in st.session_state.comanda:
        m_id = ARBOL[item['familia']].get("masa_override", {}).get(item['especialidad'], ARBOL[item['familia']]['masa'])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    with t_pesado:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            st.markdown(f"## 🛠️ Lote de Masa: {m_id.replace('_',' ')}")
            
            m_total_batch = 0
            for i in items:
                p_u_masa = ARBOL[i['familia']]['tamaños'][i['tamaño']]
                m_total_batch += (p_u_masa * i['cantidad']) / m_dna['merma']
            
            h_base = (m_total_batch * 100) / sum([v for k,v in m_dna.items() if isinstance(v, (int, float)) and k != "merma"])

            # Agrupar por Acabado para evitar repetir columnas de lo mismo
            bloques_acabado = {}
            for i in items:
                key = (i['especialidad'], i['relleno'], i['tamaño']) # Agregamos tamaño a la key para separar gramajes de relleno
                if key not in bloques_acabado: bloques_acabado[key] = []
                bloques_acabado[key].append(i)

            cols = st.columns(1 + len(bloques_acabado))

            with cols[0]:
                st.info("**🥣 MASA TOTAL**")
                for ing, porc in m_dna.items():
                    if isinstance(porc, (int, float)) and ing != "merma":
                        gr = (porc * h_base) / 100; st.write(f"• {ing}: **{gr:,.1f}g**")
                        resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
                if "tz" in m_dna: st.warning(f"⚡ TZ 1:1: {h_base*m_dna['tz'][0]:,.1f}g H / {h_base*m_dna['tz'][0]*m_dna['tz'][1]:,.1f}g L")

            for idx, ((espec, rell, tam_id), sub_items) in enumerate(bloques_acabado.items()):
                with cols[idx+1]:
                    total_pzas = sum(si['cantidad'] for si in sub_items)
                    st.success(f"✨ **{espec} {tam_id}**")
                    st.caption(f"Relleno: {rell} | Cant: {total_pzas}")
                    
                    fam_cfg = ARBOL[sub_items[0]['familia']]
                    lista_subs = fam_cfg["especialidad"][espec].get("fijos", fam_cfg["especialidad"][espec])
                    if rell != "N/A" and rell != "Sin Relleno": 
                        st.write(f"**{rell} (Puntos Críticos)**")
                        r_rec = DB_COMPLEMENTOS[rell]
                        p_rell_u = fam_cfg["p_relleno_map"][tam_id] # JALAMOS PESO SEGÚN TABLA DE INGENIERÍA
                        f_r = (p_rell_u * total_pzas) / sum([v for v in r_rec.values() if isinstance(v, (int, float))])
                        for ing, val in r_rec.items():
                            gr = val * f_r; st.write(f"- {ing}: {gr:,.1f}g")
                            resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr

                    for s_id in (lista_subs if isinstance(lista_subs, list) else []):
                        st.write(f"**{s_id}**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        p_u_extra = fam_cfg.get("p_ex", {}).get(tam_id, fam_cfg.get("p_ex", 0)) if fam_cfg['masa'] == "CONCHA" else 15
                        # Las roscas tienen una lógica de decoración visual, no solo por peso, pero mantenemos factor
                        factor_s = (p_u_extra * total_pzas) / sum([v for v in s_rec.values() if isinstance(v, (int, float))])
                        for ing, val in s_rec.items():
                            if "Cabeza" in ing: 
                                st.write(f"- {ing}: {val*total_pzas} pz"); resumen_insumos[ing] = resumen_insumos.get(ing, 0) + (val*total_pzas)
                            else:
                                gr = val * (total_pzas if "Rosca" in s_id else factor_s)
                                st.write(f"- {ing}: {gr:,.1f}g"); resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
            st.divider()

    with t_super:
        st.header("🛒 Lista Maestra de Insumos")
        df_sum = pd.DataFrame(resumen_insumos.items(), columns=["Insumo", "Cantidad"]).sort_values("Insumo")
        st.table(df_sum)
