import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. ARQUITECTURA TÉCNICA (DNA COMPLETO)
# ==========================================

# RECETARIO MAESTRO (CONCENTRA TODO LO COMPARTIDO)
DB_TECNICA = {
    "CONCHAS": {
        "masa_base": "Masa de Conchas",
        "pesos_masa": {"Estándar": 95, "Mini": 35},
        "peso_sub_unitario": {"Estándar": 30, "Mini": 10},
        "especialidades": {
            "Vainilla": ["Lágrima Vainilla"],
            "Chocolate": ["Lágrima Chocolate"],
            "Matcha": ["Lágrima Matcha"],
            "Fresa": ["Lágrima Fresa"],
            "Mazapán Intenso": ["Lágrima Mazapán"],
            "Oreo": ["Lágrima Oreo"],
            "Pinole": ["Lágrima Pinole"]
        }
    },
    "ROSCA DE REYES": {
        "masa_base": "Masa Brioche Rosca",
        "pesos_masa": {"FAMILIAR (1.5kg)": 1450, "MEDIANA (650g)": 650, "MINI (120g)": 120, "CONCHA-ROSCA (90g)": 90},
        "peso_relleno_tabla": {"FAMILIAR (1.5kg)": 450, "MEDIANA (650g)": 200, "MINI (120g)": 35, "CONCHA-ROSCA (90g)": 25},
        "especialidades": {
            "Tradicional": ["Lágrima Vainilla", "Decoración Rosca Ate"],
            "Chocolate": ["Lágrima Chocolate", "Decoración Nuez"],
            "Turín": ["Lágrima Chocolate", "Glaseado Turín Costra", "Cuerpo Conejo", "Cabeza de Conejo"]
        },
        "rellenos_crema": ["Sin Relleno", "Crema Vainilla", "Crema Chocolate", "Crema Ruby", "Crema Turín"]
    },
    "BERLINAS": {
        "masa_base": "Masa Berlinas (TZ)",
        "pesos_masa": {"Estándar (60g)": 60, "Ruby Special (70g)": 70},
        "especialidades": {
            "Ruby v2.0": ["Crema Ruby", "Glaseado Ruby"],
            "Vainilla Clásica": ["Crema Vainilla"],
            "Turín Especial": ["Crema Turín", "Glaseado Turín Costra"]
        }
    },
    "ROLLOS": {
        "masa_base": "Masa Roles Gourmet",
        "pesos_masa": {"Individual": 90},
        "especialidades": {
            "Canela Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"],
            "Manzana Canela": ["Schmear Canela", "Inclusión Manzana"],
            "Red Velvet": ["Schmear Red Velvet", "Crema Vainilla"] # Red Velvet usa masa override
        }
    },
    "PAN DE MUERTO": {
        "masa_base": "Masa Muerto",
        "pesos_masa": {"Estándar": 90},
        "especialidades": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto", "Sabor Guayaba"]}
    }
}

ING_DNA = {
    # MASAS
    "Masa de Conchas": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0},
    "Masa Berlinas (TZ)": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche": 22, "Sal": 1.8, "Levadura": 1.0, "_merma": 0.85, "_tz": (0.05, 5)},
    "Masa Roles Gourmet": {"Harina de fuerza": 93, "Huevo": 30, "Leche": 5, "Levadura fresca": 1.0, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17, "_tz_f": (70, 350)},
    "Masa Red Velvet": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla": 17, "Huevo": 30, "Leche": 4, "Sal": 1.8, "Levadura": 1.0, "Cacao": 0.8, "Rojo": 0.7},
    "Masa Brioche Rosca": {"Harina": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche": 24, "Levadura": 0.35, "Sal": 2.2, "Azahar": 0.6, "_tz": (0.025, 1)},
    "Masa Muerto": {"Harina": 100, "Leche": 30, "Yemas": 18, "Azúcar": 20, "Mantequilla": 25, "Sal": 1.8, "Guayaba Polvo": 5.0, "Levadura fresca": 5.0},
    # COMPLEMENTOS
    "Lágrima Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Chocolate": {"Harina de fuerza": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Fresa": {"Harina": 100, "Nesquik": 21, "Azúcar Glass": 79, "Mantequilla": 100},
    "Lágrima Mazapán": {"Harina": 100, "Mazapan": 66, "Azúcar Glass": 100, "Mantequilla": 100},
    "Lágrima Oreo": {"Harina": 100, "Oreo picada": 25, "Azúcar Glass": 75, "Mantequilla": 100},
    "Lágrima Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30},
    "Crema Ruby": {"Leche": 131, "Crema 35%": 131, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Crema Turín": {"Leche": 450, "Yemas": 100, "Azúcar": 90, "Fécula": 45, "Chocolate Turín": 120},
    "Schmear Canela": {"Mantequilla": 200, "Mascabado": 300, "Canela": 25},
    "Decoración Rosca Ate": {"Ate Tiras": 50, "Higo": 20, "Cereza": 10},
    "Rebozado Muerto": {"Mantequilla baño": 6.5, "Azúcar Naranja": 12.5}
}

# ==========================================
# 2. MOTOR DE UI (STABILIZADO)
# ==========================================
if 'tema' not in st.session_state: st.session_state.tema = "Claro"
if 'pedidos' not in st.session_state: st.session_state.pedidos = []
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'f_key' not in st.session_state: st.session_state.f_key = 0

# Paleta MATE PRO
if st.session_state.tema == "Oscuro":
    B_APP, B_CARD, T_MAIN, B_BRD, B_INPUT = "#0E1117", "#161B22", "#E6EDF3", "#30363D", "#1C2128"
    B_ACC = "#E67E22"
else:
    B_APP, B_CARD, T_MAIN, B_BRD, B_INPUT = "#F7F8FA", "#FFFFFF", "#24292F", "#D0D7DE", "#FFFFFF"
    B_ACC = "#D35400"

st.markdown(f"""<style>
    .stApp {{ background-color: {B_APP} !important; color: {T_MAIN}; }}
    h1, h2, h3, h4, p, span, label, div {{ color: {T_MAIN} !important; font-family: 'Segoe UI', sans-serif; }}
    div[data-testid="stExpander"], .streamlit-expanderHeader {{ background-color: {B_CARD} !important; border: 1px solid {B_BRD} !important; }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"], input {{ background-color: {B_INPUT} !important; border: 1px solid {B_BRD} !important; color: {T_MAIN} !important; }}
    div[role="listbox"] {{ background-color: {B_CARD} !important; border: 1px solid {B_BRD} !important; }}
    li[role="option"] {{ color: {T_MAIN} !important; background-color: {B_CARD} !important; }}
    .stButton > button {{ background-color: {B_CARD} !important; border: 1px solid {B_BRD} !important; color: {T_MAIN} !important; font-weight: bold; width: 100%; border-radius: 8px; }}
    .etapa-box {{ padding: 12px; border-radius: 10px; border: 1px solid {B_BRD}; margin-bottom: 8px; background-color: rgba(200,200,200,0.1); }}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("👨‍🍳 NAVEGACIÓN")
    pag = st.radio("Secciones", ["📋 Comanda (Captura)", "🖼️ Resumen Producción", "🥣 Hoja de Batido", "📞 WhatsApp", "🛒 Lista de Súper"])
    st.divider()
    if st.button("☀️/🌙 TEMA: " + st.session_state.tema):
        st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
        st.rerun()
    if st.button("🗑️ RESETEAR DÍA"): st.session_state.pedidos = []; st.session_state.carrito = []; st.rerun()

# ==========================================
# 3. PAGINA: CAPTURA (CERO BORRADO NOMBRE)
# ==========================================

if pag == "🛒 Comanda (Captura)":
    st.header("1. Registrar Pedido")
    c_n, c_w = st.columns(2)
    cli_n = c_n.text_input("Nombre Cliente", key="input_cli")
    cli_w = c_w.text_input("WhatsApp (10 dígitos)", key="input_wa")

    st.write("---")
    st.subheader("2. Añadir Panes al Carrito")
    fk = st.session_state.f_key
    c3, c4, c5, c6 = st.columns([2, 2, 2, 1])
    fam = c3.selectbox("Pan", ["-"] + list(RECETARIO.keys()), key=f"f_{fk}")
    
    if fam != "-":
        esp = c4.selectbox("Especialidad", list(RECETARIO[fam]["especialidades"].keys()), key=f"e_{fk}")
        tam = c5.selectbox("Tamaño", list(RECETARIO[fam]["pesos"].keys()), key=f"t_{fk}")
        can = c6.number_input("Cant", min_value=1, value=1, key=f"c_{fk}")
        rel = "N/A"
        if fam == "ROSCA DE REYES":
            rel = st.selectbox("Relleno de Crema", RECETARIO[fam]["rellenos_validos"], key=f"r_{fk}")

        if st.button("➕ AGREGAR A LA LISTA"):
            st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "can": can})
            st.session_state.f_key += 1; st.rerun()

    if st.session_state.carrito:
        st.info(f"**PRE-PEDIDO: {cli_n}**")
        for i, it in enumerate(st.session_state.carrito):
            st.write(f"- {it['can']}x {it['esp']} {it['fam']} ({it['tam']})")
        if st.button("✅ FINALIZAR Y GUARDAR"):
            if cli_n:
                st.session_state.pedidos.append({"cliente": cli_n, "wa": cli_w, "items": st.session_state.carrito.copy()})
                st.session_state.carrito = []; st.rerun()

# ==========================================
# 4. MOTOR DE CÁLCULO Y VISTAS
# ==========================================

if st.session_state.pedidos:
    inv_m_compra = {}
    dict_batidos = {}
    dict_extras = {}

    # CONSOLIDACIÓN
    for ped in st.session_state.pedidos:
        for it in ped['items']:
            # Agrupar Masas
            m_id = RECETARIO[it['fam']]["masa_id"]
            if it['esp'] == "Red Velvet": m_id = "Masa Red Velvet"
            if m_id not in dict_batidos: dict_batidos[m_id] = []
            it_data = it.copy(); it_data['cliente'] = ped['cliente']
            dict_batidos[m_id].append(it_data)

            # Calcular Ingredientes de Complementos
            subs = RECETARIO[it['fam']]["especialidades"][it['esp']].copy()
            if it['rel'] != "Sin Relleno" and it['rel'] != "N/A": subs.append(it['rel'])
            
            for s_id in subs:
                if s_id not in ING_DNA: continue
                # Definir peso del complemento
                if it['fam'] == "ROSCA DE REYES" and s_id == it['rel']: p_u = RECETARIO["ROSCA DE REYES"]["peso_relleno_tabla"][it['tam']]
                elif "Lágrima" in s_id: p_u = RECETARIO["CONCHAS"]["complemento_peso"][it['tam']]
                else: p_u = 15
                
                peso_batch = p_u * it['can']
                s_dna = ING_DNA[s_id]
                f_sub = peso_batch / sum(s_dna.values())
                if s_id not in dict_extras: dict_extras[s_id] = {"peso": 0, "ing": {}}
                dict_extras[s_id]["peso"] += peso_batch
                for ing_n, val_n in s_dna.items():
                    cant_n = val_n * f_sub
                    dict_extras[s_id]["ing"][ing_n] = dict_extras[s_id]["ing"].get(ing_n, 0) + cant_n
                    inv_m_compra[ing_n] = inv_m_compra.get(ing_n, 0) + cant_n

    if pag == "📋 Resumen Visual":
        for mid, items in dict_batidos.items():
            st.header(f"🛠️ BATIDO: {mid}")
            m_dna = ING_DNA[mid]; tot_m = sum([(RECETARIO[i['fam']]['pesos'][i['tam']] * i['can']) / m_dna.get('_merma',1) for i in items])
            hb = (tot_m * 100) / sum([v for k,v in m_dna.items() if not k.startswith('_')])
            col_a, col_b = st.columns([0.3, 0.7])
            with col_a: 
                st.info(f"Batido Total: {tot_m:,.0f}g")
                for k, v in m_dna.items(): 
                    if not k.startswith('_'): st.caption(f"{k}: {(v*hb/100):,.1f}g"); inv_m_compra[k] = inv_m_compra.get(k, 0) + (v*hb/100)
            with col_b:
                for it in items: st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}")

    elif pag == "🥣 Hoja de Batido":
        cm1, cm2 = st.columns(2)
        with cm1:
            st.subheader("📋 Masas Base")
            for mid, items in dict_batidos.items():
                m_dna = ING_DNA[mid]; m_pes = sum([(RECETARIO[it['fam']]['pesos'][it['tam']] * it['can']) for it in items])
                hb_l = (m_pes * 100) / sum([v for k,v in m_dna.items() if not k.startswith('_')])
                st.write(f"**Lote: {mid}**")
                for k,v in m_dna.items(): 
                    if not k.startswith('_'): st.checkbox(f"{k}: {v*hb_l/100:,.1f}g", key=f"m_{mid}_{k}")
        with cm2:
            st.subheader("📋 Lágrimas y Rellenos")
            for sid, data in dict_extras.items():
                st.write(f"**{sid} ({data['peso']:,.0f}g)**")
                for in_n, in_g in data['ing'].items():
                    st.checkbox(f"{in_n}: {in_g:,.1f}g", key=f"s_{sid}_{in_n}")

    elif pag == "📞 WhatsApp":
        for i, ped in enumerate(st.session_state.pedidos):
            with st.container(border=True):
                ca, cb = st.columns([0.7, 0.3])
                res = "\n".join([f"• {it['can']}x {it['esp']} {it['fam']} ({it['tam']})" for it in ped['items']])
                ca.write(f"👤 **{ped['cliente']}**"); ca.caption(res)
                msg = urllib.parse.quote(f"Hola {ped['cliente']}! Pedido listo:\n{res}")
                cb.link_button("🚀 WhatsApp", f"https://wa.me/521{ped['wa']}?text={msg}")
                if st.button("❌", key=f"dl_{i}"): st.session_state.pedidos.pop(i); st.rerun()

    elif pag == "🛒 Lista Súper":
        st.header("Surtido Completo (Batido + Decoración)")
        for k, v in sorted(inv_m_compra.items()): st.checkbox(f"{k}: **{v:,.1f}g**", key=f"sp_{k}")
