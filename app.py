import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0
if 'tema_oscuro' not in st.session_state: st.session_state.tema_oscuro = True

st.markdown(f"""
    <style>
    .stApp {{ background-color: {'#121212' if st.session_state.tema_oscuro else '#FFFFFF'}; color: {'#E0E0E0' if st.session_state.tema_oscuro else '#202020'}; }}
    .stCheckbox label {{ font-size: 1.1rem !important; }}
    .etapa-box {{ padding: 18px; border-radius: 12px; margin-bottom: 12px; border: 1px solid rgba(0,0,0,0.05); color: #1c1c1c !important; }}
    .etapa-titulo {{ font-weight: bold; text-transform: uppercase; font-size: 0.85rem; margin-bottom: 8px; color: rgba(0,0,0,0.7); }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS TÉCNICA (DNA + SOP)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "merma": 1.0, "factor_panadero": 1.963, "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(255, 235, 156, 0.7)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(168, 230, 173, 0.7)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.7)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.7)"}],
        "SOP": ["Autólisis 20 min.", "Incorporar levadura/vainilla.", "Azúcar en 3 tandas.", "Mantequilla en bloques."]
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1, "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(255, 235, 156, 0.7)"}, {"n": "2. Fermento", "i": ["Levadura fresca"], "c": "rgba(168, 230, 173, 0.7)"}, {"n": "3. Aromas", "i": ["Azúcar", "Miel", "Sal fina", "Agua Azahar"], "c": "rgba(162, 210, 255, 0.7)"}, {"n": "4. Grasa", "i": ["Mantequilla sin sal"], "c": "rgba(255, 179, 140, 0.7)"}],
        "SOP": ["TZ 1:1.", "Incorporar aromáticos al final.", "Bloque 12h."]
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10}
}

ARBOL = {
    "Conchas": {"espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]}, "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"},
    "Rosca de reyes": {"espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}}, "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa": "Masa Brioche Rosca"}
}

# ==========================================
# 2. INTERFAZ DE CAPTURA
# ==========================================

st.title("🥐 Comanda y Pedidos - CONCIENCIA")

with st.expander("📝 Registrar Nuevo Pedido de Cliente", expanded=not st.session_state.comanda):
    fk = st.session_state.form_key
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1: cliente = st.text_input("Nombre del Cliente", key=f"cli_{fk}")
    with col_c2: whatsapp = st.text_input("WhatsApp (ej: 52155...)", key=f"wa_{fk}")
    with col_c3: fecha = st.date_input("Fecha de Entrega", key=f"fecha_{fk}")

    st.divider()
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1: fam = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    
    if fam != "-":
        with col_p2: esp = st.selectbox("Especialidad", list(ARBOL[fam]["espec"].keys()), key=f"e_{fk}")
        with col_p3: tam = st.selectbox("Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{fk}")
        
        col_p4, col_p5 = st.columns(2)
        with col_p4:
            rel = "N/A"
            if fam == "Rosca de reyes":
                rel = st.selectbox("Relleno", ARBOL[fam]["espec"][esp]["rellenos"], key=f"r_{fk}")
        with col_p5:
            cant = st.number_input("Cantidad", min_value=1, value=1, key=f"c_{fk}")

        if st.button("✅ GUARDAR PEDIDO"):
            if cliente and whatsapp != "":
                st.session_state.comanda.append({
                    "cliente": cliente, "whatsapp": whatsapp, "fecha": str(fecha),
                    "fam": fam, "esp": esp, "tam": tam, "rel": rel, "cant": cant
                })
                st.session_state.form_key += 1
                st.rerun()
            else:
                st.error("Por favor llena el nombre y WhatsApp del cliente.")

# ==========================================
# 3. PESTAÑAS DE GESTIÓN
# ==========================================

if st.session_state.comanda:
    tab_res, tab_cli, tab_prod, tab_list = st.tabs(["📋 Resumen", "📞 Clientes", "🥣 Producción", "🛒 Súper"])

    # Cálculos iniciales
    lotes_masa = {}
    master_inv = {}
    
    for item in st.session_state.comanda:
        m_id = ARBOL[item['fam']]["masa"]
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    # --- PESTAÑA: RESUMEN VISUAL ---
    with tab_res:
        for m_id, items in lotes_masa.items():
            st.markdown(f"### 🛠️ Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch_gr = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_base = (m_batch_gr * 100) / sum(m_dna['receta'].values())
            
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info(f"**Masa ({m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100
                    st.write(f"• {ing}: {gr:,.1f}g")
                    master_inv[ing] = master_inv.get(ing, 0) + gr
            with c2:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']}) - {it['cliente']}**")
                    # Lógica de cálculo de extras aquí para el inventario...
                    subs = ARBOL[it['fam']]["espec"][it['esp']]
                    lista = subs["fijos"].copy() if isinstance(subs, dict) else subs.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: lista.append(it['rel'])
                    for s_id in lista:
                        p_u = ARBOL[it['fam']]["p_relleno_map"][it['tam']] if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (ARBOL[it['fam']]["p_ex"][it['tam']] if it['fam'] == "Conchas" else 15)
                        st.write(f"*{s_id} ({p_u * it['cant']:,.1f}g)*")
                        # Sumar al inventario maestro
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = (p_u * it['cant']) / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            master_inv[ing_s] = master_inv.get(ing_s, 0) + (val_s * fact)

    # --- PESTAÑA: GESTIÓN DE CLIENTES (WHATSAPP) ---
    with tab_cli:
        st.header("📞 Seguimiento de Pedidos")
        for i, item in enumerate(st.session_state.comanda):
            with st.container(border=True):
                col_i1, col_i2, col_i3 = st.columns([0.4, 0.3, 0.3])
                col_i1.write(f"👤 **{item['cliente']}**\n\n{item['cant']}x {item['esp']} ({item['tam']})")
                col_i2.write(f"📅 Entrega: {item['fecha']}")
                
                # Link de WhatsApp
                msg = f"¡Hola {item['cliente']}! Te saluda Panadería Conciencia 🥐. Tu pedido de {item['cant']} {item['esp']} ya está listo para entrega. ¡Te esperamos!"
                wa_url = f"https://wa.me/{item['whatsapp']}?text={urllib.parse.quote(msg)}"
                
                col_i3.link_button("🚀 Avisar por WhatsApp", wa_url)
                if col_i3.button("❌ Eliminar Pedido", key=f"del_{i}"):
                    st.session_state.comanda.pop(i)
                    st.rerun()

    # --- PESTAÑA: PRODUCCIÓN (ETAPAS) ---
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
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

    # --- PESTAÑA: LISTA MAESTRA ---
    with tab_list:
        st.header("🛒 Checklist de Almacén")
        for insumo, cant in sorted(master_inv.items()):
            st.checkbox(f"{insumo}: **{cant:,.1f}g**", key=f"m_{insumo}")

    if st.button("🗑️ BORRAR TODO EL DÍA"):
        st.session_state.comanda = []
        st.rerun()
