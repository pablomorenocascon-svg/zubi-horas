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

# --- DICCIONARIO DE ÁREAS (para mostrar la leyenda) ---
AREAS_INFO = {
    "LAB": "Laboratorio",
    "PRL": "Prevención de Riesgos Laborales",
    "ONB": "Onboarding",
    "TEA": "Equipo / Team",
    "FOR": "Formación",
    "EEX": "Experiencia Empleado",
    "SEL": "Selección",
    "COM": "Comunicación"
}

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
    with col4: area = st.selectbox("Área", list(AREAS_INFO.keys()))

    horas = st.number_input("Horas invertidas", min_value=0.5, step=0.5)
    submit = st.form_submit_button("Guardar")

    if submit:
        nueva_fila = pd.DataFrame({"Fecha": [fecha], "Empleado": [empleado], "Empresa": [empresa], "Area": [area], "Horas": [horas]})
        nueva_fila.to_csv(ARCHIVO, mode='a', header=False, index=False)
        st.success(f"✅ Guardadas {horas}h de {empleado} en {empresa}")

# --- LEYENDA DE ÁREAS ---
with st.expander("ℹ️ ¿Qué significa cada código de Área?"):
    cols_leyenda = st.columns(4)
    for i, (codigo, descripcion) in enumerate(AREAS_INFO.items()):
        with cols_leyenda[i % 4]:
            st.markdown(f"**{codigo}** → {descripcion}")

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

        # Limpieza de datos
        df['Horas'] = pd.to_numeric(df['Horas'], errors='coerce').fillna(0)
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df = df.dropna(subset=['Fecha'])

        # =========================================================
        # FILTROS GLOBALES EN SIDEBAR
        # =========================================================
        with st.sidebar:
            st.header("🔎 Filtros del Dashboard")
            st.caption("Afectan a todos los gráficos del panel")

            f_empleados = st.multiselect(
                "Empleados",
                options=sorted(df['Empleado'].unique()),
                default=sorted(df['Empleado'].unique())
            )
            f_empresas = st.multiselect(
                "Empresas",
                options=sorted(df['Empresa'].unique()),
                default=sorted(df['Empresa'].unique())
            )
            f_areas = st.multiselect(
                "Áreas",
                options=sorted(df['Area'].unique()),
                default=sorted(df['Area'].unique())
            )

            fecha_min = df['Fecha'].min().date()
            fecha_max = df['Fecha'].max().date()
            f_rango = st.date_input(
                "Rango de fechas",
                value=(fecha_min, fecha_max),
                min_value=fecha_min,
                max_value=fecha_max
            )

        # Aplicamos filtros
        df_filt = df[
            df['Empleado'].isin(f_empleados) &
            df['Empresa'].isin(f_empresas) &
            df['Area'].isin(f_areas)
        ]
        if isinstance(f_rango, tuple) and len(f_rango) == 2:
            df_filt = df_filt[
                (df_filt['Fecha'].dt.date >= f_rango[0]) &
                (df_filt['Fecha'].dt.date <= f_rango[1])
            ]

        if df_filt.empty:
            st.warning("No hay datos con los filtros seleccionados. Ajusta los filtros en la barra lateral.")
            st.stop()

        # =========================================================
        # KPIs RÁPIDOS
        # =========================================================
        st.subheader("📌 Resumen rápido")
        hoy = datetime.date.today()
        total_horas = df_filt['Horas'].sum()
        horas_mes_actual = df_filt[
            (df_filt['Fecha'].dt.month == hoy.month) &
            (df_filt['Fecha'].dt.year == hoy.year)
        ]['Horas'].sum()
        empresa_top = df_filt.groupby('Empresa')['Horas'].sum().idxmax()
        area_top = df_filt.groupby('Area')['Horas'].sum().idxmax()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total horas (filtrado)", f"{total_horas:.1f}h")
        k2.metric("Horas este mes", f"{horas_mes_actual:.1f}h")
        k3.metric("Empresa top", empresa_top)
        k4.metric("Área más trabajada", f"{area_top} - {AREAS_INFO.get(area_top, '')}")

        st.divider()

        # =========================================================
        # CONTROL DIARIO (CUARTILES) - se mantiene tu lógica
        # =========================================================
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

        # =========================================================
        # JERARQUÍA EMPRESA -> ÁREA -> EMPLEADO (SUNBURST)
        # =========================================================
        st.subheader("🌞 Jerarquía: Empresa → Área → Empleado")
        st.caption("Haz clic en una empresa para ver el desglose por área y empleado.")
        fig_sun = px.sunburst(
            df_filt,
            path=['Empresa', 'Area', 'Empleado'],
            values='Horas'
        )
        fig_sun.update_layout(margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig_sun, use_container_width=True)

        st.divider()

        # =========================================================
        # EVOLUCIÓN TEMPORAL: BARRAS MENSUALES + LÍNEA ACUMULADA
        # =========================================================
        st.subheader("📅 Evolución temporal")

        col_ev1, col_ev2 = st.columns(2)

        with col_ev1:
            df_filt['Mes'] = df_filt['Fecha'].dt.to_period('M').astype(str)
            fig_mes = px.bar(
                df_filt, x='Mes', y='Horas', color='Empresa',
                title="Horas por Mes y Empresa", barmode='stack'
            )
            st.plotly_chart(fig_mes, use_container_width=True)

        with col_ev2:
            df_acum = df_filt.sort_values('Fecha').copy()
            df_acum['Horas_Acumuladas'] = df_acum.groupby('Empleado')['Horas'].cumsum()
            fig_acum = px.line(
                df_acum, x='Fecha', y='Horas_Acumuladas', color='Empleado',
                title="Horas acumuladas por empleado", markers=True
            )
            st.plotly_chart(fig_acum, use_container_width=True)

        st.divider()

        # =========================================================
        # HEATMAP EMPLEADO vs EMPRESA
        # =========================================================
        st.subheader("🔥 Mapa de calor: Empleado vs Empresa")
        st.caption("Detecta de un vistazo qué empleado dedica más tiempo a qué empresa.")
        pivot = df_filt.pivot_table(
            values='Horas', index='Empleado', columns='Empresa',
            aggfunc='sum', fill_value=0
        )
        fig_heat = px.imshow(
            pivot, text_auto='.1f', aspect="auto",
            color_continuous_scale='Blues',
            labels=dict(x="Empresa", y="Empleado", color="Horas")
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.divider()

        # =========================================================
        # RANKING DE EMPRESAS Y DESGLOSE POR EMPLEADO/ÁREA
        # =========================================================
        st.subheader("🏢 Distribución Global")

        col_r1, col_r2 = st.columns(2)

        with col_r1:
            df_rank = df_filt.groupby('Empresa')['Horas'].sum().sort_values().reset_index()
            fig_rank = px.bar(
                df_rank, x='Horas', y='Empresa', orientation='h',
                title="Ranking de empresas por horas dedicadas",
                text='Horas'
            )
            fig_rank.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
            st.plotly_chart(fig_rank, use_container_width=True)

        with col_r2:
            fig_area_emp = px.bar(
                df_filt, x='Empleado', y='Horas', color='Area',
                title="Tareas (Áreas) por Empleado", barmode='stack'
            )
            st.plotly_chart(fig_area_emp, use_container_width=True)

    else:
        st.info("La base de datos está vacía. Guarda tu primera imputación arriba para ver los gráficos.")
except Exception as e:
    st.warning(f"Error al cargar el dashboard: {e}")
