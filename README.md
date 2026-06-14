# Santhoosh Shivan R — Portfolio Website

A premium, full-stack portfolio website built with **Python Flask**, **SQLAlchemy**, **SQLite**, and a modern dark/light UI.

---

## 🚀 Features

- **Animated Hero** with typing effect, particle background, and floating code window
- **Dark / Light Mode** toggle with localStorage persistence
- **Custom Cursor** with magnetic hover effects
- **Project Cards** with search, category filter, and detail modal
- **Skill Progress Bars** with scroll-triggered animations
- **Contact Form** with Regex validation and SQLite storage
- **Chatbot Assistant** with keyword-based responses
- **Admin Dashboard** — login, stats, project manager, message inbox
- **Chart.js** doughnut chart in admin panel
- **AOS scroll animations** throughout
- **Fully Responsive** (Bootstrap 5)
- **PWA-ready** structure

---

## 📁 Project Structure

```
santhoosh_portfolio/
├── app.py                  # Flask application & routes
├── requirements.txt        # Python dependencies
├── README.md
├── instance/
│   └── portfolio.db        # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css       # All styles (dark/light theme)
│   ├── js/
│   │   └── main.js         # Interactions, animations, chatbot
│   ├── images/             # Place project images here
│   └── fonts/              # Optional local fonts
└── templates/
    ├── index.html          # Main portfolio page
    └── admin/
        ├── login.html
        ├── dashboard.html
        ├── messages.html
        └── projects.html
```

---

## ⚙️ Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

The database is **auto-created and seeded** on first run.

---

## 🔐 Admin Panel

URL: `http://localhost:5000/admin`

| Username | Password  |
|----------|-----------|
| admin    | admin123  |

> **Change the password** in `app.py` → `seed_database()` before deploying.

---

## 🌐 Deployment (Production)

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables
Create a `.env` file:
```
SECRET_KEY=your_super_secret_key_here
DATABASE_URL=sqlite:///portfolio.db
```

### Platforms
- **Render** — free tier, push to GitHub and connect
- **Railway** — instant deploy from GitHub
- **PythonAnywhere** — free Flask hosting
- **VPS (Ubuntu)** — Nginx + Gunicorn

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, Flask 3.0 |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite |
| Frontend | HTML5, CSS3, JavaScript ES6 |
| UI Framework | Bootstrap 5.3 |
| Icons | Font Awesome 6.5 |
| Animations | AOS 2.3 |
| Charts | Chart.js |
| Fonts | Syne, Space Mono, Inter |
| Validation | Python Regex, JS Regex |

---

## 📧 Contact

**Santhoosh Shivan R**
- Email: santhooshshivan18@gmail.com
- Phone: +91 7558105935
- GitHub: [github.com/santhooshofficial](https://github.com/santhooshofficial)
- LinkedIn: [linkedin.com/in/santhoosh-shivan](https://linkedin.com/in/santhoosh-shivan)

---

*Built with ❤️ for campus placements and software developer roles.*
