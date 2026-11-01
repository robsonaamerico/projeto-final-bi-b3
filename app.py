import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="B3 Analytics | BI Financeiro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 2. Carregamento de Dados com Cache (Requisito de Performance do Edital)
@st.cache_data
def carregar_dados():
    caminho_csv = "data/b3_acoes_tratadas.csv"
    if not os.path.exists(caminho_csv):
        from src.etl import extrair_e_tratar_dados_b3

        return extrair_e_tratar_dados_b3(caminho_saida=caminho_csv)
    df = pd.read_csv(caminho_csv, parse_dates=["Data"])
    return df


df_bruto = carregar_dados()

# 3. Barra Lateral (Sidebar) - Filtros Interativos
st.sidebar.title("⚙️ Filtros de Análise")
st.sidebar.markdown("Personalize o recorte temporal, setorial e de ativos:")

# Filtro de Setor
setores_disponiveis = sorted(df_bruto["Setor"].unique())
setores_selecionados = st.sidebar.multiselect(
    "Setores da B3:", options=setores_disponiveis, default=setores_disponiveis
)

# Filtro de Ativos (dinâmico conforme setor)
tickers_filtrados_setor = sorted(
    df_bruto[df_bruto["Setor"].isin(setores_selecionados)]["Ticker"].unique()
)
tickers_selecionados = st.sidebar.multiselect(
    "Ativos (Tickers):",
    options=tickers_filtrados_setor,
    default=tickers_filtrados_setor,
)

# Filtro de Data
data_min = df_bruto["Data"].min().date()
data_max = df_bruto["Data"].max().date()
intervalo_datas = st.sidebar.date_input(
    "Período de Análise:",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
)

# Validação de segurança dos filtros
if not tickers_selecionados or len(intervalo_datas) < 2:
    st.warning(
        "⚠️ Selecione pelo menos um ativo e um intervalo de datas inicial e final na barra lateral."
    )
    st.stop()

data_inicio, data_fim = pd.to_datetime(intervalo_datas[0]), pd.to_datetime(
    intervalo_datas[1]
)

df_filtrado = df_bruto[
    (df_bruto["Ticker"].isin(tickers_selecionados))
    & (df_bruto["Data"] >= data_inicio)
    & (df_bruto["Data"] <= data_fim)
].copy()

# 4. Cabeçalho Principal e KPIs Executivos
st.title("📈 Dashboard de Business Intelligence — Ações da B3")
st.markdown(
    "Monitoramento de performance, tendências técnicas (Médias Móveis) e relação Risco x Retorno dos principais ativos da bolsa brasileira."
)

# Cálculo dos KPIs no período filtrado
resumo_periodo = (
    df_filtrado.sort_values("Data")
    .groupby("Ticker")
    .agg(
        Preco_Inicial=("Fechamento", "first"),
        Preco_Final=("Fechamento", "last"),
        Volatilidade_Media=("Volatilidade_20d", "mean"),
        Volume_Total=("Volume", "sum"),
    )
)
resumo_periodo["Rentabilidade_Periodo (%)"] = (
    (resumo_periodo["Preco_Final"] / resumo_periodo["Preco_Inicial"]) - 1
) * 100

melhor_ativo = resumo_periodo["Rentabilidade_Periodo (%)"].idxmax()
maior_alta = resumo_periodo["Rentabilidade_Periodo (%)"].max()
ativo_mais_volatil = resumo_periodo["Volatilidade_Media"].idxmax()
maior_volatilidade = resumo_periodo["Volatilidade_Media"].max()
retorno_medio_carteira = resumo_periodo["Rentabilidade_Periodo (%)"].mean()
volume_total_negociado = df_filtrado["Volume"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Retorno Médio (Seleção)",
    f"{retorno_medio_carteira:.2f}%",
    delta=f"{retorno_medio_carteira:.2f}%",
)
col2.metric(
    "Destaque de Alta",
    f"{melhor_ativo}",
    delta=f"{maior_alta:.2f}% no período",
)
col3.metric(
    "Maior Volatilidade (20d)",
    f"{ativo_mais_volatil}",
    delta=f"{maior_volatilidade:.2f}%",
    delta_color="inverse",
)
col4.metric("Volume Total Negociado", f"{volume_total_negociado:,.0f}")

st.divider()

# 5. Navegação em Abas (UX e Storytelling de Dados)
aba_tecnica, aba_risco, aba_dados = st.tabs([
    "📊 Análise Técnica e Tendência",
    "🎯 Risco, Retorno e Correlação",
    "📋 Base de Dados e Exportação",
])

with aba_tecnica:
    col_sel, col_info = st.columns([1, 3])
    with col_sel:
        ticker_destaque = st.selectbox(
            "Selecione o Ativo para Análise Técnica Detalhada:",
            options=tickers_selecionados,
        )
        exibir_mm = st.checkbox("Exibir Médias Móveis (MM20 e MM50)", value=True)

    df_ativo = df_filtrado[df_filtrado["Ticker"] == ticker_destaque].sort_values(
        "Data"
    )

    # Gráfico Candlestick + Médias Móveis
    fig_candle = go.Figure()
    fig_candle.add_trace(
        go.Candlestick(
            x=df_ativo["Data"],
            open=df_ativo["Abertura"],
            high=df_ativo["Maxima"],
            low=df_ativo["Minima"],
            close=df_ativo["Fechamento"],
            name="Cotação (OHLC)",
        )
    )

    if exibir_mm:
        fig_candle.add_trace(
            go.Scatter(
                x=df_ativo["Data"],
                y=df_ativo["MM_20"],
                mode="lines",
                name="Média Móvel 20d",
                line=dict(color="#FFA15A", width=1.8),
            )
        )
        fig_candle.add_trace(
            go.Scatter(
                x=df_ativo["Data"],
                y=df_ativo["MM_50"],
                mode="lines",
                name="Média Móvel 50d",
                line=dict(color="#19D3F3", width=1.8),
            )
        )

    fig_candle.update_layout(
        title=f"Evolução de Preços e Médias Móveis — {ticker_destaque}",
        yaxis_title="Preço (R$)",
        xaxis_title="Data",
        xaxis_rangeslider_visible=False,
        height=500,
    )
    st.plotly_chart(fig_candle, use_container_width=True)

    # Comparativo de Evolução Normalizada (Base 100)
    df_filtrado["Base_100"] = df_filtrado.groupby("Ticker")[
        "Fechamento"
    ].transform(lambda x: (x / x.iloc[0]) * 100)
    fig_comp = px.line(
        df_filtrado,
        x="Data",
        y="Base_100",
        color="Ticker",
        title="Comparativo de Performance Relativa (Base 100 no início do período)",
        labels={"Base_100": "Performance (Base 100)"},
    )
    st.plotly_chart(fig_comp, use_container_width=True)

with aba_risco:
    col_esq, col_dir = st.columns(2)

    with col_esq:
        df_risco = (
            df_filtrado.groupby(["Ticker", "Setor"])
            .agg(
                Retorno_Medio=("Retorno_Diario", "mean"),
                Volatilidade=("Volatilidade_20d", "mean"),
                Volume_Medio=("Volume", "mean"),
            )
            .reset_index()
        )

        fig_scatter = px.scatter(
            df_risco,
            x="Volatilidade",
            y="Retorno_Medio",
            text="Ticker",
            color="Setor",
            size="Volume_Medio",
            title="Matriz Risco (Volatilidade 20d) vs. Retorno Médio Diário (%)",
            labels={
                "Volatilidade": "Volatilidade Média 20d (%)",
                "Retorno_Medio": "Retorno Médio Diário (%)",
            },
        )
        fig_scatter.update_traces(textposition="top center")
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_dir:
        df_pivot = df_filtrado.pivot(
            index="Data", columns="Ticker", values="Retorno_Diario"
        )
        corr = df_pivot.corr().round(2)
        fig_corr = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            title="Correlação Cruzada dos Retornos Diários",
        )
        st.plotly_chart(fig_corr, use_container_width=True)

with aba_dados:
    st.subheader("Base de Dados Processada (Filtro Atual)")
    st.dataframe(
        df_filtrado.sort_values(["Data", "Ticker"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
    )

    csv_export = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Dados Filtrados (CSV)",
        data=csv_export,
        file_name="b3_dados_filtrados.csv",
        mime="text/csv",
    )