from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List

mcp = FastMCP("technical_indicators_server")


class PriceData(BaseModel):
    prices: List[float] = Field(description="Lista de precios históricos")
    period: int = Field(default=14, description="Período para el cálculo")


@mcp.tool()
def calculate_sma(data: PriceData) -> dict:
    """Calcula la Media Móvil Simple (SMA)"""
    if len(data.prices) < data.period:
        return {"error": "No hay suficientes datos"}

    sma = sum(data.prices[-data.period:]) / data.period

    return {
        "sma": round(sma, 2),
        "period": data.period,
        "signal": "buy" if data.prices[-1] > sma else "sell"
    }


@mcp.tool()
def calculate_rsi(data: PriceData) -> dict:
    """Calcula el RSI (Relative Strength Index)"""
    if len(data.prices) < data.period + 1:
        return {"error": "No hay suficientes datos"}

    # Calcular cambios de precio
    deltas = [data.prices[i] - data.prices[i-1] for i in range(1, len(data.prices))]

    # Separar ganancias y pérdidas
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]

    # Promedios
    avg_gain = sum(gains[-data.period:]) / data.period
    avg_loss = sum(losses[-data.period:]) / data.period

    # Calcular RSI
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    # Señales
    if rsi > 70:
        signal = "overbought"  # Sobrecompra
    elif rsi < 30:
        signal = "oversold"  # Sobreventa
    else:
        signal = "neutral"

    return {
        "rsi": round(rsi, 2),
        "signal": signal,
        "interpretation": f"RSI de {round(rsi, 2)} indica {signal}"
    }


@mcp.tool()
def detect_trend(data: PriceData) -> dict:
    """Detecta la tendencia usando dos medias móviles"""
    short_period = 20
    long_period = 50

    if len(data.prices) < long_period:
        return {"error": "No hay suficientes datos"}

    sma_short = sum(data.prices[-short_period:]) / short_period
    sma_long = sum(data.prices[-long_period:]) / long_period

    if sma_short > sma_long:
        trend = "UPTREND"
        signal = "bullish"
    elif sma_short < sma_long:
        trend = "DOWNTREND"
        signal = "bearish"
    else:
        trend = "SIDEWAYS"
        signal = "neutral"

    return {
        "trend": trend,
        "signal": signal,
        "sma_20": round(sma_short, 2),
        "sma_50": round(sma_long, 2)
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
