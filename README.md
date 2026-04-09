# SecureChat – Encrypted Communication Platform

## 1. Project Overview

### 1.1 Why
SecureChat was built to demonstrate **secure software development principles** in a real-world web application.
It addresses the critical need for security-first design — tackling common vulnerabilities such as CSRF attacks, SQL injection, brute-force login attempts, insecure file uploads, and weak session management — while delivering a polished, modern user experience.

### 1.2 What
A Flask-based secure messaging application that provides:

- **User Authentication** with bcrypt-hashed passwords
- **Role-Based Access Control (RBAC)** with admin privileges
- **CSRF-Protected Forms** via Flask-WTF
- **Rate-Limited Endpoints** to prevent brute-force attacks
- **Secure File Uploads** with type validation and size limits
- **Security Headers** enforced via Flask-Talisman
- **4-Digit Verification Codes** for destructive actions (delete)

### 1.3 How (High-Level)
- Users register and authenticate through a secure login system
- Messages are managed via full CRUD operations with ownership enforcement
- File attachments are validated, sanitized, and stored securely
- Rate limiting, CSRF tokens, and security headers protect every endpoint
- Sensitive configuration is loaded from environment variables

---

## 2. Features

| Icon | Feature | Description |
|------|---------|-------------|
| 🔐 | **Bcrypt Password Hashing** | Passwords are never stored in plaintext |
| 🛡️ | **CSRF Protection** | All forms protected via Flask-WTF CSRF tokens |
| 🚦 | **Rate Limiting** | Login endpoint restricted to 5 attempts/minute |
| 📎 | **Secure File Uploads** | Type whitelist, filename sanitization, 5 MB limit |
| 🏷️ | **Role-Based Access (RBAC)** | Admin-only routes and ownership-based operations |
| 🔒 | **Security Headers** | Talisman enforces X-Frame-Options, HSTS, etc. |
| 🍪 | **Secure Cookies** | HTTPOnly, SameSite=Lax, Secure flags enabled |
| 🎯 | **Delete Verification** | Cryptographic 4-digit code required before deletion |
| 📡 | **Server Fingerprint Masking** | Custom server header hides technology stack |
| 🎨 | **Glassmorphism UI** | Modern, responsive interface with AOS animations |

---

## 3. Tech Stack

**Backend:**

- Python 3.8+
- Flask 3.x
- Flask-SQLAlchemy (ORM)
- Flask-Bcrypt (Password Hashing)
- Flask-WTF (CSRF Protection)
- Flask-Talisman (Security Headers)
- Flask-Limiter (Rate Limiting)
- python-dotenv (Environment Management)

**Frontend:**

- HTML5 / CSS3
- Bootstrap 5.3
- Google Fonts (Outfit)
- Font Awesome 6.4
- AOS (Animate On Scroll)

**Database:**

- SQLite (development)

---

## 4. Project Structure

```
SecureChat/
├── templates/
│   ├── index.html            # Main chat console + hero page
│   ├── login.html            # Login form
│   ├── register.html         # Registration form
│   ├── update.html           # Message edit form
│   ├── confirm_delete.html   # Delete verification page
│   ├── about.html            # About / story page
│   ├── 404.html              # Custom 404 error page
│   └── 500.html              # Custom 500 error page
├── uploads/                  # User-uploaded files (gitignored)
├── instance/                 # SQLite database (gitignored)
├── app.py                    # Main Flask application
├── forms.py                  # WTForms form definitions
├── init_db.py                # Database initialization script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (gitignored)
├── .gitignore                # Git exclusion rules
└── README.md                 # This file
```

---

## 5. Setup & Usage

### 5.1 Prerequisites

- Python 3.8 or later
- pip package manager

### 5.2 Installation

```bash
git clone https://github.com/MohidUmer/SecureChat.git
cd SecureChat
pip install -r requirements.txt
```

### 5.3 Environment Configuration

Create a `.env` file in the project root:

```env
FLASK_SECRET_KEY=your_secret_key_here_change_in_production
DATABASE_URL=sqlite:///securechat.db
```

### 5.4 Initialize Database

```bash
python init_db.py
```

### 5.5 Run Locally

```bash
python app.py
```

Access the application at: **http://localhost:5000**

---

## 6. Major Components

### 6.1 Authentication System
- Registration with input validation (regex, length, email format)
- Bcrypt password hashing with salt
- Session-based authentication
- Login rate limiting (5 attempts/minute)

### 6.2 Message Console (CRUD)
- Create messages with optional file attachments
- Read all messages in a live data log table
- Update messages with ownership verification
- Delete messages with 4-digit security code challenge

### 6.3 Secure File Upload Engine
- Whitelist validation: `png, jpg, jpeg, gif, pdf, txt, doc, docx, zip`
- `secure_filename()` sanitization to prevent path traversal
- 5 MB maximum file size enforcement
- Unique stored filenames to prevent collisions
- Drag-and-drop upload UI with file chip previews

### 6.4 Role-Based Access Control
- `@login_required` decorator for authenticated routes
- `@admin_required` decorator for admin-only operations
- Ownership checks on edit/delete operations
- Admin users can manage all content

---

## 7. Security Implementation Details

| Security Layer | Implementation | Threat Mitigated |
|----------------|----------------|------------------|
| Password Storage | Bcrypt hashing with salt | Credential theft |
| CSRF Protection | Flask-WTF hidden tokens on all forms | Cross-Site Request Forgery |
| Rate Limiting | Flask-Limiter (5/min on login) | Brute-force attacks |
| Security Headers | Flask-Talisman (X-Frame, HSTS, etc.) | Clickjacking, MITM |
| Input Validation | WTForms validators + regex | Injection attacks |
| File Upload | Whitelist + secure_filename + size limit | Malicious file upload |
| Session Security | HTTPOnly, SameSite, Secure cookie flags | Session hijacking |
| Delete Verification | Cryptographic 4-digit code (secrets module) | Accidental/unauthorized deletion |
| Server Masking | Custom Werkzeug version string | Technology fingerprinting |
| Environment Secrets | python-dotenv for keys and URIs | Secret exposure in code |

---

## 8. System Workflow

```
User Registers → Password Hashed (Bcrypt) → Account Created
       ↓
User Logs In → Rate Limit Check → Session Established
       ↓
User Sends Message → CSRF Validated → File Sanitized → Stored in DB
       ↓
User Edits/Deletes → Ownership Verified → Action Authorized
       ↓
Admin Operations → RBAC Check → Elevated Actions Permitted
```

---

## 9. Data Handling & Privacy

- Passwords are **hashed and salted** — never stored in plaintext
- User sessions are **HTTPOnly** and **SameSite** protected
- File uploads are **sanitized** and stored with collision-resistant names
- No external analytics or tracking is implemented
- Environment variables keep secrets out of source code

---

## 10. API & Stability

- Rate limiting enforced via Flask-Limiter (200/day, 50/hour global; 5/min on login)
- CORS-ready architecture
- Custom error handlers for 404 and 500 responses
- Debug mode disabled in production

---

## 11. Limitations

- Single SQLite database (not suitable for production at scale)
- No real-time WebSocket messaging (HTTP request/response model)
- No password reset / email verification flow
- No message encryption at rest
- Web-only interface (no mobile app)

---

## 12. Usage Example

```
1. Register a new account → Login
2. Type a message → Attach files (optional) → Execute Transmission
3. View messages in the Live Data Logs table
4. Edit your own messages via the modify button
5. Delete messages using the 4-digit security verification
```

---

## 13. Future Improvements

- End-to-end message encryption
- WebSocket-based real-time messaging
- Password reset via email verification
- User profile pages with avatars
- Message search and filtering
- Database migration to PostgreSQL for production
- Docker containerization
- Two-factor authentication (2FA)

---

## 14. Educational & Practical Value

SecureChat demonstrates:

- **Secure authentication** with password hashing and session management
- **CSRF protection** across all state-changing operations
- **Rate limiting** to prevent abuse
- **Secure file handling** with validation and sanitization
- **Role-based access control** with decorators
- **Security headers** via middleware
- **Environment-based configuration** for secret management
- **Modern UI/UX design** with glassmorphism and animations

---

## 15. Author & Contact

**Name:** Mohid Umer  
**Email:** mohidumer112@gmail.com

---

## 16. License & Usage

- Educational and personal use only
- Proper attribution required
- Not permitted for academic plagiarism
- See repository LICENSE for details

---

> **SecureChat** showcases modern secure software development principles through a practical, well-designed messaging application that prioritizes security at every layer of the stack.
