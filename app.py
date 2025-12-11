import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

st.set_page_config(page_title="Dashboard Académico", layout="wide")
st.title("📊 Dashboard de Athens")

uploaded_file = st.file_uploader("Sube tu Excel/CSV aquí", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        # Limpieza de columnas vacías
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
        current_year = datetime.datetime.now().year
        if 'Year of birth' in df.columns:
            df['Year of birth'] = pd.to_numeric(df['Year of birth'], errors='coerce')
            df['Age'] = current_year - df['Year of birth']
        
        # --- FILTROS (Sidebar) ---
        st.sidebar.header("Filtros")
        
        # Filtro Institución
        institutions = sorted(df['Home institution'].astype(str).unique())
        selected_inst = st.sidebar.multiselect("Institución", options=institutions)
        if selected_inst:
            df = df[df['Home institution'].isin(selected_inst)]

        # Filtro Nacionalidad
        nationalities = sorted(df['Nationality_standardized'].astype(str).unique())
        selected_nat = st.sidebar.multiselect("Nacionalidad", options=nationalities)
        if selected_nat:
            df = df[df['Nationality_standardized'].isin(selected_nat)]

        # --- KPIS ---
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Estudiantes", df['ID'].nunique())
        
        avg_age = df['Age'].mean()
        kpi2.metric("Edad Media", f"{avg_age:.1f}" if pd.notnull(avg_age) else "N/A")
        
        top_nat = df['Nationality_standardized'].mode()
        kpi3.metric("Top Nacionalidad", top_nat[0] if not top_nat.empty else "N/A")

        # --- GRÁFICOS PRINCIPALES ---
        c1, c2 = st.columns(2)
        
        with c1:
            # Histograma (Carreras)
            fig = px.histogram(df, x="Field of study", color="Gender", title="Distribución por Carrera")
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            # Gráfico de Pastel (Nacionalidades) - MEJORADO
            # 1. Agrupamos primero para tener el conteo exacto
            nat_counts = df['Nationality_standardized'].value_counts().reset_index()
            nat_counts.columns = ['País', 'Alumnos']
            
            fig2 = px.pie(
                nat_counts, 
                names="País", 
                values="Alumnos", 
                title="Nacionalidades"
            )
            # 2. Personalizamos el hover: %{label} es el país, %{value} es el número
            fig2.update_traces(hovertemplate='%{label}=%{value}<extra></extra>')
            
            st.plotly_chart(fig2, use_container_width=True)

        # --- RANKING INSTITUCIONES ---
        st.subheader("Ranking por Institución")
        inst_counts = df['Home institution'].value_counts().reset_index()
        inst_counts.columns = ['Institución', 'Alumnos']
        
        fig_inst = px.bar(
            inst_counts, 
            x='Institución', 
            y='Alumnos', 
            title="Cantidad de Alumnos por Institución (Orden Descendente)",
            text='Alumnos'
        )
        fig_inst.update_layout(xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig_inst, use_container_width=True)

        # --- DATAFRAME ---
        st.dataframe(df)
        
    except Exception as e:
        st.error(f"Error: {e}")
