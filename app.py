import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS MAESTRA (DNA TÉCNICO)
# ==========================================

# RECETAS DE MASAS (% Panadero)
DB_MASAS = {
    "Conchas": {
        "receta": {"Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "merma": 1.0, "factor_panadero": 1.963
    },
    "Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche": 22, "Sal": 1.8, "Levadura seca": 1.0},
        "merma": 0.85, "tz": {"h_ratio": 0.05, "l_ratio": 5}
    },
    "Roles Gourmet": {
        "receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche": 5, "Levadura fresca": 1, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17},
        "merma": 1.0, "tz": {"h_gr": 70, "l_gr": 350, "base": 1000}
    },
    "Roles Red Velvet": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura": 1, "Cacao": 0.8, "Rojo": 0.7, "Vinagre": 0.3},
        "merma": 1.0, "tz": {"h_ratio": 0.07, "l_ratio": 5}
    },
    "Pan de Muerto Tradicional": {
        "receta": {"Harina": 100, "Leche": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla": 25, "Sal": 2, "Levadura fresca": 3, "Azahar": 2, "Ralladura Naranja": 1},
        "merma": 1.0
    },
    "Pan de Muerto Guayaba": {
        "receta": {"Harina": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Levadura fresca": 5, "Sal": 1.8, "Polvo Guayaba": 5},
        "merma": 1.0, "huesos_refuerzo": True
    },
    "Brownies": {
        "receta": {"Mantequilla avellana": 330, "Azúcar Blanca": 275, "Mascabado": 120, "Chocolate": 165, "Harina": 190, "Cocoa": 75, "Sal": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez": 140},
        "merma": 1.0, "fijo": True
    }
}

# RECETAS DE COMPLEMENTOS (Por pieza o % según tipo)
DB_COMPLEMENTOS = {
    # LÁGRIMAS CONCHA (Basado en Harina=100)
    "L_Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Mazapán_I": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66},
    "L_Oreo": {"Harina": 100, "Azúcar Glass": 75, "Mantequilla": 100, "Oreo": 25},
    # RELLENOS Y ACABADOS
    "C_Ruby": {"Leche": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "Mantequilla": 16, "Sal": 0.8},
    "G_Ruby": {"Chocolate Ruby": 80, "Azúcar Glass": 160, "Leche": 50},
    "C_Turín_Leche": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Choco Turín": 120, "Mantequilla": 20},
    "G_Turín_Costra": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche": 50, "Sal": 1, "Cabeza Conejo": 1},
    "C_Vainilla_SOP": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Sal": 1.5, "Vainilla": 6},
    "Schmear_Canela": {"Mantequilla": 200, "Azúcar Mascabado": 300, "Canela": 25, "Maicena": 20},
    "Schmear_RV": {"Mantequilla": 6, "Azúcar": 6, "Cacao": 1.8, "Maicena": 0.6, "Nuez": 4, "Chocolate": 4},
    "I_Frutos_Rojos": {"Pasas+Arandanos": 8, "Te Earl Grey": 2},
    "I_Manzana": {"Orejón Manzana": 8, "Agua tibia": 2},
    "Rebozado_Muerto": {"Mantequilla baño": 6.5, "Azúcar rebozo": 12.5}
}

# CONFIGURACIÓN JERÁRQUICA DE PRODUCTOS
CATALOGO_TECNICO = {
    "Conchas": {
        "variantes": {"Vainilla": ["L_Vainilla"], "Chocolate": ["L_Chocolate"], "Matcha": ["L_Matcha"], "Pinole": ["L_Pinole"], "Mazapán Intenso": ["L_Mazapán_I"], "Oreo": ["L_Oreo"]},
        "tamaños": {"Estándar": 95, "Mini": 35},
        "peso_ex_u": {"Estándar": 30, "Mini": 10}
    },
    "Berlinas": {
        "variantes": {
            "Ruby v2.0": ["C_Ruby", "G_Ruby"], 
            "Conejo Turín": ["C_Turín_Leche", "G_Turín_Costra"],
            "Vainilla Clásica": ["C_Vainilla_SOP"]
        },
        "tamaños": {"Estándar": 60}, # Ruby se ajusta a 70g en la lógica de pesado
        "pesos_fijos": {"Ruby v2.0": 70} 
    },
    "Rollos": {
        "variantes": {
            "Tradicional (Canela)": ["Schmear_Canela", "I_Frutos_Rojos"],
            "Manzana Canela": ["Schmear_Canela", "I_Manzana"],
            "Red Velvet Premium": ["Schmear_RV"]
        },
        "tamaños": {"Individual": 90}
    },
    "Pan de muerto": {
        "variantes": {"Tradicional": ["Rebozado_Muerto"], "Guayaba": ["Rebozado_Muerto"]},
        "tamaños": {"Estándar": 85, "Grande": 500},
        "rellenos_extra": ["Sin Relleno", "C_Vainilla_SOP", "C_Turín_Leche"]
    },
    "Brownies": {
        "variantes": {"Turín Clásico": []},
        "tamaños": {"Molde 12 pzas": 1}
    }
}

# ==========================================
# 2. INTERFAZ (ORDEN DE COMPRA)
# ==========================================

if 'pedido' not in st.session_state: st.session_state.pedido = []

st.title("🥐 Gestión de Producción - CONCIENCIA")

with st.expander("📝 Cargar Nuevo Producto", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fam_sel = st.selectbox("1. Familia", list(CATALOGO_TECNICO.keys()))
    with col2:
        var_sel = st.selectbox("2. Variante / Sabor", list(CATALOGO_TECNICO[fam_sel]["variantes"].keys()))
    with col3:
        tam_sel = st.selectbox("3. Tamaño", list(CATALOGO_TECNICO[fam_sel]["tamaños"].keys()))
    with col4:
        cant_sel = st.number_input("4. Cantidad", min_value=1, value=12)
    
    rell_sel = "N/A"
    if "rellenos_extra" in CATALOGO_TECNICO[fam_sel]:
        rell_sel = st.selectbox("5. Relleno Opcional", CATALOGO_TECNICO[fam_sel]["rellenos_extra"])

    if st.button("➕ AGREGAR A PRODUCCIÓN"):
        st.session_state.pedido.append({
            "familia": fam_sel, "variante": var_sel, "tamaño": tam_sel, 
            "cantidad": cant_sel, "relleno": rell_sel
        })
        st.rerun()

# ==========================================
# 3. HOJA DE TRABAJO (CÁLCULOS)
# ==========================================

st.divider()
if st.session_state.pedido:
    if st.button("🗑️ Limpiar Plan"): st.session_state.pedido = []; st.rerun()
    
    t_hoja, t_compras = st.tabs(["🥣 Hoja de Producción (Detalle)", "📦 Lista Maestra de Insumos"])
    total_almacen = {}

    with t_hoja:
        for item in st.session_state.pedido:
            st.subheader(f"PRODUCCIÓN: {item['cantidad']}x {item['variante']} ({item['tamaño']})")
            
            # --- LÓGICA DE MASA (COLUMNA 1) ---
            m_id = item['familia']
            if item['variante'] == "Red Velvet Premium": m_id = "Roles Red Velvet"
            elif item['variante'] == "Guayaba": m_id = "Pan de Muerto Guayaba"
            elif item['familia'] == "Pan de muerto" and item['variante'] == "Tradicional": m_id = "Pan de Muerto Tradicional"
            
            m_dna = DB_MASAS[m_id]
            peso_u = CATALOGO_TECNICO[item['familia']].get("pesos_fijos", {}).get(item['variante'], CATALOGO_TECNICO[item['familia']]["tamaños"][item['tamaño']])
            
            c1, c2 = st.columns(2)
            
            with c1:
                st.info("📦 **COLUMNA 1: MASA**")
                if m_dna.get("fijo"):
                    for ing, val in m_dna["receta"].items():
                        total_g = val * item['cantidad']
                        st.write(f"• {ing}: **{total_g:,.1f}g**")
                        total_almacen[ing] = total_almacen.get(ing, 0) + total_g
                else:
                    masa_total = (peso_u * item['cantidad']) / m_dna["merma"]
                    h_total = (masa_total * 100) / sum(m_dna["receta"].values())
                    
                    for ing, porc in m_dna["receta"].items():
                        gr = (porc * h_total) / 100
                        st.write(f"• {ing}: **{gr:,.1f}g**")
                        total_almacen[ing] = total_almacen.get(ing, 0) + gr
                    
                    if "tz" in m_dna:
                        st.warning("**⚡ Tangzhong:**")
                        if "h_gr" in m_dna["tz"]:
                            factor_tz = h_total / m_dna["tz"]["base"]
                            st.write(f"- Harina: {m_dna['tz']['h_gr']*factor_tz:,.1f}g | Leche: {m_dna['tz']['l_gr']*factor_tz:,.1f}g")
                        else:
                            tz_h = h_total * m_dna["tz"]["h_ratio"]
                            st.write(f"- Harina: {tz_h:,.1f}g | Leche: {tz_h*m_dna['tz']['l_ratio']:,.1f}g")
            
            with c2:
                st.success("✨ **COLUMNA 2: COMPLEMENTOS**")
                # Jalar lista de sub-recetas
                subs = CATALOGO_TECNICO[item['familia']]["variantes"][item['variante']]
                if item['relleno'] != "N/A" and item['relleno'] != "Sin Relleno":
                    subs.append(item['relleno'])
                
                for sub_id in subs:
                    st.write(f"**{sub_id.replace('_',' ')}**")
                    s_receta = DB_COMPLEMENTOS[sub_id]
                    
                    # Calcular peso del extra
                    if item['familia'] == "Conchas":
                        p_ex_tot = CATALOGO_TECNICO["Conchas"]["peso_ex_u"][item['tamaño']] * item['cantidad']
                    elif "Berlina" in item['familia']:
                        p_ex_tot = (80 if "CREMA" in sub_id else 16) * item['cantidad']
                    elif "Roles" in item['familia']:
                        p_ex_tot = (13.4 if "SCHMEAR" in sub_id else 8) * item['cantidad']
                    else:
                        p_ex_tot = 1 # Para rebozados se usa factor directo
                    
                    factor_s = p_ex_tot / sum([v for v in s_receta.values() if isinstance(v, (int, float))])
                    for ing, val in s_receta.items():
                        if "Cabeza" in ing:
                            st.write(f"- {ing}: {val*item['cantidad']} pzas")
                            total_almacen[ing] = total_almacen.get(ing, 0) + (val*item['cantidad'])
                        else:
                            gr_s = val * (item['cantidad'] if "Muerto" in sub_id else factor_s)
                            st.write(f"- {ing}: {gr_s:,.1f}g")
                            total_almacen[ing] = total_almacen.get(ing, 0) + gr_s
            st.divider()

    with t_compras:
        st.header("🛒 Lista Maestra de Insumos")
        df_inv = pd.DataFrame(total_almacen.items(), columns=["Ingrediente", "Total (g/pzas)"]).sort_values("Ingrediente")
        st.table(df_inv)
