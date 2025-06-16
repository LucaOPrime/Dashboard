import streamlit as st
import pandas as pd
import plotly.express as px

# Configurações globais de estilo
st.set_page_config(page_title="Dashboard - IASD Graças", layout="wide")
tema_plotly = "plotly"  # Tema padrão

with open("styles/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Carregando os dados


@st.cache_data
def load_data():
    despesas = pd.read_csv("assets/despesas.csv", sep=None, engine="python")
    pendentes = pd.read_csv("assets/pendentes.csv", sep=None, engine="python")

    # Formatando dados
    despesas['Data'] = pd.to_datetime(despesas.iloc[:, 0], dayfirst=True)
    despesas['Valor'] = despesas['Valor'].astype(str).str.replace(
        '.', '').str.replace(',', '.').astype(float)
    despesas['Tipo'] = despesas['Tipo'].astype(str)

    pendentes['Data'] = pd.to_datetime(pendentes.iloc[:, 0], dayfirst=True)
    pendentes['Valor'] = pendentes['Valor'].astype(str).str.replace(
        '.', '').str.replace(',', '.').astype(float)
    pendentes['Fornecedor'] = pendentes['Fornecedor'].astype(str)

    return despesas, pendentes


st.title("📊 Dashboard Financeiro - Construção IASD Graças")
despesas, pendentes = load_data()

# Menu lateral com filtros
st.sidebar.header("🔧 Filtros")

# Filtro por Tipo de Despesa
tipos = despesas['Tipo'].unique().tolist()
tipo_selecionado = st.sidebar.multiselect(
    "Tipo de Despesa", tipos, default=tipos)

# Filtro por Ano
anos = despesas['Data'].dt.year.unique().tolist()
ano_selecionado = st.sidebar.multiselect("Ano", anos, default=anos)

# Filtro para seleção de indicador
indicador = st.sidebar.radio("Ir para o indicador:", (
    "📊 Total por Tipo de Despesa",
    "📅 Despesas por Mês/Ano",
    "📈 Evolução Temporal das Despesas",
    "🔻 Pendentes por Fornecedor",
    "🔍 Top 5 maiores Despesas",
    "🔍 Top 5 maiores Pendências",
    "✅ Pagas vs Pendentes"
))

# Aplicando os filtros
despesas_filtradas = despesas[(despesas['Tipo'].isin(tipo_selecionado)) & (
    despesas['Data'].dt.year.isin(ano_selecionado))]
pendentes_filtradas = pendentes.copy()

# Layout para exibição dos gráficos
if indicador == "📊 Total por Tipo de Despesa" or indicador == "🔻 Pendentes por Fornecedor":
    st.subheader(
        "📊 Total por Tipo de Despesa  vs  🔻 Pendências por Fornecedor")
    col1, col2 = st.columns(2)
    with col1:
        tipo_total = despesas_filtradas.groupby('Tipo')['Valor'].sum(
        ).reset_index().sort_values(by='Valor', ascending=False)
        fig1 = px.bar(tipo_total, x='Tipo', y='Valor', title='Total por Tipo de Despesa',
                      color='Tipo', color_discrete_sequence=px.colors.qualitative.Set2, template=tema_plotly)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        pendente_total = pendentes_filtradas.groupby('Fornecedor')['Valor'].sum(
        ).reset_index().sort_values(by='Valor', ascending=False)
        fig2 = px.bar(pendente_total, x='Fornecedor', y='Valor', title='Pendências por Fornecedor',
                      color='Fornecedor', color_discrete_sequence=px.colors.qualitative.Set3, template=tema_plotly)
        st.plotly_chart(fig2, use_container_width=True)

elif indicador == "📅 Despesas por Mês/Ano":
    st.header("📅 Despesas por Mês/Ano")
    despesas_filtradas['AnoMes'] = despesas_filtradas['Data'].dt.to_period(
        'M').astype(str)
    mes_ano_total = despesas_filtradas.groupby(
        'AnoMes')['Valor'].sum().reset_index()
    fig = px.bar(mes_ano_total, x='AnoMes', y='Valor', title='Despesas por Mês/Ano',
                 color='Valor', color_continuous_scale='Tealgrn', template=tema_plotly)
    st.plotly_chart(fig, use_container_width=True)

elif indicador == "📈 Evolução Temporal das Despesas":
    st.header("📈 Evolução Temporal das Despesas")
    despesas_ordenadas = despesas_filtradas.sort_values('Data')
    fig = px.line(despesas_ordenadas, x='Data', y='Valor', title='Evolução Temporal das Despesas',
                  color_discrete_sequence=['#1f77b4'], template=tema_plotly)
    st.plotly_chart(fig, use_container_width=True)

elif indicador == "🔍 Top 5 maiores Despesas":
    st.header("🔍 Top 5 maiores Despesas")
    top_despesas = despesas_filtradas.nlargest(
        5, 'Valor')[['Data', 'Descrição', 'Valor']]
    st.dataframe(top_despesas.style.format({'Valor': 'R$ {:,.2f}'}))

elif indicador == "🔍 Top 5 maiores Pendências":
    st.header("🔍 Top 5 maiores Pendências")
    top_pendentes = pendentes_filtradas.nlargest(
        5, 'Valor')[['Data', 'Descrição', 'Valor']]
    st.dataframe(top_pendentes.style.format({'Valor': 'R$ {:,.2f}'}))

elif indicador == "✅ Pagas vs Pendentes":
    st.header("✅ Pagas vs Pendentes")
    total_pagas = despesas_filtradas['Valor'].sum()
    total_pendentes = pendentes_filtradas['Valor'].sum()
    pagas_vs_pendentes = pd.DataFrame({
        'Status': ['Pagas', 'Pendentes'],
        'Valor': [total_pagas, total_pendentes]
    })
    fig = px.pie(pagas_vs_pendentes, names='Status', values='Valor', title='Distribuição: Pagas vs Pendentes',
                 color_discrete_sequence=px.colors.sequential.RdBu, template=tema_plotly)
    st.plotly_chart(fig, use_container_width=True)
