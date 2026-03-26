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
    # LÁGRIMAS
    "L_Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Mazapan_I": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66},
    "L_Oreo": {"Harina": 100, "Azúcar Glass": 75, "Mantequilla": 100, "Oreo": 25},
    # CREMAS
    "C_Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Vainilla": 6},
    "C_Choco_Amargo": {"Leche": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Chocolate 60%": 120, "Mantequilla": 30},
    "C_Turín": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla": 20},
    # ACABADOS ESPECÍFICOS
    "G_Turín_Costra": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche": 50, "Cabeza": 1},
    "D_Tradicional_Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "D_Nuez_Fileteada": {"Nuez Fileteada": 15},
    "S_Canela": {"Mantequilla": 200, "Azúcar": 300, "Canela": 25},
    "I_FrutosRojos": {"Pasas": 4, "Arandanos": 4, "Te Earl Grey": 2},
    "I_Manzana": {"Orejón": 8, "Agua tibia": 2},
    "R_Muerto": {"Mantequilla": 6.5, "Azúcar": 12.5}
}

# ARBOL DE CONFIGURACIÓN (Lógica jerárquica corregida)
ARBOL = {
    "Conchas": {
        "especialidad": {
            "Vainilla": ["L_Vainilla"], "Chocolate": ["L_Chocolate"], "Matcha": ["L_Matcha"],
            "Mazapán Intenso": ["L_Mazapán_I"], "Pinole": ["L_Pinole"], "Oreo": ["L_Oreo"]
        },
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "CONCHA"
    },
    "Berlinas": {
        "especialidad": {
            "Vainilla Clásica": ["C_Vainilla"], "Ruby v2.0": ["C_Ruby", "G_Ruby"], "Conejo Turín": ["C_Turín", "G_Turín_Costra"]
        },
        "tamaños": {"Estándar": 60}, "masa": "BERLINA"
    },
    "Rollos": {
        "especialidad": {
            "Tradicional": ["S_Canela", "I_FrutosRojos"], "Manzana": ["S_Canela", "I_Manzana"], "Conejo Turín": ["S_Canela", "G_Turín_Costra"], "Red Velvet": ["S_RV"]
        },
        "tamaños": {"Individual": 90}, "masa": "ROL_CANELA", "p_ex": 15, "masa_override": {"Red Velvet": "ROL_RV"}
    },
    "Rosca de reyes": {
        "especialidad": {
            "Tradicional": {
                "fijos": ["L_Vainilla", "D_Tradicional_Rosca"],
                "rellenos": ["Sin Relleno", "C_Vainilla", "C_Choco_Amargo"]
            },
            "Chocolate": {
                "fijos": ["L_Chocolate", "D_Nuez_Fileteada"],
                "rellenos": ["Sin Relleno", "C_Choco_Amargo"]
            },
            "Turín": {
                "fijos": ["L_Chocolate", "G_Turín_Costra"],
                "rellenos": ["Sin Relleno", "C_Turín"]
            }
        },
        "tamaños": {"Mediana": 900, "Individual": 100}, "masa": "ROSCA", "p_ex_u": 80 # Relleno
    },
    "Pan de muerto": {
        "especialidad": {
            "Tradicional": ["R_Muerto"], "Guayaba": ["R_Muerto"]
        },
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
    
    # PASO 1: FAMILIA
    fam = st.selectbox("1. Selecciona Familia", ["-"] + list(ARBOL.keys()), key=f"f_{f_id}")
    
    if fam != "-":
        # PASO 2: ESPECIALIDAD
        espec = st.selectbox("2. Selecciona Especialidad", ["-"] + list(ARBOL[fam]["especialidad"].keys()), key=f"e_{f_id}")
        
        if espec != "-":
            # PASO 3: TAMAÑO
            tam = st.selectbox("3. Selecciona Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{f_id}")
            
            # PASO 4: RELLENO (Solo para Rosca)
            relleno = "N/A"
            if fam == "Rosca de reyes":
                rellenos_validos = ARBOL[fam]["especialidad"][espec]["rellenos"]
                relleno = st.selectbox("4. Selecciona Relleno", rellenos_validos, key=f"r_{f_id}")
            
            # PASO 5: CANTIDAD
            cant = st.number_input("Cantidad", min_value=1, value=1, key=f"c_{f_id}")
            
            if st.button("✅ AGREGAR A LA COMANDA"):
                st.session_state.comanda.append({
                    "familia": fam, "especialidad": espec, "tamaño": tam, "relleno": relleno, "cantidad": cant
                })
                st.session_state.form_id += 1
                st.session_state.expandido = False
                st.rerun()

if not st.session_state.expandido:
    if st.button("➕ Agregar otro producto"):
        st.session_state.expandido = True; st.rerun()

# ==========================================
# 3. LÓGICA DE CONSOLIDACIÓN Y PESADO
# ==========================================

if st.session_state.comanda:
    st.subheader("📋 Comanda del Día")
    st.table(pd.DataFrame(st.session_state.comanda))
    if st.button("🗑️ Vaciar todo"): st.session_state.comanda = []; st.session_state.expandido = True; st.rerun()

    t_pesado, t_super = st.tabs(["🥣 Hoja de Producción", "📦 Lista de Insumos"])
    resumen_insumos = {}

    # Agrupar por Masa Madre para consolidar batidos
    lotes_masa = {}
    for item in st.session_state.comanda:
        m_id = ARBOL[item['familia']].get("masa_override", {}).get(item['especialidad'], ARBOL[item['familia']]['masa'])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    with t_pesado:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            st.markdown(f"## 🛠️ Lote de Masa: {m_id.replace('_',' ')}")
            
            # Cálculo de Batido Consolidado
            m_total_batch = 0
            for i in items:
                p_u = ARBOL[i['familia']]['tamaños'][i['tamaño']]
                m_total_batch += (p_u * i['cantidad']) / m_dna['merma']
            
            h_base = (m_total_batch * 100) / sum([v for k,v in m_dna.items() if isinstance(v, (int, float)) and k != "merma"])

            # Agrupar por "Acabado" (Especialidad + Relleno)
            bloques_acabado = {}
            for i in items:
                key = (i['especialidad'], i['relleno'])
                if key not in bloques_acabado: bloques_acabado[key] = []
                bloques_acabado[key].append(i)

            cols = st.columns(1 + len(bloques_acabado))

            with cols[0]:
                st.info("**🥣 MASA TOTAL**")
                for ing, porc in m_dna.items():
                    if isinstance(porc, (int, float)) and ing != "merma":
                        gr = (porc * h_base) / 100; st.write(f"• {ing}: **{gr:,.1f}g**")
                        resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
                if "tz" in m_dna: st.warning(f"⚡ TZ: {h_base*m_dna['tz'][0]:,.1f}g H / {h_base*m_dna['tz'][0]*m_dna['tz'][1]:,.1f}g L")

            # Columnas de Especialidades
            for idx, ((espec, rell), sub_items) in enumerate(bloques_acabado.items()):
                with cols[idx+1]:
                    total_pzas = sum(si['cantidad'] for si in sub_items)
                    st.success(f"✨ **{espec}**")
                    st.caption(f"Relleno: {rell} | Total: {total_pzas} pzas")
                    
                    # Cargar complementos
                    fam_cfg = ARBOL[sub_items[0]['familia']]
                    # Obtener lista de sub-recetas (fijas de la especialidad + relleno si hay)
                    lista_subs = []
                    if isinstance(fam_cfg["especialidad"][espec], list):
                        lista_subs = fam_cfg["especialidad"][espec]
                    else:
                        lista_subs = fam_cfg["especialidad"][espec]["fijos"]
                    
                    if rell != "N/A" and rell != "Sin Relleno":
                        lista_subs.append(rell)

                    for s_id in lista_subs:
                        st.write(f"**{s_id}**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        
                        # Peso del extra (Lógica de Concha vs Rosca vs Relleno)
                        p_u_extra = 0
                        for si in sub_items:
                            p_cfg = fam_cfg.get("p_ex", 0)
                            if isinstance(p_cfg, dict): p_u_extra += p_cfg.get(si['tamaño'], 0) * si['cantidad']
                            else: p_u_extra += p_cfg * si['cantidad']
                        
                        # Factor de escalado
                        factor_s = p_u_extra / sum([v for v in s_rec.values() if isinstance(v, (int, float))]) if p_u_extra > 0 else 1
                        
                        for ing, val in s_rec.items():
                            if "Cabeza" in ing or "piezas" in ing:
                                st.write(f"- {ing}: {val*total_pzas} pz")
                                resumen_insumos[ing] = resumen_insumos.get(ing, 0) + (val*total_pzas)
                            else:
                                gr = val * (total_pzas if "Rosca" in s_id or "Muerto" in s_id else factor_s)
                                st.write(f"- {ing}: {gr:,.1f}g")
                                resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr
            st.divider()

    with t_super:
        st.header("🛒 Lista Maestra de Insumos")
        df_sum = pd.DataFrame(resumen_insumos.items(), columns=["Insumo", "Cantidad"]).sort_values("Insumo")
        st.table(df_sum)
