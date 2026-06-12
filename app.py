import os
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configurações de Produção básicas
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'metronet_secreto_123')

# Pega a URL bruta da nuvem e limpa ao máximo
raw_url = os.environ.get('DATABASE_URL', '')

# Força uma string limpa sem espaços, quebras de linha ou aspas soltas (evita crash no Render)
DATABASE_URL = raw_url.strip().replace('"', '').replace("'", "")

# Se a URL não começar com os padrões válidos do SQLAlchemy, joga para o SQLite local de segurança
if not DATABASE_URL.startswith("postgres://") and not DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = 'sqlite:///metronet.db'
else:
    # Correção do dialeto antigo para o SQLAlchemy moderno
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do banco de dados
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
    perfil_acesso = db.Column(db.String(20), default='funcionario') # admin, gestor, funcionario
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'), nullable=False)


# --- ROTAS DO SISTEMA ---

@app.route('/')
def index():
    # Renderiza a interface visual do Dashboard localizada em templates/index.html
    return render_template('index.html')

@app.route('/api-status')
def api_status():
    # Mantida a rota antiga formatada em JSON para checagem rápida de informações de backend
    return jsonify({
        "sistema": "MetroNet Analytics",
        "status": "Online",
        "desenvolvedor": "Thiago",
        "modo_banco": "PostgreSQL" if "postgresql" in DATABASE_URL else "SQLite de Emergência"
    })

@app.route('/test-db')
def test_db():
    # Endpoint de diagnóstico para validar a comunicação com o PostgreSQL do Render
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"banco_dados": "Conectado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"banco_dados": "Erro ao conectar", "erro": str(e)}), 500


# Cria as tabelas de forma segura em escopo de contexto do Flask
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")

if __name__ == '__main__':
    app.run(debug=True)