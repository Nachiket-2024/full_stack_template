# Full Stack Template

A scalable full-stack template with FastAPI backend and React frontend, designed for multiple user roles, supporting both email+password and Google (OAuth2) login, async operations, and JWT authentication.

---

## 🛠️ Stack

- **Backend:** FastAPI, SQLAlchemy (async), Alembic migrations  
- **Authentication:** Email + Password (with JWT access & refresh tokens), Google OAuth2 
- **Frontend:** React + Vite, Tailwind CSS, Material UI  
- **State Management:** Redux (main app state) and optional React Query (server-state caching)  
- **Database:** PostgreSQL (async)  
- **Caching & Tasks:** Redis + Celery    
- **Deployment:** Docker

---

## ⚙️ Environment Variables

All environment variables are defined in `.env.example`.  
Copy it to `.env` and update the values with your own credentials:

```bash
cp .env.example .env
```

## 📥 Installation

1. **Clone the repository**
```bash
git clone https://github.com/Nachiket-2024/full_stack_template.git
cd full_stack_template
```

2. **Set up the backend environment**
```bash
cd backend
pip install -r requirements.txt
```

3. **Set up the frontend environment**
```bash
cd frontend
npm install
```

> Make sure you have Node.js 18+ installed (or compatible version for Vite).  

---

## 🚀 Run the App

1. **Start the FastAPI backend**
```bash
uvicorn backend.app.main:app --reload
```

2. **Run the React frontend**
```bash
cd frontend
npm run dev
```

---

## 📝 Notes

- All credentials and secrets are loaded from `.env`  
- Use **Alembic** for database migrations  
- **Redis + Celery** are used for async tasks and caching  
- For security ,rate limiting with IP and brute force attack prevention files are integrated in Auth and OAuth flow
- OAuth2 setup requires Google credentials  
- JWT access and refresh tokens are handled in auth folder with modular files for clarity 
- Redux manages global app state; React Query can be used for server-side async data caching  

---

## 📦 Deployment

- Recommended via Docker Compose (can orchestrate backend, frontend, PostgreSQL, and Redis together)
- Ensure `.env` secrets are set in production
