import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN Y CONFIGURACIÓN VISUAL
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'f_key' not in st.session_state: st.session_state.f_key = 0
if 'cli_n' not in st.session_state: st.session_state.cli_n = ""
if 'cli_w' not in st.session_state: st.session_state.cli_w = ""

# Estilo Claro de Alto Contraste (Cero errores de visibilidad)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3, h4, p, span, label { color: #000000 !important; font-weight: 600; }
    div[data-testid="stExpander"] { border: 1px solid #DDDDDD !important; border-radius: 10px; background-color: #F9F9F9; }
    [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 1px solid #DDDDDD; }
    .etapa-box { padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #DDD; color: #000 !important; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS TÉCNICA (DNA COMPLETO)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "#FFF9C4"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "#C8E6C9"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "#BBDEFB"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "#FFE0B2"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "#FFF9C4"}, {"n": "2. Sabor y Fermento", "i": ["Azúcar", "Miel", "Agua Azahar", "Sal fina", "Levadura fresca"], "c": "#BBDEFB"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "#FFE0B2"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Batch Berlinas", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera"], "c": "#BBDEFB"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_f": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal", "Levadura fresca"], "c": "#C8E6C9"}]},
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "#FFF9C4"},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "c": "#E1BEE7"},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "c": "#FFF9C4"},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24, "c": "#F8BBD0"},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25, "c": "#D7CCC8"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "c": "#C8E6C9"}
}

ARBOL = {
    "Conchas": {"espec": ["Vainilla", "Chocolate"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa_id": "Masa de Conchas"},
    "Rosca de reyes": {"espec": ["Tradicional", "Turín"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "masa_id": "Masa Brioche Rosca"},
    "Berlinas": {"espec": ["Vainilla Clásica", "Ruby v2.0"], "tam": {"Estándar": 60}, "masa_id": "Masa de Berlinas", "p_man": {"Ruby v2.0": 70}},
    "Rollos": {"espec": ["Canela Tradicional"], "tam": {"Individual": 90}, "masa_id": "Masa Brioche Roles"}
}

# ==========================================
# 3. INTERFAZ DE CAPTURA
# ==========================================
with st.sidebar:
    st.title("👨‍🍳 MENÚ")
    pagina = st.radio("Ir a:", ["📋 Resumen Visual", "🥣 Producción", "📞 Clientes & WhatsApp", "🛒 Súper (Lista Maestra)"])
    st.divider()
    if st.button("🗑️ Limpiar Todo el Día"):
        st.session_state.comanda = []; st.session_state.carrito = []; st.rerun()

st.title("🥐 Producción CONCIENCIA")

with st.expander("📝 1. Capturar Pedido", expanded=not st.session_state.comanda):
    c1, c2 = st.columns(2)
    st.session_state.cli_n = c1.text_input("Nombre Cliente", value=st.session_state.cli_n)
    st.session_state.cli_w = c2.text_input("WhatsApp", value=st.session_state.cli_w)
    
    st.write("---")
    fk = st.session_state.f_key
    col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1])
    
    f_sel = col1.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if f_sel != "-":
        e_sel = col2.selectbox("Especialidad", ARBOL[f_sel]["espec"], key=f"e_{fk}")
        t_sel = col3.selectbox("Tamaño", list(ARBOL[f_sel]["tam"].keys()), key=f"t_{fk}")
        c_sel = col4.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
        rel_sel = "N/A"
        if f_sel == "Rosca de reyes": rel_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Pastelera Vainilla"], key=f"r_{fk}")
        
        if st.button("➕ AÑADIR AL CARRITO"):
            st.session_state.carrito.append({"familia": f_sel, "especialidad": e_sel, "tamano": t_sel, "cantidad": c_sel, "relleno": rel_sel})
            st.session_state.f_key += 1
            st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {st.session_state.cli_n}")
    for it in st.session_state.carrito: st.write(f"- {it['cantidad']}x {it['especialidad']} ({it['tamano']})")
    if st.button("✅ GUARDAR PEDIDO COMPLETO"):
        if st.session_state.cli_n:
            st.session_state.comanda.append({"cliente": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()

# ==========================================
# 4. EL CEREBRO (PROCESAMIENTO GLOBAL)
# ==========================================
master_inv = {}
lotes_masa = {}
lotes_complementos = {}

if st.session_state.comanda:
    for pedido in st.session_state.comanda:
        for it in pedido['items']:
            # 1. Agrupar Masas
            masa_id = ARBOL[it['familia']]["masa_id"]
            if masa_id not in lotes_masa: lotes_masa[masa_id] = []
            item_con_cliente = it.copy()
            item_con_cliente['cli'] = pedido['cliente']
            lotes_masa[masa_id].append(item_con_cliente)
            
            # 2. Identificar y Escalar Complementos
            subs = []
            if it['familia'] == "Conchas": subs.append(f"Lágrima {it['especialidad']}")
            if it['familia'] == "Rosca de reyes": 
                subs.append("Decoración Rosca")
                if it['relleno'] != "Sin Relleno": subs.append(it['relleno'].replace("Crema Pastelera ", "Crema "))
            if it['familia'] == "Rollos": subs.append("Schmear Canela")
            if it['familia'] == "Berlinas" and it['especialidad'] == "Ruby v2.0": subs.append("Crema Ruby")

            for s_id in subs:
                if s_id in DB_COMPLEMENTOS:
                    # Peso unitario según tabla de ingeniería
                    p_u = ARBOL[it['familia']].get("p_rell_map", {}).get(it['tamano'], 15) if "Crema" in s_id else (ARBOL[it['familia']].get("p_ex", {}).get(it['tamano'], 15) if "Lágrima" in s_id else 15)
                    lotes_complementos[s_id] = lotes_complementos.get(s_id, 0) + (p_u * it['cantidad'])

    # --- PÁGINA: RESUMEN ---
    if pagina == "📋 Resumen Visual":
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            # Peso total del batido
            batch_gr = sum([(ARBOL[i['familia']].get("p_man", {}).get(i['especialidad'], ARBOL[i['familia']]['tam'][i['tamano']]) * i['cantidad']) / m_dna['merma'] for i in items])
            h_base = (batch_gr * 100) / sum(m_dna['receta'].values())
            
            st.markdown(f"### 🛠️ Lote: {m_id} ({batch_gr:,.1f}g)")
            c_masa, c_cli = st.columns([0.3, 0.7])
            with c_masa:
                st.info("Masa Principal")
                for k, v in m_dna['receta'].items():
                    gr = v*h_base/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c_cli:
                for it in items: st.success(f"{it['cantidad']}x {it['especialidad']} ({it['tamano']}) — {it['cli']}")

    # --- PÁGINA: CLIENTES ---
    elif pagina == "📞 Clientes & WhatsApp":
        for i, p in enumerate(st.session_state.comanda):
            with st.container(border=True):
                c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
                res_lista = "\n".join([f"• {it['cantidad']}x {it['especialidad']} ({it['tamano']})" for it in p['items']])
                c1.write(f"👤 **{p['cliente']}**")
                c1.caption(res_lista)
                u = f"https://wa.me/521{p['wa']}?text=" + urllib.parse.quote(f"Hola {p['cliente']}! Tu pedido está listo:\n{res_lista}")
                c2.link_button("✅ Confirmar", f"https://wa.me/521{p['wa']}?text=Recibido!")
                c3.link_button("🚀 Listo", u)
                if st.button("❌ Borrar", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    # --- PÁGINA: PRODUCCIÓN ---
    elif pagina == "🥣 Producción":
        col_m, col_s = st.columns(2)
        with col_m:
            st.subheader("🥣 Batidos")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(ARBOL[it['familia']]['tam'][it['tamano']] * it['cantidad']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.write(f"**{m_id}**")
                for etapa in m_dna["etapas"]:
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><b>{etapa["n"]}</b>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        gr = m_dna['receta'][ing]*h_b/100
                        st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                        master_inv[ing] = master_inv.get(ing, 0) + gr
                    st.markdown('</div>', unsafe_allow_html=True)
        with col_s:
            st.subheader("✨ Complementos")
            for s_id, p_tot in lotes_complementos.items():
                s_rec = DB_COMPLEMENTOS[s_id]
                st.write(f"**{s_id} ({p_tot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {s_rec["c"]};">', unsafe_allow_html=True)
                fact = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
                for sk, sv in s_rec.items():
                    if sk == "c": continue
                    st.checkbox(f"{sk}: {(sv*fact):,.1f}g", key=f"sec_{s_id}_{sk}")
                    master_inv[sk] = master_inv.get(sk, 0) + sv*fact
                st.markdown('</div>', unsafe_allow_html=True)

    # --- PÁGINA: SÚPER ---
    elif pagina == "🛒 Súper (Lista Maestra)":
        st.header("🛒 Lista Maestra de Surtido")
        # Forzar re-cálculo masivo para el súper
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]; h_b = (sum([(ARBOL[it['familia']]['tam'][it['tamano']] * it['cantidad']) for it in items]) * 100) / sum(m_dna['receta'].values())
            for k, v in m_dna['receta'].items(): master_inv[k] = master_inv.get(k, 0) + (v*h_b/100)

        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"sup_{k}")
