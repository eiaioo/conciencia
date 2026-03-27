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
# 1. BASE DE DATOS TÉCNICA (DNA + SOP)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": colores["etapa2"]}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "factor": 1.963
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
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Fermentación", "i": ["Levadura fresca"], "c": colores["etapa2"]}, {"n": "3. Aromas", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": colores["etapa3"]}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1
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
    "Rollos": {"espec": {"Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"]}, "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15}
}

# ==========================================
# 2. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda Técnica y CRM - CONCIENCIA")

with st.expander("👤 1. Datos del Cliente", expanded=len(st.session_state.carrito_actual) == 0):
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre del Cliente", key="cli_name")
    cli_w = c2.text_input("WhatsApp (10 dígitos)", key="cli_wa")

with st.container(border=True):
    st.subheader("🍞 2. Agregar Productos")
    fk = st.session_state.form_key
    col1, col2, col3, col4 = st.columns([2,2,1,1])
    
    f_sel = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if f_sel != "-":
        e_sel = col2.selectbox("Especialidad", list(ARBOL[f_sel]["espec"].keys()), key=f"e_{fk}")
        t_sel = col3.selectbox("Tamaño", list(ARBOL[f_sel]["tamaños"].keys()), key=f"t_{fk}")
        c_sel = col4.number_input("Cant.", min_value=1, value=1, key=f"c_{fk}")
        
        r_sel = "N/A"
        if f_sel == "Rosca de reyes":
            r_sel = st.selectbox("Relleno", ARBOL[f_sel]["espec"][e_sel]["rellenos"], key=f"r_{fk}")
        
        if st.button("➕ Añadir al Carrito"):
            st.session_state.carrito_actual.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "rel": r_sel, "cant": c_sel})
            st.session_state.form_key += 1
            st.rerun()

if st.session_state.carrito_actual:
    st.info(f"🛒 **Carrito para {cli_n}:**")
    for p in st.session_state.carrito_actual:
        st.write(f"- {p['cant']}x {p['fam']} {p['esp']} ({p['tam']})")
    
    cb1, cb2 = st.columns(2)
    if cb1.button("✅ FINALIZAR PEDIDO"):
        if cli_n and cli_w:
            st.session_state.comanda.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito_actual.copy()})
            st.session_state.carrito_actual = []
            st.rerun()
        else: st.error("Faltan datos del cliente")
    if cb2.button("❌ Cancelar"): st.session_state.carrito_actual = []; st.rerun()

# ==========================================
# 3. GESTIÓN Y PRODUCCIÓN
# ==========================================

if st.session_state.comanda:
    st.divider()
    tab_res, tab_cli, tab_prod, tab_sup = st.tabs(["📋 Resumen", "📞 Clientes & WhatsApp", "🥣 Producción", "🛒 Súper"])
    master_inv = {}
    lotes_masa = {}

    for pedido in st.session_state.comanda:
        for item in pedido['items']:
            m_id = ARBOL[item['fam']]["masa"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = item.copy(); it_c['cli'] = pedido['cliente']
            lotes_masa[m_id].append(it_c)

    # --- TAB: CLIENTES (CON DOBLE BOTÓN) ---
    with tab_cli:
        st.header("📞 Gestión de Notificaciones")
        for i, pedido in enumerate(st.session_state.comanda):
            with st.container(border=True):
                c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
                res_txt = ", ".join([f"{it['cant']} {it['esp']}" for it in pedido['items']])
                c1.write(f"👤 **{pedido['cliente']}**\n\n{res_txt}")
                
                # Mensaje 1: Confirmación
                msg_conf = f"¡Hola {pedido['cliente']}! Te saluda Panadería Conciencia 🥐. Confirmamos tu pedido de: ({res_txt}). ¡Muchas gracias!"
                url_conf = f"https://wa.me/521{pedido['wa']}?text={urllib.parse.quote(msg_conf)}"
                c2.link_button("✅ Confirmar Pedido", url_conf, use_container_width=True)
                
                # Mensaje 2: Listo
                msg_ready = f"¡Hola {pedido['cliente']}! 🥐 Tu pedido de: ({res_txt}) ya está listo para entrega en Panadería Conciencia. ¡Te esperamos!"
                url_ready = f"https://wa.me/521{pedido['wa']}?text={urllib.parse.quote(msg_ready)}"
                c3.link_button("🚀 Avisar: ¡LISTO!", url_ready, use_container_width=True)
                
                if st.button(f"🗑️ Eliminar Pedido", key=f"del_{i}"):
                    st.session_state.comanda.pop(i); st.rerun()

    # --- TAB: RESUMEN VISUAL ---
    with tab_res:
        for m_id, items in lotes_masa.items():
            st.markdown(f"### 🛠️ Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_base = (m_batch_gr * 100) / sum(m_dna['receta'].values())
            col_m, col_c = st.columns([0.3, 0.7])
            with col_m:
                st.info(f"**Masa ({m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100; st.write(f"• {ing}: {gr:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr
            with col_c:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']}) - {it['cli']}**")
                    cfg = ARBOL[it['fam']]
                    subs = cfg["espec"][it['esp']]
                    lista = subs["fijos"].copy() if isinstance(subs, dict) else subs.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: lista.append(it['rel'])
                    for s_id in lista:
                        p_u = cfg["p_relleno_map"][it['tam']] if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg.get("p_ex", {}).get(it['tam'], 15) if isinstance(cfg.get("p_ex"), dict) else cfg.get("p_ex", 15))
                        p_tot = p_u * it['cant']; st.markdown(f"**{s_id} ({p_tot:,.1f}g)**")
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values()); 
                        for i_s, v_s in s_rec.items():
                            g_s = v_s * (it['cant'] if "Decoración" in s_id or "Rebozado" in s_id else fact)
                            st.write(f"- {i_s}: {g_s:,.1f}g"); master_inv[i_s] = master_inv.get(i_s, 0) + g_s

    # --- TAB: PRODUCCIÓN (ETAPAS) ---
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

    # --- TAB: SÚPER ---
    with tab_sup:
        st.header("🛒 Checklist de Almacén")
        for insumo, cant in sorted(master_inv.items()):
            st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"master_{insumo}")

    if st.button("🗑️ BORRAR TODA LA PRODUCCIÓN"): st.session_state.comanda = []; st.rerun()
