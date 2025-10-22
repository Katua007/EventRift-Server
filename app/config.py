import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost:5432/eventrift_dev')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-super-secret-key-change-me')
    
    # Other Configs
    SECRET_KEY = os.environ.get('SECRET_KEY', 'another-default-secret')