#!/usr/bin/env python3
"""
Production-Ready IDVerse Server Startup Script
High scalability, security, and monitoring features
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def setup_logging():
    """Setup comprehensive logging for production"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('idverse.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def setup_environment():
    """Setup production environment variables"""
    logger = logging.getLogger(__name__)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Set production defaults
    env_vars = {
        'FLASK_ENV': 'production',
        'FLASK_DEBUG': 'False',
        'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///./instance/idverse.db'),
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'change-this-in-production'),
        'SECRET_KEY': os.getenv('SECRET_KEY', 'change-this-in-production'),
        'IPFS_SERVICE_MODE': os.getenv('IPFS_SERVICE_MODE', 'mock'),
        'SIGNING_SERVICE_MODE': os.getenv('SIGNING_SERVICE_MODE', 'mock'),
        'REGISTRY_SERVICE_MODE': os.getenv('REGISTRY_SERVICE_MODE', 'mock'),
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        logger.info(f"Set {key} = {value}")
    
    return logger

def create_production_app():
    """Create production-ready Flask application"""
    logger = logging.getLogger(__name__)
    
    try:
        from backend import create_app
        app = create_app()
        
        # Production-specific configurations
        app.config.update({
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_size': int(os.getenv('DB_POOL_SIZE', 20)),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 30)),
                'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
                'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600)),
            }
        })
        
        logger.info("✅ Production app created successfully")
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to create app: {e}")
        raise

def add_security_headers(app):
    """Add security headers for production"""
    from flask import make_response
    
    @app.after_request
    def after_request(response):
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response

def add_monitoring_endpoints(app):
    """Add monitoring and health check endpoints"""
    from flask import jsonify
    import psutil
    import time
    
    @app.route('/health')
    def health_check():
        """Comprehensive health check"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Database health
            from backend.extensions import db
            db.session.execute('SELECT 1')
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent
                },
                'database': 'connected',
                'services': {
                    'ipfs': os.getenv('IPFS_SERVICE_MODE', 'mock'),
                    'signing': os.getenv('SIGNING_SERVICE_MODE', 'mock'),
                    'registry': os.getenv('REGISTRY_SERVICE_MODE', 'mock')
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    @app.route('/metrics')
    def metrics():
        """System metrics endpoint"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return jsonify({
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def main():
    """Main production server startup"""
    logger = setup_logging()
    
    logger.info("🚀 Starting IDVerse Production Server")
    logger.info(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Setup environment
        setup_environment()
        
        # Create production app
        app = create_production_app()
        
        # Add security headers
        add_security_headers(app)
        
        # Add monitoring endpoints
        add_monitoring_endpoints(app)
        
        # Get server configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info(f"🌐 Starting server on {host}:{port}")
        logger.info(f"🔧 Debug mode: {debug}")
        logger.info(f"📊 Environment: {os.getenv('FLASK_ENV', 'development')}")
        
        # Start server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=False  # Disable reloader in production
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
