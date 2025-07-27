# InsightPulse: AI-powered Sentiment Analysis Web Application

## :rocket: Overview

**InsightPulse** is a **production-ready, full-stack web application** for real-time sentiment analysis using machine learning. It combines a **FastAPI backend**, **state-of-the-art NLP preprocessing**, **JWT authentication**, **Redis caching**, **MongoDB persistence**, and a **modern, installable PWA frontend**—delivering an **industry-grade pipeline** from text input to visualized sentiment, ready for both demo and scaled deployment.

**Ideal for:**  
Recruiters, technical stakeholders, and developers seeking a **clear, maintainable, and cloud-native AI/ML project** with security, observability, and DevOps best practices.

---

## :mag: Features

- **Real-time sentiment analysis** – Submit text, get instant sentiment (positive/negative/neutral) and confidence scores.
- **Modern, responsive UI** – Dark/light theme, real-time charts, installable PWA (works offline).
- **Secure API** – JWT authentication, rate limiting, and CORS management.
- **ML Ops** – Train, version, and export models with full metrics tracking and reproducibility.
- **Caching** – Redis-backed result caching for performance at scale.
- **Structured logging** – Centralized, rotating logs for debugging and audit.
- **Modular, typed, and documented** – Clean separation of concerns, type hints, and docstrings throughout.
- **CI/CD** – GitHub Actions for linting, testing, and Docker builds.
- **Dockerized** – Ready for deployment on any cloud or PaaS.

---

## :open_file_folder: Project Structure

InsightPulse/
│
├── .env                        # Environment variables (never committed)
├── .env.example                # Example env file (for onboarding)
├── .gitignore                  # Files to exclude from version control
├── README.md                   # Project docs, setup, usage, logging overview
│
├── backend/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── requirements.txt        # Python dependencies (prod-ready)
│   ├── Dockerfile              # Container build definition (multi-stage, secure)
│   ├── logging_config.py       # Centralized, structured logging config
│   │
│   ├── core/
│   │   ├── config.py           # Settings and environment management
│   │   └── (your custom modules)
│   │
│   ├── api/
│   │   ├── deps.py             # Authentication, rate-limiting, dependencies
│   │   └── (future endpoints)
│   │
│   ├── models/
│   │   └── __init__.py         # ML model loader, versioning, health checks
│   │
│   ├── services/
│   │   ├── cache.py            # Redis-backed caching
│   │   └── cleaner.py          # Text preprocessing/NLP cleaning
│   │
│   ├── train_model.py          # ML training, evaluation, and export pipeline
│   │
│   └── (future: test/)         # Unit/integration tests
│
├── frontend/
│   ├── index.html              # Main app HTML
│   ├── style.css               # Stylesheet (themes, responsive)
│   ├── script.js               # All client-side logic
│   ├── manifest.json           # PWA configuration
│   ├── sw.js                   # Service Worker (offline/PWA)
│   └── icons/
│       ├── icon-192.png        # App icon
│       └── icon-512.png        # App icon
│
├── models/                     # All trained model versions
│   ├── 2025-07-23T18-30-00/    # Example timestamped model folder
│   │   ├── tfidf_vectorizer.pkl
│   │   ├── sentiment_model.pkl
│   │   └── metrics.json
│   └── ...                     # More model versions
│
├── logs/                       # Application logs
│   └── app.log                 # Rotating, structured logs (auto-created)
│
└── .github/
    └── workflows/
        └── ci.yml              # GitHub Actions CI/CD pipeline



---

## :wrench: Quick Start

### **1. Prerequisites**
- **Python 3.12+**
- **Docker** (for backend services and deployment)
- **MongoDB** and **Redis** (local or Docker)
- **Node.js/NPM** (optional, for advanced frontend tooling)

### **2. Clone & Setup**

### **3. Backend**
**API docs:** `http://localhost:8000/docs`

### **4. Frontend**
Open `http://localhost:8080` in your browser.

### **5. Train the Model**

### **6. Docker**

---

## :zap: Usage

- **Web UI:**  
  Open `http://localhost:8080`, log in (demo: `user` / `password`), and analyze text.
- **API:**  
  Authenticate at `/auth/login`, then POST text to `/analyze` for sentiment.
- **Admin:**  
  Access `/health`, `/readiness`, and `/liveness` for operational checks.
- **Developers:**  
  The backend is modular, typed, and tested—ready for your extensions.

---

## :lock: Security & Observability

- **JWT authentication** with bcrypt password hashing.
- **Environment-based secrets** (`.env` never committed).
- **Structured, rotating logs** (`logs/app.log`) with request correlation.
- **Rate-limited API** to prevent abuse.
- **Non-root container user** for Docker deployments.

---

## :arrows_clockwise: CI/CD

- **GitHub Actions** automates linting, testing, and Docker builds on every push.
- **Ready for Kubernetes, Render, fly.io, or any cloud**—just set your secrets and go.

---

## :handshake: Contributing

1. **Fork** the repository.
2. **Branch** for your feature (`git checkout -b feature/your-feature`).
3. **Commit** your changes (`git commit -am 'Add some feature'`).
4. **Push** to the branch (`git push origin feature/your-feature`).
5. **Open a Pull Request** with a clear description.

---

## :page_with_curl: License

MIT License. See `LICENSE` for details.

---

## :bulb: Why InsightPulse?

- **Recruiter-ready:** Demonstrates full-stack AI/ML workflows, modularity, and production DevOps.
- **Cloud-native:** Containerized, scalable, and observable by design.
- **Learning-friendly:** Clean, documented, and extensible for your next project.

**Deploy, demo, and impress!**  
If you find this useful, give it a :star: or send feedback via issues.
