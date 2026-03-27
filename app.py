import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN DE ESTADOS (ESTABILIDAD)
# ==========================================
if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'f_id' not in st.session_state: st.session_state.f_id = 0
if 'cli_n' not in st.session_state: st.session_state.cli_n = ""
if 'cli_w' not in st.session_state: st.session_state.cli_w = ""

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# Estilo Claro de Alto Contraste (Cero errores visuales)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3, h4, p, span, label { color: #000000 !important; font-weight: 500; }
    div[data-testid="stExpander"] { border: 1px solid #DDDDDD !important; border-radius: 10px; background-color: #F9F9F9; }
    .etapa-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #DDDDDD; color: #000 !important; }
    [data-testid="stSidebar"] { background-color: #F0F2F6 !important; border-right: 1px solid #DDDDDD; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS MAESTRA (AUDITADA)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2}, "merma": 1.0, 
        "etapas": [{"n": "1. Autólisis", "i": ["Harina de fuerza", "Huevo", "Leche entera"], "c": "#FFF9C4"}, {"n": "2. Activación", "i": ["Levadura seca", "Vainilla"], "c": "#C8E6C9"}, {"n": "3. Estructura", "i": ["Azúcar", "Sal fina"], "c": "#BBDEFB"}, {"n": "4. Enriquecimiento", "i": ["Mantequilla sin sal"], "c": "#FFE0B2"}]},
    "Masa Brioche Rosca": {"receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6}, "merma": 1.0, "tz": (0.025, 1),
        "etapas": [{"n": "1. Base", "i": ["Harina de fuerza", "Huevo", "Yemas", "Leche entera"], "c": "#FFF9C4"}, {"n": "2. Sabor", "i": ["Azúcar", "Miel", "Agua Azahar", "Sal fina", "Levadura fresca"], "c": "#BBDEFB"}, {"n": "3. Grasa", "i": ["Mantequilla sin sal"], "c": "#FFE0B2"}]},
    "Masa de Berlinas": {"receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0}, "merma": 0.85, "tz": (0.05, 5), "etapas": [{"n": "Masa Batch", "i": ["Harina de fuerza", "Azúcar", "Mantequilla sin sal", "Huevo", "Leche entera"], "c": "#BBDEFB"}]},
    "Masa Brioche Roles": {"receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17}, "merma": 1.0, "tz_f": (70, 350), "etapas": [{"n": "Batch Roles", "i": ["Harina de fuerza", "Huevo", "Azúcar", "Mantequilla sin sal"], "c": "#C8E6C9"}]},
    "Masa Muerto Guayaba": {"receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo Guayaba": 5}, "merma": 1.0, "huesos": True, "etapas": [{"n": "Batch Muerto", "i": ["Harina de fuerza", "Polvo Guayaba"], "c": "#FFE0B2"}]},
    "Mezcla Brownie": {"receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin": 165, "Harina de fuerza": 190, "Cocoa": 75, "Sal fina": 8, "Nuez": 140}, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Matcha": {"Harina de fuerza": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla sin sal": 100},
    "Lágrima Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66},
    "Lágrima Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Galleta Oreo": 25},
    "Crema Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla sin sal": 30},
    "Crema Chocolate": {"Leche entera": 480, "Yemas": 100, "Azúcar": 100, "Fécula": 45, "Chocolate 60%": 120},
    "Crema Ruby": {"Leche entera": 131.5, "Crema 35": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5}
}

CATALOGO = {
    "Conchas": {"espec": ["Vainilla", "Chocolate", "Matcha", "Fresa", "Mazapán", "Oreo"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas"},
    "Rosca de reyes": {"espec": ["Tradicional", "Turín"], "tam": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90}, "p_rell_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25}, "m": "Masa Brioche Rosca"},
    "Berlinas": {"espec": ["Vainilla", "Ruby v2.0"], "tam": {"Estándar": 60}, "m": "Masa de Berlinas", "p_man": {"Ruby v2.0": 70}},
    "Rollos": {"espec": ["Canela"], "tam": {"Individual": 90}, "m": "Masa Brioche Roles"},
    "Pan de muerto": {"espec": ["Guayaba"], "tam": {"Estándar": 95}, "m": "Masa Muerto Guayaba"},
    "Brownies": {"espec": ["Turín"], "tam": {"Molde 20x20": 1}, "m": "Mezcla Brownie"}
}

# ==========================================
# 3. NAVEGACIÓN (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("👨‍🍳 MENÚ")
    pagina = st.radio("Ir a:", ["📋 Resumen Visual", "🥣 Producción", "📞 Clientes & WhatsApp", "🛒 Súper (Lista Maestra)"])
    st.divider()
    if st.button("🗑️ Limpiar Todo el Día"):
        st.session_state.comanda = []; st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. INTERFAZ DE CAPTURA
# ==========================================
st.title(f"CONCIENCIA - {pagina}")

with st.expander("📝 1. Capturar Pedido", expanded=not st.session_state.comanda):
    c1, c2 = st.columns(2)
    st.session_state.cli_n = c1.text_input("Nombre Cliente", value=st.session_state.cli_n)
    st.session_state.cli_w = c2.text_input("WhatsApp", value=st.session_state.cli_w)
    st.write("---")
    fk = st.session_state.f_id
    c3, c4, c5, c6 = st.columns([2, 2, 1.5, 1])
    f_sel = c3.selectbox("Familia", ["-"] + list(CATALOGO.keys()), key=f"f_{fk}")
    if f_sel != "-":
        e_sel = c4.selectbox("Especialidad", CATALOGO[f_sel]["espec"], key=f"e_{fk}")
        t_sel = c5.selectbox("Tamaño", list(CATALOGO[f_sel]["tam"].keys()), key=f"t_{fk}")
        n_can = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
        rel_sel = "N/A"
        if f_sel == "Rosca de reyes": rel_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Vainilla", "Crema Ruby"], key=f"r_{fk}")
        if st.button("➕ AÑADIR PAN"):
            st.session_state.carrito.append({"fam": f_sel, "esp": e_sel, "tam": t_sel, "can": n_can, "rel": rel_sel})
            st.session_state.f_id += 1; st.rerun()

if st.session_state.carrito:
    st.info(f"🛒 Carrito para: {st.session_state.cli_n}")
    for it in st.session_state.carrito: st.write(f"- {it['can']}x {it['fam']} {it['esp']} ({it['tam']})")
    if st.button("✅ GUARDAR PEDIDO COMPLETO"):
        st.session_state.comanda.append({"cli": st.session_state.cli_n, "wa": st.session_state.cli_w, "items": st.session_state.carrito.copy()})
        st.session_state.carrito = []; st.session_state.cli_n = ""; st.session_state.cli_w = ""; st.rerun()

# ==========================================
# 5. MOTOR DE CÁLCULO UNIVERSAL
# ==========================================
master_inv = {}
lotes_masa = {}
lotes_comp = {}

for ped in st.session_state.comanda:
    for it in ped['items']:
        # Masa
        m_id = CATALOGO[it['fam']].get("m_ov", CATALOGO[it['fam']]["m"])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        it_c = it.copy(); it_c['cliente'] = ped['cli']; lotes_masa[m_id].append(it_c)
        # Complementos
        subs = []
        if it['fam'] == "Conchas": subs.append(f"Lágrima {it['esp']}")
        if it['fam'] == "Rosca de reyes": subs.append("Decoración Rosca"); 
        if it['rel'] != "Sin Relleno" and it['rel'] != "N/A": subs.append(it['rel'])
        if it['fam'] == "Berlinas" and it['esp'] == "Ruby v2.0": subs.append("Crema Ruby")
        if it['fam'] == "Rollos": subs.append("Schmear Canela")
        if it['fam'] == "Pan de muerto": subs.append("Rebozado Muerto")
        for s_id in subs:
            if s_id in DB_COMPLEMENTOS:
                p_u = CATALOGO[it['fam']].get("p_rell_map", {}).get(it['tam'], 15) if "Crema" in s_id else (CATALOGO[it['fam']].get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15)
                lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_u * it['can'])

# ==========================================
# 6. RENDER DE PÁGINAS
# ==========================================

if st.session_state.comanda:
    if pagina == "📋 Resumen Visual":
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_tot = sum([(CATALOGO[i['fam']].get("p_man", {}).get(i['esp'], CATALOGO[i['fam']]['tam'][i['tam']]) * i['can']) / m_dna['merma'] for i in items])
            h_b = (m_tot * 100) / sum(m_dna['receta'].values())
            st.markdown(f"#### 🛠️ Lote: {m_id} ({m_tot:,.1f}g)")
            c1, c2 = st.columns([0.3, 0.7])
            with c1:
                st.info("Masa Principal")
                for k, v in m_dna['receta'].items():
                    gr = v*h_b/100; st.write(f"• {k}: {gr:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + gr
            with c2:
                for it in items:
                    st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}")
                    # Desglose de lágrima/relleno por cliente
                    s_name = f"Lágrima {it['esp']}" if it['fam'] == "Conchas" else None
                    if s_name and s_name in DB_COMPLEMENTOS:
                        s_rec = DB_COMPLEMENTOS[s_name]; p_t = CATALOGO[it['fam']]['p_ex'][it['tam']] * it['can']
                        st.write(f"**{s_name} ({p_t:,.1f}g)**")
                        f_s = p_t / sum(s_rec.values())
                        for sk, sv in s_rec.items():
                            if sk != "c": gr_s = sv*f_s; st.write(f"- {sk}: {gr_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + gr_s

    elif pagina == "📞 Clientes":
        for i, p in enumerate(st.session_state.comanda):
            with st.container(border=True):
                c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
                list_txt = "\n".join([f"• {it['can']}x {it['esp']} ({it['tam']})" for it in p['items']])
                c1.write(f"👤 **{p['cli']}**\n\n{list_txt}")
                u = f"https://wa.me/521{p['wa']}?text="
                c2.link_button("✅ Confirmar", u + urllib.parse.quote("Pedido recibido!"))
                c3.link_button("🚀 Listo", u + urllib.parse.quote(f"Hola {p['cli']}! Tu pedido está listo:\n{list_txt}"))
                if st.button("❌ Borrar", key=f"d_{i}"): st.session_state.comanda.pop(i); st.rerun()

    elif pagina == "🥣 Producción":
        c_m, c_s = st.columns(2)
        with c_m:
            st.subheader("🥣 Batidos")
            for m_id, items in lotes_masa.items():
                m_dna = DB_MASAS[m_id]; m_batch = sum([(ARBOL[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
                h_b = (m_batch * 100) / sum(m_dna['receta'].values())
                st.write(f"**{m_id} ({m_batch:,.1f}g)**")
                for etapa in m_dna.get("etapas", []):
                    st.markdown(f'<div class="etapa-box" style="background-color: {etapa["c"]};"><b>{etapa["n"]}</b>', unsafe_allow_html=True)
                    for ing in etapa['i']: st.checkbox(f"{ing}: {m_dna['receta'][ing]*h_b/100:,.1f}g", key=f"p_{m_id}_{ing}_{etapa['n']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        with c_s:
            st.subheader("✨ Complementos")
            for s_id, p_tot in lotes_comp.items():
                s_rec = DB_COMPLEMENTOS[s_id]; st.write(f"**{s_id} ({p_tot:,.1f}g)**")
                st.markdown(f'<div class="etapa-box" style="background-color: {s_rec.get("c","#F0F0F0")};">', unsafe_allow_html=True)
                fact = p_tot / sum([v for k,v in s_rec.items() if k != "c"])
                for sk, sv in s_rec.items():
                    if sk != "c": 
                        st.checkbox(f"{sk}: {sv*fact:,.1f}g", key=f"sec_{s_id}_{sk}")
                        master_inv[sk] = master_inv.get(sk, 0) + sv*fact
                st.markdown('</div>', unsafe_allow_html=True)

    elif pagina == "🛒 Súper":
        st.header("🛒 Lista Maestra")
        for k, v in sorted(master_inv.items()): st.checkbox(f"{k}: **{v:,.1f}g**", key=f"m_{k}")
