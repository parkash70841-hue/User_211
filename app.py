import os
import re
import html
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, flash, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.urandom(32)

# ==========================================
# PERSONAL & BUSINESS CONFIGURATION
# ==========================================
TELEGRAM_BOT_TOKEN = "8988154095:AAHIoRgwHA08Mfw1viZFUPdeUpJyjF3dRTI"
TELEGRAM_CHAT_ID = "7867296083"

YOUR_BRAND_NAME = "USER_211"
INSTAGRAM_HANDLE = "user_211"
YOUR_PHONE = "7347504051"
WHATSAPP_NUMBER = "917347504051"
YOUR_EMAIL = "kaka70841@gmail.com"
ADMIN_PASSWORD = "admin_password_2026"

# Permanent Direct Logo Link
CURRENT_LOGO_URL = "https://i.postimg.cc/wBw41N4F/d9df94b8bea76ab2246d3375b3b80ee0.jpg"
FALLBACK_SVG = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' fill='%2310B981'><circle cx='50' cy='50' r='50' fill='%231E293B'/><text x='50%' y='55%' font-family='sans-serif' font-weight='800' font-size='20' fill='%2310B981' text-anchor='middle' dominant-baseline='middle'>U211</text></svg>"

LEADS_DATABASE = []
VISIT_LOGS = []  # List of timestamps for visit analytics

# ==========================================
# SECURITY HEADERS & HELPERS
# ==========================================
@app.after_request
def apply_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

def sanitize_input(text):
    if not text:
        return ""
    return html.escape(text.strip())[:250]

def send_telegram_lead(name, phone, service, details):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    message = (
        f"⚡ *NEW CLIENT INQUIRY (USER_211)*\n\n"
        f"👤 *Client Name:* {name}\n"
        f"📞 *Phone:* {phone}\n"
        f"🎯 *Selected Plan:* {service}\n"
        f"📝 *Details:* {details}"
    )
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Telegram Error:", e)

def get_visit_stats():
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    week_start = now - timedelta(days=7)
    month_start = datetime(now.year, now.month, 1)

    today_count = sum(1 for v in VISIT_LOGS if v >= today_start)
    week_count = sum(1 for v in VISIT_LOGS if v >= week_start)
    month_count = sum(1 for v in VISIT_LOGS if v >= month_start)
    total_count = len(VISIT_LOGS)

    return {
        "today": today_count,
        "week": week_count,
        "month": month_count,
        "total": total_count
    }

# ==========================================
# MAIN PUBLIC UI TEMPLATE
# ==========================================
SITE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>USER_211 | Digital Studio & Fitness</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; 
            background: #0b0f17; 
            color: #f8fafc; 
            line-height: 1.6; 
            padding-bottom: 90px; 
            -webkit-font-smoothing: antialiased;
            position: relative;
            overflow-x: hidden;
        }

        /* 3D Background Canvas */
        #bg-3d-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
        }

        header, .hero, .container, .bottom-bar {
            position: relative;
            z-index: 10;
        }

        /* Sleek Header */
        header { 
            background: rgba(11, 15, 23, 0.85); 
            backdrop-filter: blur(16px); 
            -webkit-backdrop-filter: blur(16px); 
            padding: 14px 20px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            position: sticky; 
            top: 0; 
            z-index: 1000; 
            border-bottom: 1px solid rgba(255, 255, 255, 0.06); 
        }
        .brand-container { display: flex; align-items: center; gap: 10px; }
        .avatar-img { 
            width: 38px; 
            height: 38px; 
            border-radius: 50%; 
            object-fit: cover; 
            border: 1px solid rgba(255, 255, 255, 0.15); 
        }
        .brand-logo { font-size: 17px; font-weight: 800; color: #ffffff; letter-spacing: -0.3px; }
        .brand-logo span { color: #10b981; }
        
        .header-actions { display: flex; align-items: center; gap: 8px; }
        .insta-btn { 
            background: rgba(255, 255, 255, 0.05); 
            color: #f1f5f9; 
            text-decoration: none; 
            padding: 8px 14px; 
            border-radius: 20px; 
            font-size: 12px; 
            font-weight: 600; 
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .call-btn { 
            background: #10b981; 
            color: #0b0f17; 
            text-decoration: none; 
            padding: 8px 16px; 
            border-radius: 20px; 
            font-size: 12px; 
            font-weight: 800; 
        }

        /* Hero Banner */
        .hero { 
            padding: 50px 20px 40px; 
            text-align: center; 
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            background: radial-gradient(circle at 50% 0%, rgba(16, 185, 129, 0.08) 0%, rgba(11, 15, 23, 0) 70%);
        }
        .hero-avatar { 
            width: 86px; 
            height: 86px; 
            border-radius: 50%; 
            object-fit: cover; 
            border: 2px solid #10b981; 
            margin-bottom: 16px;
            box-shadow: 0 0 25px rgba(16, 185, 129, 0.2);
        }
        .hero-badge { 
            background: rgba(16, 185, 129, 0.1); 
            color: #10b981; 
            border: 1px solid rgba(16, 185, 129, 0.25); 
            padding: 5px 14px; 
            border-radius: 30px; 
            font-size: 11px; 
            font-weight: 700; 
            display: inline-block; 
            margin-bottom: 16px; 
            letter-spacing: 0.5px;
        }
        .hero h1 { font-size: 28px; font-weight: 800; line-height: 1.3; margin-bottom: 12px; color: #ffffff; letter-spacing: -0.5px; }
        .hero p { font-size: 14px; color: #94a3b8; margin-bottom: 24px; max-width: 480px; margin-left: auto; margin-right: auto; }
        .hero-cta { 
            display: inline-block; 
            background: #10b981; 
            color: #0b0f17; 
            padding: 13px 28px; 
            border-radius: 30px; 
            font-weight: 800; 
            text-decoration: none; 
            font-size: 14px; 
            box-shadow: 0 8px 20px rgba(16, 185, 129, 0.25); 
        }

        .container { padding: 24px 20px; max-width: 600px; margin: auto; }
        .section-title { font-size: 18px; font-weight: 800; margin: 30px 0 16px; color: #ffffff; text-align: center; letter-spacing: -0.3px; }

        /* Sample Box */
        .sample-box {
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            margin-bottom: 25px;
        }
        .sample-title { font-size: 15px; font-weight: 800; color: #ffffff; margin-bottom: 4px; }
        .sample-sub { font-size: 12px; color: #94a3b8; margin-bottom: 16px; }
        .sample-buttons { display: flex; gap: 10px; justify-content: center; }
        .btn-dm-insta { background: rgba(255, 255, 255, 0.08); color: white; text-decoration: none; padding: 10px 16px; border-radius: 20px; font-size: 12px; font-weight: 700; border: 1px solid rgba(255, 255, 255, 0.12); }
        .btn-dm-wa { background: #10b981; color: #0b0f17; text-decoration: none; padding: 10px 16px; border-radius: 20px; font-size: 12px; font-weight: 800; }

        /* Grid Cards */
        .card-grid { display: grid; grid-template-columns: 1fr; gap: 14px; }
        .service-card { 
            background: rgba(15, 23, 42, 0.75); 
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.07); 
            border-radius: 16px; 
            padding: 20px; 
        }
        .card-header-flex {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 4px;
        }
        .price-tag { 
            background: rgba(16, 185, 129, 0.12); 
            color: #10b981; 
            border: 1px solid rgba(16, 185, 129, 0.3); 
            padding: 4px 10px; 
            border-radius: 20px; 
            font-size: 11px; 
            font-weight: 800; 
            white-space: nowrap;
            flex-shrink: 0;
        }
        .card-title { font-size: 16px; font-weight: 800; color: #ffffff; line-height: 1.3; }
        .card-sub { font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 14px; }
        .card-list { font-size: 12px; color: #cbd5e1; list-style: none; }
        .card-list li { margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }

        /* Form Card */
        .form-card { 
            background: rgba(15, 23, 42, 0.85); 
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1); 
            border-radius: 20px; 
            padding: 24px 20px; 
            margin-top: 30px; 
        }
        .form-card h2 { font-size: 19px; font-weight: 800; text-align: center; margin-bottom: 4px; color: #ffffff; }
        .form-card p { font-size: 12px; color: #94a3b8; text-align: center; margin-bottom: 20px; }
        
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; font-size: 11px; font-weight: 700; color: #94a3b8; margin-bottom: 6px; letter-spacing: 0.5px; }
        .form-control { 
            width: 100%; 
            padding: 12px 14px; 
            background: #0b0f17; 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            border-radius: 10px; 
            color: #ffffff; 
            font-size: 13px; 
            font-family: inherit;
            outline: none; 
        }
        .form-control:focus { border-color: #10b981; }

        .submit-btn { 
            width: 100%; 
            background: #10b981; 
            color: #0b0f17; 
            border: none; 
            padding: 14px; 
            border-radius: 10px; 
            font-weight: 800; 
            font-size: 14px; 
            cursor: pointer; 
            margin-top: 10px; 
        }

        .toast { background: #10b981; color: #0b0f17; padding: 12px; border-radius: 10px; text-align: center; font-weight: 800; font-size: 13px; margin-bottom: 18px; }

        .contact-card { 
            background: rgba(15, 23, 42, 0.75); 
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.06); 
            border-radius: 14px; 
            padding: 18px; 
            font-size: 12px; 
            color: #94a3b8; 
            margin-top: 30px; 
        }
        .contact-row { margin-bottom: 8px; }
        .contact-row b { color: #f8fafc; }

        /* Floating Bottom Bar */
        .bottom-bar { 
            position: fixed; 
            bottom: 0; 
            left: 0; 
            right: 0; 
            background: rgba(11, 15, 23, 0.92); 
            backdrop-filter: blur(16px); 
            padding: 12px 20px; 
            display: flex; 
            gap: 12px; 
            border-top: 1px solid rgba(255, 255, 255, 0.08); 
            z-index: 1000; 
        }
        .btn-whatsapp { 
            flex: 1; 
            background: #10b981; 
            color: #0b0f17; 
            text-align: center; 
            padding: 12px; 
            border-radius: 30px; 
            font-weight: 800; 
            font-size: 13px; 
            text-decoration: none; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            gap: 6px; 
        }
        .btn-book { 
            flex: 1; 
            background: rgba(255, 255, 255, 0.08); 
            color: white; 
            text-align: center; 
            padding: 12px; 
            border-radius: 30px; 
            font-weight: 700; 
            font-size: 13px; 
            text-decoration: none; 
            border: 1px solid rgba(255, 255, 255, 0.12);
        }
    </style>
</head>
<body>

    <canvas id="bg-3d-canvas"></canvas>

    <!-- Header -->
    <header>
        <div class="brand-container">
            <img src="{{ logo }}" class="avatar-img" alt="Logo" onerror="this.src='{{ fallback_logo }}'">
            <div class="brand-logo">USER<span>_211</span></div>
        </div>
        <div class="header-actions">
            <a href="https://instagram.com/{{ insta }}" target="_blank" class="insta-btn">📸 Instagram</a>
            <a href="tel:+91{{ phone }}" class="call-btn">📞 Call</a>
        </div>
    </header>

    <!-- Hero Section -->
    <div class="hero">
        <img src="{{ logo }}" class="hero-avatar" alt="USER_211" onerror="this.src='{{ fallback_logo }}'">
        <br>
        <span class="hero-badge">OFFICIAL FREELANCE STUDIO</span>
        <h1>Websites, Fitness Plans & Graphic Designs</h1>
        <p>High-performing web development, custom fitness schedules, and social media content created directly for you.</p>
        <a href="#order-form" class="hero-cta">HIRE USER_211 →</a>
    </div>

    <div class="container">
        
        <!-- Sample DM Box -->
        <div class="sample-box">
            <div class="sample-title">🎨 Want to see Work Samples or Portfolio?</div>
            <div class="sample-sub">DM me directly on Instagram or WhatsApp to check out recent web applications, poster designs, or diet plans.</div>
            <div class="sample-buttons">
                <a href="https://instagram.com/{{ insta }}" target="_blank" class="btn-dm-insta">DM on Instagram</a>
                <a href="https://wa.me/{{ whatsapp }}?text=Hi%20USER_211,%20please%20share%20your%20work%20samples" target="_blank" class="btn-dm-wa">DM on WhatsApp</a>
            </div>
        </div>

        <div class="section-title">Services & Rates</div>
        
        <div class="card-grid">
            
            <div class="service-card">
                <div class="card-header-flex">
                    <div class="card-title">💻 Web App Setup</div>
                    <span class="price-tag">₹1,999</span>
                </div>
                <div class="card-sub">Complete Business or E-Commerce Site</div>
                <ul class="card-list">
                    <li>✅ Mobile Responsive Design</li>
                    <li>✅ Admin Dashboard & Telegram Live Alerts</li>
                    <li>✅ Free Hosting Deployment</li>
                </ul>
            </div>

            <div class="service-card">
                <div class="card-header-flex">
                    <div class="card-title">⚙️ Web Maintenance</div>
                    <span class="price-tag">₹299 / Mo</span>
                </div>
                <div class="card-sub">Ongoing Support & Upgrades</div>
                <ul class="card-list">
                    <li>✅ Regular Code & Security Backups</li>
                    <li>✅ Content Updates & Bug Fixes</li>
                    <li>✅ Server Uptime Monitoring</li>
                </ul>
            </div>

            <div class="service-card" style="border-color: rgba(16, 185, 129, 0.4);">
                <div class="card-header-flex">
                    <div class="card-title">🔥 Diet + Workout Combo</div>
                    <span class="price-tag">₹349 (COMBO)</span>
                </div>
                <div class="card-sub">Full Fitness Transformation Package</div>
                <ul class="card-list">
                    <li>✅ Customized Diet Chart (Veg/Non-Veg)</li>
                    <li>✅ Home or Gym Workout Routine</li>
                    <li>✅ Direct WhatsApp Guidance</li>
                </ul>
            </div>

            <div class="service-card">
                <div class="card-header-flex">
                    <div class="card-title">🏋️‍♂️ Single Plan (Diet or Workout)</div>
                    <span class="price-tag">₹199 Each</span>
                </div>
                <div class="card-sub">Choose Diet Chart OR Workout Plan</div>
                <ul class="card-list">
                    <li>✅ Workout Plan Only: ₹199</li>
                    <li>✅ Diet Plan Only: ₹199</li>
                    <li>✅ Tailored to Your Specific Body Goal</li>
                </ul>
            </div>

            <div class="service-card">
                <div class="card-header-flex">
                    <div class="card-title">🖼️ Poster Design</div>
                    <span class="price-tag">₹149 / Poster</span>
                </div>
                <div class="card-sub">Shop, Gym & Business Posters</div>
                <ul class="card-list">
                    <li>✅ Custom Creative Graphics & Layouts</li>
                    <li>✅ High-Resolution Print Ready Files</li>
                    <li>✅ 24-Hour Express Delivery</li>
                </ul>
            </div>

            <div class="service-card">
                <div class="card-header-flex">
                    <div class="card-title">🎨 Instagram Post Design</div>
                    <span class="price-tag">₹99 / Post</span>
                </div>
                <div class="card-sub">Social Media Banners & Stories</div>
                <ul class="card-list">
                    <li>✅ Instagram Reels/Posts Graphics</li>
                    <li>✅ Modern Clean Layouts</li>
                    <li>✅ Optimized for Mobile Screens</li>
                </ul>
            </div>

        </div>

        <!-- Booking / Order Form -->
        <div class="form-card" id="order-form">
            <h2>Book a Service / Inquire</h2>
            <p>Fill out the form and I will message you directly on WhatsApp/Telegram!</p>

            {% with messages = get_flashed_messages() %}
              {% if messages %}
                {% for message in messages %}
                  <div class="toast">✅ {{ message }}</div>
                {% endfor %}
              {% endif %}
            {% endwith %}

            <form action="/submit_lead" method="POST">
                <div class="form-group">
                    <label>YOUR NAME</label>
                    <input type="text" name="name" class="form-control" placeholder="e.g. Rahul Verma" required>
                </div>
                <div class="form-group">
                    <label>MOBILE / WHATSAPP NUMBER</label>
                    <input type="tel" name="phone" class="form-control" placeholder="10-Digit Mobile Number" required>
                </div>
                <div class="form-group">
                    <label>SELECT SERVICE</label>
                    <select name="service" class="form-control">
                        <option value="Web App Setup (₹1,999)">💻 Web App Setup (₹1,999)</option>
                        <option value="Web Maintenance (₹299/mo)">⚙️ Web Maintenance (₹299/mo)</option>
                        <option value="Diet + Workout Combo (₹349)">🔥 Diet + Workout Combo (₹349)</option>
                        <option value="Workout Plan Only (₹199)">🏋️‍♂️ Workout Plan Only (₹199)</option>
                        <option value="Diet Plan Only (₹199)">🥗 Diet Plan Only (₹199)</option>
                        <option value="Poster Design (₹149)">🖼️ Poster Design (₹149)</option>
                        <option value="Instagram Post Design (₹99)">🎨 Instagram Post Design (₹99)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>YOUR REQUIREMENTS / DETAILS</label>
                    <textarea name="details" class="form-control" placeholder="Describe what you need..." style="height: 70px;"></textarea>
                </div>
                <button type="submit" class="submit-btn">SUBMIT REQUEST 🚀</button>
            </form>
        </div>

        <!-- Contact & Support Info -->
        <div class="contact-card">
            <div class="contact-row">📸 <b>Instagram:</b> @{{ insta }}</div>
            <div class="contact-row">💬 <b>WhatsApp:</b> +91 {{ phone }}</div>
            <div class="contact-row">✉️ <b>Email:</b> {{ email }}</div>
            <div class="contact-row">⚡ <b>Response Time:</b> Within 15-30 Minutes</div>
        </div>

    </div>

    <!-- Floating Mobile Bottom Bar -->
    <div class="bottom-bar">
        <a href="https://wa.me/{{ whatsapp }}?text=Hi%20USER_211,%20I%20want%20to%20hire%20you%20for%20your%20services" class="btn-whatsapp" target="_blank">
            💬 WhatsApp Chat
        </a>
        <a href="#order-form" class="btn-book">Book Service</a>
    </div>

    <script>
        const canvas = document.getElementById('bg-3d-canvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        const particles = [];
        const particleCount = window.innerWidth < 600 ? 35 : 65;

        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 0.6;
                this.vy = (Math.random() - 0.5) * 0.6;
                this.radius = Math.random() * 2 + 1;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;

                if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(16, 185, 129, 0.4)';
                ctx.fill();
            }
        }

        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();

                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(16, 185, 129, ${0.25 - dist / 480})`;
                        ctx.lineWidth = 0.8;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animate);
        }
        animate();
    </script>

</body>
</html>
"""

# ==========================================
# SECURE ADMIN PANEL WITH ANALYTICS DASHBOARD
# ==========================================
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>USER_211 Professional Admin Portal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #0b0f17; color: #f8fafc; padding: 20px; max-width: 900px; margin: auto; }
        
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 15px; margin-bottom: 24px; }
        .brand-container { display: flex; align-items: center; gap: 10px; }
        .brand-logo { font-size: 18px; font-weight: 800; color: #ffffff; }
        .avatar-img { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 1px solid #10b981; }

        /* Professional Stats Dashboard Grid */
        .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 25px; }
        @media (min-width: 600px) { .stats-grid { grid-template-columns: repeat(4, 1fr); } }
        
        .stat-card {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 16px;
            text-align: center;
        }
        .stat-val { font-size: 24px; font-weight: 800; color: #10b981; margin-top: 4px; }
        .stat-lbl { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }

        .manager-card { background: rgba(15, 23, 42, 0.8); border: 1px solid #10b981; border-radius: 14px; padding: 20px; margin-bottom: 25px; }
        .manager-card h3 { font-size: 15px; margin-bottom: 4px; color: #ffffff; }
        .manager-card p { font-size: 12px; color: #94a3b8; margin-bottom: 14px; }
        .form-control { width: 100%; padding: 10px 12px; background: #0b0f17; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: white; font-size: 12px; margin-bottom: 10px; outline: none; }
        .save-btn { background: #10b981; color: #0b0f17; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 800; font-size: 12px; cursor: pointer; }

        .section-hdr { font-size: 16px; font-weight: 800; color: #ffffff; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between; }
        
        .lead-card { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 18px; margin-bottom: 14px; }
        .lead-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .lead-name { font-weight: 800; font-size: 16px; color: #ffffff; }
        .badge { padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 800; background: #10b981; color: #0b0f17; }
        .lead-info { font-size: 12px; color: #cbd5e1; margin-bottom: 12px; line-height: 1.7; }
        .actions { display: flex; gap: 10px; }
        .btn-action { flex: 1; padding: 8px; border-radius: 8px; text-align: center; text-decoration: none; font-size: 11px; font-weight: 800; }
        .btn-call { background: rgba(255, 255, 255, 0.1); color: white; }
        .btn-wa { background: #10b981; color: #0b0f17; }
        .toast { background: #10b981; color: #0b0f17; padding: 10px; border-radius: 8px; text-align: center; font-weight: 800; font-size: 12px; margin-bottom: 15px; }
    </style>
</head>
<body>

    <div class="header">
        <div class="brand-container">
            <img src="{{ logo }}" class="avatar-img" onerror="this.src='{{ fallback_logo }}'">
            <div class="brand-logo">USER_211 Dashboard</div>
        </div>
        <a href="/admin_logout" style="color:#94a3b8; text-decoration:none; font-size:12px; font-weight:600;">Logout</a>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="toast">✅ {{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <!-- Analytics Dashboard Cards -->
    <div class="section-hdr">
        <span>📊 Website Analytics & Traffic</span>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-lbl">Today</div>
            <div class="stat-val">{{ stats.today }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-lbl">This Week</div>
            <div class="stat-val">{{ stats.week }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-lbl">This Month</div>
            <div class="stat-val">{{ stats.month }}</div>
        </div>
        <div class="stat-card">
            <div class="stat-lbl">Total Visits</div>
            <div class="stat-val">{{ stats.total }}</div>
        </div>
    </div>

    <!-- Logo Manager Section -->
    <div class="manager-card">
        <h3>🖼️ Live Logo Manager</h3>
        <p>Paste any direct image link below to update your website logo instantly.</p>
        <form action="/admin/update_logo" method="POST">
            <input type="url" name="logo_url" class="form-control" placeholder="https://i.postimg.cc/your-image.jpg" value="{{ logo }}" required>
            <button type="submit" class="save-btn">UPDATE WEBSITE LOGO 🚀</button>
        </form>
    </div>

    <div class="section-hdr">
        <span>📥 Orders & Inquiries ({{ leads|length }})</span>
    </div>

    {% if leads %}
        {% for l in leads[::-1] %}
        <div class="lead-card">
            <div class="lead-header">
                <span class="lead-name">👤 {{ l.name }}</span>
                <span class="badge">{{ l.service }}</span>
            </div>
            <div class="lead-info">
                📞 <b>Phone:</b> {{ l.phone }}<br>
                📝 <b>Details:</b> {{ l.details }}<br>
                📅 <b>Received:</b> {{ l.date }}
            </div>
            <div class="actions">
                <a href="tel:+91{{ l.phone }}" class="btn-action btn-call">📞 Call</a>
                <a href="https://wa.me/91{{ l.phone }}" class="btn-action btn-wa" target="_blank">💬 WhatsApp</a>
            </div>
        </div>
        {% endfor %}
    {% else %}
        <p style="color:#94a3b8; text-align:center; padding: 20px 0;">No inquiries received yet.</p>
    {% endif %}

    <br>
    <a href="/" style="color:#10b981; font-weight:bold; text-decoration:none;">← Back to Main Site</a>
</body>
</html>
"""

# ==========================================
# ROUTES
# ==========================================
@app.route('/')
def home():
    # Record visitor timestamp
    VISIT_LOGS.append(datetime.now())

    return render_template_string(
        SITE_HTML, 
        whatsapp=WHATSAPP_NUMBER, 
        phone=YOUR_PHONE, 
        email=YOUR_EMAIL, 
        insta=INSTAGRAM_HANDLE, 
        logo=CURRENT_LOGO_URL,
        fallback_logo=FALLBACK_SVG
    )

@app.route('/submit_lead', methods=['POST'])
def submit_lead():
    name = sanitize_input(request.form.get('name', ''))
    phone = sanitize_input(request.form.get('phone', ''))
    service = sanitize_input(request.form.get('service', 'Web Development'))
    details = sanitize_input(request.form.get('details', 'None'))

    clean_phone = re.sub(r'\D', '', phone)

    if name and clean_phone:
        send_telegram_lead(name, clean_phone, service, details)
        
        new_lead = {
            "name": name,
            "phone": clean_phone,
            "service": service,
            "details": details,
            "date": datetime.now().strftime("%d %b %Y, %I:%M %p")
        }
        LEADS_DATABASE.append(new_lead)
        flash("Inquiry Submitted! I will message/call you shortly.")

    return redirect(url_for('home') + '#order-form')

@app.route('/admin')
def admin():
    if not session.get('is_agency_admin'):
        return render_template_string("""
            <body style="background:#0b0f17; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; min-height:100vh;">
                <div style="background:#0f172a; padding:30px; border-radius:16px; text-align:center; width:300px; border:1px solid rgba(255,255,255,0.08);">
                    <h2 style="margin-bottom:15px; font-size:18px;">🔐 Admin Login</h2>
                    <form action="/admin_login" method="POST">
                        <input type="password" name="password" placeholder="Admin Password" style="width:100%; padding:10px; margin-bottom:15px; border-radius:8px; border:1px solid rgba(255,255,255,0.1); background:#0b0f17; color:white;"><br>
                        <button type="submit" style="width:100%; background:#10b981; color:#0b0f17; border:none; padding:10px; border-radius:8px; font-weight:800; cursor:pointer;">LOGIN</button>
                    </form>
                </div>
            </body>
        """)
    return render_template_string(
        ADMIN_HTML, 
        leads=LEADS_DATABASE, 
        logo=CURRENT_LOGO_URL,
        fallback_logo=FALLBACK_SVG,
        stats=get_visit_stats()
    )

@app.route('/admin_login', methods=['POST'])
def admin_login():
    if request.form.get('password') == ADMIN_PASSWORD:
        session['is_agency_admin'] = True
    return redirect(url_for('admin'))

@app.route('/admin_logout')
def admin_logout():
    session.pop('is_agency_admin', None)
    return redirect(url_for('home'))

@app.route('/admin/update_logo', methods=['POST'])
def update_logo():
    global CURRENT_LOGO_URL
    if session.get('is_agency_admin'):
        new_url = request.form.get('logo_url', '').strip()
        if new_url:
            CURRENT_LOGO_URL = new_url
            flash("Logo Updated Successfully!")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
