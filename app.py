import streamlit as st
import pandas as pd

st.set_page_config(page_title="CONCIENCIA - Sistema Maestro", layout="wide")

# ==========================================
# 1. BASE DE DATOS TÉCNICA DEFINITIVA
# ==========================================

DB_MASAS = {
    "Masa de Conchas": {"Harina de fuerza": 100, "Huevo": 40, "Leche entera": 24, "Azúcar": 30, "Mantequilla sin sal": 40, "Sal fina": 2.5, "Levadura seca": 1.8, "Vainilla": 2, "merma": 1.0},
    "Masa de Berlinas": {"Harina de fuerza": 100, "Azúcar": 22, "Mantequilla sin sal": 20, "Huevo": 25, "Leche entera": 22, "Sal fina": 1.8, "Levadura seca": 1.0, "merma": 0.85, "tz_ratio": 0.05, "tz_liq": 5},
    "Masa Brioche Roles": {"Harina de fuerza": 93, "Huevo": 30, "Leche entera": 5, "Levadura fresca": 1, "Sal fina": 1.8, "Azúcar": 16, "Mantequilla sin sal": 17, "merma": 1.0, "tz_fijo_h": 70, "tz_fijo_l": 350},
    "Masa Red Velvet": {"Harina de fuerza": 100, "Azúcar": 16, "Mantequilla sin sal": 17, "Huevo": 30, "Leche entera": 4, "Sal fina": 1.8, "Levadura instantánea": 1.0, "Cacao en polvo": 0.8, "Colorante Rojo": 0.7, "Vinagre": 0.3, "merma": 1.0, "tz_ratio": 0.07, "tz_liq": 5},
    "Masa Brioche Rosca": {"Harina de fuerza": 100, "Azúcar": 25, "Miel": 3, "Mantequilla sin sal": 30, "Huevo": 20, "Yemas": 4, "Leche entera": 24, "Levadura fresca": 0.35, "Sal fina": 2.2, "Agua Azahar": 0.6, "merma": 1.0, "tz_ratio": 0.025, "tz_liq": 1},
    "Masa Muerto Tradicional": {"Harina de fuerza": 100, "Leche entera": 25, "Yemas": 24, "Claras": 16, "Azúcar": 20, "Mantequilla sin sal": 25, "Sal fina": 2, "Levadura fresca": 3, "Agua Azahar": 2, "Ralladura Naranja": 1, "merma": 1.0},
    "Masa Muerto Guayaba": {"Harina de fuerza": 100, "Leche entera": 30, "Yemas": 18, "Claras": 12, "Azúcar": 20, "Mantequilla sin sal": 25, "Levadura fresca": 5, "Sal fina": 1.8, "Polvo de Guayaba": 5, "merma": 1.0, "huesos_refuerzo": True},
    "Mezcla de Brownies": {"Mantequilla sin sal": 330, "Azúcar Blanca": 275, "Azúcar Mascabada": 120, "Chocolate Turin Amargo": 165, "Harina de fuerza": 190, "Cocoa alcalinizada": 75, "Sal fina": 8, "Claras": 160, "Yemas": 95, "Vainilla": 8, "Nuez Tostada": 140, "Sal escamas": 1.8, "merma": 1.0, "fijo": True}
}

DB_COMPLEMENTOS = {
    "Lágrima de Vainilla": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Chocolate": {"Harina de fuerza": 87.5, "Cacao en polvo": 12.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Matcha": {"Harina de fuerza": 91.5, "Matcha en polvo": 8.5, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Fresa": {"Harina de fuerza": 100, "Azúcar Glass": 79, "Nesquik Fresa": 21, "Mantequilla sin sal": 100},
    "Lágrima de Mazapán": {"Harina de fuerza": 100, "Azúcar Glass": 100, "Mantequilla sin sal": 100, "Mazapán": 66},
    "Lágrima de Pinole": {"Harina de fuerza": 79, "Pinole": 21, "Azúcar Glass": 100, "Mantequilla sin sal": 100},
    "Lágrima de Oreo": {"Harina de fuerza": 100, "Azúcar Glass": 75, "Mantequilla sin sal": 100, "Galleta Oreo": 25},
    "Crema Pastelera Vainilla": {"Leche entera": 500, "Yemas": 100, "Azúcar": 120, "Fécula de Maíz": 45, "Mantequilla sin sal": 30, "Vainilla": 6},
    "Crema Pastelera Chocolate": {"Leche entera": 480, "Yemas": 100, "Azúcar": 100, "Fécula de Maíz": 45, "Chocolate 60%": 120},
    "Crema Pastelera Especial Turin": {"Leche entera": 450, "Yemas": 100, "Azúcar": 90, "Fécula de Maíz": 45, "Chocolate Turin": 120, "Mantequilla sin sal": 20},
    "Crema Ruby 50/50": {"Leche entera": 131.5, "Crema para batir 35%": 131.5, "Yemas": 53, "Azúcar": 63, "Fécula de Maíz": 24, "Mantequilla sin sal": 16, "Sal": 0.8},
    "Glaseado Ruby": {"Chocolate Ruby": 80, "Azúcar Glass": 160, "Leche entera": 50},
    "Glaseado Turin": {"Azúcar Glass": 200, "Chocolate Turin Cuerpos": 100, "Leche entera": 50, "Cabeza de Conejo": 1},
    "Decoración Tradicional Rosca": {"Ate de colores": 50, "Higo en almíbar": 20, "Cereza marrasquino": 10},
    "Decoración Nuez": {"Nuez Fileteada": 15},
    "Schmear Canela": {"Mantequilla sin sal": 200, "Azúcar Mascabada": 300, "Canela": 25},
    "Schmear Red Velvet": {"Mantequilla sin sal": 6, "Azúcar": 6, "Cacao": 1.8, "Nuez": 4, "Chocolate amargo": 4},
    "Rebozado Muerto": {"Mantequilla sin sal": 6.5, "Azúcar": 12.5},
    "Inclusión Frutos Rojos": {"Pasas": 4, "Arándanos": 4, "Té Earl Grey": 2, "Vainilla": 0.5},
    "Inclusión Manzana": {"Orejón de Manzana": 8, "Agua tibia": 2}
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
        "tamaños": {"Individual": 90}, "masa": "Masa Brioche Roles", "p_ex": 15, "masa_ov": {"Red Velvet": "Masa Red Velvet"}
    },
    "Rosca de reyes": {
        "espec": {
            "Tradicional": {"fijos": ["Lágrima de Vainilla", "Decoración Tradicional Rosca"], "rellenos": ["Sin Relleno", "Crema Pastelera Vainilla", "Crema Pastelera Chocolate"]},
            "Turín": {"fijos": ["Lágrima de Chocolate", "Glaseado Turin"], "rellenos": ["Sin Relleno", "Crema Pastelera Especial Turin"]}
        },
        "tamaños": {"FAMILIAR": 1450, "MEDIANA": 650, "MINI": 120, "CONCHA-ROSCA": 90},
        "p_relleno_map": {"FAMILIAR": 450, "MEDIANA": 200, "MINI": 35, "CONCHA-ROSCA": 25},
        "masa": "Masa Brioche Rosca"
    },
    "Pan de muerto": {
        "espec": {"Tradicional": ["Rebozado Muerto"], "Guayaba": ["Rebozado Muerto"]},
        "tamaños": {"Estándar": 85}, "masa": "Masa Muerto Tradicional", "p_ex": 1, "masa_ov": {"Guayaba": "Masa Muerto Guayaba"}
    },
    "Brownies": {"espec": {"Chocolate": []}, "tamaños": {"Molde 20x20": 1}, "masa": "Mezcla de Brownies"}
}

# ==========================================
# 2. LÓGICA DE INTERFAZ (RESET AUTOMÁTICO)
# ==========================================

if 'comanda' not in st.session_state: st.session_state.comanda = []
if 'form_key' not in st.session_state: st.session_state.form_key = 0

st.title("🥐 Gestión Técnica CONCIENCIA")

with st.expander("📝 Cargar Nuevo Producto", expanded=True):
    fk = st.session_state.form_key
    fam = st.selectbox("1. Familia", ["-"] + list(ARBOL.keys()), key=f"fam_{fk}")
    
    if fam != "-":
        esp = st.selectbox("2. Especialidad", ["-"] + list(ARBOL[fam]["espec"].keys()), key=f"esp_{fk}")
        if esp != "-":
            tam = st.selectbox("3. Tamaño", list(ARBOL[fam]["tamaños"].keys()), key=f"tam_{fk}")
            
            rel = "N/A"
            if fam == "Rosca de reyes":
                rel = st.selectbox("4. Relleno", ARBOL[fam]["espec"][esp]["rellenos"], key=f"rel_{fk}")
            
            cant = st.number_input("5. Cantidad", min_value=1, value=1, key=f"cant_{fk}")
            
            if st.button("✅ AGREGAR"):
                st.session_state.comanda.append({"fam": fam, "esp": esp, "tam": tam, "rel": rel, "cant": cant})
                st.session_state.form_key += 1 # Resetea los menús
                st.rerun()

# ==========================================
# 3. LÓGICA DE PRODUCCIÓN (BATCHES)
# ==========================================

if st.session_state.comanda:
    if st.button("🗑️ Limpiar Todo"): st.session_state.comanda = []; st.rerun()
    t_pes, t_sup = st.tabs(["🥣 Hoja de Producción", "📦 Lista Maestra"])
    master_inv = {}

    lotes_masa = {}
    for item in st.session_state.comanda:
        m_id = ARBOL[item['fam']].get("masa_ov", {}).get(item['esp'], ARBOL[item['fam']]['masa'])
        if m_id not in lotes_masa: lotes_masa[m_id] = []
        lotes_masa[m_id].append(item)

    with t_pes:
        for m_id, items in lotes_masa.items():
            m_dna = DB_MASAS[m_id]
            st.markdown(f"## 🛠️ Lote de Masa: {m_id}")
            
            # --- CALCULO MASA TOTAL ---
            batch_masa_gr = 0
            for i in items:
                p_u = ARBOL[i['fam']].get("override_p", {}).get(i['esp'], (ARBOL[i['fam']]['tamaños'][i['tam']], 0))[0]
                batch_masa_gr += (p_u * i['cant']) / m_dna['merma']
            
            # Suma de porcentajes excluyendo mermas y configs
            sum_porc = sum([v for k,v in m_dna.items() if isinstance(v, (int, float)) and "_" not in k and k != "merma" and k != "factor"])
            h_base = (batch_masa_gr * 100) / sum_porc

            # Agrupar complementos por sabor/especialidad
            sabores_batch = {}
            for i in items:
                key = (i['esp'], i['rel'], i['tam'])
                if key not in sabores_batch: sabores_batch[key] = []
                sabores_batch[key].append(i)

            cols = st.columns(1 + len(sabores_batch))
            with cols[0]:
                st.info("**🥣 MASA**")
                if m_dna.get("fijo"):
                    for ing, val in m_dna.items():
                        if isinstance(val, (int, float)) and "_" not in ing and ing != "merma" and ing != "fijo":
                            total = val * sum(it['cant'] for it in items)
                            st.write(f"• {ing}: {total:,.1f}g")
                            master_inv[ing] = master_inv.get(ing, 0) + total
                else:
                    for ing, porc in m_dna.items():
                        if isinstance(porc, (int, float)) and "_" not in ing and ing != "merma" and ing != "factor":
                            gr = (porc * h_base) / 100; st.write(f"• {ing}: **{gr:,.1f}g**")
                            master_inv[ing] = master_inv.get(ing, 0) + gr
                    if "tz_ratio" in m_dna: st.warning(f"⚡ TZ: {(h_base*m_dna['tz_ratio']):,.1f}g H / {(h_base*m_dna['tz_ratio']*m_dna['tz_liq']):,.1f}g L")
                    if "tz_fijo_h" in m_dna:
                        f_tz = h_base / 1000
                        st.warning(f"⚡ TZ: {(m_dna['tz_fijo_h']*f_tz):,.1f}g H / {(m_dna['tz_fijo_l']*f_tz):,.1f}g L")
                    if m_dna.get("huesos_refuerzo"):
                        r = batch_masa_gr * 0.25
                        st.info(f"🦴 Huesos: +{r*0.3:,.1f}g H / +{r*0.1:,.1f}g Y")
                        master_inv["Harina de fuerza"] = master_inv.get("Harina de fuerza", 0) + (r*0.3)
                        master_inv["Yemas"] = master_inv.get("Yemas", 0) + (r*0.1)

            for idx, ((e_name, r_name, t_name), s_items) in enumerate(sabores_batch.items()):
                with cols[idx+1]:
                    tot_p = sum(si['cant'] for si in s_items)
                    st.success(f"✨ **{e_name} ({t_name})**")
                    
                    cfg = ARBOL[s_items[0]['fam']]
                    list_subs = []
                    # Manejar diccionarios o listas de especialidad
                    base_espec = cfg["espec"][e_name]
                    if isinstance(base_espec, dict): list_subs = base_espec["fijos"].copy()
                    else: list_subs = base_espec.copy()
                    
                    if r_name not in ["N/A", "Sin Relleno"]: list_subs.append(r_name)

                    for sub_id in list_subs:
                        st.write(f"**{sub_id}**")
                        s_rec = DB_COMPLEMENTOS[sub_id]
                        # Calcular peso total de la sub-receta
                        if s_items[0]['fam'] == "Rosca de reyes" and sub_id == r_name: p_u_ex = cfg["p_relleno_map"][t_name]
                        elif s_items[0]['fam'] == "Conchas": p_u_ex = cfg["p_ex"][t_name]
                        elif "override_p" in cfg and e_name in cfg["override_p"]: p_u_ex = cfg["override_p"][e_name][1].get(sub_id, 15)
                        else: p_u_ex = 15
                        
                        fact = (p_u_ex * tot_p) / sum([v for v in s_rec.values() if isinstance(v, (int, float))])
                        for ing, val in s_rec.items():
                            if "Cabeza" in ing:
                                st.write(f"- {ing}: {val*tot_p} pz"); master_inv[ing] = master_inv.get(ing, 0) + (val*tot_p)
                            else:
                                gr_sub = val * (tot_p if "Rebozado" in sub_id or "Decoración" in sub_id else fact)
                                st.write(f"- {ing}: {gr_sub:,.1f}g"); master_inv[ing] = master_inv.get(ing, 0) + gr_sub
            st.divider()

    with t_sup:
        st.header("🛒 Lista Maestra")
        df_sum = pd.DataFrame(master_inv.items(), columns=["Insumo", "Total"]).round(1)
        st.dataframe(df_sum.sort_values("Insumo"), hide_index=True, use_container_width=True)
