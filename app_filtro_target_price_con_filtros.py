
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="🎯 Filtro Personalizado S&P 500", layout="wide")
st.title("🎯 Filtro Personalizado de Acciones del S&P 500")

# 🔵 Filtros seleccionables
st.sidebar.title("🛠️ Configura tus filtros:")

filtrar_por_target = st.sidebar.checkbox("Solo acciones bajo Target Price", value=True)
filtrar_por_roe = st.sidebar.checkbox("ROE > 10%", value=True)
filtrar_por_margen = st.sidebar.checkbox("Margen Neto > 10%", value=True)
filtrar_por_eps = st.sidebar.checkbox("EPS creciendo > 5%", value=True)
filtrar_por_pe = st.sidebar.checkbox("P/E < 20", value=True)
filtrar_por_deuda = st.sidebar.checkbox("Deuda/Equity < 1.5", value=True)

@st.cache_data
def obtener_tickers_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    table = soup.find("table", {"id": "constituents"})
    df = pd.read_html(table.prettify())[0]
    tickers = df["Symbol"].tolist()
    return [ticker.replace(".", "-") for ticker in tickers]

def analizar_ticker(ticker):
    try:
        data = yf.Ticker(ticker)
        info = data.info

        current = info.get("currentPrice")
        target = info.get("targetMeanPrice")
        roe = info.get("returnOnEquity")
        margen = info.get("profitMargins")
        eps_growth = info.get("earningsQuarterlyGrowth")
        pe = info.get("trailingPE")
        deuda = info.get("debtToEquity")

        cumple = True
        criterios = {}

        if filtrar_por_target:
            if not (current and target and current < target):
                cumple = False
            criterios["Bajo Target"] = current and target and current < target

        if filtrar_por_roe:
            if not (roe and roe > 0.10):
                cumple = False
            criterios["ROE > 10%"] = roe and roe > 0.10

        if filtrar_por_margen:
            if not (margen and margen > 0.10):
                cumple = False
            criterios["Margen Neto > 10%"] = margen and margen > 0.10

        if filtrar_por_eps:
            if not (eps_growth and eps_growth > 0.05):
                cumple = False
            criterios["EPS Creciendo > 5%"] = eps_growth and eps_growth > 0.05

        if filtrar_por_pe:
            if not (pe and pe < 20):
                cumple = False
            criterios["P/E < 20"] = pe and pe < 20

        if filtrar_por_deuda:
            if not (deuda and deuda < 150):
                cumple = False
            criterios["Deuda/Equity < 1.5"] = deuda and deuda < 150

        if cumple:
            return {
                "Ticker": ticker,
                "Precio actual": current,
                "Target Price": target,
                "ROE": roe,
                "Margen Neto": margen,
                "EPS Growth": eps_growth,
                "P/E Ratio": pe,
                "Deuda/Equity": deuda,
                **criterios
            }
    except Exception:
        return None

if st.button("🔍 Ejecutar filtro"):
    with st.spinner("Consultando datos financieros..."):
        tickers = obtener_tickers_sp500()
        resultados = []
        for t in tickers:
            analisis = analizar_ticker(t)
            if analisis:
                resultados.append(analisis)

        if resultados:
            df_resultado = pd.DataFrame(resultados)
            st.success(f"Se encontraron {len(df_resultado)} acciones que cumplen los filtros.")
            st.dataframe(df_resultado.sort_values(by="Ticker").reset_index(drop=True), use_container_width=True)
        else:
            st.warning("No se encontraron acciones que cumplan todos los filtros seleccionados.")
