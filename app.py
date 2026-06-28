"""
Santhoosh Shivan R - Portfolio Website
Flask Backend Application
+ Flask-Mail email notification system (added without changing any other file)
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
from functools import wraps
import re
import os
import hashlib
import logging

# ─────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────
app = Flask(__name__)

# Core config
app.config['SECRET_KEY'] = 'santhoosh_secret_key_2025_portfolio'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ── Flask-Mail — Gmail SMTP ──────────────────────────────────────
# Credentials are read from environment variables ONLY — never hard-coded.
# On Render: Dashboard → your service → Environment → Add Variable
app.config['MAIL_SERVER']         = 'smtp.gmail.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USE_SSL']        = False
app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME')   # e.g. santhooshshivan18@gmail.com
app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD')   # Gmail App Password (16 chars)
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

# The inbox where contact-form notifications arrive
OWNER_EMAIL = 'santhooshshivan18@gmail.com'

db   = SQLAlchemy(app)
mail = Mail(app)


# ─────────────────────────────────────────
# DATABASE MODELS  (unchanged)
# ─────────────────────────────────────────

class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    description  = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.String(500))
    features     = db.Column(db.Text)
    github_url   = db.Column(db.String(300))
    demo_url     = db.Column(db.String(300))
    image_url    = db.Column(db.String(300))
    category     = db.Column(db.String(100))
    featured     = db.Column(db.Boolean, default=False)
    order_index  = db.Column(db.Integer, default=0)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

class Skill(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    category    = db.Column(db.String(100))
    proficiency = db.Column(db.Integer, default=80)
    icon        = db.Column(db.String(100))
    order_index = db.Column(db.Integer, default=0)

class Certification(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    title          = db.Column(db.String(200), nullable=False)
    issuer         = db.Column(db.String(200))
    location       = db.Column(db.String(200))
    year           = db.Column(db.String(20))
    cert_type      = db.Column(db.String(50))
    image_url      = db.Column(db.String(300))
    credential_url = db.Column(db.String(300))

class ContactMessage(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(200), nullable=False)
    email      = db.Column(db.String(200), nullable=False)
    subject    = db.Column(db.String(300))
    message    = db.Column(db.Text, nullable=False)
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VisitorAnalytics(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    ip_address   = db.Column(db.String(50))
    user_agent   = db.Column(db.String(500))
    page_visited = db.Column(db.String(200))
    visited_at   = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
# HELPERS  (unchanged)
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
            user_agent=request.headers.get("User-Agent", "")[:500],
            page_visited=page
        )
        db.session.add(visitor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Visitor Analytics Error:", e)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────
# EMAIL HELPERS  (NEW)
# ─────────────────────────────────────────

def _mail_configured():
    """Return True only when both MAIL_USERNAME and MAIL_PASSWORD env vars are set."""
    return bool(app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'))


def send_owner_notification(name, email, subject, message, submitted_at):
    """
    Notify Santhoosh immediately when someone submits the contact form.
    Subject: "New Portfolio Contact: <visitor subject>"
    """
    email_subject = f"New Portfolio Contact: {subject}"

    # ── Plain-text body ──────────────────────────────────────────
    plain = f"""
You received a new message through your portfolio website.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CONTACT FORM SUBMISSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Visitor Name  : {name}
  Visitor Email : {email}
  Subject       : {subject}
  Date & Time   : {submitted_at.strftime('%d %B %Y, %I:%M %p')} (UTC)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MESSAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reply directly to: {email}
— Portfolio Notification System
    """.strip()

    # ── HTML body ────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#0a0118;color:#e0e0f0;margin:0;padding:0}}
  .wrap{{max-width:600px;margin:28px auto;background:#13062a;border:1px solid rgba(108,99,255,.3);border-radius:14px;overflow:hidden}}
  .hdr{{background:linear-gradient(135deg,#6c63ff,#4f46e5);padding:26px 30px}}
  .hdr h1{{margin:0;font-size:1.3rem;color:#fff}}
  .hdr p{{margin:4px 0 0;color:rgba(255,255,255,.82);font-size:.88rem}}
  .body{{padding:26px 30px}}
  .lbl{{font-size:.7rem;color:#6c63ff;letter-spacing:.1em;text-transform:uppercase;font-weight:600;margin:14px 0 3px}}
  .val{{font-size:.92rem;color:#e0e0f0;background:rgba(108,99,255,.09);border:1px solid rgba(108,99,255,.2);border-radius:8px;padding:9px 13px}}
  .msg{{background:rgba(255,255,255,.04);border:1px solid rgba(108,99,255,.15);border-radius:8px;padding:14px;line-height:1.7;white-space:pre-wrap;color:#b8b4d4;font-size:.9rem;margin-top:4px}}
  .btn{{display:inline-block;margin-top:18px;background:#6c63ff;color:#fff;padding:9px 22px;border-radius:100px;text-decoration:none;font-weight:700;font-size:.86rem}}
  .ftr{{padding:16px 30px;border-top:1px solid rgba(108,99,255,.15);font-size:.75rem;color:#6b6785}}
  .ftr a{{color:#6c63ff}}
</style>
</head>
<body>
<div class="wrap">
  <div class="hdr">
    <h1>📬 New Contact Form Submission</h1>
    <p>Someone reached out through your portfolio website</p>
  </div>
  <div class="body">
    <div class="lbl">Visitor Name</div>
    <div class="val">{name}</div>
    <div class="lbl">Visitor Email</div>
    <div class="val">{email}</div>
    <div class="lbl">Subject</div>
    <div class="val">{subject}</div>
    <div class="lbl">Date &amp; Time (UTC)</div>
    <div class="val">{submitted_at.strftime('%d %B %Y, %I:%M %p')}</div>
    <div class="lbl" style="margin-top:22px">Message</div>
    <div class="msg">{message}</div>
    <a class="btn" href="mailto:{email}">Reply to {name}</a>
  </div>
  <div class="ftr">
    Sent automatically by your portfolio contact system &nbsp;·&nbsp;
    <a href="https://portfolio1-q3e9.onrender.com">portfolio1-q3e9.onrender.com</a>
  </div>
</div>
</body>
</html>"""

    msg = Message(
        subject=email_subject,
        recipients=[OWNER_EMAIL],
        body=plain,
        html=html,
        reply_to=email
    )
    mail.send(msg)
    logger.info(f"[EMAIL] Owner notification sent for contact from {email}")


def send_visitor_confirmation(name, visitor_email, subject, message, submitted_at):
    """
    Send a professional auto-reply to the visitor confirming receipt.
    Subject: "Thank you for contacting Santhoosh Shivan R"
    """
    email_subject = "Thank you for contacting Santhoosh Shivan R"

    # ── Plain-text body ──────────────────────────────────────────
    plain = f"""
Hello {name},

Thank you for reaching out through my portfolio website.

I have successfully received your message and will review it as soon as possible.
I usually respond within 24–48 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  YOUR SUBMITTED DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Name    : {name}
  Email   : {visitor_email}
  Subject : {subject}
  Message : {message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I appreciate your interest and look forward to connecting with you.

Best Regards,
Santhoosh Shivan R
Python Full Stack Developer
Puducherry, India

GitHub    : https://github.com/santhooshofficial
LinkedIn  : https://linkedin.com/in/santhoosh-shivan
Portfolio : https://portfolio1-q3e9.onrender.com
    """.strip()

    # ── HTML body ────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
  body{{font-family:'Segoe UI',Arial,sans-serif;background:#0a0118;color:#e0e0f0;margin:0;padding:0}}
  .wrap{{max-width:600px;margin:28px auto;background:#13062a;border:1px solid rgba(108,99,255,.3);border-radius:14px;overflow:hidden}}
  .hdr{{background:linear-gradient(135deg,#6c63ff,#4f46e5);padding:30px;text-align:center}}
  .hdr h1{{margin:0;font-size:1.4rem;color:#fff}}
  .hdr p{{margin:5px 0 0;color:rgba(255,255,255,.82);font-size:.88rem}}
  .body{{padding:28px 30px}}
  .greet{{font-size:1rem;color:#e0e0f0;line-height:1.75;margin-bottom:18px}}
  .info{{background:rgba(108,99,255,.09);border:1px solid rgba(108,99,255,.2);border-radius:12px;padding:18px 22px;margin:20px 0}}
  .info h3{{margin:0 0 12px;font-size:.72rem;color:#6c63ff;letter-spacing:.1em;text-transform:uppercase}}
  .row{{display:flex;gap:8px;margin-bottom:9px;font-size:.88rem}}
  .rl{{color:#6b6785;min-width:65px;font-weight:600}}
  .rv{{color:#e0e0f0;word-break:break-word}}
  .mbox{{background:rgba(255,255,255,.04);border-left:3px solid #6c63ff;padding:11px 15px;border-radius:0 8px 8px 0;font-size:.86rem;color:#b8b4d4;line-height:1.7;white-space:pre-wrap;margin-top:5px}}
  .sig{{margin-top:26px;padding-top:18px;border-top:1px solid rgba(108,99,255,.15)}}
  .sn{{font-size:1rem;font-weight:700;color:#fff}}
  .st{{font-size:.83rem;color:#6c63ff;margin-top:2px}}
  .links{{margin-top:12px;display:flex;gap:10px;flex-wrap:wrap}}
  .lnk{{display:inline-block;background:rgba(108,99,255,.12);border:1px solid rgba(108,99,255,.3);color:#8b85ff;padding:4px 13px;border-radius:100px;text-decoration:none;font-size:.76rem;font-weight:600}}
  .ftr{{padding:14px 30px;border-top:1px solid rgba(108,99,255,.15);font-size:.73rem;color:#6b6785;text-align:center}}
</style>
</head>
<body>
<div class="wrap">
  <div class="hdr">
    <h1>✅ Message Received!</h1>
    <p>Santhoosh Shivan R · Portfolio</p>
  </div>
  <div class="body">
    <div class="greet">
      Hello <strong>{name}</strong>,<br><br>
      Thank you for reaching out through my portfolio website.<br>
      I have successfully received your message and will review it as soon as possible.
      I usually respond within <strong>24–48 hours</strong>.
    </div>
    <div class="info">
      <h3>Your Submitted Details</h3>
      <div class="row"><span class="rl">Name</span><span class="rv">{name}</span></div>
      <div class="row"><span class="rl">Email</span><span class="rv">{visitor_email}</span></div>
      <div class="row"><span class="rl">Subject</span><span class="rv">{subject}</span></div>
      <div class="row" style="flex-direction:column">
        <span class="rl">Message</span>
        <div class="mbox">{message}</div>
      </div>
    </div>
    <p style="color:#b8b4d4;font-size:.9rem;line-height:1.75">
      I appreciate your interest and look forward to connecting with you.
    </p>
    <div class="sig">
      <div class="sn">Santhoosh Shivan R</div>
      <div class="st">Python Full Stack Developer · Puducherry, India</div>
      <div class="links">
        <a class="lnk" href="https://github.com/santhooshofficial">GitHub</a>
        <a class="lnk" href="https://linkedin.com/in/santhoosh-shivan">LinkedIn</a>
        <a class="lnk" href="https://portfolio1-q3e9.onrender.com">Portfolio</a>
      </div>
    </div>
  </div>
  <div class="ftr">This is an automated confirmation. Please do not reply to this email.</div>
</div>
</body>
</html>"""

    msg = Message(
        subject=email_subject,
        recipients=[visitor_email],
        body=plain,
        html=html
    )
    mail.send(msg)
    logger.info(f"[EMAIL] Confirmation sent to visitor: {visitor_email}")


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
    data    = request.get_json()
    name    = data.get('name', '').strip()
    email   = data.get('email', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    # ── Regex Validation (unchanged) ────────────────────────────
    errors = {}
    if not name or len(name) < 2:
        errors['name']    = 'Name must be at least 2 characters.'
    if not validate_email(email):
        errors['email']   = 'Please enter a valid email address.'
    if not subject or len(subject) < 3:
        errors['subject'] = 'Subject must be at least 3 characters.'
    if not message or len(message) < 10:
        errors['message'] = 'Message must be at least 10 characters.'

    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    # ── Step 1: Save to database (unchanged logic) ───────────────
    try:
        contact_msg = ContactMessage(
            name=name, email=email, subject=subject, message=message
        )
        db.session.add(contact_msg)
        db.session.commit()
        submitted_at = contact_msg.created_at
        logger.info(f"[DB] Contact message saved — from {email}")
    except Exception as db_err:
        logger.error(f"[DB ERROR] Failed to save contact message: {db_err}")
        return jsonify({'success': False, 'message': 'Server error. Please try again.'}), 500

    # ── Step 2: Send emails — failures never affect the user ─────
    if _mail_configured():
        # 2a  Notify Santhoosh
        try:
            send_owner_notification(name, email, subject, message, submitted_at)
        except Exception as e:
            logger.error(f"[MAIL ERROR] Owner notification failed: {e}")

        # 2b  Confirm receipt to the visitor
        try:
            send_visitor_confirmation(name, email, subject, message, submitted_at)
        except Exception as e:
            logger.error(f"[MAIL ERROR] Visitor confirmation failed: {e}")
    else:
        logger.warning("[MAIL] MAIL_USERNAME / MAIL_PASSWORD not configured — emails skipped.")

    # Always return success once the DB save succeeded
    return jsonify({'success': True, 'message': 'Message sent successfully!'})


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
# ADMIN ROUTES  (unchanged)
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
# DATABASE SEEDING  (unchanged)
# ─────────────────────────────────────────

def seed_database():
    """Seed initial data into the database"""

    if not User.query.first():
        admin = User(username='admin', password_hash=hash_password('admin123'))
        db.session.add(admin)

    if not Skill.query.first():
        skills_data = [
            ('Python',      'Programming Languages', 95, 'fab fa-python',     1),
            ('JavaScript',  'Programming Languages', 80, 'fab fa-js',          2),
            ('C',           'Programming Languages', 75, 'fas fa-code',        3),
            ('HTML5',       'Web Technologies',      90, 'fab fa-html5',       4),
            ('CSS3',        'Web Technologies',      88, 'fab fa-css3-alt',    5),
            ('Bootstrap',   'Web Technologies',      85, 'fab fa-bootstrap',   6),
            ('Flask',       'Web Technologies',      90, 'fas fa-flask',       7),
            ('Django',      'Web Technologies',      78, 'fas fa-globe',       8),
            ('SQL',         'Database',              85, 'fas fa-database',    9),
            ('SQLite',      'Database',              88, 'fas fa-database',    10),
            ('MySQL',       'Database',              80, 'fas fa-database',    11),
            ('Pandas',      'Python Libraries',      82, 'fas fa-table',       12),
            ('NumPy',       'Python Libraries',      80, 'fas fa-calculator',  13),
            ('OpenCV',      'Python Libraries',      75, 'fas fa-eye',         14),
            ('Git',         'Tools',                 85, 'fab fa-git-alt',     15),
            ('GitHub',      'Tools',                 88, 'fab fa-github',      16),
            ('VS Code',     'Tools',                 90, 'fas fa-code',        17),
            ('Postman',     'Tools',                 80, 'fas fa-paper-plane', 18),
        ]
        for name, cat, prof, icon, order in skills_data:
            db.session.add(Skill(name=name, category=cat, proficiency=prof,
                                 icon=icon, order_index=order))

    if not Project.query.first():
        projects_data = [
            {
                'title': 'Sepsis & Preeclampsia Prediction System',
                'description': 'A real-time health monitoring system using multi-sensor data to predict life-threatening conditions like Sepsis and Preeclampsia with an integrated healthcare chatbot and emergency alert system.',
                'technologies': 'Python, HTML, CSS, JavaScript, SQLite',
                'features': 'Real-time health monitoring|Sensor data collection|Early disease prediction|Healthcare chatbot|Medical analytics dashboard|Emergency alert system',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Healthcare AI', 'featured': True, 'order_index': 1
            },
            {
                'title': 'Maternal & Newborn Health Monitoring System',
                'description': 'Comprehensive health tracking system for mothers and newborns with unique Health IDs, vaccination schedules, growth tracking, and birth certificate integration.',
                'technologies': 'Python, Flask, SQLite',
                'features': 'Unique Health ID|Growth tracking|Medical record management|Vaccination tracking|Birth certificate integration|Health analytics',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Healthcare', 'featured': True, 'order_index': 3
            },
            {
                'title': 'NexusPOS Enterprise Billing System',
                'description': 'Full-featured enterprise-grade Point of Sale system with inventory management, billing, sales tracking, and comprehensive reporting for businesses.',
                'technologies': 'Python, Flask, SQLite',
                'features': 'Inventory management|Billing system|Sales tracking|Reports generation|Customer management|Admin dashboard',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Enterprise', 'featured': True, 'order_index': 5
            },
            {
                'title': 'Code Execution Visualizer',
                'description': 'An educational tool that visualizes code execution step-by-step with flowchart generation, variable tracking, and memory visualization for multiple programming languages.',
                'technologies': 'Python, Flask, JavaScript',
                'features': 'Step-by-step execution|Flowchart generation|Variable tracking|Memory visualization|Multi-language support|Educational dashboard',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Education', 'featured': False, 'order_index': 6
            },
            {
                'title': 'Rice Quality Detection & Analysis System',
                'description': 'Computer vision system using OpenCV and Machine Learning to classify rice grain quality, detect defects, and generate automated quality reports.',
                'technologies': 'Python, OpenCV, Machine Learning, Flask',
                'features': 'Rice grain classification|Quality grading|Defect detection|Image processing|Quality analytics dashboard|Automated report generation',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Computer Vision', 'featured': True, 'order_index': 7
            },
            {
                'title': 'APP Suzuki Motors — Smart Dealership System',
                'description': 'A complete full-stack dealership management system for APP Suzuki Motors built with Python Flask. Customers can view bikes, book online, calculate EMI, book test rides, and order spare parts — while management gets powerful analytics, inventory control, and customer insights.',
                'technologies': 'Python, Flask, SQLite, Bootstrap 5, Chart.js, JavaScript',
                'features': 'Online bike booking|EMI calculator|Test ride booking|Spare parts store|Admin dashboard & analytics|AI bike recommender|Customer feedback system|REST API endpoints',
                'github_url': 'https://github.com/santhooshofficial',
                'category': 'Enterprise', 'featured': True, 'order_index': 8
            },
        ]
        for p in projects_data:
            db.session.add(Project(**p))

    if not Certification.query.first():
        certs_data = [
            ('Diploma in C Programming',               'Bright Tech Institute',        'Puducherry', '2025', 'certificate'),
            ('Industrial IoT & Industry 4.0 Hackathon','InGage Technologies Pvt. Ltd.','Chennai',    '2024', 'participation'),
        ]
        for title, issuer, loc, year, cert_type in certs_data:
            db.session.add(Certification(title=title, issuer=issuer,
                                         location=loc, year=year, cert_type=cert_type))

    # Remove retired projects if they exist in DB
    for title_to_remove in ['Coastal Erosion Monitoring System', 'AI-Powered Petition Management System']:
        p = Project.query.filter_by(title=title_to_remove).first()
        if p:
            db.session.delete(p)

    db.session.commit()
    print("✅ Database seeded successfully!")


# ─────────────────────────────────────────
# APP ENTRY POINT  (unchanged)
# ─────────────────────────────────────────
print("Starting Flask app...")

with app.app_context():
    print("Creating database...")
    db.create_all()
    print("Seeding database...")
    seed_database()

print("Database ready.")

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
