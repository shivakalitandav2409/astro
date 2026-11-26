# ASTRO — Explore the Cosmos & Destiny

**Developed by Shivang Saxena**

A unified Vedic & Lal Kitab astrology platform combining **GDVPanel** (Acharya SaaS workspace, courses, CRM, and PDF reports) with **AstroScience** (horoscope suite, Swiss Ephemeris Kundli, Dashas, 36-point Ashtakoot Matchmaking, Panchang, and Remedies Store).

## Tech Stack
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons (`frontend/`)
- **Backend**: FastAPI, Python 3.12+, Swiss Ephemeris (`pyswisseph` with Lahiri Ayanamsa), SQLite, FPDF2 (`backend/`)

## Deploying Frontend to Cloudflare Pages
1. Connect this GitHub repository (`shivakalitandav2409/astro`) in the **Cloudflare Dashboard → Workers & Pages → Create → Pages → Connect to Git**.
2. Use the following build settings:
   - **Framework preset**: `Vite` (or `None`)
   - **Root directory**: `frontend`
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
3. *(Optional)* Add an environment variable `VITE_API_BASE` pointing to your hosted FastAPI backend URL (e.g. `https://your-api-host.com`) so API calls route to the live astronomical engine.
4. `frontend/public/_redirects` (`/* /index.html 200`) is included so all React Router routes work seamlessly on Cloudflare Pages.

## Local Development
```bash
# 1. Start Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn pyswisseph fpdf2 pydantic
cd ..
PYTHONPATH=. backend/.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000

# 2. Build or Run Frontend
cd frontend
npm install
npm run build   # or npm run dev
```
