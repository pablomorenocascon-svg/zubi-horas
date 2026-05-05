import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import datetime

st.set_page_config(page_title="Zubi App", layout="wide")
st.title("📊 Zubi People - Gestión de Horas Real")

# --- CONEXIÓN CON GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos existentes
df = conn.read(ttl=0)

# --- FORMULARIO ---
with st.form("formulario_zubi"):
    col1, col2, col3, col4 = st.columns(4)
    with col1: fecha = st.date_input("Fecha", datetime.date.today())
    with col2: empleado = st.selectbox("Empleado", ["María", "Alicia", "Belén", "Pablo", "Alba"])
    with col3: empresa = st.selectbox("Empresa", [
        "Zubi Group Impact", "Zubi Labs Impact", "Matteco", "Kampe", "Zubi Family", 
        "Imagine", "Zubi Capital", "Zubi Capital Asset Management", "Fundación Felisa", 
        "Zubi Cities", "Zeronet", "Parque Felisa", "Social Nest", "Teradx"
    ])
    with col4: area = st.selectbox("Área", ["LAB", "PRL", "ONB", "TEA", "FOR", "EEX", "SEL", "COM"])
    
    horas = st.number_input("Horas", min_value=0.5, step=0.5)
    submit = st.form_submit_button("Guardar Imputación")

    if submit:
        nueva_fila = pd.DataFrame([{"Fecha": str(fecha), "Empleado": empleado, "Empresa": empresa, "Area": area, "Horas": horas}])
        df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
        conn.update(data=df_actualizado)
        st.success("✅ ¡Guardado directamente en Google Drive!")
        st.rerun()

# --- BOTÓN DESHACER ---
if not df.empty:
    if st.button("🗑️ Eliminar último registro"):
        df_menos_uno = df.iloc[:-1]
        conn.update(data=df_menos_uno)
        st.rerun()

st.divider()

# --- DASHBOARD ---
if not df.empty:
    
    # 1. Limpiamos los datos para asegurarnos de que las fechas y números se leen bien
    df['Horas'] = pd.to_numeric(df['Horas'], errors='coerce').fillna(0)
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    
    # --- NUEVA SECCIÓN: CONTROL DIARIO (CUARTILES) ---
    st.subheader("🎯 Progreso Diario (Objetivo: 8h)")
    st.write("Consulta cómo llevas el día o si te falta algo por imputar.")
    
    c_prog1, c_prog2 = st.columns(2)
    with c_prog1:
        emp_progreso = st.selectbox("Ver progreso de:", df['Empleado'].unique())
    with c_prog2:
        fecha_progreso = st.date_input("Día a consultar:", datetime.date.today(), key="filtro_fecha")
        
    # Filtramos las horas de esa persona en ese día concreto
    df_diario = df[(df['Empleado'] == emp_progreso) & (df['Fecha'].dt.date == fecha_progreso)]
    horas_hoy = df_diario['Horas'].sum()
    
    # Calculamos el progreso (máximo 1.0 que es el 100% de la barra)
    progreso = min(horas_hoy / 8.0, 1.0)
    st.progress(progreso)
    
    # Sistema de Cuartiles con mensajes personalizados
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

    # --- NUEVA SECCIÓN: GRÁFICO MENSUAL ---
    st.subheader("📅 Evolución Mensual")
    # Extraemos el Año-Mes de la fecha (Ej: "2026-04")
    df['Mes'] = df['Fecha'].dt.to_period('M').astype(str)
    
    # Gráfico de barras apiladas por meses
    fig_mes = px.bar(df, x='Mes', y='Horas', color='Empresa', title="Suma de Horas por Mes y Empresa", barmode='stack')
    st.plotly_chart(fig_mes, use_container_width=True)
    
    st.divider()

    # --- DASHBOARD GENERAL ---
    st.subheader("🏢 Distribución Global")
    fig_pie = px.pie(df, values='Horas', names='Empresa', title="Peso de las Empresas (Total Histórico)")
    st.plotly_chart(fig_pie, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(df, x='Empleado', y='Horas', color='Empresa', title="Dedicación por Empleado"), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(df, x='Empleado', y='Horas', color='Area', title="Tareas por Empleado"), use_container_width=True)

else:
    st.info("Esperando datos de Google Sheets...")
