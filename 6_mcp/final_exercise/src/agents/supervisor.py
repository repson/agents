from agents import Agent, Runner
from typing import Dict
import json
import re
from datetime import datetime


class TradingSupervisor:
    """
    Agente supervisor que revisa operaciones de trading.
    """
    def __init__(self):
        self.agent = Agent(
            name="Supervisor",
            model="gpt-4o-mini",
            instructions=self._get_instructions()
        )
        self.reviews = []  # Historial de revisiones

    def _get_instructions(self) -> str:
        return """
        Eres un supervisor de trading experimentado y riguroso.

        Tu rol es revisar operaciones propuestas por traders y aprobarlas o rechazarlas.

        CRITERIOS DE EVALUACIÓN:

        1. GESTIÓN DE RIESGO (40% peso):
           - Position size <= 10% del portfolio total
           - Existe stop loss configurado
           - Risk/reward ratio >= 2:1
           - No más de 3 posiciones abiertas en el mismo sector

        2. DIVERSIFICACIÓN (30% peso):
           - Una sola acción no debe superar 30% del portfolio
           - Mínimo 3 sectores diferentes en el portfolio
           - No más del 40% en un solo sector

        3. RAZONAMIENTO (20% peso):
           - Justificación clara y fundamentada
           - Análisis técnico O fundamental presente
           - Coherente con la estrategia declarada del trader
           - No basado en emociones o FOMO

        4. TIMING (10% peso):
           - Mercado abierto (si es necesario)
           - No hay earnings report en 48h
           - Volatilidad dentro de rangos normales

        FORMATO DE RESPUESTA (JSON):
        {
            "approved": true/false,
            "risk_score": 1-10,
            "feedback": "Explicación detallada de la decisión",
            "suggestions": ["Sugerencia 1", "Sugerencia 2"],
            "concerns": ["Preocupación 1", "Preocupación 2"]
        }

        Si APRUEBAS (approved: true):
        - feedback: Confirmación positiva y aspectos bien ejecutados
        - suggestions: Mejoras opcionales
        - concerns: Vacío o riesgos menores a monitorear

        Si RECHAZAS (approved: false):
        - feedback: Explicación clara de por qué se rechaza
        - suggestions: Cómo mejorar la propuesta
        - concerns: Riesgos específicos identificados

        Sé estricto pero justo. Tu objetivo es proteger el capital.
        IMPORTANTE: Responde SOLO con el JSON, sin texto adicional.
        """

    async def review_trade(self, proposal: Dict) -> Dict:
        """
        Revisa una propuesta de operación.
        """
        # Calcular métricas adicionales
        position_value = proposal['quantity'] * proposal['price']
        position_pct = (position_value / proposal['portfolio_value']) * 100

        # Extraer parámetros de riesgo si están disponibles
        risk_params = proposal.get('risk_params', {})
        risk_section = ""

        if risk_params:
            risk_section = f"""
        ANÁLISIS DE RIESGO (calculado automáticamente):
        - Cantidad recomendada: {risk_params.get('recommended_quantity', 'N/A')} acciones
        - Cantidad máxima: {risk_params.get('max_quantity', 'N/A')} acciones
        - % del portfolio: {risk_params.get('position_percent', position_pct):.1f}%
        - Riesgo por acción: ${risk_params.get('risk_per_share', 0):.2f}
        - Ratio riesgo/beneficio: {risk_params.get('risk_reward_ratio', 'N/A')}:1
        """

        # Preparar contexto para el supervisor
        context = f"""
        PROPUESTA DE OPERACIÓN

        Trader: {proposal['trader_name']}
        Estrategia: {proposal['trader_strategy']}

        OPERACIÓN:
        - Acción: {proposal['action']}
        - Símbolo: {proposal['symbol']}
        - Sector: {proposal.get('sector', 'Desconocido')}
        - Cantidad: {proposal['quantity']} acciones
        - Precio: ${proposal['price']:.2f}
        - Valor total: ${position_value:.2f}
        - % del portfolio: {position_pct:.1f}%

        GESTIÓN DE RIESGO:
        - Stop Loss: {f"${proposal['stop_loss']:.2f}" if proposal.get('stop_loss') else "NO CONFIGURADO"}
        - Take Profit: {f"${proposal['take_profit']:.2f}" if proposal.get('take_profit') else "No especificado"}
        {risk_section}
        PORTFOLIO ACTUAL:
        - Valor total: ${proposal['portfolio_value']:.2f}
        - Holdings: {json.dumps(proposal['current_holdings'], indent=2)}

        RAZONAMIENTO DEL TRADER:
        {proposal['rationale']}

        ---

        Analiza esta propuesta y responde SOLO con el JSON.
        """

        try:
            # Ejecutar agente supervisor usando Runner
            result = await Runner.run(self.agent, context, max_turns=1)

            # Extraer el contenido del último mensaje
            if result.new_items:
                last_message = result.new_items[-1]
                response_text = last_message.content[0].text if hasattr(last_message, 'content') else str(last_message)
            else:
                response_text = result.final_output if hasattr(result, 'final_output') else str(result)

            # Buscar JSON en la respuesta (puede venir con texto adicional)
            json_match = re.search(r'\{[^{}]*"approved"[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                review = json.loads(json_match.group())
            else:
                # Intentar parsear directamente
                review = json.loads(response_text)

            # Validar estructura y añadir valores por defecto
            if 'approved' not in review:
                review['approved'] = True  # Por defecto aprobar si no se especifica
            if 'risk_score' not in review:
                review['risk_score'] = 5
            if 'feedback' not in review:
                review['feedback'] = "Operación analizada"
            if 'suggestions' not in review:
                review['suggestions'] = []
            if 'concerns' not in review:
                review['concerns'] = []

            # Registrar revisión
            self._log_review(proposal, review)

            return review

        except Exception as e:
            # Fallback: aprobar por defecto pero registrar el error
            print(f"Error en supervisor review: {e}")
            return {
                "approved": True,
                "risk_score": 5,
                "feedback": f"Aprobación automática (error en evaluación: {str(e)[:50]})",
                "suggestions": [],
                "concerns": ["Revisar manualmente"]
            }

    def _log_review(self, proposal: Dict, review: Dict):
        """Registra la revisión en el historial"""
        self.reviews.append({
            "timestamp": datetime.now().isoformat(),
            "trader": proposal['trader_name'],
            "symbol": proposal['symbol'],
            "action": proposal['action'],
            "approved": review['approved'],
            "risk_score": review['risk_score']
        })

    def get_statistics(self) -> Dict:
        """Obtiene estadísticas de revisiones"""
        if not self.reviews:
            return {"total": 0, "approved": 0, "rejected": 0, "approval_rate": 0}

        approved = sum(1 for r in self.reviews if r['approved'])

        return {
            "total": len(self.reviews),
            "approved": approved,
            "rejected": len(self.reviews) - approved,
            "approval_rate": (approved / len(self.reviews)) * 100,
            "avg_risk_score": sum(r['risk_score'] for r in self.reviews) / len(self.reviews)
        }