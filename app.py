import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configurações de Produção básicas
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'metronet_secreto_123')

# Pega a URL do banco do Render. Se não achar, usa o SQLite local
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///metronet.db')

# Correção essencial para compatibilidade do SQLAlchemy com o padrão do PostgreSQL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização direta do banco
db = SQLAlchemy(app)

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

# --- ROTAS ---
@app.route('/')
def index():
    return jsonify({
        "sistema": "MetroNet Analytics",
        "status": "Online",
        "desenvolvedor": "Thiago"
    })

# Rota extra para testar se o banco conectou com sucesso na nuvem
@app.route('/test-db')
def test_db():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"banco_dados": "Conectado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"banco_dados": "Erro ao conectar", "erro": str(e)}), 500

# Cria as tabelas de forma segura em produção
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")

if __name__ == '__main__':
    app.run(debug=True)