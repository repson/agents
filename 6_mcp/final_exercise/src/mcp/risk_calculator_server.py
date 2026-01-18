from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("risk_calculator_server")


class PositionData(BaseModel):
    account_balance: float = Field(description="Balance de la cuenta")
    entry_price: float = Field(description="Precio de entrada")
    stop_loss: float = Field(description="Precio de stop loss")
    risk_percentage: float = Field(default=0.02, description="% de riesgo (default 2%)")


class StopLossData(BaseModel):
    entry_price: float = Field(description="Precio de entrada")
    stop_loss_percentage: float = Field(default=0.05, description="% de stop loss (default 5%)")


@mcp.tool()
def calculate_position_size(data: PositionData) -> dict:
    """
    Calcula el tamaño de posición basado en riesgo
    Método: Fixed Fractional Position Sizing
    """
    risk_amount = data.account_balance * data.risk_percentage
    risk_per_share = abs(data.entry_price - data.stop_loss)

    if risk_per_share == 0:
        return {"error": "Stop loss no puede ser igual al precio de entrada"}

    position_size = int(risk_amount / risk_per_share)
    total_cost = position_size * data.entry_price

    return {
        "position_size": position_size,
        "total_cost": round(total_cost, 2),
        "risk_amount": round(risk_amount, 2),
        "percentage_of_capital": round((total_cost / data.account_balance) * 100, 2)
    }


@mcp.tool()
def calculate_stop_loss(data: StopLossData) -> dict:
    """Calcula el precio de stop loss"""
    stop_loss_price = data.entry_price * (1 - data.stop_loss_percentage)

    return {
        "stop_loss_price": round(stop_loss_price, 2),
        "distance": round(data.entry_price - stop_loss_price, 2),
        "percentage": data.stop_loss_percentage * 100
    }


@mcp.tool()
def calculate_risk_reward(entry: float, stop_loss: float, take_profit: float) -> dict:
    """Calcula el ratio riesgo/beneficio"""
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)

    if risk == 0:
        return {"error": "Riesgo no puede ser 0"}

    ratio = reward / risk

    return {
        "risk_reward_ratio": round(ratio, 2),
        "is_acceptable": ratio >= 2.0,
        "recommendation": "Buena operación" if ratio >= 2.0 else "Ratio muy bajo, evitar"
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
