from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    theme = db.Column(db.String(20), default='hello-kitty')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('Event', backref='user', lazy=True, cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', backref='user', lazy=True, cascade='all, delete-orphan')
    gallery_items = db.relationship('GalleryItem', backref='user', lazy=True, cascade='all, delete-orphan')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='pessoal')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='pessoal')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    time = db.Column(db.Time, nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GalleryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    caption = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_data = db.Column(db.Text, nullable=False)  # Base64 encoded image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Dados das cartinhas diárias (60 cartinhas)
DAILY_LETTERS_DATA = [
    {
        'day': 1,
        'title': "Meu Amor por Você",
        'content': "Bom dia, minha princesa! Acordei pensando em você e no quanto você ilumina meus dias. Sua presença na minha vida é como um raio de sol em um dia nublado - traz calor, luz e esperança. Cada momento ao seu lado é um presente que guardo no meu coração.",
        'bibleVerse': "O amor é paciente, o amor é bondoso. Não inveja, não se vangloria, não se orgulha. - 1 Coríntios 13:4",
        'icon': "💖"
    },
    {
        'day': 2,
        'title': "Sua Beleza Interior",
        'content': "Minha amada, hoje quero lembrar você da sua beleza interior que transborda e contagia todos ao seu redor. Sua bondade, sua compaixão e sua força são qualidades que me inspiram todos os dias. Você é a mulher mais incrível que já conheci.",
        'bibleVerse': "O Senhor não vê como o homem: o homem vê a aparência, mas o Senhor vê o coração. - 1 Samuel 16:7",
        'icon': "✨"
    },
    # ... (adicionar as outras 58 cartinhas aqui)
    {
        'day': 60,
        'title': "Amor Infinito",
        'content': "Chegamos à 60ª cartinha, meu amor, mas isso é apenas o começo. Meu amor por você não tem fim - ele cresce, se transforma e se renova a cada dia. Você é minha eterna companheira, minha melhor amiga, o amor da minha vida. Prometo te amar, honrar e cuidar de você todos os dias da minha vida.",
        'bibleVerse': "Agora, pois, permanecem a fé, a esperança e o amor, estes três, mas o maior destes é o amor. - 1 Coríntios 13:13",
        'icon': "💖"
    }
]

def init_db():
    db.create_all()
    
    # Criar usuário padrão se não existir
    if not User.query.filter_by(username='princesa').first():
        from werkzeug.security import generate_password_hash
        default_user = User(
            username='princesa',
            password=generate_password_hash('123')
        )
        db.session.add(default_user)
        db.session.commit()