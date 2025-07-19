import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class ActionTracker:
    """Track user actions for modal popup system"""
    
    def __init__(self, modal_trigger_count: int = 15):
        self.modal_trigger_count = modal_trigger_count
        self.session_actions: Dict[str, int] = {}
        
    def track_action(self, session_id: str) -> dict:
        """Track an action and return modal data if threshold reached"""
        
        if session_id not in self.session_actions:
            self.session_actions[session_id] = 0
        
        self.session_actions[session_id] += 1
        current_count = self.session_actions[session_id]
        
        should_show_modal = (
            current_count % self.modal_trigger_count == 0 and 
            current_count > 0
        )
        
        if should_show_modal:
            logger.info(f"Modal triggered for session {session_id} at {current_count} actions")
            return {
                "show_modal": True,
                "action_count": current_count,
                "modal_data": self.get_modal_content()
            }
        
        return {
            "show_modal": False,
            "action_count": current_count,
            "next_modal_at": self.modal_trigger_count - (current_count % self.modal_trigger_count)
        }
    
    def get_modal_content(self) -> dict:
        """Get the modal content for upgrade promotion"""
        return {
            "title": "🚀 Unlock the Full Power of CV Automation",
            "features": [
                "💬 Custom Chat Integrations (Slack, WhatsApp, Telegram)",
                "🔗 CRM Integration (Salesforce, HubSpot)",
                "🧠 Smart Learning Algorithm",
                "📧 Advanced Email Automation",
                "💼 LinkedIn Automation",
                "📊 Advanced Analytics"
            ]
        }

# Global action tracker instance
action_tracker = ActionTracker(modal_trigger_count=15)