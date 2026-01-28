from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

# -------------------------------
# App & Database
# -------------------------------
app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

# Ajuste o caminho se o banco estiver em outro lugar
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql+psycopg://postgres:Arahuzim26052300!@db.voibxmtriglolckeomgh.supabase.co:5432/postgres'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
