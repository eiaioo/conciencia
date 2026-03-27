import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN DE TEMA Y ESTILOS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0

# Paleta de colores suaves (70% opacidad aprox)
colores = {
    "etapa1": "rgba(255, 235, 156, 0.7)", # Amarillo suave (Autólisis)
    "etapa2": "rgba(168, 230, 173, 0.7)", # Verde suave (Activación/Gluten)
    "etapa3": "rgba(162, 210, 255, 0.7)", # Azul suave (Estructura/Azúcar)
    "etapa4": "rgba(255, 179, 140, 0.7)", # Naranja suave (Enriquecimiento)
}

st.markdown(f"""
    <style>
    /* Arreglo para checklist en móvil */
    .stCheckbox {{ display: flex !important; align-items: center !important; }}
    .stCheckbox div[data-testid="stMarkdownContainer"] p {{
        font-size: 1.1rem !important;
        white-space: nowrap !important;
        margin-bottom: 0px !important;
        padding-left: 10px;
    }}
    
    /* Contenedores de Etapas */
    .etapa-box {{
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(0,0,0,0.1);
    }}
    .etapa-titulo {{
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.9rem;
        margin-bottom: 10px;
        color: #333;
    }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN SOL/LUNA
c_top1, c_top2 = st.columns([0.9, 0.1])
with c_top2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS TÉCNICA (DNA + ETAPAS)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "merma": 1.0, "factor_panadero": 1.963,
        "etapas": [
            {"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]},
            {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": colores["etapa2"]},
            {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]},
            {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}
        ]
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "merma": 0.85, "tz": (0.05, 5),
        "etapas": [
            {"n": "1. Preparación", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]},
            {"n": "2. Desarrollo", "i": ["Azúcar", "Levadura seca", "Sal fina"], "c": colores["etapa3"]},
            {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}
        ]
    },
    "Masa Brioche Roles": {
        "receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17},
        "merma": 1.0, "tz_fijo": (70, 350),
        "etapas": [
            {"n": "1. Hidratación", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]},
            {"n": "2. Fermento", "i": ["Levadura fresca"], "c": colores["etapa2"]},
            {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]},
            {"n": "4. Grasas", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}
        ]
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "merma": 1.0, "tz": (0.025, 1),
        "etapas": [
            {"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": colores["etapa1"]},
            {"n": "2. Fermentación", "i": ["Levadura fresca"], "c": colores["etapa2"]},
            {"n": "3. Aromas y Dulzor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": colores["etapa3"]},
            {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}
        ]
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Glaseado Turin": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"MEDIANA": 650, "MINI": 120}, "p_relleno_map": {"MEDIANA": 200, "MINI": 35}, "masa": "Masa Brioche Rosca"}
}

# ==========================================
# 2. INTERFAZ (COMMAND CENTER)
# ==========================================

with st.expander("📝 Configurar Producción", expanded=len(st.session_state.comanda) == 0):
    fk = st.session_state.form_id
    fam = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if fam != "-":
        esp_list = list(ARBOL[fam]["espec"].keys())
        esp = st.selectbox("Especialidad", ["-"] + esp_list, key=f"e_{fk}")
        if esp != "-":
            tam = st.selectbox("Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{fk}")
            rel = "N/A"
            if fam == "Rosca de reyes":
                rel = st.selectbox("Relleno", ARBOL[fam]["espec"][esp]["rellenos"], key=f"r_{fk}")
            cant = st.number_input("Piezas", min_value=1, value=1, key=f"c_{fk}")
            if st.button("✅ AGREGAR"):
                st.session_state.comanda.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "cant": cant})
                st.session_state.form_id += 1
                st.rerun()

# ==========================================
# 3. LÓGICA DE CÁLCULO Y PESTAÑAS
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()

    # Consolidación de datos para compras y lotes
    compras_master = {}
    lotes_masa = {}
    sub_recetas_dia = {}

    for item in st.session_state.comanda:
        m_id = ARBOL[item['fam']]["masa"]
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    # Tabs dinámicos
    tabs = st.tabs(["📋 Resumen", "🛒 Lista Maestra"] + list(lotes_masa.keys()))

    # --- T1: RESUMEN (VUELVE LA INFO DE LÁGRIMAS) ---
    with tabs[0]:
        for m_id, items in lotes_masa.items():
            st.subheader(f"🛠️ Lote: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_base_total = (m_batch_gr * 100) / sum(m_dna['receta'].values())

            c_masa, c_comps = st.columns([0.4, 0.6])
            with c_masa:
                st.info(f"**Masa Principal ({m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = (porc * h_base_total) / 100
                    st.write(f"• {ing}: {gr:,.1f}g")
                    compras_master[ing] = compras_master.get(ing, 0) + gr

            with c_comps:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']})**")
                    cfg = ARBOL[it['fam']]
                    # Obtener lista de subrecetas
                    subs = cfg["espec"][it['esp']]
                    lista = subs["fijos"].copy() if isinstance(subs, dict) else subs.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: lista.append(it['rel'])
                    
                    for s_id in lista:
                        # Calcular peso
                        p_u = cfg["p_relleno_map"][it['tam']] if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg["p_ex"][it['tam']] if it['fam'] == "Conchas" else 15)
                        p_tot = p_u * it['cant']
                        st.markdown(f"*{s_id} (Total: {p_tot:,.1f}g)*")
                        
                        # Desglosar para compras
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum([v for k,v in s_rec.items() if k != "SOP"])
                        for ing_s, val_s in s_rec.items():
                            if ing_s != "SOP":
                                gr_s = val_s * (it['cant'] if "Rebozado" in s_id or "Decoración" in s_id else fact)
                                compras_master[ing_s] = compras_master.get(ing_s, 0) + gr_s

    # --- T2: LISTA MAESTRA ---
    with tabs[1]:
        st.header("📦 Surtido General")
        for insumo, cant in sorted(compras_master.items()):
            col_c, col_t = st.columns([0.05, 0.95])
            if col_c.checkbox("", key=f"m_{insumo}"):
                col_t.markdown(f"~~{insumo}: {cant:,.1f}g~~")
            else: col_t.write(f"**{insumo}:** {cant:,.1f}g")

    # --- T-ESPECÍFICAS: MASA CON RECUADROS POR ETAPAS ---
    for i, (m_id, items) in enumerate(lotes_masa.items()):
        with tabs[i+2]:
            st.header(f"🥣 Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())

            for etapa in m_dna.get("etapas", []):
                st.markdown(f"""<div class="etapa-box" style="background-color: {etapa['c']};">
                    <div class="etapa-titulo">{etapa['n']}</div>""", unsafe_allow_html=True)
                
                for ing in etapa['i']:
                    gr_final = (m_dna['receta'][ing] * h_b) / 100
                    c1, c2 = st.columns([0.05, 0.95])
                    chk = c1.checkbox("", key=f"cp_{m_id}_{etapa['n']}_{ing}")
                    if chk:
                        c2.markdown(f"~~{ing}: {gr_final:,.1f}g~~")
                    else:
                        c2.write(f"**{ing}:** {gr_final:,.1f}g")
                st.markdown("</div>", unsafe_allow_html=True)

            # AGREGAMOS EL SOP ESCRITO AL FINAL
            with st.expander("📖 Ver instrucciones detalladas (SOP)"):
                for step in m_dna["SOP"]: st.write(step)
