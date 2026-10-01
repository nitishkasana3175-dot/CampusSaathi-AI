# CampusSaathi AI 🎓

An AI-powered university FAQ chatbot for ABES Engineering College built with React, Node.js/Express, Python/FastAPI, Google Gemini, FAISS, and Supabase.

---

## 🔑 Required Environment Variables

Create `.env` files in `server/`, `client/`, and `rag/api/` based on `.env.example`:

- **Client (`client/.env`)**:
  ```env
  VITE_BACKEND_URL=http://localhost:5000
  ```
- **Server (`server/.env`)**:
  ```env
  PORT=5000
  RAG_API_URL=http://localhost:8000
  ```
- **RAG Service (`rag/api/.env`)**:
  ```env
  GEMINI_API_KEY=your_google_gemini_api_key_here
  ```

---

## 🚀 Exact Commands to Start All Services Locally

Open 3 terminal windows in `C:\Users\Nitish Kasana\Desktop\CampusSaathi-AI`:

### Terminal 1: Python FastAPI RAG Service (Port 8000)
```powershell
cd rag/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
*Automatically loads and indexes `rag/data/ABES_FAQ.pdf` on startup.*

### Terminal 2: Node.js Express Backend (Port 5000)
```powershell
cd server
npm start
```
*Health endpoint available at `http://localhost:5000/api/health`.*

### Terminal 3: React Vite Client (Port 5173)
```powershell
cd client
npm run dev
```
*Open `http://localhost:5173` in your browser.*

---

## 📁 Repository Structure

```
CampusSaathi-AI/
├── client/              # React + Vite Frontend (Blue & White Theme)
├── server/              # Node.js + Express Backend API
├── rag/
│   ├── data/
│   │   └── ABES_FAQ.pdf # Official ABES FAQ PDF Document
│   ├── colab/           # CampusSaathi_RAG.ipynb (Colab RAG pipeline)
│   └── api/             # FastAPI RAG Service (main.py, requirements.txt)
├── docs/                # Architecture diagram & Supabase PostgreSQL Schema
├── .gitignore
└── README.md
```

---

## 🧪 Testing & Verification

- **FastAPI Health Check**: `GET http://localhost:8000/health`
- **Node Backend Health Check**: `GET http://localhost:5000/api/health`
- **End-to-End Chat Test**: Send question from the React Chat UI or POST to `http://localhost:5000/api/chat` with `{ "message": "What is the fee structure?" }`.

---

## 📋 RESUME CHECKLIST

- [x] Indexed `rag/data/ABES_FAQ.pdf` in FastAPI RAG service.
- [x] Connected Node backend to FastAPI service (`RAG_API_URL`).
- [x] Connected React UI to Node backend (`/api/chat`).
- [x] Configured Gemini grounding & fallback message when info is missing from PDF.
- [x] Verified build and health tests.
