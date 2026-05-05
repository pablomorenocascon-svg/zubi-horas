import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

st.set_page_config(page_title="Zubi App", layout="wide")
st.title("📊 Zubi People - Imputación de Horas (Fase Pruebas)")

# --- BASE DE DATOS TEMPORAL (Borrador) ---
ARCHIVO = "datos_temporales.csv"

if not os.path.exists(ARCHIVO):
    df_vacio = pd.DataFrame(columns=["Fecha", "Empleado", "Empresa", "Area", "Horas"])
    df_vacio.to_csv(ARCHIVO, index=False)

# --- FORMULARIO ---
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
            df_check = df_check.iloc[:-1]
            df_check.to_csv(ARCHIVO, index=False)
            st.rerun()

st.divider()

# --- DASHBOARD VISUAL ---
try:
    df = pd.read_csv(ARCHIVO)
    if not df.empty:
        
        # Limpiamos los datos para que no haya errores
        df['Horas'] = pd.to_numeric(df['Horas'], errors='coerce').fillna(0)
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        
        # --- CONTROL DIARIO (CUARTILES) ---
        st.subheader("🎯 Progreso Diario (Objetivo: 8h)")
        st.write("Consulta cómo llevas el día o si te falta algo por imputar.")
        
        c_prog1, c_prog2 = st.columns(2)
        with c_prog1:
            emp_progreso = st.selectbox("Ver progreso de:", df['Empleado'].unique())
        with c_prog2:
            fecha_progreso = st.date_input("Día a consultar:", datetime.date.today(), key="filtro_fecha")
            
        df_diario = df[(df['Empleado'] == emp_progreso) & (df['Fecha'].dt.date == fecha_progreso)]
        horas_hoy = df_diario['Horas'].sum()
        
        progreso = min(horas_hoy / 8.0, 1.0)
        st.progress(progreso)
        
        if horas_hoy == 0:
            st.info(f"Aún no hay horas imputadas para {emp_progreso} en este día.")
        elif horas_hoy <= 2:
            st.warning(f"**{horas_hoy}h imputadas (Q1 - 25%).** Queda jornada por delante.")
        elif horas_hoy <= 4:
            st.warning(f"**{horas_hoy}h imputadas (Q2 - 50%).** Mitad de la jornada registrada.")
        elif horas_hoy <= 6:
            st.info(f"**{horas_hoy}h imputadas (Q3 - 75%).** Buen progreso, considerando reuniones.")
        elif horas_hoy < 8:
            st.success(f"**{horas_hoy}h imputadas.** ¡Casi el 100%!")
        else:
            st.success(f"🌟 **¡Objetivo Diario Completado! ({horas_hoy}h)**")
            
        st.divider()

        # --- GRÁFICO MENSUAL ---
        st.subheader("📅 Evolución Mensual")
        df['Mes'] = df['Fecha'].dt.to_period('M').astype(str)
        fig_mes = px.bar(df, x='Mes', y='Horas', color='Empresa', title="Suma de Horas por Mes y Empresa", barmode='stack')
        st.plotly_chart(fig_mes, use_container_width=True)
        
        st.divider()

        # --- DASHBOARD GENERAL ---
        st.subheader("🏢 Distribución Global")
        fig_pie = px.pie(df, values='Horas', names='Empresa', title="Peso de las Empresas (Total Histórico)")
        st.plotly_chart(fig_pie, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.bar(df, x='Empleado', y='Horas', color='Empresa', title="Dedicación por Empleado", barmode='stack'), use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(df, x='Empleado', y='Horas', color='Area', title="Tareas por Empleado", barmode='stack'), use_container_width=True)

    else:
        st.info("La base de datos está vacía. Guarda tu primera imputación arriba para ver los gráficos.")
except Exception as e:
    st.warning("Creando base de datos... Actualiza la página en unos segundos.")
