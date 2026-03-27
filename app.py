import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0

# Paleta de colores suaves (70% opacidad)
colores = {
    "etapa1": "rgba(255, 235, 156, 0.7)", # Amarillo - Autólisis / Base
    "etapa2": "rgba(168, 230, 173, 0.7)", # Verde - Activación / Gluten
    "etapa3": "rgba(162, 210, 255, 0.7)", # Azul - Estructura / Azúcar
    "etapa4": "rgba(255, 179, 140, 0.7)", # Naranja - Enriquecimiento
}

st.markdown(f"""
    <style>
    .stApp {{ background-color: {'#121212' if st.session_state.tema_oscuro else '#FFFFFF'}; }}
    
    /* Arreglo para checklist en móvil */
    .stCheckbox {{ display: flex !important; align-items: center !important; }}
    .stCheckbox label {{ font-size: 1.1rem !important; line-height: 1.2 !important; }}
    
    /* Contenedores de Etapas */
    .etapa-box {{
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid rgba(0,0,0,0.05);
        color: #1c1c1c !important;
    }}
    .etapa-titulo {{
        font-weight: bold;
        text-transform: uppercase;
        font-size: 0.85rem;
        margin-bottom: 8px;
        color: rgba(0,0,0,0.6);
    }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN SOL/LUNA
c_t1, c_t2 = st.columns([0.9, 0.1])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS TÉCNICA (DNA + SOP)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "etapas": [
            {"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]},
            {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": colores["etapa2"]},
            {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]},
            {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}
        ],
        "merma": 1.0, "SOP": ["Autólisis 20 min.", "Incorporar levadura/vainilla.", "Azúcar en 3 tandas.", "Mantequilla en bloques."]
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "etapas": [
            {"n": "1. Base y TZ", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]},
            {"n": "2. Desarrollo", "i": ["Azúcar", "Levadura seca", "Sal fina"], "c": colores["etapa3"]},
            {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}
        ],
        "merma": 0.85, "tz": (0.05, 5), "SOP": ["TZ 1:5 frío.", "Gluten 70% antes de azúcar.", "Fritura 172°C."]
    },
    "Masa Brioche Roles": {
        "receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17},
        "etapas": [
            {"n": "1. Hidratación", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]},
            {"n": "2. Fermento", "i": ["Levadura fresca"], "c": colores["etapa2"]},
            {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]},
            {"n": "4. Grasas", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}
        ],
        "merma": 1.0, "tz_fijo": (70, 350), "SOP": ["TZ 1:5 frío.", "DDT 24°C.", "Reposo bloque 12h."]
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "etapas": [
            {"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": colores["etapa1"]},
            {"n": "2. Fermentación", "i": ["Levadura fresca"], "c": colores["etapa2"]},
            {"n": "3. Aromas y Dulzor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": colores["etapa3"]},
            {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}
        ],
        "merma": 1.0, "tz": (0.025, 1), "SOP": ["TZ 1:1.", "Incorporar aromáticos al final.", "Bloque 12h."]
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "SOP": "Cremar pomada + secos."},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "SOP": "Cacao con harina + proceso base."},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "Vainilla": 6, "SOP": "82-85°C. Emulsión mantequilla al final."},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "SOP": "Colocación tradicional."}
}

ARBOL = {
    "Conchas": {
        "espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"
    },
    "Rosca de reyes": {
        "espec": {
            "Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}
        },
        "tamaños": {"MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90},
        "p_relleno_map": {"MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25},
        "masa": "Masa Brioche Rosca"
    }
}

# ==========================================
# 2. INTERFAZ
# ==========================================

with st.expander("📝 Cargar Producto", expanded=True):
    fk = st.session_state.form_id
    fam = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if fam != "-":
        esp = st.selectbox("Especialidad", ["-"] + list(ARBOL[fam]["espec"].keys()), key=f"e_{fk}")
        if esp != "-":
            tam = st.selectbox("Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{fk}")
            rel = "N/A"
            if fam == "Rosca de reyes":
                rel = st.selectbox("Relleno", ARBOL[fam]["espec"][esp]["rellenos"], key=f"r_{fk}")
            cant = st.number_input("Cantidad", min_value=1, value=1, key=f"c_{fk}")
            if st.button("✅ AGREGAR"):
                st.session_state.comanda.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "cant": cant})
                st.session_state.form_id += 1
                st.rerun()

# ==========================================
# 3. MOTOR DE CÁLCULO (BLINDADO)
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()

    lotes_masa = {}
    compras_finales = {}

    # Agrupar por Masa Madre
    for item in st.session_state.comanda:
        m_id = ARBOL[item['fam']]["masa"]
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    tabs = st.tabs(["📋 Resumen Visual", "🛒 Lista Maestra"] + list(lotes_masa.keys()))

    # --- T1: RESUMEN (CONSOLIDADO POR SABOR) ---
    with tabs[0]:
        for m_id, items in lotes_masa.items():
            st.markdown(f"## 🛠️ Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_base = (m_batch_gr * 100) / sum(m_dna['receta'].values())

            # Agrupar por Sabor/Especialidad para una sola columna
            sabores_consolidado = {}
            for i in items:
                key = (i['esp'], i.get('rel', 'N/A'))
                if key not in sabores_consolidado: sabores_consolidado[key] = []
                sabores_consolidado[key].append(i)

            cols = st.columns(1 + len(sabores_consolidado))
            with cols[0]:
                st.info(f"**Masa (Total: {m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = (porc * h_base) / 100
                    st.write(f"• {ing}: {gr:,.1f}g")
                    compras_finales[ing] = compras_finales.get(ing, 0) + gr

            for idx, ((e_name, r_name), s_items) in enumerate(sabores_consolidado.items()):
                with cols[idx+1]:
                    st.success(f"✨ **{e_name}**")
                    pzas_tot = sum(si['cant'] for si in s_items)
                    
                    # Cargar subrecetas
                    cfg = ARBOL[s_items[0]['fam']]
                    lista_subs = cfg["espec"][e_name]
                    if isinstance(lista_subs, dict): lista_subs = lista_subs["fijos"].copy()
                    else: lista_subs = lista_subs.copy()
                    if r_name not in ["N/A", "Sin Relleno", None]: lista_subs.append(r_name)

                    for sub_id in lista_subs:
                        if sub_id not in DB_COMPLEMENTOS: continue
                        s_rec = DB_COMPLEMENTOS[sub_id]
                        
                        # Sumar peso necesario de este extra
                        p_sub_tot = 0
                        for si in s_items:
                            if si['fam'] == "Rosca de reyes" and sub_id == r_name: p_u = cfg["p_relleno_map"][si['tam']]
                            elif si['fam'] == "Conchas": p_u = cfg["p_ex"][si['tam']]
                            else: p_u = 15
                            p_sub_tot += p_u * si['cant']
                        
                        st.markdown(f"**{sub_id} ({p_sub_tot:,.1f}g)**")
                        fact = p_sub_tot / sum([v for k,v in s_rec.items() if k != "SOP"])
                        for ing_s, val_s in s_rec.items():
                            if ing_s == "SOP": continue
                            gr_s = val_s * (pzas_tot if "Rebozado" in sub_id or "Decoración" in sub_id else fact)
                            st.write(f"- {ing_s}: {gr_s:,.1f}g")
                            compras_finales[ing_s] = compras_finales.get(ing_s, 0) + gr_s
            st.divider()

    # --- T2: LISTA MAESTRA ---
    with tabs[1]:
        st.header("📦 Surtido de Almacén")
        for insumo, cant in sorted(compras_finales.items()):
            c1, c2 = st.columns([0.05, 0.95])
            txt = f"{insumo}: **{cant:,.1f}g**"
            if c1.checkbox("", key=f"main_{insumo}"): c2.markdown(f"~~{txt}~~")
            else: c2.write(txt)

    # --- T-MASAS: DETALLE POR ETAPAS ---
    for i, m_id in enumerate(lotes_masa.keys()):
        with tabs[i+2]:
            st.header(f"🥣 Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in lotes_masa[m_id]])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())

            for etapa in m_dna.get("etapas", []):
                st.markdown(f"""<div class="etapa-box" style="background-color: {etapa['c']};">
                    <div class="etapa-titulo">{etapa['n']}</div>""", unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = (m_dna['receta'][ing] * h_b) / 100
                    c1, c2 = st.columns([0.05, 0.95])
                    if c1.checkbox("", key=f"det_{m_id}_{etapa['n']}_{ing}"):
                        c2.markdown(f"~~{ing}: {gr:,.1f}g~~")
                    else: c2.write(f"**{ing}:** {gr:,.1f}g")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with st.expander("📖 Ver instrucciones detalladas"):
                for step in m_dna["SOP"]: st.write(step)
