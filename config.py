
import os
from dotenv import load_dotenv

class DefaultConfig:    
    load_dotenv('.env')
    
    PORT = os.environ.get('PORT', 3978)
