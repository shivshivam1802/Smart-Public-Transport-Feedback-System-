# Run Smart Transport Feedback (Local)

## 1. Open terminal in project folder

```bash
cd c:\Users\Shivam\Downloads\smart-transport-feedback
```

(Use your actual project path if different.)

---

## 2. Create and activate virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in the prompt.

---

## 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

---

## 4. Start the server

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Wait until you see: `Uvicorn running on http://127.0.0.1:8000`

---

## 5. URLs to open in browser

| What | URL |
|------|-----|
| **API docs (Swagger)** | http://127.0.0.1:8000/docs |
| **Demo home** | http://127.0.0.1:8000/demo |
| **Dashboard** | http://127.0.0.1:8000/demo/dashboard |
| **Submit feedback** | http://127.0.0.1:8000/demo/submit |
| **API info (JSON)** | http://127.0.0.1:8000/api |
| **Root** | http://127.0.0.1:8000/ |

Use these from the same machine where the server is running. Replace `8000` with your port if you changed it.

---

## 6. Common errors and fixes

**Port 8000 already in use**

- Use another port:
  ```bash
  python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
  ```
- Then open: http://127.0.0.1:8001/docs

**`uvicorn: command not found`**

- Run via Python:
  ```bash
  python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
  ```

**`No module named 'fastapi'` (or similar)**

- Activate the venv (step 2), then:
  ```bash
  pip install -r backend/requirements.txt
  ```

**PowerShell: "running scripts is disabled"**

- Allow scripts for this session:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
  ```
- Then run again: `.venv\Scripts\Activate.ps1`

**Wrong directory / app not found**

- Ensure you are in the project root (where `backend` and `demo` folders are), then run the uvicorn command again.

---

## 7. Quick checklist

- [ ] Terminal in project folder  
- [ ] Virtual environment created and activated  
- [ ] `pip install -r backend/requirements.txt` done  
- [ ] `python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000` running  
- [ ] Open http://127.0.0.1:8000/docs to test APIs (Swagger UI)
