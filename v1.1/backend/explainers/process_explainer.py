import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator
import json
import asyncio
from enum import Enum

from ..models.workflow_models import ProcessStep

logger = logging.getLogger(__name__)

class ExplanationLevel(str, Enum):
    MINIMAL = "minimal"
    MODERATE = "moderate"
    DETAILED = "detailed"

class ProcessExplainer:
    """Real-time process explanation engine for CV analysis"""
    
    def __init__(self, session_id: str, detail_level: ExplanationLevel = ExplanationLevel.MODERATE):
        self.session_id = session_id
        self.detail_level = detail_level
        self.explanation_log: List[Dict[str, Any]] = []
        self.current_step = 0
        self.human_interventions: List[Dict[str, Any]] = []
        self.websocket_callbacks: List[callable] = []
        
    def add_websocket_callback(self, callback: callable):
        """Add WebSocket callback for real-time updates"""
        self.websocket_callbacks.append(callback)
    
    async def start_analysis_session(self):
        """Initialize process explanation session"""
        await self.explain_step(
            "🚀 **Starting Enhanced CV Analysis**",
            "Initializing comprehensive analysis using 10 skill categories optimized for digital media recruiting",
            {
                "session_id": self.session_id,
                "detail_level": self.detail_level,
                "expected_steps": 15,
                "analysis_config": {
                    "skill_categories": 10,
                    "keyword_extraction": True,
                    "pattern_matching": True,
                    "industry_analysis": True
                }
            }
        )
    
    async def explain_step(
        self, 
        title: str, 
        description: str, 
        data: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None,
        human_intervention_available: bool = False
    ):
        """Add explanation step with optional data"""
        self.current_step += 1
        
        explanation = {
            "step": self.current_step,
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "description": description,
            "data": data or {},
            "confidence": confidence,
            "human_intervention_available": human_intervention_available,
            "type": "process_update",
            "session_id": self.session_id
        }
        
        self.explanation_log.append(explanation)
        
        # Real-time broadcast to frontend
        await self._broadcast_to_frontend(explanation)
        
        # Add small delay for realistic timing
        await asyncio.sleep(0.5)
        
        return explanation
