"""
Santhoosh Shivan R - Portfolio Website
Flask Backend Application
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
import os
import hashlib

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'santhoosh_secret_key_2025_portfolio'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─────────────────────────────────────────
# DATABASE MODELS
# ─────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(500))
    features = db.Column(db.Text)
    github_url = db.Column(db.String(300))
    demo_url = db.Column(db.String(300))
    image_url = db.Column(db.String(300))
    category = db.Column(db.String(100))
    featured = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    proficiency = db.Column(db.Integer, default=80)  # 0-100
    icon = db.Column(db.String(100))
    order_index = db.Column(db.Integer, default=0)

class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(200))
    location = db.Column(db.String(200))
    year = db.Column(db.String(20))
    cert_type = db.Column(db.String(50))  # 'certificate' or 'participation'
    image_url = db.Column(db.String(300))
    credential_url = db.Column(db.String(300))

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(300))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VisitorAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    page_visited = db.Column(db.String(200))
    visited_at = db.Column(db.DateTime, default=datetime.utcnow)

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_name(name):
    return bool(re.match(r'^[a-zA-Z\s]{2,100}$', name.strip()))

def log_visitor(page):
    try:
        visitor = VisitorAnalytics(
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500],
            page_visited=page
        )
        db.session.add(visitor)
        db.session.commit()
    except:
        pass

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────
# MAIN ROUTES
# ─────────────────────────────────────────

@app.route('/')
def index():
    log_visitor('home')
    projects = Project.query.order_by(Project.order_index).all()
    skills = Skill.query.order_by(Skill.order_index).all()
    certifications = Certification.query.all()
    visitor_count = VisitorAnalytics.query.count()
    return render_template('index.html',
        projects=projects,
        skills=skills,
        certifications=certifications,
        visitor_count=visitor_count
    )

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    # Regex Validation
    errors = {}
    if not name or len(name) < 2:
        errors['name'] = 'Name must be at least 2 characters.'
    if not validate_email(email):
        errors['email'] = 'Please enter a valid email address.'
    if not subject or len(subject) < 3:
        errors['subject'] = 'Subject must be at least 3 characters.'
    if not message or len(message) < 10:
        errors['message'] = 'Message must be at least 10 characters.'

    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    try:
        msg = ContactMessage(name=name, email=email, subject=subject, message=message)
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Message sent successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error. Please try again.'}), 500

@app.route('/api/visitor-count')
def visitor_count():
    count = VisitorAnalytics.query.count()
    return jsonify({'count': count})

@app.route('/api/projects')
def api_projects():
    projects = Project.query.order_by(Project.order_index).all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'description': p.description,
        'technologies': p.technologies,
        'features': p.features,
        'github_url': p.github_url,
        'demo_url': p.demo_url,
        'image_url': p.image_url,
        'category': p.category,
        'featured': p.featured
    } for p in projects])

# ─────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password_hash=hash_password(password)).first()
        if user:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = {
        'projects': Project.query.count(),
        'skills': Skill.query.count(),
        'certifications': Certification.query.count(),
        'messages': ContactMessage.query.count(),
        'unread_messages': ContactMessage.query.filter_by(is_read=False).count(),
        'visitors': VisitorAnalytics.query.count(),
    }
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_messages=recent_messages)

@app.route('/admin/messages')
@admin_required
def admin_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    # Mark all as read
    ContactMessage.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('admin/messages.html', messages=messages)

@app.route('/admin/projects')
@admin_required
def admin_projects():
    projects = Project.query.order_by(Project.order_index).all()
    return render_template('admin/projects.html', projects=projects)

@app.route('/admin/projects/delete/<int:id>', methods=['POST'])
@admin_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('admin_projects'))

# ─────────────────────────────────────────
# DATABASE SEEDING
# ─────────────────────────────────────────

def seed_database():
    """Seed initial data into the database"""

    # Admin user
    if not User.query.first():
        admin = User(username='admin', password_hash=hash_password('admin123'))
        db.session.add(admin)

    # Skills
    if not Skill.query.first():
        skills_data = [
            # Programming Languages
            ('Python', 'Programming Languages', 95, 'fab fa-python', 1),
            ('JavaScript', 'Programming Languages', 80, 'fab fa-js', 2),
            ('C', 'Programming Languages', 75, 'fas fa-code', 3),
            # Web Technologies
            ('HTML5', 'Web Technologies', 90, 'fab fa-html5', 4),
            ('CSS3', 'Web Technologies', 88, 'fab fa-css3-alt', 5),
            ('Bootstrap', 'Web Technologies', 85, 'fab fa-bootstrap', 6),
            ('Flask', 'Web Technologies', 90, 'fas fa-flask', 7),
            ('Django', 'Web Technologies', 78, 'fas fa-globe', 8),
            # Databases
            ('SQL', 'Database', 85, 'fas fa-database', 9),
            ('SQLite', 'Database', 88, 'fas fa-database', 10),
            ('MySQL', 'Database', 80, 'fas fa-database', 11),
            # Libraries & Tools
            ('Pandas', 'Python Libraries', 82, 'fas fa-table', 12),
            ('NumPy', 'Python Libraries', 80, 'fas fa-calculator', 13),
            ('OpenCV', 'Python Libraries', 75, 'fas fa-eye', 14),
            ('Git', 'Tools', 85, 'fab fa-git-alt', 15),
            ('GitHub', 'Tools', 88, 'fab fa-github', 16),
            ('VS Code', 'Tools', 90, 'fas fa-code', 17),
            ('Postman', 'Tools', 80, 'fas fa-paper-plane', 18),
        ]
        for name, cat, prof, icon, order in skills_data:
            db.session.add(Skill(name=name, category=cat, proficiency=prof, icon=icon, order_index=order))

    # Projects
    if not Project.query.first():
        projects_data = [
            {
                'title': 'Sepsis & Preeclampsia Prediction System',
                'description': 'A real-time health monitoring system using multi-sensor data to predict life-threatening conditions like Sepsis and Preeclampsia with an integrated healthcare chatbot and emergency alert system.',
                'technologies': 'Python, HTML, CSS, JavaScript, SQLite',
                'features': 'Real-time health monitoring|Sensor data collection|Early disease prediction|Healthcare chatbot|Medical analytics dashboard|Emergency alert system',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Healthcare AI',
                'featured': True,
                'order_index': 1
            },
            {
                'title': 'AI-Powered Petition Management System',
                'description': 'An intelligent petition management platform leveraging Machine Learning for automatic categorization, department allocation, and urgency detection with citizen communication portal.',
                'technologies': 'Python, Flask, SQLite, Machine Learning',
                'features': 'AI categorization|Department allocation|Urgency detection|Automated reminders|Status tracking|Citizen communication portal|Analytics dashboard',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'AI & ML',
                'featured': True,
                'order_index': 2
            },
            {
                'title': 'Maternal & Newborn Health Monitoring System',
                'description': 'Comprehensive health tracking system for mothers and newborns with unique Health IDs, vaccination schedules, growth tracking, and birth certificate integration.',
                'technologies': 'Python, Flask, SQLite',
                'features': 'Unique Health ID|Growth tracking|Medical record management|Vaccination tracking|Birth certificate integration|Health analytics',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Healthcare',
                'featured': True,
                'order_index': 3
            },
            {
                'title': 'Coastal Erosion Monitoring System',
                'description': 'GIS-powered coastal monitoring system with AI prediction models for tracking erosion patterns, climate analysis, and coastal risk assessment.',
                'technologies': 'Python, GIS, Remote Sensing',
                'features': 'GIS integration|AI prediction|Climate analysis|Coastal monitoring dashboard|Risk assessment',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'GIS & Environment',
                'featured': False,
                'order_index': 4
            },
            {
                'title': 'NexusPOS Enterprise Billing System',
                'description': 'Full-featured enterprise-grade Point of Sale system with inventory management, billing, sales tracking, and comprehensive reporting for businesses.',
                'technologies': 'Python, Flask, SQLite',
                'features': 'Inventory management|Billing system|Sales tracking|Reports generation|Customer management|Admin dashboard',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Enterprise',
                'featured': True,
                'order_index': 5
            },
            {
                'title': 'Code Execution Visualizer',
                'description': 'An educational tool that visualizes code execution step-by-step with flowchart generation, variable tracking, and memory visualization for multiple programming languages.',
                'technologies': 'Python, Flask, JavaScript',
                'features': 'Step-by-step execution|Flowchart generation|Variable tracking|Memory visualization|Multi-language support|Educational dashboard',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Education',
                'featured': False,
                'order_index': 6
            },
            {
                'title': 'Rice Quality Detection & Analysis System',
                'description': 'Computer vision system using OpenCV and Machine Learning to classify rice grain quality, detect defects, and generate automated quality reports.',
                'technologies': 'Python, OpenCV, Machine Learning, Flask',
                'features': 'Rice grain classification|Quality grading|Defect detection|Image processing|Quality analytics dashboard|Automated report generation',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Computer Vision',
                'featured': True,
                'order_index': 7
            },
        ]
        for p in projects_data:
            db.session.add(Project(**p))

    # Certifications
    if not Certification.query.first():
        certs_data = [
            ('Diploma in C Programming', 'Bright Tech Institute', 'Puducherry', '2025', 'certificate'),
            ('Industrial IoT & Industry 4.0 Hackathon', 'InGage Technologies Pvt. Ltd.', 'Chennai', '2024', 'participation'),
        ]
        for title, issuer, loc, year, cert_type in certs_data:
            db.session.add(Certification(title=title, issuer=issuer, location=loc, year=year, cert_type=cert_type))

    db.session.commit()
    print("✅ Database seeded successfully!")


# ─────────────────────────────────────────
# APP ENTRY POINT
# ─────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(debug=True, port=5000)
