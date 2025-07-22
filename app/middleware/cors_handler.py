"""
Enhanced CORS handler for AWS Lambda deployment
Ensures proper CORS headers for all responses including errors
"""

from typing import Dict, Any
import json


class CORSHandler:
    """Handle CORS headers for Lambda responses"""
    
    @staticmethod
    def get_cors_headers(origin: str = "*") -> Dict[str, str]:
        """Get standard CORS headers"""
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent,X-Requested-With",
            "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
            "Access-Control-Allow-Credentials": "false",
            "Access-Control-Max-Age": "86400"
        }
    
    @staticmethod
    def handle_preflight(event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OPTIONS preflight requests"""
        return {
            "statusCode": 200,
            "headers": CORSHandler.get_cors_headers(),
            "body": ""
        }
    
    @staticmethod
    def add_cors_headers(response: Dict[str, Any], origin: str = "*") -> Dict[str, Any]:
        """Add CORS headers to any response"""
        if "headers" not in response:
            response["headers"] = {}
        
        response["headers"].update(CORSHandler.get_cors_headers(origin))
        return response
    
    @staticmethod
    def create_cors_response(
        status_code: int,
        body: Any,
        headers: Dict[str, str] = None,
        origin: str = "*"
    ) -> Dict[str, Any]:
        """Create a complete CORS-enabled response"""
        response_headers = CORSHandler.get_cors_headers(origin)
        if headers:
            response_headers.update(headers)
        
        # Ensure body is a string
        if isinstance(body, dict) or isinstance(body, list):
            body = json.dumps(body)
        
        return {
            "statusCode": status_code,
            "headers": response_headers,
            "body": body
        }
    
    @staticmethod
    def handle_error(error: Exception, status_code: int = 500) -> Dict[str, Any]:
        """Create CORS-enabled error response"""
        error_body = {
            "error": "Internal server error" if status_code == 500 else "Bad request",
            "message": str(error) if status_code != 500 else "An unexpected error occurred"
        }
        
        return CORSHandler.create_cors_response(
            status_code=status_code,
            body=error_body
        )