"""
Risk Manager - Gestión de riesgo para operaciones de trading.

Este módulo proporciona funciones y clases para calcular:
- Stop Loss automático
- Take Profit automático
- Tamaño de posición basado en riesgo
- Validación de límites de exposición
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TradeRiskParams:
    """Parámetros de riesgo calculados para una operación"""
    stop_loss: float
    take_profit: float
    recommended_quantity: int
    max_quantity: int
    position_percent: float
    risk_per_share: float
    risk_reward_ratio: float
    is_valid: bool
    issues: List[str]


class RiskManager:
    """
    Gestor de riesgo para operaciones de trading.

    Calcula automáticamente stop loss, take profit y tamaño de posición
    basándose en reglas de gestión de riesgo profesionales.
    """
    def __init__(
        self,
        max_position_percent: float = 10.0,
        max_sector_percent: float = 30.0,
        default_stop_loss_percent: float = 5.0,
        default_take_profit_percent: float = 10.0,
        max_risk_per_trade_percent: float = 2.0
    ):
        """
        Args:
            max_position_percent: Máximo % del portfolio para una posición (default: 10%)
            max_sector_percent: Máximo % del portfolio en un sector (default: 30%)
            default_stop_loss_percent: Stop loss por defecto (default: 5% abajo)
            default_take_profit_percent: Take profit por defecto (default: 10% arriba)
            max_risk_per_trade_percent: Máximo riesgo por operación (default: 2%)
        """
        self.max_position_percent = max_position_percent
        self.max_sector_percent = max_sector_percent
        self.default_stop_loss_percent = default_stop_loss_percent
        self.default_take_profit_percent = default_take_profit_percent
        self.max_risk_per_trade_percent = max_risk_per_trade_percent

    def calculate_stop_loss(self, entry_price: float, percent: float = None) -> float:
        """
        Calcula el precio de stop loss.

        Args:
            entry_price: Precio de entrada
            percent: Porcentaje de pérdida permitida (default: usa configuración)

        Returns:
            Precio de stop loss
        """
        if percent is None:
            percent = self.default_stop_loss_percent
        return round(entry_price * (1 - percent / 100), 2)

    def calculate_take_profit(self, entry_price: float, percent: float = None) -> float:
        """
        Calcula el precio de take profit.

        Args:
            entry_price: Precio de entrada
            percent: Porcentaje de ganancia objetivo (default: usa configuración)

        Returns:
            Precio de take profit
        """
        if percent is None:
            percent = self.default_take_profit_percent
        return round(entry_price * (1 + percent / 100), 2)

    def calculate_position_size(
        self,
        portfolio_value: float,
        entry_price: float,
        stop_loss: float = None
    ) -> int:
        """
        Calcula el tamaño de posición óptimo basado en riesgo.

        Fórmula: (Capital × Riesgo%) / (Precio - StopLoss)

        Args:
            portfolio_value: Valor total del portfolio
            entry_price: Precio de entrada
            stop_loss: Precio de stop loss (default: calculado automáticamente)

        Returns:
            Número máximo de acciones a comprar
        """
        if stop_loss is None:
            stop_loss = self.calculate_stop_loss(entry_price)

        # Calcular riesgo máximo en dólares
        risk_amount = portfolio_value * (self.max_risk_per_trade_percent / 100)

        # Riesgo por acción
        risk_per_share = entry_price - stop_loss

        if risk_per_share <= 0:
            return 0

        # Tamaño por riesgo
        size_by_risk = int(risk_amount / risk_per_share)

        # Limitar por exposición máxima
        max_position_value = portfolio_value * (self.max_position_percent / 100)
        size_by_exposure = int(max_position_value / entry_price)

        # Retornar el menor de los dos
        return max(1, min(size_by_risk, size_by_exposure))

    def calculate_risk_reward_ratio(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float
    ) -> float:
        """
        Calcula el ratio riesgo/beneficio.

        Args:
            entry_price: Precio de entrada
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit

        Returns:
            Ratio (ej: 2.0 significa potencial de ganancia 2x mayor que pérdida)
        """
        risk = entry_price - stop_loss
        reward = take_profit - entry_price

        if risk <= 0:
            return 0.0

        return round(reward / risk, 2)

    def analyze_trade(
        self,
        portfolio_value: float,
        current_holdings: Dict[str, int],
        symbol: str,
        quantity: int,
        price: float,
        action: str = "BUY"
    ) -> TradeRiskParams:
        """
        Analiza una operación y retorna parámetros de riesgo.

        Args:
            portfolio_value: Valor total del portfolio
            current_holdings: Holdings actuales {symbol: quantity}
            symbol: Símbolo a operar
            quantity: Cantidad solicitada
            price: Precio actual
            action: "BUY" o "SELL"

        Returns:
            TradeRiskParams con todos los parámetros calculados
        """
        issues = []

        # Calcular stop loss y take profit
        stop_loss = self.calculate_stop_loss(price)
        take_profit = self.calculate_take_profit(price)

        # Calcular tamaño recomendado
        recommended_quantity = self.calculate_position_size(portfolio_value, price, stop_loss)

        # Calcular exposición
        position_value = quantity * price
        position_percent = (position_value / portfolio_value) * 100 if portfolio_value > 0 else 0

        # Calcular riesgo por acción
        risk_per_share = price - stop_loss

        # Calcular ratio riesgo/beneficio
        risk_reward_ratio = self.calculate_risk_reward_ratio(price, stop_loss, take_profit)

        # Validaciones
        if action == "BUY":
            # Verificar exposición máxima
            if position_percent > self.max_position_percent:
                issues.append(
                    f"Posición ({position_percent:.1f}%) excede límite de {self.max_position_percent}%"
                )

            # Verificar cantidad vs recomendada
            if quantity > recommended_quantity:
                issues.append(
                    f"Cantidad ({quantity}) excede recomendada ({recommended_quantity})"
                )

        # Calcular cantidad máxima permitida
        max_position_value = portfolio_value * (self.max_position_percent / 100)
        max_quantity = int(max_position_value / price) if price > 0 else 0

        return TradeRiskParams(
            stop_loss=stop_loss,
            take_profit=take_profit,
            recommended_quantity=recommended_quantity,
            max_quantity=max_quantity,
            position_percent=round(position_percent, 2),
            risk_per_share=round(risk_per_share, 2),
            risk_reward_ratio=risk_reward_ratio,
            is_valid=len(issues) == 0,
            issues=issues
        )


# Instancia global con configuración por defecto
default_risk_manager = RiskManager()
