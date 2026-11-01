import os
import yfinance as yf
import pandas as pd


def extrair_e_tratar_dados_b3(
    tickers=None, periodo="2y", caminho_saida="data/b3_acoes_tratadas.csv"
):
    """Extrai cotações históricas da B3 via yfinance, realiza a limpeza e

    engenharia de atributos (retornos e médias móveis) e salva em CSV.
    """
    if tickers is None:
        # Principais papéis da B3 por setor
        tickers = [
            "PETR4.SA",
            "VALE3.SA",
            "ITUB4.SA",
            "BBDC4.SA",
            "BBAS3.SA",
            "WEGE3.SA",
            "ABEV3.SA",
            "RENT3.SA",
        ]

    mapa_setores = {
        "PETR4.SA": "Petróleo e Gás",
        "VALE3.SA": "Mineração",
        "ITUB4.SA": "Financeiro",
        "BBDC4.SA": "Financeiro",
        "BBAS3.SA": "Financeiro",
        "WEGE3.SA": "Bens Industriais",
        "ABEV3.SA": "Consumo Não Cíclico",
        "RENT3.SA": "Consumo Cíclico",
    }

    lista_dfs = []
    print("Iniciando extração de dados da B3...")

    for ticker in tickers:
        df_ticker = yf.Ticker(ticker).history(period=periodo)
        if df_ticker.empty:
            continue

        df_ticker = df_ticker.reset_index()
        # Padroniza fuso horário e formato de data
        df_ticker["Date"] = pd.to_datetime(df_ticker["Date"]).dt.tz_localize(
            None
        )
        df_ticker["Ticker"] = ticker.replace(".SA", "")
        df_ticker["Setor"] = mapa_setores.get(ticker, "Outros")

        # Seleciona e renomeia colunas principais
        df_ticker = df_ticker[
            ["Date", "Ticker", "Setor", "Open", "High", "Low", "Close", "Volume"]
        ]
        df_ticker.columns = [
            "Data",
            "Ticker",
            "Setor",
            "Abertura",
            "Maxima",
            "Minima",
            "Fechamento",
            "Volume",
        ]

        # Ordenação cronológica para cálculos de janela móvel
        df_ticker = df_ticker.sort_values("Data")

        # Engenharia de atributos (KPIs financeiros)
        df_ticker["Retorno_Diario"] = df_ticker["Fechamento"].pct_change() * 100
        df_ticker["MM_20"] = (
            df_ticker["Fechamento"].rolling(window=20).mean()
        )
        df_ticker["MM_50"] = (
            df_ticker["Fechamento"].rolling(window=50).mean()
        )
        df_ticker["Volatilidade_20d"] = (
            df_ticker["Retorno_Diario"].rolling(window=20).std()
        )

        lista_dfs.append(df_ticker)

    df_final = pd.concat(lista_dfs, ignore_index=True)

    # Limpeza de dados: remove linhas sem retorno diário (primeiro dia de cada ativo)
    df_final = df_final.dropna(subset=["Retorno_Diario"])
    df_final = df_final.round(2)

    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    df_final.to_csv(caminho_saida, index=False, encoding="utf-8")
    print(
        f"ETL concluído com sucesso! {len(df_final)} registros salvos em '{caminho_saida}'."
    )
    return df_final


if __name__ == "__main__":
    extrair_e_tratar_dados_b3()