import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Calculadora Panadera - Conciencia", layout="wide")
st.title("🥐 Sistema de Producción - Panadería Conciencia")

# --- 1. BASE DE DATOS DE RECETAS ---
RECETAS = {
    "Concha": {
        "factor_masa": 1.963,
        "ingredientes_base_porcentaje": {
            "Harina": 100, "Huevo": 40, "Leche": 24, "Azúcar": 30, 
            "Mantequilla": 40, "Sal": 2.5, "Levadura seca": 1.8, "Vainilla": 2
        },
        "procedimiento": "1. Autólisis (harina, huevo, leche) 20 min. \n2. Agregar levadura + vainilla. \n3. Azúcar en 3 tandas. \n4. Sal. \n5. Desarrollar gluten. \n6. Mantequilla en bloques. \n7. T° final: 24-26°C.",
        "presentaciones": {"Estándar": 95, "Mini": 35}
    }
}

TOPPINGS = {
    "Chocolate": {"Harina": 87.5, "Cacao": 12.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Matcha": {"Harina": 91.5, "Matcha": 8.5, "Azúcar Glass": 100, "Mantequilla": 100},
    "Mazapán": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100, "Mazapán": 66},
    "Vainilla (Base)": {"Harina": 100, "Azúcar Glass": 100, "Mantequilla": 100}
}

# --- INTERFAZ ---
tabs = st.tabs(["📋 Plan de Producción", "🥣 Masas", "✨ Lágrimas/Toppings", "🛒 Lista Maestra"])

# --- PESTAÑA 1: PLAN DE PRODUCCIÓN ---
with tabs[0]:
    st.header("¿Qué vamos a hornear hoy?")
    if 'plan' not in st.session_state:
        st.session_state.plan = []

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        producto = st.selectbox("Producto", list(RECETAS.keys()))
    with col2:
        tipo = st.selectbox("Tamaño", list(RECETAS[producto]["presentaciones"].keys()))
    with col3:
        sabor = st.selectbox("Sabor Lágrima/Topping", list(TOPPINGS.keys()))
    with col4:
        cantidad = st.number_input("Cantidad de piezas", min_value=1, value=10)

    if st.button("Añadir al plan"):
        st.session_state.plan.append({
            "Producto": producto, "Tamaño": tipo, 
            "Sabor": sabor, "Cantidad": cantidad,
            "Peso Unitario": RECETAS[producto]["presentaciones"][tipo]
        })

    if st.session_state.plan:
        st.table(pd.DataFrame(st.session_state.plan))
        if st.button("Limpiar plan"):
            st.session_state.plan = []

# --- LÓGICA DE CÁLCULO ---
total_insumos = {}

def sumar_insumo(nombre, cantidad):
    total_insumos[nombre] = total_insumos.get(nombre, 0) + cantidad

# --- PESTAÑAS DE RESULTADOS ---
if st.session_state.plan:
    with tabs[1]: # MASAS
        st.header("Cálculo de Masas")
        for item in st.session_state.plan:
            receta = RECETAS[item["Producto"]]
            masa_total = item["Cantidad"] * item["Peso Unitario"]
            harina_base = masa_total / receta["factor_masa"]
            
            st.subheader(f"{item['Cantidad']}x {item['Producto']} ({item['Tamaño']})")
            st.write(f"**Masa total necesaria: {masa_total:,.2f}g**")
            
            for ing, porc in receta["ingredientes_base_porcentaje"].items():
                peso = (porc * harina_base) / 100
                st.write(f"- {ing}: {peso:,.2f}g")
                sumar_insumo(ing, peso)
            st.info(f"**Procedimiento:**\n{receta['procedimiento']}")

    with tabs[2]: # LÁGRIMAS
        st.header("Cálculo de Coberturas")
        for item in st.session_state.plan:
            peso_topping_unitario = 30 if item["Tamaño"] == "Estándar" else 10
            topping_total = item["Cantidad"] * peso_topping_unitario
            sabor_receta = TOPPINGS[item["Sabor"]]
            
            suma_porcentajes = sum(sabor_receta.values())
            harina_topping = (topping_total * 100) / suma_porcentajes
            
            st.subheader(f"Lágrima de {item['Sabor']} para {item['Cantidad']} piezas")
            for ing, porc in sabor_receta.items():
                peso = (porc * harina_topping) / 100
                st.write(f"- {ing}: {peso:,.2f}g")
                sumar_insumo(ing, peso)

    with tabs[3]: # LISTA MAESTRA
        st.header("🛒 Lista Total de Insumos")
        df_final = pd.DataFrame(total_insumos.items(), columns=["Ingrediente", "Gramos Totales"])
        st.dataframe(df_final.style.format({"Gramos Totales": "{:,.2f}g"}))
