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
├── .env                     # Real environment (private, not committed)
├── .env.example             # Public config template
├── .gitignore               # Ignore rules
├── README.md                # Documentation

├── backend/                 # FastAPI backend
│   ├── main.py              # API entrypoint
│   ├── train_model.py       # Model training script
│   ├── requirements.txt     # Backend dependencies
│   ├── Dockerfile           # Backend Docker container spec
│   ├── core/
│   │   ├── config.py
│   │   └── logging_config.py
│   ├── api/
│   │   └── deps.py
│   ├── models/
│   │   └── __init__.py
│   ├── services/
│   │   ├── cache.py
│   │   └── cleaner.py
│   └── logs/
│       └── app.log
│
├── models/                  # Versioned model artifacts (timestamped folders)
│   └── <timestamp>/         # e.g. 2025-07-26T16-02-54
│       ├── sentiment_model.pkl
│       ├── tfidf_vectorizer.pkl
│       └── metrics.json
│
├── data/                    # Training datasets
│   ├── train.csv
│   └── (test.csv etc.)
│
├── frontend/                # Static PWA frontend
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   ├── manifest.json
│   ├── sw.js
│   └── icons/
│       ├── icon-192.png
│       └── icon-512.png
│
└── .github/
    └── workflows/
        └── ci.yml          # GitHub Actions workflow



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

## :bulb: Why InsightPulse?

- **Recruiter-ready:** Demonstrates full-stack AI/ML workflows, modularity, and production DevOps.
- **Cloud-native:** Containerized, scalable, and observable by design.
- **Learning-friendly:** Clean, documented, and extensible for your next project.

**Deploy, demo, and impress!**  
If you find this useful, give it a :star: or send feedback via issues.
