import streamlit as st
import pandas as pd
import urllib.parse

# ==========================================
# 1. BASE DE DATOS EXTERNA (Simulada)
# ==========================================

RECETARIO = {
    "CONCHAS": {
        "masa_id": "Masa_Conchas",
        "pesos": {"Estándar": 95, "Mini": 35},
        "complemento_peso": {"Estándar": 30, "Mini": 10},
        "especialidades": {
            "Vainilla": ["L_Vainilla"],
            "Chocolate": ["L_Chocolate"],
            "Matcha": ["L_Matcha"],
            "Fresa": ["L_Fresa"],
            "Mazapán Intenso": ["L_Mazapan_I"],
            "Pinole": ["L_Pinole"],
            "Oreo": ["L_Oreo"]
        }
    },
    "ROSCA_DE_REYES": {
        "masa_id": "Masa_Rosca",
        "pesos": {"Familiar (10-12p)": 1450, "Mediana (6-8p)": 650, "Mini (1-2p)": 120, "Concha-Rosca": 90},
        "relleno_auto": {"Familiar (10-12p)": 450, "Mediana (6-8p)": 200, "Mini (1-2p)": 35, "Concha-Rosca": 25},
        "especialidades": {
            "Tradicional": ["L_Vainilla", "Decoracion_Ate"],
            "Chocolate": ["L_Chocolate", "Nuez_Fileteada"],
            "Turín": ["L_Chocolate", "Glaseado_Turin", "Cuerpos_Conejo", "Cabeza_Conejo"]
        },
        "rellenos_validos": ["Sin Relleno", "Crema Vainilla", "Crema Chocolate", "Crema Turin"]
    },
    "BERLINAS": {
        "masa_id": "Masa_Berlina",
        "pesos": {"Estándar": 60, "Ruby Special": 70},
        "especialidades": {
            "Vainilla": ["Crema Vainilla"],
            "Ruby v2.0": ["Crema Ruby", "Glaseado Ruby"],
            "Chocolate": ["Crema Chocolate"]
        }
    },
    "ROLES": {
        "masa_id": "Masa_Roles",
        "pesos": {"Individual": 90},
        "especialidades": {
            "Canela Tradicional": ["Schmear_Canela", "Pasas_Arandanos"],
            "Manzana Canela": ["Schmear_Canela", "Manzana_Tratada"],
            "Red Velvet": ["Schmear_RV", "Glaseado_Roles"]
        }
    }
}

ING_DNA = {
    "Masa_Conchas": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2.0, "_merma": 1.0},
    "Masa_Berlina": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla": 20, "Huevo": 25, "Leche": 22, "Sal fina": 1.8, "Levadura": 1.0, "_merma": 0.85, "_tz": (0.05, 5)},
    "Masa_Roles": {"Harina de fuerza": 93, "Huevo": 30, "Leche": 5, "Levadura fresca": 1.0, "Sal": 1.8, "Azúcar": 16, "Mantequilla": 17, "_merma": 1.0, "_tz_f": (70, 350, 1000)},
    "Masa_Rosca": {"Harina": 100, "Azúcar": 25, "Miel": 3, "Mantequilla": 30, "Huevo": 20, "Yemas": 4, "Leche": 24, "Levadura": 0.35, "Sal": 2.2, "Agua Azahar": 0.6, "_merma": 1.0, "_tz": (0.025, 1)},
    "L_Vainilla": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Fresa": {"Harina": 100, "Azúcar Glass": 79, "Nesquik": 21, "Mantequilla": 100},
    "L_Oreo": {"Harina": 100, "Oreo picada": 25, "Azúcar Glass": 75, "Mantequilla": 100},
    "L_Pinole": {"Harina": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla": 100},
    "L_Mazapan_I": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapan": 66},
    "Crema Vainilla": {"Leche": 500, "Yemas": 100, "Azúcar": 120, "Fécula": 45, "Mantequilla": 30, "Vainilla": 6},
    "Crema Ruby": {"Leche": 131, "Crema 35": 131, "Yemas": 53, "Azúcar": 63, "Fécula": 24},
    "Schmear_Canela": {"Mantequilla": 200, "Mascabado": 300, "Canela": 25},
    "Decoracion_Ate": {"Ate Tiras": 50, "Higo": 20, "Cereza": 10}
}

# ==========================================
# 2. INICIALIZACIÓN DE ESTADO Y UI
# ==========================================
st.set_page_config(page_title="CONCIENCIA MASTER", layout="wide")

if 'tema' not in st.session_state: st.session_state.tema = "Oscuro"
if 'comanda' not in st.session_state: st.session_state.comanda = [] # Estructura final por cliente
if 'carrito' not in st.session_state: st.session_state.carrito = [] # Temporal para un cliente
if 'form_key' not in st.session_state: st.session_state.form_key = 0

C_BG = "#0E1117" if st.session_state.tema == "Oscuro" else "#FFFFFF"
C_SEC = "#161B22" if st.session_state.tema == "Oscuro" else "#F0F2F6"
C_TXT = "#E6EDF3" if st.session_state.tema == "Oscuro" else "#1F2328"
C_BRD = "#30363D" if st.session_state.tema == "Oscuro" else "#D0D7DE"

st.markdown(f"""<style>
    .stApp {{ background-color: {C_BG} !important; color: {C_TXT}; }}
    h1, h2, h3, h4, p, label {{ color: {C_TXT} !important; }}
    div[data-testid="stExpander"], .streamlit-expanderHeader {{ background-color: {C_SEC} !important; border: 1px solid {C_BRD} !important; color: {C_TXT} !important; }}
    div[data-baseweb="select"] > div, input {{ background-color: {C_BG} !important; color: {C_TXT} !important; border: 1px solid {C_BRD} !important; }}
    ul[role="listbox"] {{ background-color: {C_SEC} !important; color: {C_TXT} !important; }}
    .etapa-card {{ padding: 15px; border-radius: 12px; border: 1px solid {C_BRD}; margin-bottom: 10px; color: #111 !important; font-weight: 600; opacity: 0.5; }}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("👨‍🍳 NAVEGACIÓN")
    pag = st.radio("Paginas", ["🛒 Comanda (Captura)", "📋 Resumen Visual", "🥣 Producción", "📦 Lista Súper"])
    if st.button("☀️/🌙 " + st.session_state.tema):
        st.session_state.tema = "Claro" if st.session_state.tema == "Oscuro" else "Oscuro"
        st.rerun()
    if st.button("🗑️ VACIAR TODO"): st.session_state.comanda = []; st.rerun()

# ==========================================
# 3. PAGINA 1: CAPTURA (LÓGICA PERSISTENTE)
# ==========================================

if pag == "🛒 Comanda (Captura)":
    st.header("Cargar Pedidos de Clientes")
    with st.container():
        c1, c2 = st.columns(2)
        cli_name = c1.text_input("Nombre Cliente", key="input_cli")
        cli_tel = c2.text_input("Celular (10 dígitos)", key="input_wa")
    
    st.write("---")
    fk = st.session_state.form_key
    sc1, sc2, sc3, sc4, sc5 = st.columns([2, 2, 2, 1, 1])
    fam = sc1.selectbox("Pan", ["-"] + list(RECETARIO.keys()), key=f"f_{fk}")
    
    if fam != "-":
        esp = sc2.selectbox("Sabor", RECETARIO[fam]["especialidades"].keys(), key=f"e_{fk}")
        tam = sc3.selectbox("Tamaño", list(RECETARIO[fam]["pesos"].keys()), key=f"t_{fk}")
        can = sc4.number_input("Cant", min_value=1, key=f"c_{fk}")
        rel = "N/A"
        if fam == "ROSCA_DE_REYES": 
            rel = sc2.selectbox("Relleno", RECETARIO[fam]["rellenos_validos"], key=f"r_{fk}")
            
        if sc5.button("➕"):
            st.session_state.carrito.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "can": can})
            st.session_state.form_key += 1; st.rerun()
            
    if st.session_state.carrito:
        st.success(f"CARRITO ACTUAL: {cli_name}")
        for it in st.session_state.carrito: st.caption(f"{it['can']}x {it['esp']} {it['fam']} ({it['tam']})")
        if st.button("✅ FINALIZAR PEDIDO COMPLETO"):
            if cli_name:
                st.session_state.comanda.append({"cliente": cli_name, "wa": cli_tel, "items": st.session_state.carrito.copy()})
                st.session_state.carrito = []; st.rerun()
            else: st.error("Debes poner el nombre.")

# ==========================================
# 4. MOTOR DE CÁLCULO CENTRAL (CERO ERRORES)
# ==========================================

if st.session_state.comanda:
    master_compra = {}
    lotes_masa = {}
    lotes_subs = {}

    # Consolidación Global
    for ped in st.session_state.comanda:
        for it in ped['items']:
            m_id = RECETARIO[it['fam']]["masa_id"]
            if m_id not in lotes_masa: lotes_masa[m_id] = []
            it_v = it.copy(); it_v['cliente'] = ped['cliente']
            lotes_masa[m_id].append(it_v)
            
            # Sumar Complementos (Lágrimas/Cremas)
            actual_subs = []
            if it['fam'] == "CONCHAS": actual_subs.append(f"L_{it['esp'].replace(' Intenso','')}")
            if it['fam'] == "ROSCA_DE_REYES": 
                actual_subs.append("Decoracion_Ate")
                if it['rel'] != "Sin Relleno": actual_subs.append(it['rel'])
            if it['fam'] == "BERLINAS": 
                if "Ruby" in it['esp']: actual_subs.append("Crema Ruby")
                else: actual_subs.append("Crema Vainilla")
            
            for s_id in actual_subs:
                p_unit_extra = 0
                if s_id in ["Crema Vainilla", "Crema Chocolate", "Crema Ruby", "Crema Turin"]:
                    p_unit_extra = RECETARIO[it['fam']]["relleno_auto"].get(it['tam'], 15)
                elif "Lágrima" in s_id or "L_" in s_id:
                    p_unit_extra = RECETARIO[it['fam']]["complemento_peso"][it['tam']]
                else: p_unit_extra = 15
                
                lotes_subs[s_id] = lotes_subs.get(s_id, 0) + (p_unit_extra * it['can'])

    if pag == "📋 Resumen Visual":
        for m_id, items in lotes_masa.items():
            st.subheader(f"🛠️ BATIDO: {m_id}")
            m_dna = ING_DNA[m_id]
            # Suma peso total masa cruda
            tot_gr = sum([(RECETARIO[it['fam']]['pesos'][it['tam']] * it['can']) / m_dna.get('_merma',1) for it in items])
            hb = (tot_gr * 100) / sum([v for k,v in m_dna.items() if not k.startswith('_')])
            
            ca, cb = st.columns([0.3, 0.7])
            with ca: 
                st.write(f"Masa Total: **{tot_gr:,.0f}g**")
                for k,v in m_dna.items(): 
                    if not k.startswith('_'): st.caption(f"{k}: {(v*hb/100):,.1f}g"); master_compra[k] = master_compra.get(k,0) + (v*hb/100)
            with cb:
                for it in items: st.success(f"{it['can']}x {it['esp']} ({it['tam']}) — {it['cliente']}")

    elif pag == "🥣 Producción":
        st.header("🥣 Amasado y Pesado")
        cl_m, cl_s = st.columns(2)
        with cl_m:
            st.write("### Batidos de Masa")
            for m_id, items in lotes_masa.items():
                m_dna = ING_DNA[m_id]
                batch_g = sum([(RECETARIO[it['fam']]['pesos'][it['tam']] * it['can']) for it in items])
                hb_p = (batch_g*100) / sum([v for k,v in m_dna.items() if not k.startswith('_')])
                st.write(f"**Lote: {m_id}**")
                # Solo una caja suave por lote para checklist
                st.markdown(f'<div class="etapa-box" style="background-color:rgba(212, 163, 115, 0.2)"><b>INGR. MASA TOTAL ({batch_g:,.0f}g)</b>', unsafe_allow_html=True)
                for k,v in m_dna.items():
                    if not k.startswith('_'): st.checkbox(f"{k}: {(v*hb_p/100):,.1f}g", key=f"p_{m_id}_{k}_{v}")
                st.markdown('</div>', unsafe_allow_html=True)

        with cl_s:
            st.write("### Complementos (Lágrimas/Rellenos)")
            for s_id, pt in lotes_subs.items():
                if s_id not in ING_DNA: continue
                s_dna = ING_DNA[s_id]
                st.write(f"**{s_id}**")
                st.markdown(f'<div class="etapa-box" style="background-color:rgba(168, 230, 173, 0.2)"><b>BOWL ({pt:,.0f}g)</b>', unsafe_allow_html=True)
                fact = pt / sum(s_dna.values())
                for k,v in s_dna.items(): 
                    st.checkbox(f"{k}: {(v*fact):,.1f}g", key=f"s_{s_id}_{k}")
                    master_compra[k] = master_compra.get(k, 0) + (v*fact)
                st.markdown('</div>', unsafe_allow_html=True)

    elif pag == "📞 Gestión Clientes":
        for i, ped in enumerate(st.session_state.comanda):
            with st.container(border=True):
                txt_list = "\n".join([f"• {it['can']}x {it['esp']} ({it['tam']})" for it in ped['items']])
                st.write(f"👤 **{ped['cliente']}**"); st.caption(txt_list)
                u = f"https://wa.me/521{ped['wa']}?text="
                c_btn1, c_btn2 = st.columns(2)
                c_btn1.link_button("✅ CONFIRMAR", u + urllib.parse.quote(f"Hola {ped['cliente']}! Recibimos pedido:\n{txt_list}"))
                c_btn2.link_button("🚀 AVISAR LISTO", u + urllib.parse.quote(f"¡Hola! Tu pan en Panadería Conciencia ya está listo!"))
                if st.button("❌ BORRAR PEDIDO", key=f"f_{i}"): st.session_state.comanda.pop(i); st.rerun()

    elif pag == "🛒 Súper (Total)":
        st.header("Lista de Insumos (Recalculada)")
        # Para forzar cálculo total, barremos comanda
        final_inv = {}
        for mid, items in lotes_masa.items():
            m_dna = DB_MASAS[mid]; m_batch = sum([(RECETARIO[it['fam']]['pesos'][it['tam']] * it['can']) for it in items]); hb_f = (m_batch*100)/sum([v for k,v in m_dna['receta'].items()]);
            for k,v in m_dna['receta'].items(): final_inv[k] = final_inv.get(k,0)+(v*hb_f/100)
        for sid, ptot in lotes_subs.items():
            s_dna = ING_DNA.get(sid, {}); factor_s = ptot / sum(s_dna.values()) if s_dna else 0
            for k,v in s_dna.items(): final_inv[k] = final_inv.get(k,0)+(v*factor_s)
        
        for k, v in sorted(final_inv.items()): st.checkbox(f"{k}: **{v:,.1f}g**", key=f"mstr_{k}")
