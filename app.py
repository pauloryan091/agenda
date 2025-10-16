from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date
import json
import base64

from database import db, init_db, User, Task, Goal, Event, Reminder, GalleryItem, DAILY_LETTERS_DATA

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_muito_segura_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Rota principal - Login
@app.route('/')
def index():
    # Se já está logado, redireciona para o planner
    if 'user_id' in session:
        return redirect('/site')
    return render_template('index.html')

# Rota de login
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['theme'] = user.theme
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Usuário ou senha incorretos'})

# Rota de logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Rota do planner principal
@app.route('/site')
def site():
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Buscar dados do usuário
    tasks = Task.query.filter_by(user_id=user_id).all()
    goals = Goal.query.filter_by(user_id=user_id).all()
    events = Event.query.filter_by(user_id=user_id).all()
    reminders = Reminder.query.filter_by(user_id=user_id).all()
    gallery_items = GalleryItem.query.filter_by(user_id=user_id).all()
    
    # Calcular cartinha do dia
    start_date = date(2024, 3, 22)
    today = date.today()
    days_passed = (today - start_date).days
    current_day = (days_passed % 60) + 1
    daily_letter = DAILY_LETTERS_DATA[current_day - 1]
    
    # Calcular dias juntos
    relationship_date = date(2025, 9, 7)
    days_together = (today - relationship_date).days
    
    return render_template('site.html',
        username=session['username'],
        theme=user.theme,
        tasks=tasks,
        goals=goals,
        events=events,
        reminders=reminders,
        gallery_items=gallery_items,
        daily_letter=daily_letter,
        current_day=current_day,
        days_together=days_together
    )

# API Routes - Tarefas
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'id': task.id,
        'text': task.text,
        'category': task.category,
        'completed': task.completed,
        'created_at': task.created_at.isoformat()
    } for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    task = Task(
        user_id=session['user_id'],
        text=data['text'],
        category=data.get('category', 'pessoal')
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'success': True, 'id': task.id})

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if not task:
        return jsonify({'error': 'Tarefa não encontrada'}), 404
    
    data = request.get_json()
    if 'completed' in data:
        task.completed = data['completed']
    if 'text' in data:
        task.text = data['text']
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
    if not task:
        return jsonify({'error': 'Tarefa não encontrada'}), 404
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})

# API Routes - Metas
@app.route('/api/goals', methods=['GET'])
def get_goals():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    goals = Goal.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'id': goal.id,
        'text': goal.text,
        'progress': goal.progress,
        'created_at': goal.created_at.isoformat()
    } for goal in goals])

@app.route('/api/goals', methods=['POST'])
def add_goal():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    goal = Goal(
        user_id=session['user_id'],
        text=data['text'],
        progress=data.get('progress', 0)
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify({'success': True, 'id': goal.id})

@app.route('/api/goals/<int:goal_id>', methods=['PUT'])
def update_goal(goal_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    goal = Goal.query.filter_by(id=goal_id, user_id=session['user_id']).first()
    if not goal:
        return jsonify({'error': 'Meta não encontrada'}), 404
    
    data = request.get_json()
    if 'progress' in data:
        goal.progress = data['progress']
    if 'text' in data:
        goal.text = data['text']
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/goals/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    goal = Goal.query.filter_by(id=goal_id, user_id=session['user_id']).first()
    if not goal:
        return jsonify({'error': 'Meta não encontrada'}), 404
    
    db.session.delete(goal)
    db.session.commit()
    return jsonify({'success': True})

# API Routes - Eventos
@app.route('/api/events', methods=['GET'])
def get_events():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    events = Event.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'id': event.id,
        'title': event.title,
        'date': event.date.isoformat(),
        'time': event.time.strftime('%H:%M'),
        'category': event.category,
        'created_at': event.created_at.isoformat()
    } for event in events])

@app.route('/api/events', methods=['POST'])
def add_event():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    event = Event(
        user_id=session['user_id'],
        title=data['title'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        time=datetime.strptime(data['time'], '%H:%M').time(),
        category=data.get('category', 'pessoal')
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({'success': True, 'id': event.id})

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    event = Event.query.filter_by(id=event_id, user_id=session['user_id']).first()
    if not event:
        return jsonify({'error': 'Evento não encontrado'}), 404
    
    db.session.delete(event)
    db.session.commit()
    return jsonify({'success': True})

# API Routes - Lembretes
@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    reminders = Reminder.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'id': reminder.id,
        'title': reminder.title,
        'time': reminder.time.strftime('%H:%M'),
        'active': reminder.active,
        'created_at': reminder.created_at.isoformat()
    } for reminder in reminders])

@app.route('/api/reminders', methods=['POST'])
def add_reminder():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    reminder = Reminder(
        user_id=session['user_id'],
        title=data['title'],
        time=datetime.strptime(data['time'], '%H:%M').time(),
        active=data.get('active', True)
    )
    db.session.add(reminder)
    db.session.commit()
    return jsonify({'success': True, 'id': reminder.id})

@app.route('/api/reminders/<int:reminder_id>', methods=['PUT'])
def update_reminder(reminder_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    reminder = Reminder.query.filter_by(id=reminder_id, user_id=session['user_id']).first()
    if not reminder:
        return jsonify({'error': 'Lembrete não encontrado'}), 404
    
    data = request.get_json()
    if 'active' in data:
        reminder.active = data['active']
    if 'time' in data:
        reminder.time = datetime.strptime(data['time'], '%H:%M').time()
    if 'title' in data:
        reminder.title = data['title']
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    reminder = Reminder.query.filter_by(id=reminder_id, user_id=session['user_id']).first()
    if not reminder:
        return jsonify({'error': 'Lembrete não encontrado'}), 404
    
    db.session.delete(reminder)
    db.session.commit()
    return jsonify({'success': True})

# API Routes - Galeria
@app.route('/api/gallery', methods=['GET'])
def get_gallery():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    gallery_items = GalleryItem.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'id': item.id,
        'caption': item.caption,
        'category': item.category,
        'image_data': item.image_data,
        'created_at': item.created_at.isoformat()
    } for item in gallery_items])

@app.route('/api/gallery', methods=['POST'])
def add_gallery_item():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    gallery_item = GalleryItem(
        user_id=session['user_id'],
        caption=data['caption'],
        category=data['category'],
        image_data=data['image_data']
    )
    db.session.add(gallery_item)
    db.session.commit()
    return jsonify({'success': True, 'id': gallery_item.id})

@app.route('/api/gallery/<int:item_id>', methods=['DELETE'])
def delete_gallery_item(item_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    item = GalleryItem.query.filter_by(id=item_id, user_id=session['user_id']).first()
    if not item:
        return jsonify({'error': 'Item não encontrado'}), 404
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

# API Routes - Tema
@app.route('/api/theme', methods=['PUT'])
def update_theme():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    user = User.query.get(session['user_id'])
    user.theme = data['theme']
    session['theme'] = data['theme']
    db.session.commit()
    return jsonify({'success': True})

# API Routes - Cartinha do Dia
@app.route('/api/daily-letter')
def get_daily_letter():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    start_date = date(2024, 3, 22)
    today = date.today()
    days_passed = (today - start_date).days
    current_day = (days_passed % 60) + 1
    
    letter_data = DAILY_LETTERS_DATA[current_day - 1]
    
    return jsonify({
        'day': current_day,
        'title': letter_data['title'],
        'content': letter_data['content'],
        'bibleVerse': letter_data['bibleVerse'],
        'icon': letter_data['icon'],
        'total_days': 60
    })

# API Routes - Estatísticas
@app.route('/api/stats')
def get_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
    
    # Calcular dias juntos
    relationship_date = date(2025, 9, 7)
    today = date.today()
    days_together = (today - relationship_date).days
    
    # Contar itens
    tasks_count = Task.query.filter_by(user_id=session['user_id']).count()
    goals_count = Goal.query.filter_by(user_id=session['user_id']).count()
    gallery_count = GalleryItem.query.filter_by(user_id=session['user_id']).count()
    
    # Próximo aniversário
    next_anniversary_year = today.year
    next_anniversary = date(next_anniversary_year, 9, 7)
    if next_anniversary < today:
        next_anniversary = date(next_anniversary_year + 1, 9, 7)
    
    return jsonify({
        'days_together': days_together,
        'tasks_count': tasks_count,
        'goals_count': goals_count,
        'gallery_count': gallery_count,
        'next_anniversary': next_anniversary.isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)