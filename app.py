import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA (DNA CONCIENCIA)
# ==========================================

# Definimos los panes y sus árboles de decisión
ESTRUCTURA_PRODUCTOS = {
    "Conchas": {
        "sabores": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán Estándar", "Mazapán Intenso", "Oreo", "Pinole"],
        "tamaños": {"Estándar": 95, "Mini": 35},
        "rellenos": ["Sin Relleno"],
        "masa_id": "Masa_Concha",
        "factor_masa": 1.963
    },
    "Berlinas": {
        "sabores": ["Ruby v2.0", "Conejo Turín", "Vainilla Clásica", "Chocolate Amargo"],
        "tamaños": {"Estándar": 60}, # Ruby se ajusta a 70g en lógica
        "rellenos": ["Relleno según Ficha"], 
        "masa_id": "Masa_Berlina"
    },
    "Rollos": {
        "sabores": ["Tradicional (Canela)", "Manzana", "Conejo Turín", "Red Velvet Premium"],
        "tamaños": {"Individual": 90},
        "rellenos": ["Schmear según Ficha"],
        "masa_id": "Masa_Rol"
    },
    "Rosca de reyes": {
        "sabores": ["Tradicional", "Vainilla", "Chocolate Amargo", "Línea Turín"],
        "tamaños": {"Mediana": 900, "Individual": 100},
        "rellenos": ["Sin Relleno", "Rellena"],
        "masa_id": "Masa_Rosca"
    },
    "Pan de muerto": {
        "sabores": ["Tradicional (Naranja/Azahar)", "Guayaba (Huesos Reforzados)"],
        "tamaños": {"Estándar": 85}, # Guayaba se ajusta a 95g
        "rellenos": ["Sin Relleno", "Crema Vainilla", "Crema Chocolate", "Crema Turín"],
        "masa_id": "Masa_Muerto"
    },
    "Brownies": {
        "sabores": ["Turín Clásico"],
        "tamaños": {"Molde 20x20": 1},
        "rellenos": ["N/A"],
        "masa_id": "Masa_Brownie"
    }
}

# --- DATOS DE INGREDIENTES ---
MASAS_DNA = {
    "Masa_Concha": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
    "Masa_Berlina": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche": 22, "Sal": 1.8, "Levadura seca": 1.0, "__merma": 0.85, "__tz": (0.05, 5)},
    "Masa_Rol": {"Harina de fuerza": 93, "Huevo": 30, "Leche": 5, "Levadura fresca": 1, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17, "__tz": (70/1000, 5)},
    "Masa_RV": {"Harina": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7, "Vinagre": 0.3},
    "Masa_Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla": 30, "Huevo": 20, "Yema": 4, "Leche": 24, "Levadura": 0.35, "Sal": 2.2, "Agua Azahar": 0.6, "__tz": (0.025, 1)},
    "Masa_Muerto": {"Harina": 100, "Leche": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla": 25, "Sal": 2, "Levadura": 3, "Azahar": 2},
    "Masa_Muerto_Guayaba": {"Harina": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura": 5, "Sal": 1.8, "Guayaba": 5, "__huesos": True},
    "Masa_Brownie": {"Mantequilla": 330, "Azúcar Blanca": 275, "Mascabado": 120, "Chocolate": 165, "Harina": 190, "Cocoa": 75, "Sal": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez": 140}
}

# ==========================================
# 2. LÓGICA DE INTERFAZ (FLUJO POR PASOS)
# ==========================================

if 'comanda' not in st.session_state:
    st.session_state.comanda = []

st.title("🥐 Comanda Técnica CONCIENCIA")

with st.expander("➕ Agregar Nuevo Pan a la Producción", expanded=True):
    # PASO 1: Familia de Pan
    pan_tipo = st.selectbox("1. Tipo de Pan", ["Selecciona..."] + list(ESTRUCTURA_PRODUCTOS.keys()))
    
    if pan_tipo != "Selecciona...":
        datos = ESTRUCTURA_PRODUCTOS[pan_tipo]
        
        # PASO 2: Sabor
        sabor_sel = st.selectbox(f"2. Sabor de {pan_tipo}", datos["sabores"])
        
        # PASO 3: Tamaño
        tamano_sel = st.selectbox("3. Tamaño / Presentación", list(datos["tamaños"].keys()))
        
        # PASO 4: Relleno (si aplica)
        relleno_sel = "N/A"
        if len(datos["rellenos"]) > 1 or datos["rellenos"][0] == "Rellena":
            relleno_sel = st.selectbox("4. Opción de Relleno", datos["rellenos"])
        
        # PASO 5: Cantidad
        cant = st.number_input("5. Número de piezas", min_value=1, value=1, step=1)
        
        # BOTÓN FINAL
        if st.button("✅ AGREGAR A LA COMANDA"):
            st.session_state.comanda.append({
                "pan": pan_tipo,
                "sabor": sabor_sel,
                "tamano": tamano_sel,
                "relleno": relleno_sel,
                "cantidad": cant
            })
            st.success(f"{pan_tipo} agregado correctamente.")
            st.rerun()

# ==========================================
# 3. VISUALIZACIÓN DE LA COMANDA
# ==========================================

st.subheader("📋 Comanda del Día")
if st.session_state.comanda:
    df_comanda = pd.DataFrame(st.session_state.comanda)
    st.table(df_comanda)
    if st.button("🗑️ Limpiar Todo el Día"):
        st.session_state.comanda = []
        st.rerun()

    # ==========================================
    # 4. LÓGICA DE CÁLCULO (TRAS BAMBALINAS)
    # ==========================================
    almacen_total = {}

    def sumar(ing, g):
        almacen_total[ing] = almacen_total.get(ing, 0) + g

    t_recetas, t_super = st.tabs(["🥣 Hoja de Producción (Pesado)", "📦 Lista Maestra de Insumos"])

    with t_recetas:
        for item in st.session_state.comanda:
            st.write(f"### {item['cantidad']}x {item['pan']} ({item['sabor']})")
            
            # -- Lógica de Selección de Masa --
            masa_key = ESTRUCTURA_PRODUCTOS[item['pan']]["masa_id"]
            if item['sabor'] == "Red Velvet Premium": masa_key = "Masa_RV"
            if item['sabor'] == "Guayaba (Huesos Reforzados)": masa_key = "Masa_Muerto_Guayaba"
            
            m_dna = MASAS_DNA[masa_key]
            
            # Peso y Masa Total
            peso_unitario = ESTRUCTURA_PRODUCTOS[item['pan']]["tamaños"][item['tamano']]
            if item['sabor'] == "Ruby v2.0": peso_unitario = 70
            if item['sabor'] == "Guayaba (Huesos Reforzados)": peso_unitario = 95
            
            # Merma
            merma = m_dna.get("__merma", 1.0)
            masa_total = (peso_unitario * item['cantidad']) / merma
            
            # Harina Base (100%)
            sum_porcentajes = sum([v for k,v in m_dna.items() if not k.startswith("__")])
            h_base = (masa_total * 100) / sum_porcentajes

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Masa:**")
                for ing, val in m_dna.items():
                    if not ing.startswith("__"):
                        gr = (val * h_base) / 100
                        st.write(f"- {ing}: {gr:,.1f}g")
                        sumar(ing, gr)
            
            with col2:
                # Tangzhong
                if "__tz" in m_dna:
                    st.write("**⚡ Tangzhong:**")
                    tz_h = h_base * m_dna["__tz"][0]
                    tz_l = tz_h * m_dna["__tz"][1]
                    st.warning(f"Harina: {tz_h:,.1f}g / Leche: {tz_l:,.1f}g")
                    # (Ya sumados en harina/leche total)
                
                # Huesos refuerzo
                if "__huesos" in m_dna:
                    h_ex = masa_total * 0.25 * 0.30
                    y_ex = masa_total * 0.25 * 0.10
                    st.info(f"🦴 Refuerzo Huesos: +{h_ex:,.1f}g Harina / +{y_ex:,.1f}g Yema")
                    sumar("Harina Refuerzo", h_ex)
                    sumar("Yemas Extra", y_ex)

            st.divider()

    with t_super:
        st.header("📦 Necesidades de Compra")
        df_inv = pd.DataFrame(almacen_total.items(), columns=["Ingrediente", "Total (g)"]).sort_values("Ingrediente")
        st.dataframe(df_inv, use_container_width=True)

else:
    st.info("La comanda está vacía. Selecciona productos arriba para empezar.")
