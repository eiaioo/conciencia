import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA (DNA + SOP)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "merma": 1.0, "factor_panadero": 1.963, "SOP": ["1. Autólisis: Harina, huevo, leche (20 min).", "2. Levadura + Vainilla.", "3. Azúcar en 3 tandas.", "4. Sal y desarrollar gluten.", "5. Mantequilla en bloques.", "6. T° final: 24-26°C."]
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5, "SOP": ["1. Preparar TZ (5% harina) y enfriar.", "2. Amasar hasta 70% gluten antes de azúcar.", "3. Mantequilla al final.", "4. Fritura a 172°C."]
    },
    "Masa Brioche Roles": {
        "receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17},
        "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350, "SOP": ["1. TZ frío + Huevo + Secos.", "2. Autólisis 15 min.", "3. Gluten antes de azúcar.", "4. Mantequilla en 3 tandas.", "5. DDT 24°C."]
    },
    "Masa Red Velvet": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao en polvo": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3},
        "merma": 1.0, "tz_ratio": 0.07, "tz_liq": 5, "SOP": ["1. Colorante en líquidos.", "2. Cacao en secos.", "3. Proceso Brioche Master."]
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1, "SOP": ["1. TZ 1:1.", "2. Miel y Azahar al final.", "3. Bloque 12h a 4°C."]
    },
    "Masa Muerto Tradicional": {
        "receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3, "Agua Azahar": 2, "Ralladura Naranja": 1},
        "merma": 1.0, "SOP": ["1. Activar levadura.", "2. Amasar harina/huevo 5-8 min.", "3. Azúcar en 2 partes.", "4. Mantequilla poco a poco.", "5. Sal y aromas al final."]
    },
    "Masa Muerto Guayaba": {
        "receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5},
        "merma": 1.0, "huesos": True, "SOP": ["1. Integrar guayaba tras hidratación inicial.", "2. Reforzar huesos (+30% Harina, +10% Yema)."]
    },
    "Mezcla Brownie": {
        "receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa alcalinizada": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez Tostada": 140, "Sal escamas": 1.8},
        "merma": 1.0, "fijo": True, "SOP": ["1. Brown Butter (275g).", "2. Mezclar con choco.", "3. Azúcares 90s.", "4. Huevos sin montar.", "5. 175°C (22-26 min)."]
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "SOP": "Cremar pomada + secos."},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "SOP": "Cacao con harina + proceso base."},
    "Lágrima de Matcha": {"Harina de fuerza": 91.5, "Matcha en polvo": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "SOP": "Matcha con harina + proceso base."},
    "Lágrima de Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik Fresa": 21, "Mantequilla sin sal": 100, "SOP": "Proceso base."},
    "Lágrima de Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66, "SOP": "Mazapán a mantequilla antes de secos."},
    "Lágrima de Pinole": {"Harina de fuerza": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "SOP": "Proceso base."},
    "Lágrima de Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Galleta Oreo": 25, "SOP": "Oreo triturada final."},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "Vainilla": 6, "SOP": "82-85°C. Emulsión mantequilla al final."},
    "Crema Pastelera Chocolate": {"Leche entera": 480, "Yemas": 100, "Azúcar": 100, "Fécula de Maíz": 45, "Chocolate 60%": 120, "SOP": "Chocolate post-fuego."},
    "Crema Pastelera Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula de Maíz": 45, "Chocolate Turin": 120, "Mantequilla sin sal": 20, "SOP": "Chocolate Turin fuera del fuego."},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema para batir 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula de Maíz": 24, "Mantequilla sin sal": 16, "Sal fina": 0.8, "SOP": "Ebullición real 30s."},
    "Glaseado Turin": {"Azúcar Glass": 200, "Choco Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1, "SOP": "Choco 45°C + Leche 80°C. Coronar con cabeza."},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25, "SOP": "Pasta densa opaca (pomada)."},
    "Schmear Red Velvet": {"Mantequilla sin sal": 6, "Azúcar": 6, "Cacao": 1.8, "Nuez": 4, "Chocolate amargo": 4, "SOP": "Integrar todo hasta pasta."},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2, "Vainilla": 0.5, "SOP": "Hidratar en té caliente 20m. Secar."},
    "Inclusión Manzana": {"Orejón de Manzana": 8, "Agua tibia": 2, "SOP": "Hidratar 10m. Secar."},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5, "SOP": "Barnizar caliente + azúcar naranja."},
    "Decoración Rosca": {"Ate": 50, "Higo": 20, "Cereza": 10, "SOP": "Colocación tradicional."}
}

ARBOL = {
    "Conchas": {
        "espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"], "Matcha": ["Lágrima de Matcha"], "Fresa": ["Lágrima de Fresa"], "Mazapán": ["Lágrima de Mazapán"], "Oreo": ["Lágrima de Oreo"], "Pinole": ["Lágrima de Pinole"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"
    },
    "Berlinas": {
        "espec": {"Vainilla": ["Crema Pastelera Vainilla"], "Ruby v2.0": ["Crema Ruby 50/50", "Glaseado de Chocolate Ruby"], "Turín": ["Crema Pastelera Turin", "Glaseado Turin"]},
        "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas",
        "override_p": {"Ruby v2.0": (70, {"Crema Ruby 50/50": 40, "Glaseado de Chocolate Ruby": 8}), "Turín": (60, {"Crema Pastelera Turin": 80, "Glaseado Turin": 16}), "Vainilla": (60, {"Crema Pastelera Vainilla": 80})}
    },
    "Rollos": {
        "espec": {"Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"], "Manzana": ["Schmear Canela", "Inclusión Manzana"], "Red Velvet": ["Schmear Red Velvet"]},
        "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "override": {"Red Velvet": "Masa Red Velvet"}
    },
    "Rosca de reyes": {
        "espec": {
            "Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate"]},
            "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Pastelera Turin"]}
        },
        "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90},
        "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25},
        "masa": "Masa Brioche Rosca"
    },
    "Pan de muerto": {
        "espec": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto"]},
        "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "override": {"Guayaba": "Masa Muerto Guayaba"}
    },
    "Brownies": {"espec": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla Brownie"}
}

# ==========================================
# 2. LÓGICA DE INTERFAZ
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_id' not in st.session_state: st.session_state.form_id = 0

st.title("🥐 Gestión Técnica CONCIENCIA")

with st.expander("📝 Cargar Nuevo Producto", expanded=True):
    fk = st.session_state.form_id
    fam = st.selectbox("1. Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if fam != "-":
        esp = st.selectbox("2. Especialidad", ["-"] + list(ARBOL[fam]["espec"].keys()), key=f"e_{fk}")
        if esp != "-":
            tam = st.selectbox("3. Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{fk}")
            rel = "N/A"
            if fam == "Rosca de reyes":
                rel = st.selectbox("4. Relleno", ARBOL[fam]["espec"][esp]["rellenos"], key=f"r_{fk}")
            cant = st.number_input("5. Cantidad", min_value=1, value=1, key=f"c_{fk}")
            if st.button("✅ AGREGAR"):
                st.session_state.comanda.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "cant": cant})
                st.session_state.form_id += 1
                st.rerun()

# ==========================================
# 3. MOTOR DE CÁLCULO
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()

    # --- Cálculos Consolidados ---
    lotes_masa = {}
    sub_recetas_dia = {}
    compras_totales = {}

    for item in st.session_state.comanda:
        m_id = ARBOL[item['fam']].get("override", {}).get(item['esp'], ARBOL[item['fam']]['masa'])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    # Procesar todo antes de mostrar
    for m_id, items in lotes_masa.items():
        m_dna = DB_MASAS[m_id]
        m_batch_gr = sum([(ARBOL[i['fam']].get("override_p", {}).get(i['esp'], (ARBOL[i['fam']]['tamaños'][i['tam']],0))[0] * i['cant']) / m_dna['merma'] for i in items])
        h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
        for ing, porc in m_dna['receta'].items():
            compras_totales[ing] = compras_totales.get(ing, 0) + (porc * h_base / 100)
        if m_dna.get("huesos"):
            compras_totales["Harina de fuerza"] = compras_totales.get("Harina de fuerza", 0) + (m_batch_gr * 0.25 * 0.3)
            compras_totales["Yemas"] = compras_totales.get("Yemas", 0) + (m_batch_gr * 0.25 * 0.1)

    for item in st.session_state.comanda:
        cfg = ARBOL[item['fam']]
        subs = cfg["espec"][item['esp']]
        lista = subs["fijos"].copy() if isinstance(subs, dict) else subs.copy()
        if item['rel'] not in ["N/A", "Sin Relleno"]: lista.append(item['rel'])
        
        for s_id in lista:
            if s_id not in sub_recetas_dia: sub_recetas_dia[s_id] = {"ing": {}, "piezas": 0}
            sub_recetas_dia[s_id]["piezas"] += item['cant']
            
            # Peso unitario extra
            if item['fam'] == "Rosca de reyes" and s_id == item['rel']: p_u = cfg["p_relleno_map"][item['tam']]
            elif item['fam'] == "Conchas": p_u = cfg["p_ex"][item['tam']]
            elif "override_p" in cfg and item['esp'] in cfg["override_p"]: p_u = cfg["override_p"][item['esp']][1].get(s_id, 15)
            else: p_u = 15
            
            p_batch = p_u * item['cant']
            s_rec = {k: v for k, v in DB_COMPLEMENTOS[s_id].items() if k != "SOP"}
            fact = p_batch / sum(s_rec.values())
            for ing, val in s_rec.items():
                gr = val * (item['cant'] if "Rebozado" in s_id or "Decoración" in s_id else fact)
                sub_recetas_dia[s_id]["ing"][ing] = sub_recetas_dia[s_id]["ing"].get(ing, 0) + gr
                compras_totales[ing] = compras_totales.get(ing, 0) + gr

    # --- PESTAÑAS ---
    tabs = st.tabs(["📋 Resumen Visual", "🛒 Lista Maestra"] + list(lotes_masa.keys()) + sorted(list(sub_recetas_dia.keys())))

    # T1: RESUMEN (La pantalla que querías de vuelta)
    with tabs[0]:
        for m_id, items in lotes_masa.items():
            st.markdown(f"### 🛠️ Batido: {m_id}")
            m_dna = DB_MASAS[m_id]
            m_batch_gr = sum([(ARBOL[it['fam']].get("override_p", {}).get(it['esp'], (ARBOL[it['fam']]['tamaños'][it['tam']],0))[0] * it['cant']) / m_dna['merma'] for it in items])
            h_base = (m_batch_gr * 100) / sum([v for k,v in m_dna['receta'].items()])
            
            cols = st.columns(1 + len(items))
            with cols[0]:
                st.info(f"**Masa (Total: {m_batch_gr:,.1f}g)**")
                for ing, porc in m_dna['receta'].items():
                    st.write(f"• {ing}: {porc*h_base/100:,.1f}g")
            
            for idx, it in enumerate(items):
                with cols[idx+1]:
                    st.success(f"**{it['esp']} ({it['tam']})**")
                    # Aquí mostramos los complementos de ese item específico
                    subs_item = ARBOL[it['fam']]["espec"][it['esp']]
                    lista_it = subs_item["fijos"].copy() if isinstance(subs_item, dict) else subs_item.copy()
                    if it['rel'] not in ["N/A", "Sin Relleno"]: lista_it.append(it['rel'])
                    
                    for s_id in lista_it:
                        if it['fam'] == "Rosca de reyes" and s_id == it['rel']: p_u = ARBOL[it['fam']]["p_relleno_map"][it['tam']]
                        elif it['fam'] == "Conchas": p_u = ARBOL[it['fam']]["p_ex"][it['tam']]
                        else: p_u = 15
                        st.markdown(f"*{s_id} ({p_u*it['cant']:,.1f}g)*")

    # T2: LISTA MAESTRA
    with tabs[1]:
        st.header("📦 Surtido de Almacén")
        for insumo, cant in sorted(compras_totales.items()):
            c1, c2 = st.columns([0.05, 0.95])
            if c1.checkbox("", key=f"main_{insumo}"):
                c2.markdown(f"~~{insumo}: {cant:,.1f}~~")
            else: c2.write(f"**{insumo}:** {cant:,.1f}")

    # T-MASAS (Detalle + SOP)
    for i, m_id in enumerate(lotes_masa.keys()):
        with tabs[i+2]:
            st.header(f"🥣 Receta Detallada: {m_id}")
            m_dna = DB_MASAS[m_id]
            # Recalcular base para esta pestaña
            m_batch = sum([(ARBOL[it['fam']].get("override_p", {}).get(it['esp'], (ARBOL[it['fam']]['tamaños'][it['tam']],0))[0] * it['cant']) / m_dna['merma'] for it in lotes_masa[m_id]])
            h_b = (m_batch * 100) / sum(m_dna['receta'].values())
            
            for ing, porc in m_dna['receta'].items():
                c1, c2 = st.columns([0.05, 0.95])
                if c1.checkbox(f"{ing}", key=f"det_{m_id}_{ing}"):
                    c2.markdown(f"~~{ing}: {porc*h_b/100:,.1f}g~~")
                else: c2.write(f"**{ing}:** {porc*h_b/100:,.1f}g")
            st.info("### 📝 Procedimiento (SOP)")
            for s in m_dna["SOP"]: st.write(s)

    # T-SUBRECETAS (Detalle + SOP)
    offset = 2 + len(lotes_masa)
    for i, (s_id, data) in enumerate(sorted(sub_recetas_dia.items())):
        with tabs[offset + i]:
            st.header(f"✨ Sub-receta: {s_id}")
            for ing, gr in data['ing'].items():
                c1, c2 = st.columns([0.05, 0.95])
                if c1.checkbox(f"{ing}", key=f"sub_det_{s_id}_{ing}"):
                    c2.markdown(f"~~{ing}: {gr:,.1f}g~~")
                else: c2.write(f"**{ing}:** {gr:,.1f}g")
            st.warning(f"### 📝 SOP: {DB_COMPLEMENTOS[s_id]['SOP']}")
