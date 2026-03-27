import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE TEMA Y ESTILOS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] 
if 'form_key' not in st.session_state: st.session_state.form_key = 0

colores = {
    "etapa1": "rgba(255, 235, 156, 0.7)", "etapa2": "rgba(168, 230, 173, 0.7)",
    "etapa3": "rgba(162, 210, 255, 0.7)", "etapa4": "rgba(255, 179, 140, 0.7)",
}

st.markdown(f"""
    <style>
    .stApp {{ background-color: {'#121212' if st.session_state.tema_oscuro else '#FFFFFF'}; color: {'#E0E0E0' if st.session_state.tema_oscuro else '#202020'}; }}
    .stCheckbox label {{ font-size: 1.1rem !important; color: inherit !important; }}
    .etapa-box {{ padding: 18px; border-radius: 12px; margin-bottom: 12px; border: 1px solid rgba(0,0,0,0.05); color: #1c1c1c !important; }}
    .etapa-titulo {{ font-weight: bold; text-transform: uppercase; font-size: 0.85rem; margin-bottom: 8px; color: rgba(0,0,0,0.7); }}
    </style>
""", unsafe_allow_html=True)

# BOTÓN SOL/LUNA
c_t1, c_t2 = st.columns([0.92, 0.08])
with c_t2:
    if st.button("🌙" if st.session_state.tema_oscuro else "☀️"):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# ==========================================
# 1. BASE DE DATOS TÉCNICA COMPLETA (AUDITADA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": colores["etapa2"]}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "etapas": [{"n": "1. Base y TZ", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Desarrollo", "i": ["Azúcar", "Levadura seca", "Sal fina"], "c": colores["etapa3"]}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5
    },
    "Masa Brioche Roles": {
        "receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17},
        "etapas": [{"n": "1. Hidratación", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Fermento", "i": ["Levadura fresca"], "c": colores["etapa2"]}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Grasas", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350
    },
    "Masa Red Velvet": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao en polvo": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3},
        "etapas": [{"n": "1. Líquidos", "i": ["Harina de fuerza", "Huevo", "Leche entera", "Colorante Rojo", "Vinagre"], "c": colores["etapa1"]}, {"n": "2. Secos", "i": ["Cacao en polvo", "Levadura instantánea"], "c": colores["etapa2"]}, {"n": "3. Dulzor", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "tz_ratio": 0.07, "tz_liq": 5
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Activación", "i": ["Levadura fresca"], "c": colores["etapa2"]}, {"n": "3. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": colores["etapa3"]}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1
    },
    "Masa Muerto Tradicional": {
        "receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3, "Agua Azahar": 2, "Ralladura Naranja": 1},
        "etapas": [{"n": "1. Mezcla", "i": ["Harina de fuerza", "Leche entera", "Yemas", "Claras"], "c": colores["etapa1"]}, {"n": "2. Fermento", "i": ["Levadura fresca"], "c": colores["etapa2"]}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Acabado", "i": ["Mantequilla sin sal", "Agua Azahar", "Ralladura Naranja"], "c": colores["etapa4"]}],
        "merma": 1.0
    },
    "Masa Muerto Guayaba": {
        "receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5},
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Leche entera", "Yemas", "Claras"], "c": colores["etapa1"]}, {"n": "2. Fruta", "i": ["Polvo de Guayaba", "Levadura fresca"], "c": colores["etapa2"]}, {"n": "3. Dulzor", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "huesos_refuerzo": True
    },
    "Mezcla de Brownies": {
        "receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa alcalinizada": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez Tostada": 140, "Sal escamas": 1.8},
        "etapas": [{"n": "1. Brown Butter", "i": ["Mantequilla sin sal"], "c": colores["etapa1"]}, {"n": "2. Emulsión", "i": ["Azúcar Blanca", "Azúcar Mascabada", "Chocolate Turin Amargo"], "c": colores["etapa2"]}, {"n": "3. Batido", "i": ["Claras", "Yemas", "Vainilla"], "c": colores["etapa3"]}, {"n": "4. Secos", "i": ["Harina de fuerza", "Cocoa alcalinizada", "Sal fina", "Nuez Tostada", "Sal escamas"], "c": colores["etapa4"]}],
        "merma": 1.0, "fijo": True
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Matcha": {"Harina de fuerza": 91.5, "Matcha en polvo": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik Fresa": 21, "Mantequilla sin sal": 100},
    "Lágrima de Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66},
    "Lágrima de Pinole": {"Harina de fuerza": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Galleta Oreo": 25},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Crema Pastelera Chocolate": {"Leche entera": 480, "Yemas": 100, "Azúcar": 100, "Fécula de Maíz": 45, "Chocolate 60%": 120, "Mantequilla sin sal": 30},
    "Crema Especial Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula de Maíz": 45, "Chocolate Turin": 120, "Mantequilla sin sal": 20},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema para batir 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula de Maíz": 24, "Mantequilla sin sal": 16, "Sal": 0.8},
    "Glaseado Ruby": {"Chocolate Ruby": 80, "Azúcar Glass": 160, "Leche entera": 50},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Turin Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1},
    "Decoración Tradicional Rosca": {"Ate de colores": 50, "Higo en almíbar": 20, "Cereza marrasquino": 10},
    "Decoración Nuez": {"Nuez Fileteada": 15},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Schmear Red Velvet": {"Mantequilla sin sal": 6, "Azúcar": 6, "Cacao": 1.8, "Nuez": 4, "Chocolate amargo": 4},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2, "Vainilla": 0.5},
    "Inclusión Manzana": {"Orejón de Manzana": 8, "Agua tibia": 2}
}

ARBOL = {
    "Conchas": {
        "espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"], "Matcha": ["Lágrima de Matcha"], "Fresa": ["Lágrima de Fresa"], "Mazapán": ["Lágrima de Mazapán"], "Oreo": ["Lágrima de Oreo"], "Pinole": ["Lágrima de Pinole"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"
    },
    "Berlinas": {
        "espec": {
            "Vainilla Clásica": ["Crema Pastelera Vainilla"], 
            "Ruby v2.0": ["Crema Ruby 50/50", "Glaseado Ruby"], 
            "Conejo Turín": ["Crema Especial Turin", "Glaseado Turin"]
        },
        "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas",
        "override_p": {"Ruby v2.0": (70, {"Crema Ruby 50/50": 40, "Glaseado Ruby": 8}), "Conejo Turín": (60, {"Crema Especial Turin": 80, "Glaseado Turin": 16})}
    },
    "Rollos": {
        "espec": {
            "Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"], 
            "Manzana": ["Schmear Canela", "Inclusión Manzana"], 
            "Conejo Turín": ["Schmear Canela", "Glaseado Turin"],
            "Red Velvet Premium": ["Schmear Red Velvet"]
        },
        "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "masa_ov": {"Red Velvet Premium": "Masa Red Velvet"}
    },
    "Rosca de reyes": {
        "espec": {
            "Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Tradicional Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate"]},
            "Chocolate": {"fijos": ["Lágrima de Chocolate", "Decoración Nuez"], "rellenos": ["Sin Relleno", "Crema Pastelera Chocolate"]},
            "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Especial Turin"]}
        },
        "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90},
        "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"
    },
    "Pan de muerto": {
        "espec": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto"]},
        "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}
    },
    "Brownies": {"espec": {"Chocolate Turín": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla de Brownies"}
}

# ==========================================
# 2. INTERFAZ DE CAPTURA (CARRITO)
# ==========================================

with st.expander("👤 1. Datos del Cliente", expanded=len(st.session_state.carrito_actual) == 0):
    fk_cli = st.session_state.form_key
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre Cliente", key=f"cn_{fk_cli}")
    cli_w = c2.text_input("WhatsApp (10 dígitos)", key=f"cw_{fk_cli}")

with st.container(border=True):
    st.subheader("🍞 2. Seleccionar Panes")
    fk = st.session_state.form_key
    col1, col2, col3, col4 = st.columns([2,2,1,1])
    
    fam_sel = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_sel_{fk}")
    if fam_sel != "-":
        esp_sel = col2.selectbox("Especialidad", list(ARBOL[fam_sel]["espec"].keys()), key=f"e_sel_{fk}")
        tam_sel = col3.selectbox("Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()), key=f"t_sel_{fk}")
        cant_sel = col4.number_input("Cant.", min_value=1, value=1, key=f"c_sel_{fk}")
        
        rel_sel = "N/A"
        if fam_sel == "Rosca de reyes":
            rel_sel = st.selectbox("Relleno", ARBOL[fam_sel]["espec"][esp_sel]["rellenos"], key=f"r_sel_{fk}")
        
        if st.button("➕ Añadir al Pedido"):
            st.session_state.carrito_actual.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rel": rel_sel, "cant": cant_sel})
            st.session_state.form_key += 1
            st.rerun()

if st.session_state.carrito_actual:
    st.info(f"🛒 **CARRITO: {cli_n}**")
    for p in st.session_state.carrito_actual:
        st.write(f"• {p['cant']}x {p['fam']} {p['esp']} ({p['tam']})")
    
    cb1, cb2 = st.columns(2)
    if cb1.button("✅ FINALIZAR Y GUARDAR TODO"):
        if cli_n and cli_w:
            st.session_state.comanda.append({"cliente": cli_n, "whatsapp": cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []
            st.session_state.form_key += 1
            st.rerun()
        else: st.error("Faltan datos del cliente")
    if cb2.button("❌ Borrar Carrito"): st.session_state.carrito_actual = []; st.rerun()

# ==========================================
# 3. LÓGICA DE PRODUCCIÓN Y CRM
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar todo"): st.session_state.comanda = []; st.rerun()
    tab_res, tab_cli, tab_prod, tab_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    master_inv = {}
    lotes_masa = {}

    for pedido in st.session_state.comanda:
        for item in pedido['items']:
            m_id = ARBOL[item['fam']].get("masa_ov", {}).get(item['esp'], ARBOL[item['fam']]['masa'])
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_con_cli = item.copy()
            it_con_cli['cliente'] = pedido['cliente']
            lotes_masa[m_id].append(it_con_cli)

    with tab_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            st.markdown(f"## 🛠️ Batido: {m_id}")
            
            m_batch_gr = 0
            for i in items:
                p_u_m = ARBOL[i['fam']].get("override_p", {}).get(i['esp'], (ARBOL[i['fam']]['tamaños'][i['tam']], 0))[0]
                m_batch_gr += (p_u_m * i['cant']) / m_dna['merma']
            
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            
            c_masa, c_comp = st.columns([0.3, 0.7])
            with c_masa:
                st.info(f"**Masa ({m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
                if "tz_ratio" in m_dna:
                    th = h_base*m_dna['tz_ratio']; master_inv["Harina de fuerza"] = master_inv.get("Harina de fuerza",0)+th; master_inv["Leche entera"] = master_inv.get("Leche entera",0)+th*m_dna['tz_liq']

            with c_comp:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']}) — {it['cliente']}**")
                    cfg = ARBOL[it['fam']]
                    base_espec = cfg["espec"][it['esp']]
                    lista = base_espec["fijos"].copy() if isinstance(base_espec, dict) else base_espec.copy()
                    if it.get('rel') not in ["N/A", "Sin Relleno", None]: lista.append(it['rel'])
                    
                    for s_id in lista:
                        if s_id not in DB_COMPLEMENTOS: continue
                        p_u = cfg["p_relleno_map"][it['tam']] if it['fam'] == "Rosca de reyes" and s_id == it.get('rel') else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']; st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            g_s = val_s * (it['cant'] if "Decoración" in s_id or "Rebozado" in s_id or "Cabeza" in ing_s else fact)
                            st.write(f"- {ing_s}: {g_s:,.1f}g"); master_inv[ing_s] = master_inv.get(ing_s, 0) + g_s

    with tab_cli:
        for i, ped in enumerate(st.session_state.comanda):
            with st.container(border=True):
                c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
                res_txt = ", ".join([f"{it['cant']} {it['esp']}" for it in ped['items']])
                c1.write(f"👤 **{ped['cliente']}**\n\n{res_txt}")
                url_b = f"https://wa.me/521{ped['whatsapp']}?text="
                c2.link_button("✅ Confirmar", url_b + urllib.parse.quote(f"¡Hola {ped['cliente']}! Recibimos tu pedido de ({res_txt}). Gracias!"))
                c3.link_button("🚀 Avisar Listo", url_b + urllib.parse.quote(f"¡Hola {ped['cliente']}! Tu pedido de ({res_txt}) ya está listo 🥐."))
                if st.button("❌ Borrar", key=f"final_del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    with tab_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']].get("override_p", {}).get(it['esp'], (ARBOL[it['fam']]['tamaños'][it['tam']], 0))[0] * it['cant']) / m_dna['merma'] for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna["etapas"]:
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_sup:
        st.header("📦 Surtido de Insumos")
        for insumo, cant in sorted(master_inv.items()):
            col1, col2 = st.columns([0.05, 0.95])
            if col1.checkbox("", key=f"master_{insumo}"): col2.markdown(f"~~{insumo}: {cant:,.1f}g~~")
            else: col2.write(f"{insumo}: {cant:,.1f}g")
