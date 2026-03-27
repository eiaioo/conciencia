import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ESTADO DE LA APLICACIÓN (CERO ERRORES)
# ==========================================
if 'pedidos' not in st.session_state: st.session_state.pedidos = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0

st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

# ==========================================
# 2. BASE DE DATOS MAESTRA (DNA PANADERO)
# ==========================================

# Aquí reside toda la inteligencia de las fichas técnicas
DATABASE = {
    "CONCHAS": {
        "masa": "Dough Brioche Concha",
        "tallas": {"Estándar": 95, "Mini": 35},
        "complementos": {
            "Vainilla": {"Lágrima Vainilla": 30}, # Peso para Estándar, se ajusta para mini solo
            "Chocolate": {"Lágrima Chocolate": 30},
            "Matcha": {"Lágrima Matcha": 30},
            "Fresa": {"Lágrima Fresa": 30},
            "Mazapán": {"Lágrima Mazapán": 30},
            "Oreo": {"Lágrima Oreo": 30},
            "Pinole": {"Lágrima Pinole": 30}
        }
    },
    "ROSCAS": {
        "masa": "Dough Brioche Rosca",
        "tallas": {"Familiar": 1450, "Mediana": 650, "Mini": 120, "Individual": 90},
        "relleno_map": {"Familiar": 450, "Mediana": 200, "Mini": 35, "Individual": 25},
        "especialidades": {
            "Tradicional": ["Lágrima Vainilla", "Decoración Rosca Ate"],
            "Chocolate": ["Lágrima Chocolate", "Decoración Nuez"],
            "Turín": ["Lágrima Chocolate", "Crema Turín", "Glaseado Turín Costra", "Cabezas Conejo"]
        },
        "cremas_extra": ["Sin Relleno", "Crema Vainilla", "Crema Chocolate", "Crema Ruby"]
    },
    "BERLINAS": {
        "masa": "Dough Berlín TZ",
        "tallas": {"Estándar": 60, "Ruby Special": 70},
        "especialidades": {
            "Vainilla": ["Crema Vainilla"],
            "Ruby v2.0": ["Crema Ruby", "Glaseado Ruby"],
            "Turín": ["Crema Turín", "Glaseado Turín Costra"]
        }
    },
    "ROLES": {
        "masa": "Dough Roles Master",
        "tallas": {"Individual": 90},
        "especialidades": {
            "Tradicional Canela": ["Schmear Canela", "Inclusión Pasas Arándanos", "Té Earl Grey"],
            "Manzana": ["Schmear Canela", "Inclusión Manzana", "Agua Tibia"],
            "Red Velvet": ["Masa Red Velvet", "Schmear RV", "Crema Vainilla"]
        }
    },
    "PAN DE MUERTO": {
        "masa": "Dough Muerto",
        "tallas": {"Estándar": 90},
        "especialidades": {
            "Tradicional Naranja": ["Rebozado Muerto"],
            "Guayaba Huesos-Ref": ["Rebozado Muerto", "Yemas Huesos", "Harina Huesos"]
        }
    },
    "BROWNIES": {
        "masa": "Mezcla Brownie",
        "tallas": {"Molde 20x20": 1},
        "especialidades": {"Turín Amargo": []}
    }
}

# Recetas desglosadas por 100g de Harina (Masa) o Batch Completo (Extras)
ING_RECETARIO = {
    "Dough Brioche Concha": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla": 40, "Sal fina": 2.5, "Levadura": 1.8},
    "Dough Berlín TZ": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche": 22, "Sal fina": 1.8, "Levadura": 1.0, "_merma": 0.85},
    "Dough Brioche Rosca": {"Harina": 100, "Azúcar": 25, "Miel": 3, "Mantequilla": 30, "Huevo": 20, "Yemas": 4, "Leche": 24, "Sal": 2.2, "Azahar": 0.6},
    "Dough Roles Master": {"Harina de fuerza": 93, "Huevo": 30, "Leche": 5, "Levadura": 1.0, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17},
    "Masa Red Velvet": {"Harina": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Levadura": 1, "Rojo Rojo": 0.7, "Vinagre": 0.3},
    "Dough Muerto": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Azúcar": 20, "Mantequilla": 25, "Sal": 1.8, "Levadura fresca": 5.0},
    "Mezcla Brownie": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa": 75},
    
    # --- COMPLEMENTOS (Sub-recetas) ---
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Ruby": {"Leche": 131, "Crema 35%": 131, "Yemas": 53, "Azúcar": 63},
    "Crema Turín": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Chocolate Turin": 120},
    "Schmear Canela": {"Mantequilla pomada": 200, "Mascabado": 300, "Canela": 25, "Maicena": 20}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA (WORKSHOP STYLE)
# ==========================================

st.title("🍞 Producción Integral CONCIENCIA")

with st.container():
    col_c1, col_c2 = st.columns(2)
    cliente = col_c1.text_input("Nombre del Cliente", placeholder="Lalo...")
    telefono = col_c2.text_input("WhatsApp (10 dígitos)")

st.subheader("🛠️ Selección de Pan")
fk = st.session_state.form_key
c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1, 0.6])

familia = c1.selectbox("Familia de Pan", ["-"] + list(DATABASE.keys()), key=f"fam_{fk}")

if familia != "-":
    # Selección Inteligente de especialidades
    espec_options = list(DATABASE[familia]["especialidades"].keys()) if "especialidades" in DATABASE[familia] else list(DATABASE[familia]["complementos"].keys())
    especialidad = c2.selectbox("Sabor / Variante", espec_options, key=f"esp_{fk}")
    
    # Tamaños
    tallas_keys = list(DATABASE[familia]["tallas"].keys())
    talla = c3.selectbox("Tamaño", tallas_keys, key=f"tam_{fk}")
    
    # Cantidad
    cantidad = c4.number_input("Cantidad", min_value=1, value=1, key=f"cnt_{fk}")
    
    # Rellenos (Solo si es Rosca)
    relleno_final = "N/A"
    if familia == "ROSCA_DE_REYES":
        relleno_final = st.selectbox("Añadir Relleno de Crema", DATABASE[familia]["rellenos_validos"], key=f"rell_{fk}")

    # Alineación del botón ➕
    c5.write(" ")
    c5.write(" ")
    if c5.button("➕"):
        st.session_state.carrito.append({
            "fam": familia, "esp": especialidad, "tam": talla, "cant": cantidad, "rel": relleno_final
        })
        st.session_state.form_key += 1
        st.rerun()

# --- REVISIÓN DEL CARRITO ---
if st.session_state.carrito:
    with st.expander(f"🛒 Ver carrito para {cliente if cliente else 'Venta General'}", expanded=True):
        for it in st.session_state.carrito:
            st.write(f"- {it['cant']}x {it['fam']} — {it['esp']} ({it['tam']}) {'+ '+it['rel'] if it['rel']!='N/A' else ''}")
        
        btn_c1, btn_c2 = st.columns(2)
        if btn_c1.button("✅ FINALIZAR PEDIDO Y ENVIAR A COCINA"):
            st.session_state.pedidos.append({"cliente": cliente, "wa": telefono, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()
        if btn_c2.button("🗑️ VACIAR"): st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PROCESAMIENTO (LA LÓGICA)
# ==========================================

if st.session_state.pedidos:
    st.divider()
    tab_sum, tab_pes, tab_super = st.tabs(["📋 Resumen de Órdenes", "🥣 Hojas de Trabajo", "🛒 Lista de Compras"])
    
    inv_compras = {}
    batidos_lote = {}
    complementos_lote = {} # Agrupa todas las lágrimas/rellenos del día

    # Recorrido del Motor
    for orden in st.session_state.pedidos:
        for it in orden['items']:
            # -- LÓGICA MASA --
            m_id = DATABASE[it['fam']]["masa"]
            if it['esp'] == "Red Velvet": m_id = "Masa Red Velvet"
            if m_id not in batidos_lote: batidos_lote[m_id] = []
            
            # Crear registro para el resumen
            it_cl = it.copy(); it_cl['cliente'] = orden['cliente']
            batidos_lote[m_id].append(it_cl)

            # -- LÓGICA COMPLEMENTOS (Sub-recetas) --
            # Aquí es donde desglosamos lo que lleva cada pan
            lista_extras = []
            cfg = DATABASE[it['fam']]
            if it['fam'] == "CONCHAS": lista_extras.append(cfg["complementos"][it['esp']][0] if isinstance(cfg["complementos"][it['esp']], list) else cfg["complementos"][it['esp']]) # Para conchas viejas
            # Actualizado para consistencia
            if it['fam'] == "CONCHAS": lista_extras = [f"Lágrima {it['esp']}"]
            if it['fam'] == "ROSCA DE REYES":
                espec_data = cfg["especialidades"][it['esp']]
                lista_extras.extend(espec_data)
                if it['rel'] != "Sin Relleno" and it['rel'] != "N/A": lista_extras.append(it['rel'])
            if it['fam'] == "BERLINAS":
                lista_extras.extend(cfg["especialidades"][it['esp']])
            if it['fam'] == "ROLLOS":
                lista_extras.extend(cfg["especialidades"][it['esp']])
            if it['fam'] == "PAN DE MUERTO":
                lista_extras.extend(cfg["especialidades"][it['esp']])

            for sid in lista_extras:
                # Definir peso del complemento
                p_unit = 15
                if "Lágrima" in sid and it['fam'] == "CONCHAS": p_unit = cfg["p_ex"][it['tam']]
                elif "Crema" in sid and it['fam'] == "ROSCAS": p_unit = cfg["p_relleno_map"][it['tam']]
                elif "Decoración Rosca" in sid: p_unit = 50 if it['tam'] == "Familiar" else 20
                
                complementos_lote[sid] = complementos_lote.get(sid, 0) + (p_unit * it['cant'])

    # --- RENDER: RESUMEN VISUAL ---
    with tab_sum:
        for mid, items in batidos_lote.items():
            m_dna = ING_RECETARIO[mid]
            m_sum = sum([(DATABASE[i['fam']]['tallas'][i['tam']] * i['cant']) for i in items])
            hb = (m_sum * 100) / sum([v for k,v in m_dna.items() if not k.startswith("_")])
            
            st.markdown(f"#### 🏷️ Lote de Masa: {mid} ({m_sum:,.1f}g)")
            ca, cb = st.columns([0.4, 0.6])
            with ca:
                for k,v in m_dna.items(): 
                    if not k.startswith("_"): gr = v*hb/100; st.write(f"- {k}: **{gr:,.1f}g**"); inv_compras[k] = inv_compras.get(k, 0) + gr
            with cb:
                for i in items: st.info(f"{i['cant']}x {i['esp']} — {i['cliente']} ({i['tam']})")

    # --- RENDER: PRODUCCIÓN ---
    with tab_pes:
        col_m, col_e = st.columns(2)
        with col_m:
            st.subheader("Masas")
            for mid, items in batidos_lote.items():
                m_dna = ING_RECETARIO[mid]
                m_pes = sum([(DATABASE[it['fam']]['tallas'][it['tam']]*it['cant']) for it in items])
                hb_p = (m_pes * 100) / sum([v for k,v in m_dna.items() if not k.startswith("_")])
                st.write(f"**Lote {mid} ({m_pes:,.0f}g)**")
                for k,v in m_dna.items():
                    if not k.startswith("_"): st.checkbox(f"{k}: {v*hb_p/100:,.1f}g", key=f"c_p_{mid}_{k}")
        with col_e:
            st.subheader("Rellenos y Lágrimas")
            for sid, ptot in complementos_lote.items():
                if sid not in ING_RECETARIO: 
                    st.write(f"• **{sid}:** {ptot} pzs/gr"); inv_compras[sid] = inv_compras.get(sid,0) + ptot; continue
                s_dna = ING_RECETARIO[sid]
                st.write(f"**{sid} ({ptot:,.0f}g)**")
                fs = ptot / sum(s_dna.values())
                for k,v in s_dna.items():
                    st.checkbox(f"{k}: {v*fs:,.1f}g", key=f"c_s_{sid}_{k}")
                    inv_compras[k] = inv_compras.get(k, 0) + (v*fs)

    # --- RENDER: SÚPER ---
    with tab_super:
        st.header("Surtido Completo (Consolidado)")
        for k, v in sorted(inv_compras.items()):
            if not k.startswith("_"): st.checkbox(f"{k}: **{v:,.1f}g**", key=f"fin_{k}")
