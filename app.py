import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'metronet_secreto_123')

# Pega a URL bruta e higieniza ao máximo
raw_url = os.environ.get('DATABASE_URL', '')

# Força uma string limpa sem espaços, quebras de linha ou aspas soltas
DATABASE_URL = raw_url.strip().replace('"', '').replace("'", "")

# Se a URL não começar com os padrões válidos do SQLALchemy, joga para o SQLite local de segurança
if not DATABASE_URL.startswith("postgres://") and not DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = 'sqlite:///metronet.db'
else:
    # Correção do dialeto antigo do Heroku/Render para o SQLAlchemy moderno
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS ---
class Setor(db.Model):
    __tablename__ = 'setores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    usuarios = db.relationship('Usuario', backref='setor', lazy=True)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil_acesso = db.Column(db.String(20), default='funcionario')
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)

# --- ROTAS ---
@app.route('/')
def index():
    return jsonify({
        "sistema": "MetroNet Analytics",
        "status": "Online",
        "desenvolvedor": "Thiago",
        "modo_banco": "PostgreSQL" if "postgresql" in DATABASE_URL else "SQLite de Emergência"
    })

@app.route('/test-db')
def test_db():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"banco_dados": "Conectado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"banco_dados": "Erro ao conectar", "erro": str(e)}), 500

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")

if __name__ == '__main__':
    app.run(debug=True)