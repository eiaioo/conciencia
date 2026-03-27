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

# Paleta de colores suaves (70% opacidad)
colores = {
    "etapa1": "rgba(255, 235, 156, 0.7)", # Amarillo
    "etapa2": "rgba(168, 230, 173, 0.7)", # Verde
    "etapa3": "rgba(162, 210, 255, 0.7)", # Azul
    "etapa4": "rgba(255, 179, 140, 0.7)", # Naranja
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
# 1. BASE DE DATOS TÉCNICA
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": colores["etapa1"]}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": colores["etapa2"]}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": colores["etapa3"]}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": colores["etapa4"]}],
        "merma": 1.0, "factor": 1.963
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
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10}
}

ARBOL = {
    "Conchas": {
        "espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"
    },
    "Rosca de reyes": {
        "espec": {"Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla"]}},
        "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120},
        "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35}, "masa": "Masa Brioche Rosca"
    }
}

# ==========================================
# 2. CAPTURA DE PEDIDOS (CRM)
# ==========================================

with st.expander("📝 Registrar Pedido", expanded=not st.session_state.comanda):
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
            st.session_state.comanda.append({
                "cli": cli_n if cli_n else "Venta General",
                "wa": cli_w,
                "fam": fam, "esp": esp, "tam": tam, "rel": rel, "cant": cant
            })
            st.session_state.form_key += 1
            st.rerun()

# ==========================================
# 3. PESTAÑAS DE TRABAJO
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar todo"): st.session_state.comanda = []; st.rerun()
    
    tab_res, tab_cli, tab_prod, tab_sup = st.tabs(["📋 Resumen Visual", "📞 Clientes", "🥣 Producción", "🛒 Lista Maestra"])
    master_inv = {}

    lotes_masa = {}
    for it in st.session_state.comanda:
        m_id = ARBOL[it['fam']]["masa"]
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(it)

    with tab_res:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch_gr = sum([(ARBOL[i['fam']]['tamaños'][i['tam']] * i['cant']) / m_dna['merma'] for i in items])
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            
            st.markdown(f"## 🛠️ Batido: {m_id}")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info(f"**Masa (Total: {m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    gr = porc*h_base/100
                    st.write(f"• {ing}: {gr:,.1f}g")
                    master_inv[ing] = master_inv.get(ing, 0) + gr
            with c2:
                for it in items:
                    st.success(f"**{it['cant']}x {it['esp']} ({it['tam']}) - {it['cli']}**")
                    cfg = ARBOL[it['fam']]
                    # Listar sub-recetas
                    lista_subs = cfg["espec"][it['esp']]
                    if isinstance(lista_subs, dict): lista_subs = lista_subs["fijos"].copy()
                    else: lista_subs = lista_subs.copy()
                    if it.get('rel') not in ["N/A", "Sin Relleno", None]: lista_subs.append(it['rel'])
                    
                    for s_id in lista_subs:
                        p_u = cfg["p_relleno_map"][it['tam']] if it['fam'] == "Rosca de reyes" and s_id == it['rel'] else (cfg["p_ex"][it['tam']] if it['fam'] == "Conchas" else 15)
                        p_tot = p_u * it['cant']
                        st.markdown(f"**{s_id} (Total: {p_tot:,.1f}g)**")
                        # Desglose de ingredientes del extra
                        s_rec = DB_COMPLEMENTOS[s_id]
                        fact = p_tot / sum(s_rec.values())
                        for ing_s, val_s in s_rec.items():
                            gr_s = val_s * (it['cant'] if "Decoración" in s_id or "Rebozado" in s_id else fact)
                            st.write(f"- {ing_s}: {gr_s:,.1f}g")
                            master_inv[ing_s] = master_inv.get(ing_s, 0) + gr_s

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
            m_batch = sum([(ARBOL[it['fam']]['tamaños'][it['tam']] * it['cant']) / m_dna['merma'] for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for etapa in m_dna["etapas"]:
                st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                for ing in etapa['i']:
                    gr = m_dna['receta'][ing]*h_b/100
                    st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{etapa['n']}_{ing}_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_sup:
        st.header("📦 Surtido de Insumos")
        for insumo, cant in sorted(master_inv.items()):
            col1, col2 = st.columns([0.05, 0.95])
            if col1.checkbox("", key=f"m_{insumo}"):
                col2.markdown(f"~~{insumo}: {cant:,.1f}g~~")
            else: col2.write(f"{insumo}: {cant:,.1f}g")
