import os
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configurações de Produção básicas
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'metronet_secreto_123')

# Pega a URL bruta da nuvem e limpa ao máximo (evita erros de clipboard)
raw_url = os.environ.get('DATABASE_URL', '')
DATABASE_URL = raw_url.strip().replace('"', '').replace("'", "")

# Se a URL não começar com os padrões válidos do SQLAlchemy, joga para o SQLite local de segurança
if not DATABASE_URL.startswith("postgres://") and not DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = 'sqlite:///metronet.db'
else:
    # Correção do dialeto antigo do Heroku/Render para o SQLAlchemy moderno
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
    # Busca todos os funcionários e também os setores para listar no select do modal
    funcionarios_banco = Usuario.query.all()
    setores_banco = Setor.query.all()
    
    return render_template('index.html', funcionarios=funcionarios_banco, setores=setores_banco)

@app.route('/cadastrar-funcionario', methods=['POST'])
def cadastrar_funcionario():
    # Coleta os dados vindos do formulário HTML
    nome = request.form.get('nome')
    email = request.form.get('email')
    setor_id = request.form.get('setor_id')
    
    if nome and email and setor_id:
        try:
            # Cria a nova instância do funcionário
            novo_func = Usuario(
                nome=nome,
                email=email,
                setor_id=int(setor_id),
                senha_hash="scrypt:32768:8:1$padrao123" # Senha padrão inicial temporária
            )
            db.session.add(novo_func)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao cadastrar funcionário: {e}")
            
    # Redireciona de volta para a página inicial atualizada
    return redirect(url_for('index'))

@app.route('/api-status')
def api_status():
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


# Inicialização e carga de teste se o banco estiver zerado
with app.app_context():
    try:
        db.create_all()
        
        if not Setor.query.first():
            comercial = Setor(nome="Comercial")
            retencao = Setor(nome="Retenção")
            suporte = Setor(nome="Suporte Técnico")
            db.session.add_all([comercial, retencao, suporte])
            db.session.commit()
            
            usuario_teste = Usuario(
                nome="Thiago Desenvolvedor",
                email="thiago@metronet.com.br",
                senha_hash="scrypt:32768:8:1$hash_fake_seguro",
                perfil_acesso="admin",
                setor_id=comercial.id
            )
            db.session.add(usuario_teste)
            db.session.commit()
            
    except Exception as e:
        print(f"Erro ao inicializar dados: {e}")

if __name__ == '__main__':
    app.run(debug=True)