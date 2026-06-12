import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

# Inicializa o SQLAlchemy fora da criação do app (Evita loop de importação no Gunicorn)
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'metronet_secreto_123')
    
    # Configuração do Banco de Dados
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///metronet.db')
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # --- ROTAS ---
    @app.route('/')
    def index():
        return jsonify({
            "sistema": "MetroNet Analytics",
            "status": "Online",
            "desenvolvedor": "Thiago"
        })
        
    # Cria as tabelas dentro do escopo do app
    with app.app_context():
        db.create_all()
        
    return app

# Instância que o Gunicorn (app:app) vai procurar na raiz do arquivo
app = create_app()

# --- MODELOS DO BANCO DE DADOS ---
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

if __name__ == '__main__':
    app.run(debug=True)