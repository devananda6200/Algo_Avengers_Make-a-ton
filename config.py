import os

class Config:
    """Base configuration with default settings."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Secret key for sessions
    DEBUG = False  # Default: No debugging
    TESTING = False  # Default: Not in testing mode
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')  # Default: SQLite DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable track modifications to save resources

class DevelopmentConfig(Config):
    """Configuration for development."""
    DEBUG = True  # Enable debug mode for development
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'sqlite:///dev.db')

class TestingConfig(Config):
    """Configuration for testing."""
    TESTING = True  # Enable testing mode
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')
    DEBUG = True  # Enable debug mode for testing

class ProductionConfig(Config):
    """Configuration for production."""
    DEBUG = False  # Disable debug mode
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/prod_db')

# Dictionary to access configurations easily
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
