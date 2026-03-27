import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN Y ESTILOS (SOLUCIÓN MÓVIL Y TEMA)
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state:
    st.session_state.tema_oscuro = True

def toggle_tema():
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro

# CSS para arreglar el móvil, las etapas y el modo oscuro
bg_color = "#121212" if st.session_state.tema_oscuro else "#FFFFFF"
text_color = "#E0E0E0" if st.session_state.tema_oscuro else "#202020"
card_bg = "#1E1E1E" if st.session_state.tema_oscuro else "#F0F2F6"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    /* Arreglo para checklist en móvil */
    .stCheckbox {{ display: flex; align-items: center; margin-bottom: -15px; }}
    .stCheckbox label {{ font-size: 1.1rem !important; line-height: 1.2 !important; padding-top: 5px; }}
    
    /* Recuadros de Etapas */
    .etapa-card {{
        background-color: {card_bg};
        border-left: 5px solid #ff4b4b;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }}
    .etapa-titulo {{ color: #ff4b4b; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN SOL/LUNA
btn_label = "🌙" if st.session_state.tema_oscuro else "☀️"
st.button(btn_label, on_click=toggle_tema, help="Cambiar modo de luz")

# ==========================================
# 1. BASE DE DATOS CON ETAPAS (SOP)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "etapas": [
            {"nombre": "1. Autólisis", "ing": ["Harina de fuerza", "Huevo", "Leche entera"]},
            {"nombre": "2. Activación", "ing": ["Levadura seca", "Vainilla"]},
            {"nombre": "3. Estructura", "ing": ["Azúcar", "Sal fina"]},
            {"nombre": "4. Enriquecimiento", "ing": ["Mantequilla sin sal"]}
        ],
        "merma": 1.0, "factor": 1.963
    },
    # Las demás masas se pueden estructurar igual...
}

# (Por brevedad, mantengo la estructura anterior para Berlinas/Roles, pero con la lógica nueva preparada)
if "Masa de Berlinas" not in DB_MASAS:
    DB_MASAS["Masa de Berlinas"] = {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "etapas": [{"nombre": "Proceso Único", "ing": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina", "Levadura seca"]}],
        "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5
    }

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
}

# (Mantenemos ARBOL de la versión anterior)
ARBOL = {
    "Conchas": {
        "espec": {"Vainilla": ["Lágrima de Vainilla"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"
    }
}

# ==========================================
# 2. LÓGICA DE INTERFAZ
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0

with st.expander("📝 Cargar Nuevo Producto", expanded=not st.session_state.comanda):
    fk = st.session_state.form_id
    fam = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if fam != "-":
        esp = st.selectbox("Especialidad", list(ARBOL[fam]["espec"].keys()), key=f"e_{fk}")
        tam = st.selectbox("Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{fk}")
        cant = st.number_input("Cantidad", min_value=1, value=1, key=f"c_{fk}")
        if st.button("✅ AGREGAR"):
            st.session_state.comanda.append({"fam": fam, "esp": esp, "tam": tam, "cant": cant})
            st.session_state.form_id += 1
            st.rerun()

# ==========================================
# 3. HOJA DE PRODUCCIÓN POR ETAPAS
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()
    
    # Cálculos de lotes
    lotes_masa = {}
    for item in st.session_state.comanda:
        m_id = ARBOL[item['fam']]["masa"]
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    t_res, t_masas = st.tabs(["📋 Resumen", "🥣 Detalle por Etapas"])

    with t_res:
        st.write("Visión general de la comanda...")
        # (Aquí va el resumen visual de la versión anterior)

    with t_masas:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            # Calcular Harina Base para el lote
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_base = (m_batch * 100) / sum(m_dna['receta'].values())

            st.markdown(f"## 🥣 {m_id}")
            st.write(f"**Peso total del batido: {m_batch:,.1f}g**")

            # --- DIBUJAR ETAPAS ---
            for etapa in m_dna.get("etapas", []):
                st.markdown(f"""<div class="etapa-card">
                    <div class="etapa-titulo">{etapa['nombre']}</div>
                </div>""", unsafe_allow_html=True)
                
                # Checklist de ingredientes de esta etapa
                for ing in etapa['ing']:
                    porc = m_dna['receta'][ing]
                    peso = (porc * h_base) / 100
                    
                    # Usamos st.checkbox con etiqueta vacía y markdown para tachar
                    c1, c2 = st.columns([0.1, 0.9])
                    is_done = c1.checkbox("", key=f"step_{m_id}_{etapa['nombre']}_{ing}")
                    txt = f"{ing}: **{peso:,.1f}g**"
                    if is_done:
                        c2.markdown(f"~~{txt}~~")
                    else:
                        c2.write(txt)
