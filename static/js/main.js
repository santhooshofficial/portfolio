/* ═══════════════════════════════════════════════════
   SANTHOOSH SHIVAN R - PORTFOLIO MAIN JS
   Typing, Particles, Counters, Chatbot, Forms
═══════════════════════════════════════════════════ */

// ─── INIT AOS ───
AOS.init({ duration: 700, easing: 'ease-out-cubic', once: true, offset: 60 });

// ─── THEME TOGGLE ───
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
let currentTheme = localStorage.getItem('theme') || 'dark';
document.documentElement.setAttribute('data-theme', currentTheme);
updateThemeIcon();

function updateThemeIcon() {
  if (currentTheme === 'light') {
    themeIcon.className = 'fas fa-moon';
  } else {
    themeIcon.className = 'fas fa-sun';
  }
}

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeIcon();
  });
}

const cursorDot = document.getElementById('cursorDot');
const cursorOutline = document.getElementById('cursorOutline');
if (cursorDot && cursorOutline && window.innerWidth > 768) {
  let mouseX = window.innerWidth / 2, mouseY = window.innerHeight / 2;
  let trailX = mouseX, trailY = mouseY;
  let dotAngle = 0, trailAngle = 0;
  const DOT_SIZE = 18, TRAIL_SIZE = 32;

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  function lerp(a, b, t) { return a + (b - a) * t; }

  function animate() {
    trailX = lerp(trailX, mouseX, 0.08);
    trailY = lerp(trailY, mouseY, 0.08);
    dotAngle   = (dotAngle   + 3) % 360;
    trailAngle = (trailAngle + 1.2) % 360;

    cursorDot.style.transform =
      `translate(${mouseX - DOT_SIZE / 2}px, ${mouseY - DOT_SIZE / 2}px) rotate(${dotAngle}deg)`;
    cursorOutline.style.transform =
      `translate(${trailX - TRAIL_SIZE / 2}px, ${trailY - TRAIL_SIZE / 2}px) rotate(${trailAngle}deg)`;

    requestAnimationFrame(animate);
  }
  animate();

  document.querySelectorAll('a, button, .project-card, .filter-btn').forEach(el => {
    el.addEventListener('mouseenter', () => {
      cursorOutline.style.filter = 'drop-shadow(0 0 10px #6366f1) drop-shadow(0 0 20px #8b5cf6)';
      cursorOutline.style.opacity = '0.9';
      cursorDot.querySelector('polygon').setAttribute('fill', '#a5b4fc');
    });
    el.addEventListener('mouseleave', () => {
      cursorOutline.style.filter = 'drop-shadow(0 0 6px #6366f1) drop-shadow(0 0 12px #8b5cf6)';
      cursorOutline.style.opacity = '0.55';
      cursorDot.querySelector('polygon').setAttribute('fill', '#6366f1');
    });
  });
}

// ─── PARTICLE BACKGROUND ───
const canvas = document.getElementById('particleCanvas');
if (canvas) {
  const ctx = canvas.getContext('2d');
  let particles = [];
  let animId;

  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.size = Math.random() * 1.5 + 0.3;
      this.speedX = (Math.random() - 0.5) * 0.4;
      this.speedY = (Math.random() - 0.5) * 0.4;
      this.opacity = Math.random() * 0.5 + 0.1;
    }
    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) this.reset();
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(99,102,241,${this.opacity})`;
      ctx.fill();
    }
  }

  for (let i = 0; i < 80; i++) particles.push(new Particle());

  function connectParticles() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(99,102,241,${0.06 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }
  }

  function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => { p.update(); p.draw(); });
    connectParticles();
    animId = requestAnimationFrame(animateParticles);
  }
  animateParticles();
}

// ─── TYPING ANIMATION ───
const typingEl = document.getElementById('typingText');
if (typingEl) {
  const roles = [
    'Python Full Stack Developer',
    'ECE Final Year Student',
    'AI & Software Developer',
    'Flask & Django Engineer',
    'Backend Developer'
  ];
  let roleIdx = 0, charIdx = 0, deleting = false;

  function typeRole() {
    const current = roles[roleIdx];
    if (!deleting) {
      typingEl.textContent = current.substring(0, charIdx + 1);
      charIdx++;
      if (charIdx === current.length) {
        deleting = true;
        setTimeout(typeRole, 1800);
        return;
      }
    } else {
      typingEl.textContent = current.substring(0, charIdx - 1);
      charIdx--;
      if (charIdx === 0) {
        deleting = false;
        roleIdx = (roleIdx + 1) % roles.length;
      }
    }
    setTimeout(typeRole, deleting ? 50 : 90);
  }
  typeRole();
}

// ─── ANIMATED COUNTERS ───
function animateCounters() {
  document.querySelectorAll('.stat-number').forEach(el => {
    const target = parseInt(el.getAttribute('data-target')) || 0;
    let current = 0;
    const step = Math.ceil(target / 50);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(timer);
    }, 40);
  });
}

// ─── SKILL BARS ANIMATION ───
function animateSkillBars() {
  document.querySelectorAll('.skill-fill').forEach(bar => {
    const width = bar.getAttribute('data-width');
    bar.style.width = width + '%';
  });
}

// ─── INTERSECTION OBSERVER (trigger animations on scroll) ───
const skillsSection = document.getElementById('skills');
const heroSection = document.getElementById('home');
let countersTriggered = false;
let skillsTriggered = false;

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.target === heroSection && entry.isIntersecting && !countersTriggered) {
      countersTriggered = true;
      setTimeout(animateCounters, 500);
    }
    if (entry.target === skillsSection && entry.isIntersecting && !skillsTriggered) {
      skillsTriggered = true;
      setTimeout(animateSkillBars, 300);
    }
  });
}, { threshold: 0.3 });

if (heroSection) observer.observe(heroSection);
if (skillsSection) observer.observe(skillsSection);

// Trigger counters on load if hero is visible
window.addEventListener('load', () => {
  const rect = document.querySelector('.hero-stats')?.getBoundingClientRect();
  if (rect && rect.top < window.innerHeight) {
    setTimeout(animateCounters, 600);
    countersTriggered = true;
  }
});

// ─── NAVBAR SCROLL ───
const navbar = document.getElementById('mainNav');
window.addEventListener('scroll', () => {
  if (navbar) {
    navbar.classList.toggle('scrolled', window.scrollY > 50);
  }
  // Active nav link
  const sections = ['home', 'about', 'skills', 'projects', 'certifications', 'contact'];
  const scrollY = window.scrollY + 100;
  sections.forEach(id => {
    const section = document.getElementById(id);
    if (section) {
      const top = section.offsetTop;
      const bottom = top + section.offsetHeight;
      const link = document.querySelector(`.nav-link[href="#${id}"]`);
      if (link) link.classList.toggle('active', scrollY >= top && scrollY < bottom);
    }
  });
  // Back to top
  const btt = document.getElementById('backToTop');
  if (btt) btt.classList.toggle('visible', window.scrollY > 400);
});

// ─── PROJECT SEARCH & FILTER ───
const searchInput = document.getElementById('projectSearch');
const filterBtns = document.querySelectorAll('.filter-btn');
let activeFilter = 'all';

function filterProjects() {
  const query = searchInput ? searchInput.value.toLowerCase() : '';
  document.querySelectorAll('.project-card-col').forEach(col => {
    const cat = col.getAttribute('data-category') || '';
    const title = col.getAttribute('data-title') || '';
    const matchFilter = activeFilter === 'all' || cat === activeFilter;
    const matchSearch = title.includes(query);
    col.style.display = matchFilter && matchSearch ? '' : 'none';
  });
}

if (searchInput) searchInput.addEventListener('input', filterProjects);
filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.getAttribute('data-filter');
    filterProjects();
  });
});

// ─── PROJECT MODAL ───
function openProjectModal(btn) {
  const title = btn.getAttribute('data-title');
  const desc = btn.getAttribute('data-desc');
  const tech = btn.getAttribute('data-tech');
  const features = btn.getAttribute('data-features');
  const github = btn.getAttribute('data-github');

  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalDesc').textContent = desc;

  // Tech tags
  const techContainer = document.getElementById('modalTech');
  techContainer.innerHTML = '';
  tech.split(', ').forEach(t => {
    const span = document.createElement('span');
    span.textContent = t;
    techContainer.appendChild(span);
  });

  // Features
  const featuresList = document.getElementById('modalFeatures');
  featuresList.innerHTML = '';
  if (features) {
    features.split('|').forEach(f => {
      const li = document.createElement('li');
      li.textContent = f.trim();
      featuresList.appendChild(li);
    });
  }

  // GitHub
  const githubWrap = document.getElementById('modalGithubWrap');
  const githubLink = document.getElementById('modalGithub');
  if (github) {
    githubLink.href = github;
    githubWrap.style.display = '';
  } else {
    githubWrap.style.display = 'none';
  }

  const modal = new bootstrap.Modal(document.getElementById('projectModal'));
  modal.show();
}

// ─── CONTACT FORM ───
function clearErrors() {
  ['name', 'email', 'subject', 'message'].forEach(field => {
    const err = document.getElementById(field + 'Error');
    const input = document.getElementById('contact' + field.charAt(0).toUpperCase() + field.slice(1));
    if (err) err.textContent = '';
    if (input) input.classList.remove('error');
  });
}

async function submitContact() {
  clearErrors();
  const name = document.getElementById('contactName')?.value.trim() || '';
  const email = document.getElementById('contactEmail')?.value.trim() || '';
  const subject = document.getElementById('contactSubject')?.value.trim() || '';
  const message = document.getElementById('contactMessage')?.value.trim() || '';

  // Client-side validation
  let hasErrors = false;
  const emailRegex = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

  if (!name || name.length < 2) {
    showError('nameError', 'contactName', 'Name must be at least 2 characters.');
    hasErrors = true;
  }
  if (!emailRegex.test(email)) {
    showError('emailError', 'contactEmail', 'Please enter a valid email address.');
    hasErrors = true;
  }
  if (!subject || subject.length < 3) {
    showError('subjectError', 'contactSubject', 'Subject must be at least 3 characters.');
    hasErrors = true;
  }
  if (!message || message.length < 10) {
    showError('messageError', 'contactMessage', 'Message must be at least 10 characters.');
    hasErrors = true;
  }
  if (hasErrors) return;

  // Submit
  const btn = document.getElementById('submitBtn');
  document.getElementById('submitText').style.display = 'none';
  document.getElementById('submitLoading').style.display = '';
  btn.disabled = true;

  try {
    const res = await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, subject, message })
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('formSuccess').style.display = 'block';
      document.getElementById('contactName').value = '';
      document.getElementById('contactEmail').value = '';
      document.getElementById('contactSubject').value = '';
      document.getElementById('contactMessage').value = '';
    } else if (data.errors) {
      Object.entries(data.errors).forEach(([field, msg]) => {
        showError(field + 'Error', 'contact' + field.charAt(0).toUpperCase() + field.slice(1), msg);
      });
    }
  } catch (err) {
    console.error('Contact form error:', err);
  } finally {
    document.getElementById('submitText').style.display = '';
    document.getElementById('submitLoading').style.display = 'none';
    btn.disabled = false;
  }
}

function showError(errId, inputId, msg) {
  const errEl = document.getElementById(errId);
  const inputEl = document.getElementById(inputId);
  if (errEl) errEl.textContent = msg;
  if (inputEl) inputEl.classList.add('error');
}

// ─── CHATBOT ───
const chatbotResponses = {
  'hello': "Hi there! I'm Santhoosh's portfolio assistant. How can I help you?",
  'hi': "Hello! Want to know about Santhoosh's projects, skills, or how to contact him?",
  'skills': "Santhoosh is skilled in Python, Flask, Django, JavaScript, HTML/CSS, SQLite, and more! He's also experienced with AI/ML, pandas, NumPy, and OpenCV.",
  'projects': "Santhoosh has built 7 impressive projects including an AI Petition Management System, Sepsis Prediction System, NexusPOS Billing System, and a Rice Quality Detection system!",
  'contact': "You can reach Santhoosh at santhooshshivan18@gmail.com or call +91 7558105935. LinkedIn: linkedin.com/in/santhoosh-shivan",
  'github': "Find all of Santhoosh's code at github.com/santhooshofficial",
  'experience': "Santhoosh completed a Python Full Stack Development internship at FITA Academy, Puducherry, gaining hands-on experience with Flask, Django, and REST APIs.",
  'education': "Santhoosh is a final-year B.E. ECE student at Mailam Engineering College with a CGPA of 8.36.",
  'hire': "Santhoosh is actively looking for internships and software developer roles. Send a message via the contact form!",
  'python': "Python is Santhoosh's primary language — he uses it for backend development, data processing, automation, and AI projects.",
  'flask': "Flask is Santhoosh's go-to framework for building lightweight, scalable web APIs and full-stack applications.",
  'django': "Santhoosh has built Django projects and showcases it as part of his full-stack toolkit.",
  'default': "I'm not sure about that, but I'd suggest scrolling through the portfolio or using the contact form to reach Santhoosh directly!"
};

function toggleChatbot() {
  const box = document.getElementById('chatbotBox');
  const icon = document.getElementById('chatIcon');
  const closeIcon = document.getElementById('chatClose');
  if (box.style.display === 'none') {
    box.style.display = 'block';
    icon.style.display = 'none';
    closeIcon.style.display = '';
  } else {
    box.style.display = 'none';
    icon.style.display = '';
    closeIcon.style.display = 'none';
  }
}

function sendChat() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg) return;

  addChatMsg(msg, 'user');
  input.value = '';

  const key = Object.keys(chatbotResponses).find(k => msg.toLowerCase().includes(k));
  const reply = chatbotResponses[key] || chatbotResponses['default'];
  setTimeout(() => addChatMsg(reply, 'bot'), 500);
}

function addChatMsg(text, type) {
  const messages = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `chat-msg ${type === 'bot' ? 'bot-msg' : 'user-msg'}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function chatEnter(e) {
  if (e.key === 'Enter') sendChat();
}

// ─── SMOOTH SCROLL FOR NAV LINKS ───
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', (e) => {
    const href = a.getAttribute('href');
    if (href === '#') return;
    const target = document.querySelector(href);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Close mobile nav
      const navCollapse = document.getElementById('navbarNav');
      if (navCollapse && navCollapse.classList.contains('show')) {
        new bootstrap.Collapse(navCollapse).hide();
      }
    }
  });
});

// ─── INIT ───
document.addEventListener('DOMContentLoaded', () => {
  // Skill bars trigger if already visible
  const skillsEl = document.getElementById('skills');
  if (skillsEl) {
    const rect = skillsEl.getBoundingClientRect();
    if (rect.top < window.innerHeight) animateSkillBars();
  }
});

console.log('%c Santhoosh Shivan R | Portfolio ', 'background: #6366f1; color: #fff; font-size: 14px; padding: 6px 12px; border-radius: 4px;');
console.log('%c Python Full Stack Developer | Built with Flask & ❤️ ', 'color: #6366f1; font-size: 11px;');
