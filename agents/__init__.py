"""
Multi-Agent package containing BaseAgent and its specialized implementations.
"""

from .base_agent import BaseAgent
from .research_agent import ResearchAgent
from .analyst_agent import AnalystAgent
from .workforce_query_agent import WorkforceQueryAgent
from .utilization_agent import UtilizationAgent
from .forecast_agent import ForecastAgent
from .recommendation_agent import RecommendationAgent
from .manager_agent import ManagerAgent

__all__ = [
    "BaseAgent",
    "ResearchAgent",
    "AnalystAgent",
    "WorkforceQueryAgent",
    "UtilizationAgent",
    "ForecastAgent",
    "RecommendationAgent",
    "ManagerAgent",
]
