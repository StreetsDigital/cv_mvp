from typing import Dict, Any
from ..config import settings

class MVPLimitationHandler:
    """Handles feature limitations and provides upgrade messaging"""
    
    @staticmethod
    def get_limitation_message(feature: str) -> Dict[str, Any]:
        """Get standardized limitation message for premium features"""
        
        feature_messages = {
            "email_integration": {
                "title": "📧 Email Automation",
                "message": f"Automated email generation and sending is available in our premium plan.\n\n"
                          f"**What you're missing:**\n"
                          f"• Personalized email generation\n"
                          f"• Automated follow-up sequences\n"
                          f"• Email template customization\n"
                          f"• Send tracking and analytics\n\n"
                          f"**You can still:**\n"
                          f"• Copy the candidate analysis\n"
                          f"• Manually draft emails\n"
                          f"• Use the insights for outreach",
                "upgrade_benefit": "Automate your entire candidate outreach process."
            },
            "linkedin_integration": {
                "title": "💼 LinkedIn Integration", 
                "message": f"LinkedIn profile search and automated connection requests are premium features.\n\n"
                          f"**What you're missing:**\n"
                          f"• Automatic LinkedIn profile discovery\n"
                          f"• Connection request automation\n"
                          f"• Profile data enrichment\n"
                          f"• Social media insights\n\n"
                          f"**You can still:**\n"
                          f"• Use the candidate name for manual search\n"
                          f"• Copy analysis for LinkedIn messages\n"
                          f"• Manual profile research",
                "upgrade_benefit": "Streamline your LinkedIn recruiting workflow."
            }
        }
        
        base_message = feature_messages.get(feature, {
            "title": "🔒 Premium Feature",
            "message": f"This feature is available in our premium plan.",
            "upgrade_benefit": "Unlock advanced recruiting capabilities."
        })
        
        return {
            "type": "limitation",
            "title": base_message["title"],
            "content": base_message["message"],
            "upgrade_benefit": base_message["upgrade_benefit"],
            "contact_email": settings.premium_contact_email,
            "actions": [
                {
                    "type": "contact_sales",
                    "label": "💬 Contact Sales",
                    "email": settings.premium_contact_email
                },
                {
                    "type": "continue_free",
                    "label": "📋 Continue with Free Features"
                }
            ]
        }
    
    @staticmethod
    def is_feature_enabled(feature: str) -> bool:
        """Check if a feature is enabled"""
        feature_flags = {
            "email_integration": settings.enable_email_integration,
            "linkedin_integration": settings.enable_linkedin_integration,
            "analytics": settings.enable_analytics,
        }
        return feature_flags.get(feature, False)