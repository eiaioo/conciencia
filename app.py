import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA (DNA + SOP)
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {
        "receta": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2},
        "merma": 1.0, "SOP": ["1. Autólisis: Mezclar harina, huevo y leche. Reposo 20 min.", "2. Agregar levadura y vainilla.", "3. Incorporar azúcar en 3 tandas.", "4. Agregar sal y desarrollar gluten.", "5. Incorporar mantequilla en bloques.", "6. T° final: 24-26°C. Fermentación bloque: 30-40 min. Retardado: 8-12h."]
    },
    "Masa de Berlinas": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0},
        "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5, 
        "SOP": ["1. Preparar Tangzhong (5% harina) y dejar enfriar.", "2. Amasar hasta 70% de gluten antes de agregar azúcar.", "3. Integrar mantequilla al final.", "4. Fermentación corta. Fritura a 172°C (2.5-3 min por lado)."]
    },
    "Masa Brioche Roles": {
        "receta": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17},
        "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350,
        "SOP": ["1. Mezclar TZ frío con huevo y secos.", "2. Autólisis pasiva 15 min.", "3. Desarrollar gluten antes de azúcar.", "4. Mantequilla en 3 tandas.", "5. DDT 24°C. Bloque 12h a 4°C."]
    },
    "Masa Red Velvet": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao en polvo": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3},
        "merma": 1.0, "tz_ratio": 0.07, "tz_liq": 5,
        "SOP": ["1. Disolver colorante en líquidos.", "2. Mezclar cacao con harina.", "3. Seguir proceso de Brioche Roles.", "4. No buscar sobrevelo extremo."]
    },
    "Masa Brioche Rosca": {
        "receta": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6},
        "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1,
        "SOP": ["1. Preparar TZ 1:1.", "2. Incorporar miel y azahar en fase de aromáticos.", "3. Reposo en bloque extendido 12h a 4°C."]
    },
    "Masa Muerto Tradicional": {
        "receta": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3, "Agua Azahar": 2, "Ralladura Naranja": 1},
        "merma": 1.0, "SOP": ["1. Activar levadura en leche tibia.", "2. Amasar harina y huevos 5-8 min.", "3. Agregar azúcar en 2 partes.", "4. Mantequilla poco a poco.", "5. Sal, azahar y ralladura al final."]
    },
    "Masa Muerto Guayaba": {
        "receta": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5},
        "merma": 1.0, "huesos": True, "SOP": ["1. Mezcla base sin grasa.", "2. Integrar polvo de guayaba tras hidratación inicial.", "3. Mantequilla y sal al final.", "4. Reforzar masa de huesos (+30% harina, +10% yema)."]
    },
    "Mezcla Brownie": {
        "receta": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez Tostada": 140, "Sal escamas": 1.8},
        "merma": 1.0, "fijo": True, "SOP": ["1. Brown Butter: Avellanar mantequilla y pesar 275g finales.", "2. Verter sobre chocolate y emulsionar.", "3. Añadir azúcares vigorosamente 60-90s.", "4. Incorporar huevos sin montar.", "5. Hornear 175°C por 22-26 min."]
    }
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "SOP": ["1. Cremar mantequilla pomada.", "2. Integrar secos.", "3. Mezclar hasta pasta homogénea. No airear."]},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "SOP": ["1. Mezclar cacao con harina.", "2. Seguir proceso de lágrima base."]},
    "Lágrima de Matcha": {"Harina de fuerza": 91.5, "Matcha en polvo": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "SOP": ["1. Tamizar matcha con harina.", "2. Seguir proceso de lágrima base."]},
    "Lágrima de Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik Fresa": 21, "Mantequilla sin sal": 100, "SOP": ["1. Seguir proceso de lágrima base."]},
    "Lágrima de Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66, "SOP": ["1. Integrar el mazapán a la mantequilla antes de los secos."]},
    "Lágrima de Pinole": {"Harina de fuerza": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "SOP": ["1. Seguir proceso de lágrima base."]},
    "Lágrima de Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Galleta Oreo": 25, "SOP": ["1. Triturar oreo finamente e integrar."]},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "Vainilla": 6, "SOP": ["1. Infusionar leche a 70°C.", "2. Temperar yemas con azúcar y fécula.", "3. Cocer a 82-85°C (burbujeo lento).", "4. Emulsionar mantequilla fría al final.", "5. Enfriado rápido a <10°C."]},
    "Crema Pastelera Chocolate": {"Leche entera": 480, "Yemas": 100, "Azúcar": 100, "Fécula de Maíz": 45, "Chocolate 60%": 120, "SOP": ["1. Seguir proceso Vainilla.", "2. Integrar chocolate picado tras retirar del fuego."]},
    "Crema Pastelera Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula de Maíz": 45, "Chocolate Turin": 120, "Mantequilla sin sal": 20, "SOP": ["1. Seguir proceso Vainilla.", "2. Integrar chocolate Turin fuera del fuego."]},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema para batir 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula de Maíz": 24, "Mantequilla sin sal": 16, "Sal": 0.8, "SOP": ["1. Cocer hasta ebullición real (30s) para activar fécula.", "2. Enfriar rápido a contacto."]},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Turin Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1, "SOP": ["1. Fundir cuerpos a 45°C.", "2. Integrar glass y leche caliente (80°C).", "3. Aplicar sobre rol tibio/frío.", "4. Coronar con cabeza de conejo antes de secar."]},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25, "SOP": ["1. Mantequilla punto pomada (18-20°C).", "2. Batir con azúcar y canela hasta pasta densa opaca."]},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2, "Vainilla": 0.5, "SOP": ["1. Hidratar frutos en té caliente y vainilla (20 min).", "2. Drenar y secar perfectamente con papel."]},
    "Inclusión Manzana": {"Orejón de Manzana": 8, "Agua tibia": 2, "SOP": ["1. Picar en cubos 0.5cm.", "2. Hidratar en agua tibia 10 min.", "3. Secar rigurosamente."]},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5, "SOP": ["1. Fundir mantequilla.", "2. Barnizar pan caliente.", "3. Rebozar en azúcar naranja."]}
}

ARBOL = {
    "Conchas": {
        "espec": {"Vainilla": ["Lágrima de Vainilla"], "Chocolate": ["Lágrima de Chocolate"], "Matcha": ["Lágrima de Matcha"], "Fresa": ["Lágrima de Fresa"], "Mazapán": ["Lágrima de Mazapán"], "Oreo": ["Lágrima de Oreo"], "Pinole": ["Lágrima de Pinole"]},
        "tamaños": {"Estándar": 95, "Mini": 35}, "p_ex": {"Estándar": 30, "Mini": 10}, "masa": "Masa de Conchas"
    },
    "Berlinas": {
        "espec": {"Vainilla": ["Crema Pastelera Vainilla"], "Ruby v2.0": ["Crema Ruby 50/50", "Glaseado Ruby"], "Turín": ["Crema Pastelera Especial Turin", "Glaseado Turin"]},
        "tamaños": {"Estándar": 60}, "masa": "Masa de Berlinas",
        "override_p": {"Ruby v2.0": (70, {"Crema Ruby 50/50": 40, "Glaseado Ruby": 8}), "Turín": (60, {"Crema Pastelera Especial Turin": 80, "Glaseado Turin": 16}), "Vainilla": (60, {"Crema Pastelera Vainilla": 80})}
    },
    "Rollos": {
        "espec": {"Tradicional": ["Schmear Canela", "Inclusión Frutos Rojos"], "Manzana": ["Schmear Canela", "Inclusión Manzana"], "Red Velvet": ["Schmear Red Velvet"]},
        "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "override": {"Red Velvet": "Masa Red Velvet"}
    },
    "Rosca de reyes": {
        "espec": {
            "Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate"]},
            "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Pastelera Especial Turin"]}
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
if 'form_key' not in st.session_state: st.session_state.form_key = 0

st.title("🥐 Producción Técnica CONCIENCIA")

with st.expander("📝 Cargar Pedido", expanded=True):
    fk = st.session_state.form_key
    fam = st.selectbox("Familia", ["-"] + list(ARBOL.keys()), key=f"f_{fk}")
    if fam != "-":
        esp = st.selectbox("Especialidad", ["-"] + list(ARBOL[fam]["espec"].keys()), key=f"e_{fk}")
        if esp != "-":
            tam = st.selectbox("Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"t_{fk}")
            rel = "N/A"
            if fam == "Rosca de reyes":
                rel = st.selectbox("Relleno", ARBOL[fam]["espec"][esp]["rellenos"], key=f"r_{fk}")
            cant = st.number_input("Cantidad", min_value=1, value=1, key=f"c_{fk}")
            if st.button("✅ AGREGAR"):
                st.session_state.comanda.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "cant": cant})
                st.session_state.form_key += 1
                st.rerun()

# ==========================================
# 3. MOTOR DE CÁLCULO
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()
    
    # Cálculos previos
    lotes_masa = {}
    total_compras = {}
    sub_recetas_dia = {} # {Nombre: {Ingredientes: Cantidad, SOP: []}}

    for item in st.session_state.comanda:
        m_id = ARBOL[item['fam']].get("override", {}).get(item['esp'], ARBOL[item['fam']]['masa'])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    # Identificar nombres de pestañas dinámicas
    active_masses = sorted(list(lotes_masa.keys()))
    
    # Recolectar sub-recetas activas
    for item in st.session_state.comanda:
        cfg = ARBOL[item['fam']]
        subs = cfg["espec"][item['esp']]
        lista = subs["fijos"].copy() if isinstance(subs, dict) else subs.copy()
        if item['rel'] not in ["N/A", "Sin Relleno"]: lista.append(item['rel'])
        
        for s_id in lista:
            if s_id not in sub_recetas_dia: sub_recetas_dia[s_id] = {"ingredientes": {}, "cant_piezas": 0}
            sub_recetas_dia[s_id]["cant_piezas"] += item['cant']
            
            # Calcular peso necesario para esta sub-receta
            if item['fam'] == "Rosca de reyes" and s_id == item['rel']: p_u = cfg["p_relleno_map"][item['tam']]
            elif item['fam'] == "Conchas": p_u = cfg["p_ex"][item['tam']]
            elif "override_p" in cfg and item['esp'] in cfg["override_p"]: p_u = cfg["override_p"][item['esp']][1].get(s_id, 15)
            else: p_u = 15
            
            p_batch = p_u * item['cant']
            s_rec = DB_COMPLEMENTOS[s_id]
            fact = p_batch / sum([v for k,v in s_rec.items() if k != "SOP"])
            for ing, val in s_rec.items():
                if ing != "SOP":
                    gr = val * (item['cant'] if "Rebozado" in s_id or "Decoración" in s_id else fact)
                    sub_recetas_dia[s_id]["ingredientes"][ing] = sub_recetas_dia[s_id]["ingredientes"].get(ing, 0) + gr
                    total_compras[ing] = total_compras.get(ing, 0) + gr

    # PESTAÑAS
    tabs = st.tabs(["🛒 Lista Maestra"] + active_masses + sorted(list(sub_recetas_dia.keys())))

    # T1: LISTA MAESTRA
    with tabs[0]:
        st.header("📦 Lista Consolidada de Surtido")
        # Sumar masas al total de compras aquí
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            m_batch = sum([(ARBOL[i['fam']].get("override_p", {}).get(i['esp'], (ARBOL[i['fam']]['tamaños'][i['tam']], 0))[0] * i['cant']) / m_dna['merma'] for i in items])
            h_base = (m_batch * 100) / sum([v for k,v in m_dna['receta'].items()])
            for ing, porc in m_dna['receta'].items():
                total_compras[ing] = total_compras.get(ing, 0) + (porc * h_base / 100)
            if m_dna.get("huesos"):
                total_compras["Harina de fuerza"] = total_compras.get("Harina de fuerza", 0) + (m_batch * 0.25 * 0.3)
                total_compras["Yemas"] = total_compras.get("Yemas", 0) + (m_batch * 0.25 * 0.1)

        sorted_items = sorted(total_compras.items())
        for insumo, cantidad in sorted_items:
            c1, c2 = st.columns([0.05, 0.95])
            if c1.checkbox("", key=f"main_{insumo}"):
                c2.markdown(f"~~{insumo}: {cantidad:,.1f}g~~")
            else:
                c2.write(f"**{insumo}:** {cantidad:,.1f}g")

    # T-MASAS
    for i, m_id in enumerate(active_masses):
        with tabs[i+1]:
            st.header(f"🥣 Receta: {m_id}")
            m_dna = DB_MASAS[m_id]
            items = lotes_masa[m_id]
            m_batch = sum([(ARBOL[it['fam']].get("override_p", {}).get(it['esp'], (ARBOL[it['fam']]['tamaños'][it['tam']], 0))[0] * it['cant']) / m_dna['merma'] for it in items])
            h_base = (m_batch * 100) / sum([v for k,v in m_dna['receta'].items()])
            
            st.subheader(f"Peso Total del Batido: {m_batch:,.1f}g")
            st.caption(" | ".join([f"{it['cant']}x {it['esp']} {it['tam']}" for it in items]))
            
            for ing, porc in m_dna['receta'].items():
                c1, c2 = st.columns([0.05, 0.95])
                gr = porc * h_base / 100
                if c1.checkbox("", key=f"check_{m_id}_{ing}"):
                    c2.markdown(f"~~{ing}: {gr:,.1f}g~~")
                else:
                    c2.write(f"**{ing}:** {gr:,.1f}g")
            
            st.markdown("### 📝 Instrucciones de Proceso")
            for step in m_dna["SOP"]: st.write(step)

    # T-SUBRECETAS
    start_idx = 1 + len(active_masses)
    for i, (s_id, data) in enumerate(sorted(sub_recetas_dia.items())):
        with tabs[start_idx + i]:
            st.header(f"✨ Sub-receta: {s_id}")
            st.subheader(f"Para {data['cant_piezas']} piezas")
            
            for ing, gr in data['ingredientes'].items():
                c1, c2 = st.columns([0.05, 0.95])
                if c1.checkbox("", key=f"sub_{s_id}_{ing}"):
                    c2.markdown(f"~~{ing}: {gr:,.1f}g~~")
                else:
                    c2.write(f"**{ing}:** {gr:,.1f}g")
            
            st.markdown("### 📝 Instrucciones")
            for step in DB_COMPLEMENTOS[s_id]["SOP"]: st.write(step)
