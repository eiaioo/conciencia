import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA (LIMPIEZA DE NOMBRES)
# ==========================================

DB_MASAS = {
    "Masa Concha": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "merma": 1.0},
    "Masa Berlina": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0, "merma": 0.85, "tz": (0.05, 5)},
    "Masa Roles Canela": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17, "merma": 1.0, "tz_fijo": (70, 350)},
    "Masa Roles Red Velvet": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3, "merma": 1.0, "tz": (0.07, 5)},
    "Masa Brioche Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6, "merma": 1.0, "tz": (0.025, 1)},
    "Masa Muerto Tradicional": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3, "Agua Azahar": 2, "Ralladura Naranja": 1, "merma": 1.0},
    "Masa Muerto Guayaba": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5, "merma": 1.0, "huesos": True},
    "Mezcla Brownie": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez": 140, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Crema Pastelera Chocolate": {"Leche entera": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Chocolate 60%": 120, "Mantequilla sin sal": 30},
    "Crema Pastelera Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turin": 120, "Mantequilla sin sal": 20},
    "Glaseado Turin": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {
        "especialidad": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa Concha"
    },
    "Rosca de reyes": {
        "especialidad": {
            "Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate"]},
            "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Pastelera Turin"]}
        },
        "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90},
        "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25},
        "masa": "Masa Brioche Rosca"
    },
    "Berlinas": {
        "especialidad": {"Vainilla Clásica": ["Crema Pastelera Vainilla"]},
        "tamaños": {"Estándar": 60}, "masa": "Masa Berlina"
    }
}

# ==========================================
# 2. INTERFAZ
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0
if 'expandido' not in st.session_state: st.session_state.expandido = True

st.title("🥐 Gestión Técnica CONCIENCIA")

with st.expander("📝 Cargar Nuevo Producto", expanded=st.session_state.expandido):
    f_id = st.session_state.form_id
    fam = st.selectbox("1. Familia", ["-"] + list(ARBOL.keys()), key=f"f_{f_id}")
    if fam != "-":
        espec = st.selectbox("2. Especialidad", ["-"] + list(ARBOL[fam]["especialidad"].keys()), key=f"e_{f_id}")
        if espec != "-":
            tam = st.selectbox("3. Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{f_id}")
            relleno = "N/A"
            if fam == "Rosca de reyes":
                relleno = st.selectbox("4. Relleno", ARBOL[fam]["especialidad"][espec]["rellenos"], key=f"r_{f_id}")
            cant = st.number_input("Cantidad", min_value=1, value=1, key=f"c_{f_id}")
            if st.button("✅ AGREGAR"):
                st.session_state.comanda.append({"familia": fam, "especialidad": espec, "tamaño": tam, "relleno": relleno, "cantidad": cant})
                st.session_state.form_id += 1
                st.session_state.expandido = False
                st.rerun()

if not st.session_state.expandido:
    if st.button("➕ Agregar otro"): st.session_state.expandido = True; st.rerun()

# ==========================================
# 3. LÓGICA DE PRODUCCIÓN
# ==========================================

if st.session_state.comanda:
    st.subheader("📋 Comanda Activa")
    st.table(pd.DataFrame(st.session_state.comanda))
    if st.button("🗑️ Limpiar todo"): st.session_state.comanda = []; st.session_state.expandido = True; st.rerun()

    t_pesado, t_super = st.tabs(["🥣 Hoja de Producción", "📦 Lista Maestra"])
    resumen_insumos = {}

    def add_almacen(ing, gr):
        if not any(x in ing for x in ["merma", "factor", "huesos"]): # Filtro de seguridad
            resumen_insumos[ing] = resumen_insumos.get(ing, 0) + gr

    lotes_masa = {}
    for item in st.session_state.comanda:
        m_id = ARBOL[item['familia']].get("masa", ARBOL[item['familia']]['masa'])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    with t_pesado:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            st.markdown(f"## 🛠️ Batido: {m_id}")
            m_tot_batch = 0
            for i in items:
                m_tot_batch += (ARBOL[i['familia']]['tamaños'][i['tamaño']] * i['cantidad']) / m_dna['merma']
            
            h_base = (m_tot_batch * 100) / sum([v for k,v in m_dna.items() if isinstance(v, (int, float)) and k != "merma"])

            cols = st.columns(2)
            with cols[0]:
                st.info("**Masa Agrupada**")
                for ing, porc in m_dna.items():
                    if isinstance(porc, (int, float)) and ing != "merma":
                        gr = (porc * h_base) / 100
                        st.write(f"• {ing}: **{gr:,.1f}g**")
                        add_almacen(ing, gr)
            
            with cols[1]:
                st.success("**Complementos por Especialidad**")
                for i in items:
                    fam_cfg = ARBOL[i['familia']]
                    lista_subs = fam_cfg["especialidad"][i['especialidad']].get("fijos", fam_cfg["especialidad"][i['especialidad']])
                    if i['relleno'] not in ["N/A", "Sin Relleno"]:
                        st.write(f"**{i['relleno']} ({i['cantidad']}x {i['tamaño']})**")
                        r_rec = DB_COMPLEMENTOS[i['relleno']]
                        p_r_u = fam_cfg["p_relleno_map"][i['tamaño']]
                        f_r = (p_r_u * i['cantidad']) / sum(r_rec.values())
                        for ing, val in r_rec.items():
                            gr = val * f_r; st.write(f"- {ing}: {gr:,.1f}g"); add_almacen(ing, gr)
                    
                    for s_id in (lista_subs if isinstance(lista_subs, list) else []):
                        st.write(f"**{s_id}**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        p_u_e = fam_cfg.get("p_ex", {}).get(i['tamaño'], 15)
                        f_s = (p_u_e * i['cantidad']) / sum(s_rec.values())
                        for ing, val in s_rec.items():
                            gr = val * f_s; st.write(f"- {ing}: {gr:,.1f}g"); add_almacen(ing, gr)
            st.divider()

    with t_super:
        st.header("🛒 Lista Maestra de Insumos")
        # CREAMOS EL DATAFRAME Y OCULTAMOS EL ÍNDICE
        df_sum = pd.DataFrame(resumen_insumos.items(), columns=["Insumo", "Cantidad Total (g/pz)"])
        df_sum["Cantidad Total (g/pz)"] = df_sum["Cantidad Total (g/pz)"].round(1)
        st.dataframe(df_sum.sort_values("Insumo"), use_container_width=True, hide_index=True)
