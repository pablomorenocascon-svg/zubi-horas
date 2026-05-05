import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

st.set_page_config(page_title="Zubi App", layout="wide")
st.title("📊 Zubi People - Imputación de Horas")

# Forzamos la ruta exacta dentro del cerebro de Google Colab
ARCHIVO = "/content/datos_temporales.csv"

# Bloque de seguridad: si no existe, lo crea al instante
if not os.path.exists(ARCHIVO):
    df_vacio = pd.DataFrame(columns=["Fecha", "Empleado", "Empresa", "Area", "Horas"])
    df_vacio.to_csv(ARCHIVO, index=False)

# --- FORMULARIO ---
with st.form("mi_formulario", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1: fecha = st.date_input("Fecha", datetime.date.today())
    with col2: empleado = st.selectbox("Empleado", ["María", "Alicia", "Belén", "Pablo", "Alba"])
    with col3: empresa = st.selectbox("Empresa", ["ZUBI GROUP IMPACT", "ZERONET", "MATTECO", "DEVERA"])
    with col4: area = st.selectbox("Área", ["LAB", "PRL", "ONB", "TEA", "FOR", "EEX", "SEL", "COM"])

    horas = st.number_input("Horas invertidas", min_value=0.5, step=0.5)
    submit = st.form_submit_button("Guardar")

    if submit:
        nueva_fila = pd.DataFrame({"Fecha": [fecha], "Empleado": [empleado], "Empresa": [empresa], "Area": [area], "Horas": [horas]})
        nueva_fila.to_csv(ARCHIVO, mode='a', header=False, index=False)
        st.success(f"✅ Guardadas {horas}h de {empleado} en {empresa}")

st.divider()

# --- DASHBOARD (A prueba de errores) ---
try:
    df = pd.read_csv(ARCHIVO)
    if not df.empty:
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.subheader("Esfuerzo por Empresa")
            st.plotly_chart(px.pie(df, values='Horas', names='Empresa'), use_container_width=True)
        with col_graf2:
            st.subheader("Horas por Empleado y Área")
            st.plotly_chart(px.bar(df, x='Empleado', y='Horas', color='Area', barmode='stack'), use_container_width=True)
    else:
        st.info("La base de datos está vacía. Guarda tu primera imputación arriba para ver los gráficos.")
except FileNotFoundError:
    st.warning("Creando base de datos... Actualiza la página en unos segundos.")
