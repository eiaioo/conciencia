import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="CONCIENCIA - Maestro", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] 
if 'carrito' not in st.session_state: st.session_state.carrito = [] 
if 'f_key' not in st.session_state: st.session_state.f_key = 0

C_BG = "#0E1117" if st.session_state.tema == "Oscuro" else "#F0F2F6"
C_SEC = "#161B22" if st.session_state.tema == "Oscuro" else "#FFFFFF"
C_TXT = "#E6EDF3" if st.session_state.tema == "Oscuro" else "#1F2328"
C_BRD = "#30363D" if st.session_state.tema == "Oscuro" else "#D0D7DE"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, span, label {{ color: {C_TXT} !important; }}
    div[data-testid="stExpander"], .streamlit-expanderHeader {{ background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{ background-color: {C_BG} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important; }}
    .etapa-box {{ padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); color: #1a1a1a !important; font-weight: 500; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS TÉCNICA COMPLETA
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "rgba(183, 183, 164, 0.3)"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "rgba(162, 210, 255, 0.3)"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "rgba(212, 163, 115, 0.3)"}, {"n": "2. Sabor", "i": ["Azúcar", "Miel", "Agua Azahar", "Levadura fresca"], "c": "rgba(165, 165, 141, 0.3)"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal", "Sal fina"], "c": "rgba(107, 112, 92, 0.3)"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Batch Berlinas", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera", "Sal fina", "Levadura seca"], "c": "rgba(162, 210, 255, 0.3)"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_f": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal", "Sal fina", "Levadura fresca"], "c": "rgba(168, 230, 173, 0.3)"}]},
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "c": "rgba(255, 235, 156, 0.3)"},
    "Lágrima Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100, "c": "rgba(162, 210, 255, 0.3)"},
    "Lágrima Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100, "c": "rgba(168, 230, 173, 0.3)"},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "c": "rgba(255, 179, 140, 0.3)"},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar Mascabada": 300, "Canela": 25, "c": "rgba(183, 183, 164, 0.3)"},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "c": "rgba(212, 163, 115, 0.3)"}
}

ARBOL = {
    "Conchas": {"espec": ["Vainilla", "Chocolate", "Matcha"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas"},
    "Rosca de reyes": {"espec": ["Tradicional"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120}, "p_rel_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35}, "m": "Masa Brioche Rosca"},
    "Berlinas": {"espec": ["Vainilla Clásica"], "tam": {"Estándar": 60}, "m": "Masa de Berlinas"},
    "Rollos": {"espec": ["Tradicional"], "tam": {"Individual": 90}, "m": "Masa Brioche Roles"}
}

# ==========================================
# 3. INTERFAZ DE NAVEGACIÓN (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("🥐 Menú Maestro")
    pagina = st.radio("Ir a:", ["📋 Resumen Visual", "🥣 Producción", "📞 Clientes & WhatsApp", "🛒 Súper (Lista Maestra)"])
    st.divider()
    if st.button("☀️/🌙 Cambiar Tema"):
        st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
        st.rerun()
    if st.button("🗑️ Limpiar Todo"):
        st.session_state.comanda = []
        st.rerun()

# ==========================================
# 4. CAPTURA DE PEDIDOS
# ==========================================
st.title(f"CONCIENCIA - {pagina}")

with st.expander("📝 1. Iniciar Nuevo Pedido", expanded=not st.session_state.comanda):
    c1, c2 = st.columns(2)
    cli_n = c1.text_input("Nombre Cliente", key="cli_n_val")
    cli_w = c2.text_input("WhatsApp (10 dígitos)", key="cli_w_val")
    st.write("---")
    fk = st.session_state.f_key
    c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1, 0.8])
    f_sel = c3.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if f_sel != "-":
        e_sel = c4.selectbox("Especialidad", ARBOL[f_sel]["espec"], key=f"e_{fk}")
        t_sel = c5.selectbox("Tamaño", list(ARBOL[f_sel]["tam"].keys()), key=f"t_{fk}")
        c_sel = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
        rel_sel = "N/A"
        if f_sel == "Rosca de reyes":
            rel_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Vainilla"], key=f"r_{fk}")
        if c7.button("➕"):
            st.session_state.carrito.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "can": c_sel, "rel": rel_sel})
            st.session_state.f_key += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {cli_n}")
    if st.button("✅ FINALIZAR PEDIDO"):
        if cli_n:
            st.session_state.comanda.append({"cli": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
            st.session_state.carrito = []; st.rerun()

# ==========================================
# 5. MOTOR DE CÁLCULO UNIVERSAL (SOLUCIÓN SÚPER)
# ==========================================
master_inv = {}
lotes_masa = {}
lotes_comp = {}

if st.session_state.comanda:
    for ped in st.session_state.comanda:
        for it in ped['items']:
            # Agrupar Masas
            m_id = ARBOL[it['fam']]["m"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_c = it.copy(); it_c['cliente'] = ped['cli']; lotes_masa[m_id].append(it_c)
            
            # Agrupar Complementos
            subs = []
            if it['fam'] == "Conchas": subs.append(f"Lágrima {it['esp']}")
            if it['fam'] == "Rosca de reyes" and it['rel'] != "Sin Relleno": subs.append(it['rel'])
            if it['fam'] == "Berlinas": subs.append("Crema Vainilla")
            if it['fam'] == "Rollos": subs.append("Schmear Canela")
            
            for s_id in subs:
                if s_id in DB_COMPLEMENTOS:
                    p_u = ARBOL[it['fam']].get("p_rell_map", {}).get(it['tam'], 15) if "Crema" in s_id else (ARBOL[it['fam']].get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15)
                    lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

    # --- PÁGINA: RESUMEN ---
    if pagina == "📋 Resumen Visual":
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[i['fam']]['tam'][i['tam']] * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_batch:,.1f}g)")
            c_izq, c_der = st.columns([0.3, 0.7])
            with c_izq:
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c_der:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}")

    # --- PÁGINA: CLIENTES ---
    elif pagina == "📞 Clientes & WhatsApp":
        for i, p in enumerate(st.session_state.comanda):
            with st.container(border=True):
                c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
                # Formatear pedido en renglones
                resumen_lista = [f"• {it['can']}x {it['esp']} ({it['tam']})" for it in p['items']]
                c1.write(f"👤 **{p['cli']}**")
                for r in resumen_lista: c1.caption(r)
                
                # WhatsApp con saltos de línea (%0A)
                msg_wa = f"Hola {p['cli']}! 🥐 Tu pedido ya está listo:%0A" + "%0A".join(resumen_lista)
                u_wa = f"https://wa.me/521{p['wa']}?text="
                c2.link_button("✅ Confirmar", u_wa + "Recibido")
                c3.link_button("🚀 Listo", u_wa + msg_wa)
                if st.button("❌ Borrar", key=f"del_{i}"): st.session_state.comanda.pop(i); st.rerun()

    # --- PÁGINA: PRODUCCIÓN ---
    elif pagina == "🥣 Producción":
        col_m, col_s = st.columns(2)
        with col_m:
            st.subheader("🥣 Masas")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]
                m_batch = sum([(ARBOL[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.write(f"**Lote: {m_id}**")
                for etapa in m_dna["etapas"]:
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><div class="etapa-titulo">{etapa["n"]}</div>', unsafe_allow_html=True)
                    for ing in etapa['i']:
                        gr = m_dna['receta'][ing]*h_b/100
                        st.checkbox(f"{ing}: {gr:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                        master_inv[ing] = master_inv.get(ing, 0) + gr
                    st.markdown('</div>', unsafe_allow_html=True)
        with col_s:
            st.subheader("✨ Complementos")
            for s_id, p_tot in lotes_comp.items():
                s_rec = DB_COMPLEMENTOS[s_id]
                st.write(f"**{s_id} ({p_tot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {s_rec["c"]};">', unsafe_allow_html=True)
                fact = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
                for sk, sv in s_rec.items():
                    if sk == "c": continue
                    gr_s = sv * fact
                    st.checkbox(f"{sk}: {gr_s:,.1f}g", key=f"sec_{s_id}_{sk}")
                    master_inv[sk] = master_inv.get(sk, 0) + gr_s
                st.markdown('</div>', unsafe_allow_html=True)

    # --- PÁGINA: SÚPER ---
    elif pagina == "🛒 Súper (Lista Maestra)":
        st.header("🛒 Lista Maestra de Surtido")
        # Aquí forzamos el cálculo de nuevo por si acaso
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            for k, v in m_dna['receta'].items(): master_inv[k] = master_inv.get(k, 0) + (v*h_b/100)
        
        for k, v in sorted(master_inv.items()):
            st.checkbox(f"{k}: **{v:,.1f}g**", key=f"master_{k}")
