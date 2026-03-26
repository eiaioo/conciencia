import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro de Producción", layout="wide")

# ==========================================
# BASE DE DATOS TÉCNICA (NÚCLEO DEL SISTEMA)
# ==========================================

# 1. CATÁLOGO DE MASAS (DNA Base)
DB_MASAS = {
    "CONCHAS": {
        "harina_fuerza": 100, "huevo_entero": 40, "leche_entera": 24, "azucar_refinada": 30, 
        "mantequilla_sin_sal": 40, "sal_fina": 2.5, "levadura_seca": 1.8, "vainilla_extracto": 2.0
    },
    "BERLINAS": {
        "harina_fuerza": 100, "azucar_refinada": 22, "mantequilla_sin_sal": 20, 
        "huevo_entero": 25, "leche_entera": 22, "sal_fina": 1.8, "levadura_seca": 1.0,
        "__config__": {"tangzhong": True, "tz_ratio": 0.05, "tz_liquido": 5, "merma_corte": 0.85}
    },
    "ROLES_CANELA": {
        "harina_fuerza": 93, "huevo_entero": 30, "leche_ajuste": 5, "levadura_fresca": 1, 
        "sal_fina": 1.8, "azucar_refinada": 16, "mantequilla_sin_sal": 17,
        "__config__": {"tangzhong": True, "tz_h_gr": 70, "tz_l_gr": 350, "total_h_sistema": 1000}
    },
    "ROLES_RED_VELVET": {
        "harina_fuerza": 100, "azucar_refinada": 16, "mantequilla_sin_sal": 17, "huevo_entero": 30, 
        "leche_entera": 4, "sal_fina": 1.8, "levadura_instantanea": 1.0, "cacao_polvo": 0.8, 
        "colorante_rojo": 0.7, "vinagre": 0.3,
        "__config__": {"tangzhong": True, "tz_ratio": 0.07, "tz_liquido": 5}
    },
    "MUERTO_TRADICIONAL": {
        "harina_panificable": 100, "leche_entera": 25, "yemas": 24, "claras": 16, 
        "azucar_refinada": 20, "mantequilla_sin_sal": 25, "sal_fina": 2.0, "levadura_fresca": 3.0, 
        "agua_azahar": 2.0, "ralladura_naranja": 1.0
    },
    "MUERTO_GUAYABA": {
        "harina_fuerza": 100, "leche_entera": 30, "yemas": 18, "claras": 12, "azucar_refinada": 20, 
        "mantequilla_sin_sal": 25, "levadura_fresca": 5.0, "sal_fina": 1.8, "polvo_guayaba": 5.0,
        "__config__": {"refuerzo_huesos": True}
    },
    "REPOSTERIA_BROWNIE": {
        "mantequilla_82": 330, "azucar_blanca": 275, "azucar_mascabado": 120, "chocolate_turin_amargo": 165, 
        "harina_trigo": 190, "cocoa_alcalinizada": 75, "sal_fina": 8, "claras": 160, "yemas": 95, 
        "vainilla_extracto": 8, "nuez_tostada": 140, "sal_escamas": 1.8,
        "__config__": {"batch_fijo": True, "piezas_batch": 12}
    }
}

# 2. COMPONENTES (Rellenos, Inclusiones, Acabados)
DB_EXTRAS = {
    # Berlinas
    "CREMA_RUBY": {"leche": 131.5, "crema_35": 131.5, "yemas": 53, "azucar": 63, "fecula_maiz": 24, "mantequilla": 16, "sal": 0.8},
    "GLASEADO_RUBY": {"chocolate_ruby": 80, "azucar_glass": 160, "leche": 50},
    "CREMA_TURIN_LECHE": {"leche_entera": 450, "yemas": 100, "azucar_refinada": 90, "fecula_maiz": 45, "chocolate_turin_leche": 120, "mantequilla": 20, "sal_fina": 1.5},
    "GLASEADO_TURIN_COSTRA": {"azucar_glass": 200, "choco_turin_cuerpos": 100, "leche_caliente": 50, "sal_fina": 1, "conejo_turin_cabezas": 1},
    "CREMA_VAINILLA_SOP": {"leche_entera": 500, "yemas": 100, "azucar_refinada": 120, "fecula_maiz": 45, "mantequilla": 30, "sal_fina": 1.5, "vainilla_natural": 6},
    # Roles
    "SCHMEAR_CANELA": {"mantequilla_pomada": 200, "azucar_mascabado": 300, "canela_polvo": 25, "maicena": 20, "sal_fina": 3},
    "SCHMEAR_RED_VELVET": {"mantequilla": 6, "azucar": 6, "cacao": 1.8, "maicena": 0.6, "nuez": 4, "chocolate": 4},
    "INCL_FRUTOS_ROJOS": {"pasas": 4, "arandanos": 4, "te_earl_grey": 2, "vainilla": 0.5},
    "INCL_MANZANA": {"orejon_manzana": 8, "agua_tibia": 2},
    "GLASEADO_VAINILLA_FLAT": {"azucar_glass": 200, "leche": 35, "vainilla_extracto": 5, "sal_fina": 0.5},
    # Conchas (Porcentajes sobre Harina=100)
    "LAGRIMA_VAINILLA": {"harina": 100, "azucar_glass": 100, "mantequilla": 100},
    "LAGRIMA_CHOCO": {"harina": 87.5, "cacao": 12.5, "azucar_glass": 100, "mantequilla": 100},
    "LAGRIMA_MATCHA": {"harina": 91.5, "matcha": 8.5, "azucar_glass": 100, "mantequilla": 100},
    "LAGRIMA_PINOLE": {"harina": 79, "pinole": 21, "azucar_glass": 100, "mantequilla": 100},
    "LAGRIMA_MAZAPAN_INTENSO": {"harina": 100, "azucar_glass": 100, "mantequilla": 100, "mazapan": 66},
    # Muertos
    "REBOZADO_MUERTO": {"mantequilla_baño": 6.5, "azucar_rebozo": 12.5, "ralladura_naranja": 0.25}
}

# 3. PRODUCTOS FINALES (La Comanda)
PRODUCTOS = {
    "CONCHAS": {
        "Vainilla": {"masa": "CONCHAS", "peso": 95, "extras": ["LAGRIMA_VAINILLA"], "peso_ex": 30},
        "Chocolate": {"masa": "CONCHAS", "peso": 95, "extras": ["LAGRIMA_CHOCO"], "peso_ex": 30},
        "Matcha": {"masa": "CONCHAS", "peso": 95, "extras": ["LAGRIMA_MATCHA"], "peso_ex": 30},
        "Mazapán Intenso": {"masa": "CONCHAS", "peso": 95, "extras": ["LAGRIMA_MAZAPAN_INTENSO"], "peso_ex": 30},
        "Pinole": {"masa": "CONCHAS", "peso": 95, "extras": ["LAGRIMA_PINOLE"], "peso_ex": 30},
        "Mini Vainilla": {"masa": "CONCHAS", "peso": 35, "extras": ["LAGRIMA_VAINILLA"], "peso_ex": 10}
    },
    "BERLINAS": {
        "Ruby v2.0": {"masa": "BERLINAS", "peso": 70, "extras": ["CREMA_RUBY", "GLASEADO_RUBY"], "peso_ex_manual": {"CREMA_RUBY": 40, "GLASEADO_RUBY": 8}},
        "Conejo Turín": {"masa": "BERLINAS", "peso": 60, "extras": ["CREMA_TURIN_LECHE", "GLASEADO_TURIN_COSTRA"], "peso_ex_manual": {"CREMA_TURIN_LECHE": 80, "GLASEADO_TURIN_COSTRA": 16}},
        "Vainilla Clásica": {"masa": "BERLINAS", "peso": 60, "extras": ["CREMA_VAINILLA_SOP"], "peso_ex_manual": {"CREMA_VAINILLA_SOP": 80}}
    },
    "ROLES": {
        "Tradicional (Frutos Rojos)": {"masa": "ROLES_CANELA", "peso": 90, "extras": ["SCHMEAR_CANELA", "INCL_FRUTOS_ROJOS", "GLASEADO_VAINILLA_FLAT"], "peso_ex_manual": {"SCHMEAR_CANELA": 13.4, "INCL_FRUTOS_ROJOS": 8.5, "GLASEADO_VAINILLA_FLAT": 10}},
        "Manzana Canela": {"masa": "ROLES_CANELA", "peso": 90, "extras": ["SCHMEAR_CANELA", "INCL_MANZANA", "GLASEADO_VAINILLA_FLAT"], "peso_ex_manual": {"SCHMEAR_CANELA": 13.4, "INCL_MANZANA": 10, "GLASEADO_VAINILLA_FLAT": 10}},
        "Red Velvet Premium": {"masa": "ROLES_RED_VELVET", "peso": 90, "extras": ["SCHMEAR_RED_VELVET", "GLASEADO_VAINILLA_FLAT"], "peso_ex_manual": {"SCHMEAR_RED_VELVET": 15, "GLASEADO_VAINILLA_FLAT": 10}}
    },
    "PAN DE MUERTO": {
        "Tradicional Naranja": {"masa": "MUERTO_TRADICIONAL", "peso": 85, "extras": ["REBOZADO_MUERTO"], "peso_ex": 19},
        "Guayaba Huesos-Ref": {"masa": "MUERTO_GUAYABA", "peso": 95, "extras": ["REBOZADO_MUERTO"], "peso_ex": 19}
    },
    "BROWNIES": {
        "Brownie Turín 20x20": {"masa": "REPOSTERIA_BROWNIE", "peso": 1, "extras": []}
    }
}

# ==========================================
# INTERFAZ Y LÓGICA DE CÁLCULO
# ==========================================

st.title("🥐 Sistema de Producción Técnico CONCIENCIA")
if 'plan' not in st.session_state: st.session_state.plan = []

t_ord, t_rec, t_super = st.tabs(["🛒 Comanda", "🥣 Hoja de Pesado", "📦 Totales Almacén"])

with t_ord:
    c1, c2, c3 = st.columns(3)
    with c1: cat_sel = st.selectbox("Categoría Técnica", list(PRODUCTOS.keys()))
    with c2: prod_sel = st.selectbox("Producto Final", list(PRODUCTOS[cat_sel].keys()))
    with c3: cant = st.number_input("Cantidad", min_value=1, value=12)
    
    if st.button("➕ Añadir a Producción"):
        st.session_state.plan.append({"cat": cat_sel, "prod": prod_sel, "cant": cant})
    
    if st.session_state.plan:
        st.table(pd.DataFrame(st.session_state.plan))
        if st.button("🗑️ Vaciar Plan"): st.session_state.plan = []

almacen = {}

if st.session_state.plan:
    with t_rec:
        for item in st.session_state.plan:
            p_config = PRODUCTOS[item['cat']][item['prod']]
            m_id = p_config['masa']
            m_db = DB_MASAS[m_id]
            
            st.header(f"📦 {item['prod']} (Batch: {item['cant']})")
            
            # --- CÁLCULO DE MASA ---
            if m_db.get("__config__", {}).get("batch_fijo"):
                for ing, val in m_db.items():
                    if ing != "__config__":
                        total = val * item['cant']
                        st.write(f"• {ing}: **{total:,.1f}g**")
                        almacen[ing] = almacen.get(ing, 0) + total
            else:
                m_total = (p_config['peso'] * item['cant']) / m_db.get("__config__", {}).get("merma_corte", 1.0)
                h_base = (m_total * 100) / sum([v for k,v in m_db.items() if k != "__config__"])
                
                col_masa, col_sub = st.columns(2)
                with col_masa:
                    st.subheader("Masa Principal")
                    for ing, porc in m_db.items():
                        if ing != "__config__":
                            peso = (porc * h_base) / 100
                            st.write(f"• {ing}: **{peso:,.1f}g**")
                            almacen[ing] = almacen.get(ing, 0) + peso
                
                with col_sub:
                    cfg = m_db.get("__config__", {})
                    if cfg.get("tangzhong"):
                        st.subheader("⚡ Tangzhong")
                        if "tz_h_gr" in cfg: # Caso Roles
                            factor_tz = h_base / 930
                            h_tz, l_tz = cfg["tz_h_gr"]*factor_tz, cfg["tz_l_gr"]*factor_tz
                        else:
                            h_tz = h_base * cfg["tz_ratio"]
                            l_tz = h_tz * cfg["tz_liquido"]
                        st.warning(f"Harina: {h_tz:,.1f}g | Leche: {l_tz:,.1f}g")
                        almacen["Harina de fuerza"] = almacen.get("Harina de fuerza", 0) + h_tz
                        almacen["Leche"] = almacen.get("Leche", 0) + l_tz

            # --- CÁLCULO COMPLEMENTOS ---
            for ext_id in p_config['extras']:
                st.subheader(f"✨ {ext_id.replace('_',' ')}")
                ext_db = DB_EXTRAS[ext_id]
                # Determinar peso total del extra
                if "peso_ex_manual" in p_config:
                    p_ex_tot = p_config["peso_ex_manual"][ext_id] * item['cant']
                else:
                    p_ex_tot = p_config["peso_ex"] * item['cant']
                
                factor_ex = p_ex_tot / sum(ext_db.values())
                for ing, val in ext_db.items():
                    if "cabezas" in ing:
                        unidades = val * item['cant']
                        st.write(f"- {ing}: {unidades} pzas")
                        almacen[ing] = almacen.get(ing, 0) + unidades
                    else:
                        p = val * factor_ex
                        st.write(f"- {ing}: {p:,.1f}g")
                        almacen[ing] = almacen.get(ing, 0) + p
            st.divider()

    with t_super:
        st.header("🛒 Lista Maestra de Insumos")
        df_f = pd.DataFrame(almacen.items(), columns=["Insumo", "Cantidad"]).sort_values("Insumo")
        st.table(df_f)
