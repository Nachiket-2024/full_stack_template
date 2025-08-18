# Full Stack Template

A scalable full-stack template with FastAPI backend and React frontend, designed for multiple user roles, supporting both email+password and Google (OAuth2) login, async operations, and JWT authentication.

---

## Stack

- **Backend:** FastAPI, SQLAlchemy (async), Alembic migrations  
- **Authentication:** JWT (access + refresh), Google OAuth2  
- **Frontend:** React + Vite, Tailwind CSS, Material UI  
- **State Management:** Redux (main app state) and optional React Query (server-state caching)  
- **Database:** PostgreSQL (async)  
- **Caching & Tasks:** Redis + Celery  
- **Testing:** Pytest, coverage  
- **Deployment:** Docker Compose, Traefik for automatic HTTPS  

---

## Environment Variables

Create a `.env` file in the `backend/` folder with the following content:

```env
# ---------------------------- App Config ----------------------------
APP_NAME=YourAppName
DEBUG=True

# ---------------------------- Database Config ----------------------------
# Format: postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/your_db_name

# ---------------------------- JWT Config ----------------------------
SECRET_KEY=your_super_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=1440

# ---------------------------- OAuth2 / Gmail Config ----------------------------
GMAIL_CLIENT_ID=your_google_client_id
GMAIL_CLIENT_SECRET=your_google_client_secret
GMAIL_REDIRECT_URI=http://localhost:8000/auth/google/callback

# ---------------------------- Redis Config ----------------------------
REDIS_URL=redis://localhost:6379/0

# ---------------------------- Celery Config ----------------------------
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

> **Note:** Replace all placeholders with your own credentials.  
> For `SECRET_KEY`, generate a strong random key using:  
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

---

## Installation

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

## Run the App

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

## Notes

- All credentials and secrets are loaded from `.env`  
- Use **Alembic** for database migrations  
- **Redis + Celery** are optional but recommended for async tasks and caching  
- OAuth2 setup requires Google credentials  
- JWT access and refresh tokens are handled in `core/security.py`  
- Redux manages global app state; React Query can be used for server-side async data caching  

---

## Testing

Run backend tests with:
```bash
pytest --cov=app tests/
```

---

## Deployment

- Recommended via Docker Compose
- Traefik can handle automatic HTTPS certificates
- Ensure `.env` secrets are set in production
