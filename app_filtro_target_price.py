
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="🎯 Filtro por Target Price", layout="wide")
st.title("🎯 Acciones del S&P 500 por debajo del Target Price")

@st.cache_data
def obtener_tickers_sp500():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    table = soup.find("table", {"id": "constituents"})
    df = pd.read_html(table.prettify())[0]
    tickers = df["Symbol"].tolist()
    return [ticker.replace(".", "-") for ticker in tickers]

def acciones_bajo_target_price(tickers):
    resultados = []
    for ticker in tickers:
        try:
            data = yf.Ticker(ticker)
            info = data.info
            current = info.get("currentPrice")
            target = info.get("targetMeanPrice")
            if current and target and current < target:
                diferencia = round((target - current) / current * 100, 2)
                oportunidad = diferencia > 15
                resultados.append({
                    "Ticker": ticker,
                    "Precio actual": current,
                    "Target Price": target,
                    "Diferencia %": diferencia,
                    "✔️ Oportunidad (>15%)": "✅" if oportunidad else ""
                })
        except Exception:
            pass
    return pd.DataFrame(resultados)

if st.button("🔍 Ejecutar filtro"):
    with st.spinner("Consultando Yahoo Finance..."):
        tickers = obtener_tickers_sp500()
        df = acciones_bajo_target_price(tickers)
        st.success(f"Se encontraron {len(df)} acciones bajo el target price.")
        st.dataframe(df.sort_values(by="Diferencia %", ascending=False).reset_index(drop=True), use_container_width=True)
