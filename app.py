import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. INICIALIZACIÓN Y BASE DE DATOS TOTAL
# ==========================================
if 'pedidos' not in st.session_state: st.session_state.pedidos = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0

DB_MASAS = {
    "Masa de Conchas": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0, "merma": 1.0},
    "Masa Brioche Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6, "merma": 1.0},
    "Masa Berlinas (TZ)": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0, "merma": 0.85},
    "Masa Brioche Roles": {"Harina de fuerza": 93, "Huevo": 30, "Leche": 5, "Levadura fresca": 1.0, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla": 17, "merma": 1.0},
    "Masa Muerto": {"Harina": 100, "Leche": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla": 25, "Sal": 1.8, "Levadura fresca": 5, "merma": 1.0}
}

DB_COMPLEMENTOS = {
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Matcha": {"Harina de fuerza": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Fresa": {"Harina": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla": 100},
    "Lágrima Oreo": {"Harina": 100, "Oreo": 25, "Azúcar Glass": 75, "Mantequilla": 100},
    "Lágrima Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Mazapán": {"Harina": 100, "Mazapán": 66, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Ruby": {"Leche": 131, "Crema 35%": 131, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10},
    "Schmear Canela": {"Mantequilla": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Frutos Rojos Earl Grey": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2, "Vainilla": 0.5}
}

ARBOL = {
    "CONCHAS": {"esp": ["Vainilla", "Chocolate", "Matcha", "Oreo", "Fresa", "Mazapán", "Pinole"], "tam": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "m": "Masa de Conchas"},
    "ROSCAS": {"esp": ["Tradicional", "Turín"], "tam": {"Familiar (1.5kg)": 1450, "Mediana (650g)": 650, "Mini (120g)": 120, "Concha-Rosca": 90}, "p_rel_map": {"Familiar (1.5kg)": 450, "Mediana (650g)": 200, "Mini (120g)": 35, "Concha-Rosca": 25}, "m": "Masa Brioche Rosca"},
    "BERLINAS": {"esp": ["Vainilla Clásica", "Ruby v2.0"], "tam": {"Estándar": 60}, "p_man": {"Ruby v2.0": 70}, "m": "Masa Berlinas (TZ)"},
    "ROLES": {"esp": ["Tradicional", "Manzana"], "tam": {"Individual": 90}, "m": "Masa Brioche Roles"}
}

# ==========================================
# 2. NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.title("🥖 MENÚ MAESTRO")
    pagina = st.radio("Secciones:", ["➕ Captura", "📋 Resumen Visual", "🥣 Producción", "🛒 Súper"])
    st.divider()
    if st.button("🗑️ Resetear Día"): 
        st.session_state.pedidos = []; st.session_state.carrito = []; st.rerun()

# ==========================================
# 3. PÁGINA: CAPTURA
# ==========================================
if pagina == "➕ Captura":
    st.header("Capturar Pedidos de Clientes")
    with st.container():
        c1, c2 = st.columns(2)
        c_n = c1.text_input("Nombre Cliente", key="in_name")
        c_w = c2.text_input("WhatsApp (10 dígitos)", key="in_wa")
    
    st.divider()
    fk = st.session_state.form_key
    c3, c4, c5, c6, c7 = st.columns([2, 2, 1.5, 1, 0.5])
    fam_sel = c3.selectbox("Pan", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    
    if fam_sel != "-":
        esp_sel = c4.selectbox("Especialidad", ARBOL[fam_sel]["esp"], key=f"e_{fk}")
        tam_sel = c5.selectbox("Tamaño", list(ARBOL[fam_sel]["tam"].keys()), key=f"t_{fk}")
        can_sel = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
        rel_sel = "N/A"
        if fam_sel == "ROSCAS": rel_sel = st.selectbox("Relleno", ["Sin Relleno", "Crema Vainilla", "Crema Ruby"], key=f"r_{fk}")
        
        if c7.button("➕"):
            st.session_state.carrito.append({"fam": fam_sel, "esp": esp_sel, "tam": tam_sel, "can": can_sel, "rel": rel_sel})
            st.session_state.form_key += 1; st.rerun()

    if st.session_state.carrito:
        st.info(f"🛒 Carrito de {c_n}")
        for p in st.session_state.carrito: st.write(f"- {p['can']}x {p['esp']} ({p['tam']})")
        if st.button("✅ FINALIZAR PEDIDO"):
            if c_n:
                st.session_state.pedidos.append({"cli": c_n, "wa": c_w, "items": st.session_state.carrito.copy()})
                st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE PROCESAMIENTO (CENTRAL)
# ==========================================
master_inv = {}
lotes_masa = {}
lotes_comp = {}

for ped in st.session_state.pedidos:
    for it in ped['items']:
        # Masa
        m_id = ARBOL[it['fam']]["m"]
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append({"can": it['can'], "esp": it['esp'], "tam": it['tam'], "cli": ped['cli'], "rel": it['rel'], "fam": it['fam']})
        
        # Complementos (Lágrimas/Rellenos)
        subs = []
        if it['fam'] == "CONCHAS": subs.append(f"Lágrima {it['esp']}")
        if it['fam'] == "ROSCAS":
            subs.append("Decoración Rosca")
            if it['rel'] != "Sin Relleno": subs.append(it['rel'])
        if it['fam'] == "BERLINAS":
            if "Ruby" in it['esp']: subs.append("Crema Ruby")
            else: subs.append("Crema Vainilla")
        if it['fam'] == "ROLES":
            subs.append("Schmear Canela")
            if "Tradicional" in it['esp']: subs.append("Frutos Rojos Earl Grey")

        for s_id in subs:
            if s_id in DB_COMPLEMENTOS:
                p_unit = ARBOL[it['fam']].get("p_rel_map", {}).get(it['tam'], 15) if "Crema" in s_id else (ARBOL[it['fam']].get("p_ex", {}).get(it['tam'], 15) if "Lágrima" in s_id else 15)
                lotes_comp[s_id] = lotes_comp.get(s_id, 0) + (p_unit * it['can'])

# ==========================================
# 5. PESTAÑAS DE TRABAJO
# ==========================================

if st.session_state.pedidos:
    if pagina == "📋 Resumen Visual":
        for mid, items in lotes_masa.items():
            st.header(f"🛠️ BATIDO: {mid}")
            m_dna = DB_MASAS[mid]
            m_batch = sum([(ARBOL[it['fam']].get("p_man", {}).get(it['esp'], ARBOL[it['fam']]['tam'][it['tam']]) * it['can']) / m_dna['merma'] for it in items])
            hb = (m_batch * 100) / sum(m_dna['receta'].values())
            
            c_m, c_c = st.columns([0.4, 0.6])
            with c_m:
                st.write(f"Masa Total: **{m_batch:,.1f}g**")
                for k,v in m_dna['receta'].items(): 
                    g = v*hb/100; st.caption(f"{k}: {g:,.1f}g"); master_inv[k] = master_inv.get(k, 0) + g
            with c_c:
                for it in items:
                    st.success(f"**{it['can']}x {it['esp']} ({it['tam']}) — {it['cli']}**")
                    # Sub-recetas del cliente
                    sub_n = f"Lágrima {it['esp']}" if it['fam'] == "CONCHAS" else None
                    if sub_n and sub_n in DB_COMPLEMENTOS:
                        s_dna = DB_COMPLEMENTOS[sub_n]; p_tot = ARBOL[it['fam']]['p_ex'][it['tam']] * it['can']
                        f_s = p_tot / sum(s_dna.values())
                        st.markdown(f"**{sub_n} ({p_tot:,.0f}g):**")
                        for sk, sv in s_dna.items(): 
                            gr_s = sv*f_s; st.write(f"- {sk}: {gr_s:,.1f}g"); master_inv[sk] = master_inv.get(sk, 0) + gr_s

    elif pagina == "🥣 Producción":
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🥣 Masas")
            for mid, items in lotes_masa.items():
                m_dna = DB_MASAS[mid]
                bt_p = sum([(ARBOL[it['fam']]['tam'][it['tam']] * it['can']) for it in items])
                hb_p = (bt_p * 100) / sum(m_dna['receta'].values())
                st.write(f"**{mid} ({bt_p:,.0f}g)**")
                for etapa in m_dna.get("etapas", [{"n": "Proceso Único", "i": list(m_dna['receta'].keys())}]):
                    st.write(f"*{etapa['n']}*")
                    for ing in etapa['i']: st.checkbox(f"{ing}: {m_dna['receta'][ing]*hb_p/100:,.1f}g", key=f"p_{mid}_{ing}_{ing}")
        with col2:
            st.subheader("✨ Complementos")
            for sid, pt in lotes_comp.items():
                st.write(f"**{sid} ({pt:,.1f}g)**")
                s_dna = DB_COMPLEMENTOS[sid]; fact = pt / sum(s_dna.values())
                for sk, sv in s_dna.items(): 
                    st.checkbox(f"{sk}: {sv*fact:,.1f}g", key=f"s_{sid}_{sk}"); master_inv[sk] = master_inv.get(sk, 0) + sv*fact

    elif pagina == "📞 WhatsApp":
        for i, ped in enumerate(st.session_state.pedidos):
            with st.container(border=True):
                r = "\n".join([f"• {it['can']}x {it['esp']} ({it['tam']})" for it in ped['items']])
                st.write(f"👤 **{ped['cli']}**"); st.caption(r)
                msg = urllib.parse.quote(f"Hola {ped['cli']}! Tu pedido de {r} ya esta listo!")
                st.link_button("🚀 Avisar por WhatsApp", f"https://wa.me/521{ped['wa']}?text={msg}")
                if st.button("❌ Borrar Pedido", key=f"final_{i}"): st.session_state.pedidos.pop(i); st.rerun()

    elif pagina == "🛒 Súper":
        st.header("🛒 Insumos Totales del Día")
        for k, v in sorted(master_inv.items()): st.checkbox(f"{k}: **{v:,.1f}g**", key=f"inv_{k}")
