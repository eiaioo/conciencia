import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE TEMA Y ESTILOS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = []
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
# 1. BASE DE DATOS TÉCNICA (RESTAURADA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": colores["etapa2"]}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "SOP": ["Autólisis 20 min.", "Levadura/Vainilla.", "Azúcar 3 tandas.", "Mantequilla bloques."]
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "etapas": [{"n": "1. Base y TZ", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Desarrollo", "i": ["Azúcar", "Levadura seca", "Sal fina"], "c": colores["etapa3"]}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5, "SOP": ["TZ 1:5 frío.", "Gluten 70% antes de azúcar.", "Fritura 172°C."]
    },
    "Masa Brioche Roles": {
        "receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17},
        "etapas": [{"n": "1. Hidratación", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Fermento", "i": ["Levadura fresca"], "c": colores["etapa2"]}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Grasas", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350, "SOP": ["TZ 1:5 frío.", "DDT 24°C.", "Bloque 12h."]
    },
    "Masa Red Velvet": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao en polvo": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3},
        "etapas": [{"n": "1. Líquidos", "i": ["Harina de fuerza", "Huevo", "Leche entera", "Colorante Rojo", "Vinagre"], "c": colores["etapa1"]}, {"n": "2. Secos", "i": ["Cacao en polvo", "Levadura instantánea"], "c": colores["etapa2"]}, {"n": "3. Dulzor", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "tz_ratio": 0.07, "tz_liq": 5, "SOP": ["Colorante en líquidos.", "Cacao con harina."]
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Activación", "i": ["Levadura fresca"], "c": colores["etapa2"]}, {"n": "3. Sabor", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": colores["etapa3"]}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1, "SOP": ["TZ 1:1.", "Incorporar miel/azahar al final."]
    },
    "Masa Muerto Tradicional": {
        "receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3, "Agua Azahar": 2, "Ralladura Naranja": 1},
        "etapas": [{"n": "1. Mezcla", "i": ["Harina de fuerza", "Leche entera", "Yemas", "Claras"], "c": colores["etapa1"]}, {"n": "2. Fermento", "i": ["Levadura fresca"], "c": colores["etapa2"]}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Acabado", "i": ["Mantequilla sin sal", "Agua Azahar", "Ralladura Naranja"], "c": colores["etapa4"]}],
        "merma": 1.0, "SOP": ["Mantequilla 18-20°C.", "Sal al final."]
    },
    "Masa Muerto Guayaba": {
        "receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5},
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Leche entera", "Yemas", "Claras"], "c": colores["etapa1"]}, {"n": "2. Fruta", "i": ["Polvo de Guayaba", "Levadura fresca"], "c": colores["etapa2"]}, {"n": "3. Dulzor", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "huesos_refuerzo": True, "SOP": ["Guayaba post-hidratación base."]
    },
    "Mezcla de Brownies": {
        "receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa alcalinizada": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez Tostada": 140, "Sal escamas": 1.8},
        "etapas": [{"n": "1. Brown Butter", "i": ["Mantequilla sin sal"], "c": colores["etapa1"]}, {"n": "2. Emulsión", "i": ["Azúcar Blanca", "Azúcar Mascabada", "Chocolate Turin Amargo"], "c": colores["etapa2"]}, {"n": "3. Batido", "i": ["Claras", "Yemas", "Vainilla"], "c": colores["etapa3"]}, {"n": "4. Secos", "i": ["Harina de fuerza", "Cocoa alcalinizada", "Sal fina", "Nuez Tostada", "Sal escamas"], "c": colores["etapa4"]}],
        "merma": 1.0, "fijo": True, "SOP": ["Brown butter color avellana.", "No montar huevos."]
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Matcha": {"Harina de fuerza": 91.5, "Matcha en polvo": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik Fresa": 21, "Mantequilla sin sal": 100},
    "Lágrima de Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66},
    "Lágrima de Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Galleta Oreo": 25},
    "Lágrima de Pinole": {"Harina de fuerza": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Crema Pastelera Chocolate": {"Leche entera": 480, "Yemas": 100, "Azúcar": 100, "Fécula de Maíz": 45, "Chocolate 60%": 120, "Mantequilla sin sal": 30},
    "Crema Especial Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula de Maíz": 45, "Chocolate Turin": 120, "Mantequilla sin sal": 20},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema para batir 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula de Maíz": 24, "Mantequilla sin sal": 16, "Sal": 0.8},
    "Glaseado Ruby": {"Chocolate Ruby": 80, "Azúcar Glass": 160, "Leche entera": 50},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Turin Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1},
    "Decoración Tradicional Rosca": {"Ate de colores": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Schmear Red Velvet": {"Mantequilla sin sal": 6, "Azúcar": 6, "Cacao": 1.8, "Nuez": 4, "Chocolate amargo": 4},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2, "Vainilla": 0.5},
    "Inclusión Manzana": {"Orejón de Manzana": 8, "Agua tibia": 2},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {
        "espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"], "Matcha": ["Lágrima de Matcha"], "Fresa": ["Lágrima de Fresa"], "Mazapán": ["Lágrima de Mazapán"], "Oreo": ["Lágrima de Oreo"], "Pinole": ["Lágrima de Pinole"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"
    },
    "Berlinas": {
        "espec": {"Vainilla Clásica": ["Crema Pastelera Vainilla"], "Ruby v2.0": ["Crema Ruby 50/50", "Glaseado Ruby"], "Turín": ["Crema Especial Turin", "Glaseado Turin"]},
        "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas",
        "override_p": {"Ruby v2.0": (70, {"Crema Ruby 50/50": 40, "Glaseado Ruby": 8}), "Turín": (60, {"Crema Especial Turin": 80, "Glaseado Turin": 16}), "Vainilla Clásica": (60, {"Crema Pastelera Vainilla": 80})}
    },
    "Rollos": {
        "espec": {"Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"], "Manzana": ["Schmear Canela", "Inclusión Manzana"], "Red Velvet": ["Schmear Red Velvet"]},
        "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "masa_ov": {"Red Velvet": "Masa Red Velvet"}
    },
    "Rosca de reyes": {
        "espec": {
            "Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Tradicional Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate"]},
            "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Especial Turin"]}
        },
        "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90},
        "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"
    },
    "Pan de muerto": {
        "espec": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto"]},
        "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}
    },
    "Brownies": {"espec": {"Turín": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla de Brownies"}
}

# ==========================================
# 2. INTERFAZ (CRM)
# ==========================================

with st.expander("📝 Registrar Nuevo Pedido", expanded=not st.session_state.comanda):
    fk = st.session_state.form_key
    c1, c2, c3 = st.columns(3)
    cli_n = c1.text_input("Cliente", key=f"cn_{fk}")
    cli_w = c2.text_input("WhatsApp (10 dígitos)", key=f"cw_{fk}")
    fam = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    
    if fam != "-":
        c4, c5, c6 = st.columns(3)
        esp = c4.selectbox("Especialidad", list(ARBOL[fam]["espec"].keys()), key=f"e_{fk}")
        tam = c5.selectbox("Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{fk}")
        rel = "N/A"
        if fam == "Rosca de reyes":
            rel = c6.selectbox("Relleno", ARBOL[fam]["espec"][esp]["rellenos"], key=f"r_{fk}")
        cant = st.number_input("Cantidad", min_value=1, value=1, key=f"c_{fk}")
        if st.button("✅ GUARDAR PEDIDO"):
            st.session_state.comanda.append({"cli": cli_n if cli_n else "Venta General", "wa": cli_w, "fam": fam, "esp": esp, "tam": tam, "rel": rel, "cant": cant})
            st.session_state.form_key += 1; st.rerun()

# ==========================================
# 3. MOTOR DE CÁLCULO Y PESTAÑAS
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()
    
    tab_res, tab_cli, tab_prod, tab_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🥣 Producción", "🛒 Lista Maestra"])
    master_inv = {}
    lotes_masa = {}
    
    for it in st.session_state.comanda:
        m_id = ARBOL[it['fam']].get("masa_ov", {}).get(it['esp'], ARBOL[it['fam']]['masa'])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(it)

    with tab_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            st.markdown(f"### 🛠️ Batido: {m_id}")
            m_batch_gr = sum([(ARBOL[it['fam']].get("override_p", {}).get(it['esp'], (ARBOL[it['fam']]['tamaños'][it['tam']],0))[0] * it['cant']) / m_dna['merma'] for it in items])
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            
            c_masa, c_comps = st.columns([0.3, 0.7])
            with c_masa:
                st.info(f"**Masa ({m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
                if "tz_ratio" in m_dna:
                    th = h_base*m_dna['tz_ratio']; master_inv["Harina de fuerza"] = master_inv.get("Harina de fuerza",0)+th; master_inv["Leche entera"] = master_inv.get("Leche entera",0)+th*m_dna['tz_liq']
            with c_comps:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']}) - {it['cli']}**")
                    cfg = ARBOL[it['fam']]
                    list_subs = []
                    base_espec = cfg["espec"][it['esp']]
                    if isinstance(base_espec, dict): list_subs = base_espec["fijos"].copy()
                    else: list_subs = base_espec.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: list_subs.append(it['rel'])
                    
                    for s_id in list_subs:
                        p_u = cfg["p_relleno_map"][it['tam']] if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']; st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = {k: v for k, v in DB_COMPLEMENTOS[s_id].items() if k != "SOP"}
                        fact = p_tot / sum(s_rec.values())
                        for i_s, v_s in s_rec.items():
                            g_s = v_s * (it['cant'] if "Decoración" in s_id or "Rebozado" in s_id or "Cabeza" in i_s else fact)
                            st.write(f"- {i_s}: {g_s:,.1f}g"); master_inv[i_s] = master_inv.get(i_s, 0) + g_s

    with tab_cli:
        for i, it in enumerate(st.session_state.comanda):
            with st.container(border=True):
                col1, col2 = st.columns([0.7, 0.3])
                col1.write(f"👤 **{it['cli']}**\n\nPedido: {it['cant']}x {it['esp']} ({it['tam']})")
                if it['wa']:
                    msg = f"¡Hola {it['cli']}! 🥐 Tu pedido en Panadería Conciencia ya está listo."
                    url = f"https://wa.me/521{it['wa']}?text={urllib.parse.quote(msg)}"
                    col2.link_button("🚀 WhatsApp", url)
                if col2.button("❌ Borrar", key=f"del_{i}"):
                    st.session_state.comanda.pop(i); st.rerun()

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
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_sup:
        st.header("📦 Surtido de Insumos")
        for insumo, cant in sorted(master_inv.items()):
            col1, col2 = st.columns([0.05, 0.95])
            if col1.checkbox("", key=f"m_{insumo}"): col2.markdown(f"~~{insumo}: {cant:,.1f}g~~")
            else: col2.write(f"{insumo}: {cant:,.1f}g")
