from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Note

routes = Blueprint('routes', __name__)

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(password) < 8:
            flash("Password must be at least 8 characters!", "danger")
            return redirect(url_for('routes.register'))
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully! Please login.", "success")
        return redirect(url_for('routes.login'))
    return render_template('register.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f"Welcome, {current_user.username}!", "success")
            return redirect(url_for('routes.notes'))
        flash("Invalid credentials!", "danger")
    return render_template('login.html')

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('routes.login'))

@routes.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        note = Note(title=title, content=content, owner=current_user)
        db.session.add(note)
        db.session.commit()
        flash("Note added!", "success")
        return redirect(url_for('routes.notes'))

    all_notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('notes.html', notes=all_notes)

@routes.route('/delete/<int:id>')
@login_required
def delete(id):
    note = Note.query.get_or_404(id)
    if note.owner != current_user:
        flash("You cannot delete this note!", "danger")
    else:
        db.session.delete(note)
        db.session.commit()
        flash("Note deleted!", "info")
    return redirect(url_for('routes.notes'))
