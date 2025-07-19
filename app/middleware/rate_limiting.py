import logging
from typing import Dict
from datetime import datetime, timedelta
from fastapi import Request

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter for MVP"""
    
    def __init__(self, max_calls: int = 5, window_hours: int = 24):
        self.max_calls = max_calls
        self.window_hours = window_hours
        self.calls: Dict[str, list] = {}
        self.contact_email = "andrew@automateengage.com"
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"
    
    def is_rate_limited(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit"""
        now = datetime.now()
        window_start = now - timedelta(hours=self.window_hours)
        
        if client_ip not in self.calls:
            self.calls[client_ip] = []
        
        # Clean old entries
        self.calls[client_ip] = [
            timestamp for timestamp in self.calls[client_ip] 
            if timestamp > window_start
        ]
        
        return len(self.calls[client_ip]) >= self.max_calls
    
    def record_call(self, client_ip: str):
        """Record a new API call"""
        if client_ip not in self.calls:
            self.calls[client_ip] = []
        
        self.calls[client_ip].append(datetime.now())
    
    def get_rate_limit_response(self, client_ip: str) -> dict:
        """Get rate limit exceeded response"""
        calls_made = len(self.calls.get(client_ip, []))
        
        return {
            "error": "Rate limit exceeded",
            "message": f"🚫 **Free tier limit reached!**\n\n"
                      f"You've used {calls_made}/{self.max_calls} daily CV analyses.\n\n"
                      f"**Want unlimited access?** Contact {self.contact_email}",
            "contact_email": self.contact_email,
            "calls_made": calls_made,
            "max_calls": self.max_calls
        }

# Global rate limiter instance
rate_limiter = RateLimiter(max_calls=5, window_hours=24)

def check_rate_limit(request: Request):
    """Middleware function to check rate limits"""
    client_ip = rate_limiter.get_client_ip(request)
    
    # Skip rate limiting for local development
    if client_ip in ["127.0.0.1", "localhost", "unknown"]:
        return None
    
    if rate_limiter.is_rate_limited(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return rate_limiter.get_rate_limit_response(client_ip)
    
    rate_limiter.record_call(client_ip)
    return None