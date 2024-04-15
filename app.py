from flask import Flask
from dotenv import load_dotenv, dotenv_values

# Define app.
app = Flask(__name__)

# Load the .env file.
load_dotenv()
config = dotenv_values()

app.config.from_mapping(config)

# Import the __init__.py from modules which had imported all files from the folder.
import modules
