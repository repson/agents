from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict

mcp = FastMCP("portfolio_analytics_server")


class PortfolioData(BaseModel):
    holdings: Dict[str, int] = Field(description="Diccionario {symbol: quantity}")
    prices: Dict[str, float] = Field(description="Diccionario {symbol: price}")
    initial_investment: float = Field(description="Inversión inicial total")


class TradeHistory(BaseModel):
    trades: List[Dict] = Field(description="Lista de trades con pnl")


@mcp.tool()
def calculate_portfolio_value(data: PortfolioData) -> dict:
    """Calcula el valor total del portfolio"""
    total_value = 0
    positions = []

    for symbol, quantity in data.holdings.items():
        if symbol in data.prices:
            position_value = quantity * data.prices[symbol]
            total_value += position_value

            positions.append({
                "symbol": symbol,
                "quantity": quantity,
                "price": data.prices[symbol],
                "value": round(position_value, 2),
                "percentage": 0  # Se calculará después
            })

    # Calcular porcentajes
    for position in positions:
        position["percentage"] = round((position["value"] / total_value) * 100, 2)

    pnl = total_value - data.initial_investment
    pnl_percentage = (pnl / data.initial_investment) * 100

    return {
        "total_value": round(total_value, 2),
        "pnl": round(pnl, 2),
        "pnl_percentage": round(pnl_percentage, 2),
        "positions": positions
    }


@mcp.tool()
def calculate_diversification(data: PortfolioData) -> dict:
    """Analiza la diversificación del portfolio"""
    total_value = sum(
        data.holdings.get(symbol, 0) * data.prices.get(symbol, 0)
        for symbol in data.holdings
    )

    if total_value == 0:
        return {"error": "Portfolio vacío"}

    concentrations = []
    for symbol, quantity in data.holdings.items():
        if symbol in data.prices:
            value = quantity * data.prices[symbol]
            percentage = (value / total_value) * 100
            concentrations.append({
                "symbol": symbol,
                "percentage": round(percentage, 2)
            })

    # Ordenar por concentración
    concentrations.sort(key=lambda x: x["percentage"], reverse=True)

    # Análisis
    max_concentration = concentrations[0]["percentage"] if concentrations else 0

    if max_concentration > 50:
        risk_level = "HIGH"
        recommendation = "Muy concentrado, considerar diversificar"
    elif max_concentration > 30:
        risk_level = "MEDIUM"
        recommendation = "Concentración moderada"
    else:
        risk_level = "LOW"
        recommendation = "Bien diversificado"

    return {
        "concentrations": concentrations,
        "max_concentration": round(max_concentration, 2),
        "risk_level": risk_level,
        "recommendation": recommendation,
        "number_of_positions": len(concentrations)
    }


@mcp.tool()
def calculate_win_rate(data: TradeHistory) -> dict:
    """Calcula el win rate y estadísticas de trading"""
    if not data.trades:
        return {"error": "No hay trades"}

    winning_trades = [t for t in data.trades if t.get('pnl', 0) > 0]
    losing_trades = [t for t in data.trades if t.get('pnl', 0) < 0]

    win_rate = (len(winning_trades) / len(data.trades)) * 100

    avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0

    return {
        "total_trades": len(data.trades),
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "win_rate": round(win_rate, 2),
        "average_win": round(avg_win, 2),
        "average_loss": round(avg_loss, 2),
        "expectancy": round(avg_win * (win_rate/100) + avg_loss * ((100-win_rate)/100), 2)
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
