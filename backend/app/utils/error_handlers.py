"""Error handling utilities and middleware."""
from flask import jsonify
from datetime import datetime
from werkzeug.exceptions import HTTPException


def create_error_response(message, code='ERROR', status_code=400):
    """
    Create a standardized error response.
    
    Args:
        message (str): Human-readable error message
        code (str): Error code for programmatic handling
        status_code (int): HTTP status code
        
    Returns:
        tuple: (response, status_code)
    """
    return jsonify({
        'error': True,
        'message': message,
        'code': code,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), status_code


def register_error_handlers(app):
    """
    Register error handlers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return create_error_response(
            message=str(error.description) if hasattr(error, 'description') else 'Bad Request',
            code='BAD_REQUEST',
            status_code=400
        )
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return create_error_response(
            message='Resource not found',
            code='NOT_FOUND',
            status_code=404
        )
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return create_error_response(
            message='Method not allowed',
            code='METHOD_NOT_ALLOWED',
            status_code=405
        )
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        return create_error_response(
            message='Internal server error',
            code='INTERNAL_SERVER_ERROR',
            status_code=500
        )
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions."""
        # Pass through HTTP errors
        if isinstance(error, HTTPException):
            return error
        
        # Log the error
        app.logger.error(f'Unhandled exception: {str(error)}', exc_info=True)
        
        # Return generic error response
        return create_error_response(
            message='An unexpected error occurred',
            code='INTERNAL_ERROR',
            status_code=500
        )


class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message, code='VALIDATION_ERROR'):
        self.message = message
        self.code = code
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """Custom exception for business logic errors."""
    def __init__(self, message, code='BUSINESS_LOGIC_ERROR'):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ResourceNotFoundError(Exception):
    """Custom exception for resource not found errors."""
    def __init__(self, message, code='RESOURCE_NOT_FOUND'):
        self.message = message
        self.code = code
        super().__init__(self.message)
