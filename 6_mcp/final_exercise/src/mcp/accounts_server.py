import json

from mcp.server.fastmcp import FastMCP
from src.core.accounts import Account
from src.agents.supervisor import TradingSupervisor
from src.core.market import get_share_price
from src.core.risk_manager import RiskManager
from pathlib import Path
from datetime import datetime

mcp = FastMCP("accounts_server")

# Crear instancias globales
risk_manager = RiskManager()
# Crear instancia global del supervisor
supervisor = TradingSupervisor()

def _log_supervisor_review_to_json(name: str, proposal: dict, review: dict):
    """Registra la propuesta y respuesta del supervisor en JSON"""
    log_file = Path(f"data/logs/trades_{name}.json")

    # Leer archivo existente
    try:
        with open(log_file, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # Crear entrada
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proposal": {
            "action": proposal['action'],
            "symbol": proposal['symbol'],
            "quantity": proposal['quantity'],
            "price": proposal['price'],
            "rationale": proposal['rationale'],
            "stop_loss": proposal.get('stop_loss'),
            "take_profit": proposal.get('take_profit'),
            "sector": proposal.get('sector', 'Unknown')
        },
        "risk_params": proposal.get('risk_params', {}),
        "supervisor_review": {
            "approved": review['approved'],
            "risk_score": review['risk_score'],
            "feedback": review['feedback'],
            "suggestions": review.get('suggestions', []),
            "concerns": review.get('concerns', [])
        },
        "executed": review['approved']
    }

    data.append(entry)

    # Guardar con formato legible
    with open(log_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@mcp.tool()
async def get_balance(name: str) -> float:
    """Obtiene el saldo en efectivo de la cuenta indicada.

    Args:
        name: El nombre del titular de la cuenta
    """
    return Account.get(name).balance

@mcp.tool()
async def get_holdings(name: str) -> dict[str, int]:
    """Obtiene las tenencias de la cuenta indicada.

    Args:
        name: El nombre del titular de la cuenta
    """
    return Account.get(name).holdings

@mcp.tool()
async def buy_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Compra acciones de una empresa.

    Args:
        name: El nombre del titular de la cuenta
        symbol: El símbolo de la acción
        quantity: La cantidad de acciones a comprar
        rationale: La razón de la compra y su relación con la estrategia de la cuenta
    """
    account = Account.get(name)
    price = get_share_price(symbol)
    portfolio_value = account.calculate_portfolio_value()

    # Calcular parámetros de riesgo automáticamente
    risk_params = risk_manager.analyze_trade(
        portfolio_value=portfolio_value,
        current_holdings=account.holdings,
        symbol=symbol,
        quantity=quantity,
        price=price,
        action="BUY"
    )

    # Preparar propuesta para el supervisor con parámetros de riesgo
    proposal = {
        "trader_name": name,
        "trader_strategy": account.get_strategy(),
        "action": "BUY",
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
        "rationale": rationale,
        "stop_loss": risk_params.stop_loss,
        "take_profit": risk_params.take_profit,
        "sector": "Unknown",
        "portfolio_value": portfolio_value,
        "current_holdings": account.holdings,
        "risk_params": {
            "recommended_quantity": risk_params.recommended_quantity,
            "max_quantity": risk_params.max_quantity,
            "position_percent": risk_params.position_percent,
            "risk_per_share": risk_params.risk_per_share,
            "risk_reward_ratio": risk_params.risk_reward_ratio
        }
    }

    # Consultar al supervisor
    review = await supervisor.review_trade(proposal)

    # Registrar en JSON
    _log_supervisor_review_to_json(name, proposal, review)

    # Si está aprobada, ejecutar
    if review['approved']:
        return account.buy_shares(symbol, quantity, f"{rationale} | Supervisor: {review['feedback']}")
    else:
        # Si está rechazada, no ejecutar y retornar mensaje
        raise ValueError(f"Operación RECHAZADA por supervisor: {review['feedback']}")


@mcp.tool()
async def sell_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Vende acciones de una empresa.

    Args:
        name: El nombre del titular de la cuenta
        symbol: El símbolo de la acción
        quantity: La cantidad de acciones a vender
        rationale: La razón de la venta y su relación con la estrategia de la cuenta
    """
    account = Account.get(name)
    price = get_share_price(symbol)
    portfolio_value = account.calculate_portfolio_value()

    # Calcular parámetros de riesgo automáticamente
    risk_params = risk_manager.analyze_trade(
        portfolio_value=portfolio_value,
        current_holdings=account.holdings,
        symbol=symbol,
        quantity=quantity,
        price=price,
        action="SELL"
    )

    # Preparar propuesta para el supervisor con parámetros de riesgo
    proposal = {
        "trader_name": name,
        "trader_strategy": account.get_strategy(),
        "action": "SELL",
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
        "rationale": rationale,
        "stop_loss": risk_params.stop_loss,
        "take_profit": risk_params.take_profit,
        "sector": "Unknown",
        "portfolio_value": portfolio_value,
        "current_holdings": account.holdings,
        "risk_params": {
            "position_percent": risk_params.position_percent,
            "risk_per_share": risk_params.risk_per_share,
            "risk_reward_ratio": risk_params.risk_reward_ratio
        }
    }

    # Consultar al supervisor
    review = await supervisor.review_trade(proposal)

    # Registrar en JSON
    _log_supervisor_review_to_json(name, proposal, review)

    # Si está aprobada, ejecutar
    if review['approved']:
        return account.sell_shares(symbol, quantity, f"{rationale} | Supervisor: {review['feedback']}")
    else:
        # Si está rechazada, no ejecutar y retornar mensaje
        raise ValueError(f"Operación RECHAZADA por supervisor: {review['feedback']}")

@mcp.tool()
async def change_strategy(name: str, strategy: str) -> str:
    """A tu discreción, si lo deseas, llama a esto para cambiar tu estrategia de inversión futura.

    Args:
        name: El nombre del titular de la cuenta
        strategy: La nueva estrategia para la cuenta
    """
    return Account.get(name).change_strategy(strategy)

@mcp.resource("accounts://accounts_server/{name}")
async def read_account_resource(name: str) -> str:
    account = Account.get(name.lower())
    return account.report()

@mcp.resource("accounts://strategy/{name}")
async def read_strategy_resource(name: str) -> str:
    account = Account.get(name.lower())
    return account.get_strategy()

if __name__ == "__main__":
    mcp.run(transport='stdio')