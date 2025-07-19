import pytest
from datetime import datetime, timedelta
from app.middleware.rate_limiting import RateLimiter

def test_rate_limiter_initialization():
    limiter = RateLimiter(max_calls=5, window_hours=24)
    assert limiter.max_calls == 5
    assert limiter.window_hours == 24
    assert limiter.calls == {}

def test_rate_limiting_basic():
    limiter = RateLimiter(max_calls=2, window_hours=24)
    client_ip = "192.168.1.1"
    
    # First call should not be rate limited
    assert not limiter.is_rate_limited(client_ip)
    limiter.record_call(client_ip)
    
    # Second call should not be rate limited
    assert not limiter.is_rate_limited(client_ip)
    limiter.record_call(client_ip)
    
    # Third call should be rate limited
    assert limiter.is_rate_limited(client_ip)

def test_rate_limiting_window():
    limiter = RateLimiter(max_calls=1, window_hours=24)
    client_ip = "192.168.1.2"
    
    # Make a call
    limiter.record_call(client_ip)
    
    # Should be rate limited
    assert limiter.is_rate_limited(client_ip)
    
    # Simulate call from past (outside window)
    past_time = datetime.now() - timedelta(hours=25)
    limiter.calls[client_ip] = [past_time]
    
    # Should not be rate limited now
    assert not limiter.is_rate_limited(client_ip)

def test_rate_limit_response():
    limiter = RateLimiter(max_calls=2, window_hours=24)
    client_ip = "192.168.1.3"
    
    # Make max calls
    limiter.record_call(client_ip)
    limiter.record_call(client_ip)
    
    response = limiter.get_rate_limit_response(client_ip)
    
    assert "error" in response
    assert response["calls_made"] == 2
    assert response["max_calls"] == 2
    assert "contact_email" in response

def test_cleanup_old_calls():
    limiter = RateLimiter(max_calls=5, window_hours=1)
    client_ip = "192.168.1.4"
    
    # Add old call
    old_time = datetime.now() - timedelta(hours=2)
    limiter.calls[client_ip] = [old_time]
    
    # Check if rate limited (should clean old calls)
    assert not limiter.is_rate_limited(client_ip)
    
    # Old call should be removed
    assert len(limiter.calls[client_ip]) == 0