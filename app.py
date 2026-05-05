import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

st.set_page_config(page_title="Zubi App", layout="wide")
st.title("📊 Zubi People - Imputación de Horas")

# Ruta de la base de datos temporal
ARCHIVO = "datos_temporales.csv"

# Si no existe, la creamos
if not os.path.exists(ARCHIVO):
    df_vacio = pd.DataFrame(columns=["Fecha", "Empleado", "Empresa", "Area", "Horas"])
    df_vacio.to_csv(ARCHIVO, index=False)

# --- FORMULARIO DE IMPUTACIÓN ---
with st.form("mi_formulario", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1: fecha = st.date_input("Fecha", datetime.date.today())
    with col2: empleado = st.selectbox("Empleado", ["María", "Alicia", "Belén", "Pablo", "Alba"])
    with col3: empresa = st.selectbox("Empresa", [
        "Zubi Group Impact", "Zubi Labs Impact", "Matteco", "Kampe", "Zubi Family", 
        "Imagine", "Zubi Capital", "Zubi Capital Asset Management", "Fundación Felisa", 
        "Zubi Cities", "Zeronet", "Parque Felisa", "Social Nest", "Teradx"
    ])
    with col4: area = st.selectbox("Área", ["LAB", "PRL", "ONB", "TEA", "FOR", "EEX", "SEL", "COM"])
    
    horas = st.number_input("Horas invertidas", min_value=0.5, step=0.5)
    submit = st.form_submit_button("Guardar")
    
    if submit:
        nueva_fila = pd.DataFrame({"Fecha": [fecha], "Empleado": [empleado], "Empresa": [empresa], "Area": [area], "Horas": [horas]})
        nueva_fila.to_csv(ARCHIVO, mode='a', header=False, index=False)
        st.success(f"✅ Guardadas {horas}h de {empleado} en {empresa}")

# --- BOTÓN PARA DESHACER ERRORES ---
df_check = pd.read_csv(ARCHIVO)
if not df_check.empty:
    col_vacia, col_boton = st.columns([4, 1])
    with col_boton:
        if st.button("🗑️ Deshacer último registro"):
            # Quitamos la última fila y guardamos
            df_check = df_check.iloc[:-1]
            df_check.to_csv(ARCHIVO, index=False)
            st.rerun() # Recarga la página al instante

st.divider()

# --- DASHBOARD VISUAL ---
try:
    df = pd.read_csv(ARCHIVO)
    if not df.empty:
        
        # 1. Gráfico General Circular por Empresas
        st.subheader("Distribución General por Empresas")
        fig_pie = px.pie(df, values='Horas', names='Empresa', hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.divider()
        
        # 2. Análisis detallado por Empleado
        st.subheader("Análisis de dedicación por Empleado")
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.write("**¿En qué Empresas invierte su tiempo cada empleado?**")
            # Gráfico de barras apiladas por empresa
            fig_empresa = px.bar(df, x='Empleado', y='Horas', color='Empresa', barmode='stack')
            st.plotly_chart(fig_empresa, use_container_width=True)
            
        with col_graf2:
            st.write("**¿Qué Áreas (tareas) absorben a cada empleado?**")
            # Gráfico de barras apiladas por área
            fig_area = px.bar(df, x='Empleado', y='Horas', color='Area', barmode='stack')
            st.plotly_chart(fig_area, use_container_width=True)
            
    else:
        st.info("La base de datos está vacía. Guarda tu primera imputación arriba para ver los gráficos.")
except FileNotFoundError:
    st.warning("Creando base de datos... Actualiza la página en unos segundos.")
