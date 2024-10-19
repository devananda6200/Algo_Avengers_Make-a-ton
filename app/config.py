import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Example with SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QDRANT_URL='https://eb73641e-e337-4ffb-aca0-cd971124d92b.europe-west3-0.gcp.cloud.qdrant.io'
    QDRANT_API_KEY='4ej2CtpmKE58hpx-JPbzF-IoUBuobQ-JBRlNI_TmdlOlu6bk48ujXw'
    TOGETHER_API = 'feda905a3fc3a4250e1c91e84e8639544eb02b0c9366d4d4047d3b70e69aad92'

