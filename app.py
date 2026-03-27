import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN DE TEMA Y ESTILOS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True
if 'comanda' not in st.session_state: st.session_state.comanda = [] # Pedidos finales
if 'carrito_actual' not in st.session_state: st.session_state.carrito_actual = [] # Lo que se está armando
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
# 1. BASE DE DATOS TÉCNICA COMPLETA
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
    "Mezcla de Brownies": {
        "receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa alcalinizada": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez Tostada": 140, "Sal escamas": 1.8},
        "merma": 1.0, "fijo": True
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2, "Vainilla": 0.5},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"},
    "Berlinas": {"espec": {"Vainilla": ["Crema Pastelera Vainilla"]}, "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas"},
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15},
    "Pan de muerto": {"espec": {"Tradicional": ["Rebozado Muerto"]}, "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1},
    "Brownies": {"espec": {"Turín": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla de Brownies"}
}

# ==========================================
# 2. INTERFAZ DE CAPTURA MULTI-PRODUCTO
# ==========================================

st.title("🥐 Gestión de Pedidos - CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=len(st.session_state.carrito_actual) == 0):
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre", key="cli_name")
    cli_w = c2.text_input("WhatsApp (10 dígitos)", key="cli_wa")

with st.container(border=True):
    st.subheader("🍞 2. Agregar Panes al Carrito")
    fk = st.session_state.form_key
    col1, col2, col3, col4 = st.columns([2,2,1,1])
    
    fam_sel = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"fam_{fk}")
    if fam_sel != "-":
        esp_sel = col2.selectbox("Especialidad", list(ARBOL[fam_sel]["espec"].keys()), key=f"esp_{fk}")
        tam_sel = col3.selectbox("Tamaño", list(ARBOL[fam_sel]["tamaños"].keys()), key=f"tam_{fk}")
        cant_sel = col4.number_input("Cant.", min_value=1, value=1, key=f"cant_{fk}")
        
        rel_sel = "N/A"
        if fam_sel == "Rosca de reyes":
            rel_sel = st.selectbox("Relleno", ARBOL[fam_sel]["espec"][esp_sel]["rellenos"], key=f"rel_{fk}")
        
        if st.button("➕ Añadir a la lista de " + (cli_n if cli_n else "este cliente")):
            st.session_state.carrito_actual.append({
                "fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "rel": rel_sel, "cant": cant_sel
            })
            st.session_state.form_key += 1
            st.rerun()

# MOSTRAR CARRITO ACTUAL
if st.session_state.carrito_actual:
    st.info(f"🛒 **Pedido actual para {cli_n}:**")
    for i, p in enumerate(st.session_state.carrito_actual):
        st.write(f"- {p['cant']}x {p['fam']} {p['esp']} ({p['tam']})")
    
    c_btn1, c_btn2 = st.columns(2)
    if c_btn1.button("✅ FINALIZAR Y GUARDAR PEDIDO"):
        if cli_n and cli_w:
            # Guardamos todo el grupo como una lista de items bajo el mismo cliente
            st.session_state.comanda.append({
                "cliente": cli_n, "whatsapp": cli_w, "items": st.session_state.carrito_actual.copy()
            })
            st.session_state.carrito_actual = [] # Limpiar carrito
            st.success("Pedido guardado con éxito.")
            st.rerun()
        else: st.error("Faltan datos del cliente")
    if c_btn2.button("❌ Cancelar Carrito"):
        st.session_state.carrito_actual = []
        st.rerun()

# ==========================================
# 3. LÓGICA DE PRODUCCIÓN Y CRM
# ==========================================

if st.session_state.comanda:
    st.divider()
    tab_res, tab_cli, tab_prod, tab_sup = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])
    master_inv = {}
    lotes_masa = {}

    # Desglosar los items de todos los pedidos para la lógica de producción
    for pedido in st.session_state.comanda:
        for item in pedido['items']:
            m_id = ARBOL[item['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            # Inyectamos el nombre del cliente en el item para el resumen
            item_con_cli = item.copy()
            item_con_cli['cli'] = pedido['cliente']
            lotes_masa[m_id].append(item_con_cli)

    with tab_res:
        for m_id, items in lotes_masa.items():
            st.markdown(f"## 🛠️ Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            # Sumar pesos de masa
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_base = (m_batch_gr * 100) / sum(m_dna['receta'].values())
            
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info(f"**Masa ({m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
            with c2:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']}) - {it['cli']}**")
                    cfg = ARBOL[it['fam']]
                    # Obtener subrecetas
                    lista_subs = cfg["espec"][it['esp']]
                    if isinstance(lista_subs, dict): lista_subs = lista_subs["fijos"].copy()
                    else: lista_subs = lista_subs.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: lista_subs.append(it['rel'])
                    
                    for s_id in lista_subs:
                        p_u = cfg["p_relleno_map"][it['tam']] if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']; st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            gr_s = val_s * (it['cant'] if "Decoración" in s_id or "Rebozado" in s_id else fact)
                            st.write(f"- {ing_s}: {gr_s:,.1f}g"); master_inv[ing_s] = master_inv.get(ing_s, 0) + gr_s

    with tab_cli:
        for i, pedido in enumerate(st.session_state.comanda):
            with st.container(border=True):
                col1, col2 = st.columns([0.7, 0.3])
                resumen_txt = ", ".join([f"{it['cant']} {it['esp']}" for it in pedido['items']])
                col1.write(f"👤 **{pedido['cliente']}**\n\nLleva: {resumen_txt}")
                msg = f"¡Hola {pedido['cliente']}! 🥐 Tu pedido de ({resumen_txt}) en Panadería Conciencia ya está listo."
                url = f"https://wa.me/521{pedido['whatsapp']}?text={urllib.parse.quote(msg)}"
                col2.link_button("🚀 WhatsApp Business", url)
                if col2.button("❌ Eliminar", key=f"final_del_{i}"):
                    st.session_state.comanda.pop(i); st.rerun()

    with tab_prod:
        for m_id, items in lotes_masa.items():
            st.header(f"🥣 Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna["etapas"]:
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_sup:
        st.header("🛒 Lista Maestra de Surtido")
        for insumo, cant in sorted(master_inv.items()):
            col1, col2 = st.columns([0.05, 0.95])
            if col1.checkbox("", key=f"master_{insumo}"): col2.markdown(f"~~{insumo}: {cant:,.1f}g~~")
            else: col2.write(f"{insumo}: {cant:,.1f}g")

    if st.button("🗑️ BORRAR TODA LA PRODUCCIÓN"):
        st.session_state.comanda = []; st.rerun()
