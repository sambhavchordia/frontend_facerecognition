## Face Recognition V2 – Project Report

### Overview
This project is a full‑stack face recognition attendance system:
- Backend: Flask API for authentication, student management, face registration, demo recognition, and attendance sessions using DeepFace (Facenet512), MTCNN, MongoDB, and NumPy/SciPy.
- Frontend: Next.js App Router (Next 15), React 19, TypeScript, TailwindCSS, and client‑side camera capture for live/demo recognition flows.
- Deployment: Config present for Vercel (frontend) and Procfile/Gunicorn runtime (backend), plus optional GitHub Pages static export basePath.
- Extras: Legacy `tkinter` sample requirements for desktop experiments.

### Technologies Used
- Frontend
  - Next.js 15 (App Router, `output: "export"`)
  - React 19, React DOM 19
  - TypeScript 5
  - TailwindCSS 4 (via `@tailwindcss/postcss` and `postcss.config.mjs`)
  - UI/UX: `framer-motion`, `lucide-react`
  - Client camera: `navigator.mediaDevices.getUserMedia` with `<video>` and canvas overlay
  - Build/Deploy: Vercel config (`vercel.json`), Next config for GitHub Pages basePath
  - Other: `xlsx` (export), `socket.io-client` (present as dependency; not referenced in sources scanned)

- Backend
  - Python 3.11.9 (via `runtime.txt`)
  - Flask, Flask‑CORS, Flask‑Bcrypt
  - MongoDB (`pymongo`)
  - Face AI: DeepFace (Facenet512), MTCNN, NumPy, SciPy
  - Image processing: Pillow, OpenCV (headless in requirements; interactive OpenCV used in a separate CLI script)
  - Config: `python-dotenv`
  - Server: Gunicorn (`Procfile`)

- Legacy/Desktop (experimental)
  - `legacy-tkinter/requirements.txt`: numpy, opencv, pandas, pillow, openpyxl, pyttsx3

### Deployment and Configuration
- Frontend
  - `frontend/next.config.ts`: static export, images unoptimized, conditional `basePath`/`assetPrefix` when `GITHUB_PAGES=true` for repo `face-recognition-system`.
  - `vercel.json`: build uses `@vercel/next` targeting `frontend/next.config.ts`.
  - `frontend/lib/config.ts`: API base URL from `NEXT_PUBLIC_API_BASE_URL` (defaults to `http://127.0.0.1:5000`).

- Backend
  - `backend/runtime.txt`: Python 3.11.9
  - `backend/Procfile`: `gunicorn app:app ... -b 0.0.0.0:$PORT`
  - `backend/requirements.txt`: all backend runtime deps
  - Environment: expects `MONGODB_URI`, `DATABASE_NAME`, `COLLECTION_NAME`, `THRESHOLD` (with sensible defaults)

### Folder Structure
```
face_recognitionV2/
  .github/workflows/gh-pages.yml                # CI for GitHub Pages (frontend static export)
  .gitignore                                   # Git ignore rules
  vercel.json                                  # Vercel build config for frontend
  PROJECT_REPORT.md                             # This report

  backend/
    app.py                                     # Flask app, model manager, blueprint registration, health
    Procfile                                   # Gunicorn process file
    requirements.txt                           # Backend Python dependencies
    runtime.txt                                # Python version
    check_attendance.py                        # Utility: DB listing and migration from old DB
    recognition.py                             # Standalone OpenCV CLI demo (webcam register/recognize)
    auth/
      routes.py                                # Signup/signin/logout/profile/switch-role endpoints
    student/
      __init__.py
      registration.py                          # Student registration + embedding pipeline
      updatedetails.py                         # Student CRUD (student/teacher role-based)
      demo_session.py                          # Demo recognition endpoints
      view_attendance.py                       # (Present in tree; contents not used in routes list if absent)
    teacher/
      __init__.py
      attendance_records.py                    # Attendance session create/end/mark + model status

  frontend/
    app/
      layout.tsx                               # Root layout
      page.tsx                                 # Landing
      globals.css                              # Global styles (Tailwind)
      favicon.ico
      signin/page.tsx                          # Sign-in UI
      signup/page.tsx                          # Sign-up UI
      dashboard/page.tsx                       # Student/teacher dashboard (front)
      student/
        demo-session/page.tsx                  # Student demo recognition page
        registrationform/page.tsx              # Registration form + 5‑image capture
        updatedetails/page.tsx                 # Update details flow
        updatedetails/page_old.tsx             # Older version retained
        view-attendance/page.tsx               # View attendance
      teacher/
        dashboard/page.tsx                     # Teacher dashboard
        start-session/page.tsx                 # Start session + live recognition UI
        updatedetails/page.tsx                 # Teacher update details
      components/
        CameraCapture.tsx                      # Live camera capture w/ face boxes overlay
        MultiCameraCapture.tsx                 # Guided 5‑photo capture workflow
        (About/Contact/Feature/Footer/Hero/Pricing/Testimonials/Work/Navbar)
    lib/config.ts                              # API base URL helper
    types/face-api.d.ts                        # Type declarations for face API library
    public/...                                 # Static assets
    next.config.ts                             # Next config (export/static settings)
    tsconfig.json                              # TypeScript config
    eslint.config.mjs, postcss.config.mjs      # Lint/build pipeline configs
    package.json, package-lock.json            # Frontend npm dependencies and lock

  legacy-tkinter/
    requirements.txt                           # Legacy desktop experiment deps
```

### Backend Architecture and Endpoints
- Application entry: `backend/app.py`
  - Loads environment, connects to MongoDB, configures Flask and CORS, initializes a singleton `ModelManager` to preload MTCNN and DeepFace (Facenet512) and expose health checks.
  - Registers blueprints: `auth`, `student.registration`, `student.updatedetails`, `student.demo_session`, `student.view_attendance` (if importable), and `teacher.attendance_records`.
  - Health: `GET /health` returns model readiness/health.

- Authentication (`backend/auth/routes.py`)
  - `POST /api/signup` – Student/Teacher registration with hashed password (bcrypt), role‑aware collections
  - `POST /api/signin` – Verify credentials; returns user info (includes role and, if present, student profile)
  - `POST /api/logout` – Placeholder logout
  - `GET /api/user/profile` – Fetch profile by `X-User-Email` and `X-User-Type`
  - `POST /api/switch-role` – Switch context if user has both roles

- Student registration (`backend/student/registration.py`)
  - `POST /api/register-student` – Validates details and exactly 5 images; detects single face via MTCNN per image; extracts embeddings via DeepFace; stores averaged embeddings per student
  - `GET /api/students/count` – Count students
  - `GET /api/students/departments` – Distinct departments

- Student CRUD and search (`backend/student/updatedetails.py`)
  - Student‑scoped CRUD with email‑based authorization:
    - `GET /api/students` – Current user’s record (student) with filters
    - `GET /api/students/<id>` – Fetch specific student with auth checks
    - `PUT /api/students/<id>` – Update student; students cannot change email; teachers can
    - `DELETE /api/students/<id>` – Delete record with role checks
  - Admin/Teacher endpoints:
    - `GET /api/admin/students` – List/filter all students
    - `GET /api/teacher/students/search` – Advanced search
    - `GET /api/teacher/student/<idOrDbId>` – Fetch by studentId or _id
    - `PUT /api/teacher/student/<dbId>` – Update any record
    - `DELETE /api/teacher/student/<dbId>` – Delete any record
  - Utilities:
    - `GET /api/students/search` – General search with auth limits
    - `GET /api/students/stats` – Aggregated stats (teacher/admin only)

- Demo recognition (`backend/student/demo_session.py`)
  - `POST /api/demo/recognize` – Accepts base64 image; detects faces (MTCNN), extracts embeddings (DeepFace), cosine match against cached student embeddings; returns matches and timing
  - `POST /api/demo/session` – Create a demo session doc
  - `POST /api/demo/session/<session_id>/log` – Log results
  - `GET /api/demo/models/status` – Model preload and health status

- Attendance sessions (`backend/teacher/attendance_records.py` – url_prefix `/api/attendance`)
  - `POST /api/attendance/create_session` – Create session, prefill student roster by filters (department/year/division)
  - `POST /api/attendance/real-mark` – Recognize faces and mark present; prevents duplicates; supports dynamic add if not prefilled
  - `POST /api/attendance/end_session` – Finalize session; mark absentees; return stats
  - `GET /api/attendance/models/status` – Health/model cache info

- Utilities
  - `backend/check_attendance.py` – Console utility to list both DBs and migrate old `attendance_records` into the primary DB
  - `backend/recognition.py` – Standalone webcam registration/recognition demo (OpenCV GUI)

### Frontend Architecture
- App Router pages under `frontend/app/`
  - Landing and marketing sections (`HeroSection`, `FeatureSection`, etc.) furnish the home page.
  - Auth: `app/signin/page.tsx`, `app/signup/page.tsx`
  - Student: registration (form + `MultiCameraCapture`), demo recognition, view attendance, update details
  - Teacher: dashboard, start session (`CameraCapture` live loop), teacher update details
  - `CameraCapture.tsx`: starts webcam, draws bounding boxes/names from server responses, periodically captures frames via canvas to JPEG base64 and posts to backend APIs.
  - `MultiCameraCapture.tsx`: guides 5 specific head poses and returns 5 JPEG base64 images for embedding generation.

- Configuration
  - API base: `NEXT_PUBLIC_API_BASE_URL` → defaults to `http://127.0.0.1:5000`
  - TypeScript path alias: `@/*` → project root
  - ESLint, PostCSS/Tailwind pipeline present

### Notable Design Choices
- Model warm‑up: The backend preloads MTCNN and DeepFace embeddings with dummy images to ensure first‑request latency is reduced.
- Embedding caching: Separate caches for demo and attendance flows to reduce DB reads and speed up matching.
- Role‑aware collections: `auth_users` vs `auth_teachers` plus a unified `students` collection.
- Duplicate prevention in attendance ensures one present mark per student per session.
- Static export for frontend enables GitHub Pages hosting; Vercel config also present.

### Environment Variables
- `MONGODB_URI` – MongoDB connection string (default: `mongodb://localhost:27017/`)
- `DATABASE_NAME` – Primary DB name (default: `facerecognition` in app config)
- `COLLECTION_NAME` – Students collection (default: `students`)
- `THRESHOLD` – Cosine distance threshold for recognition (default: `0.6`)
- Frontend: `NEXT_PUBLIC_API_BASE_URL` – Backend base URL for API calls

### File-by-File Highlights
- Backend
  - `backend/app.py`: Flask setup, model preload, config bindings, health, blueprint registration, run server.
  - `backend/auth/routes.py`: Signup/signin/logout/profile/switch‑role with bcrypt and MongoDB.
  - `backend/student/registration.py`: Validates student payload, ensures exactly one face per image, extracts DeepFace embeddings, stores embeddings list.
  - `backend/student/updatedetails.py`: Student/teacher role‑based CRUD, admin listing/search, aggregated stats.
  - `backend/student/demo_session.py`: Demo recognition endpoint with optimized image handling and embedding cache.
  - `backend/teacher/attendance_records.py`: Attendance sessions: create, mark (duplicate‑safe), end + stats; model health endpoint.
  - `backend/check_attendance.py`: Console migration helper between old/new DBs.
  - `backend/recognition.py`: CLI webcam demo using OpenCV, MTCNN, DeepFace, cosine metric.

- Frontend (selected)
  - `frontend/app/teacher/start-session/page.tsx`: UI to create attendance session and stream frames for live recognition/marking; overlays live results.
  - `frontend/app/student/registrationform/page.tsx`: Form validation + guided 5‑photo capture; posts to `/api/register-student`.
  - `frontend/app/components/CameraCapture.tsx`: Camera control and interval capture with canvas overlays from server face boxes.
  - `frontend/app/components/MultiCameraCapture.tsx`: Five guided captures (Front/Left/Right/Up/Down) and returns base64 images.
  - Other pages (`signin`, `signup`, `dashboard`, `student/*`, `teacher/*`) compose the UI and call backend endpoints as needed.
  - `frontend/next.config.ts`: static export and GitHub Pages basePath toggles.
  - `frontend/tsconfig.json`: strict TS, bundler resolution, path alias.
  - `frontend/package.json`: Next 15, React 19, Tailwind 4, ESLint 9, TypeScript 5, face‑api client, and UI libs.

### How to Run (local, high‑level)
- Backend
  1) Create `.env` with `MONGODB_URI`, `DATABASE_NAME`, `COLLECTION_NAME`, `THRESHOLD` (optional).
  2) `pip install -r backend/requirements.txt`
  3) `python backend/app.py` (for development) or `cd backend && gunicorn app:app -b 0.0.0.0:5000`.

- Frontend
  1) `cd frontend`
  2) `npm install`
  3) `npm run dev`
  4) Ensure `NEXT_PUBLIC_API_BASE_URL` points to backend (default `http://127.0.0.1:5000`).

### Potential Improvements
- Add rate limiting/auth tokens for sensitive endpoints.
- Persist session/user context with proper auth (JWT/NextAuth) rather than localStorage flags.
- Add unit/integration tests for recognition pipeline and REST endpoints.
- Centralize config (env schema validation, 12‑factor).
- Containerize with Docker for consistent deployment.


