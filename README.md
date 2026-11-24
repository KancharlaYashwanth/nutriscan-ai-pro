# NutriScan AI Pro

A polished Flask-based food intelligence student project with account authentication, personal profiles, Open Food Facts barcode lookup, manual/camera scanning, portion-weight nutrition calculations and a per-user food journal.

## Features included
- Registration, login and logout with Werkzeug password hashing and Flask sessions.
- SQLite database for users, profiles and each user's scan history.
- Responsive dark editorial dashboard with nutrition summary, recent scans and visual macro bars.
- Barcode lookup through Open Food Facts; manual entry and optional camera scanning (camera library is loaded from a CDN and needs internet access).
- Portion input in grams, quick portion buttons and live calculations from per-100 g product data.
- Ingredients and declared allergen display, profile-aware educational notes.
- Search history, delete one scan, clear all history, and daily intake totals based on saved portions.

## Run on Windows PowerShell
Use Python 3.11 or 3.12 if possible.

```powershell
cd path\to\NutriScan-AI-Pro
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. Create an account from the welcome page.

## Important setup and limitations
- SQLite database `nutriscan.db` is created automatically in the project folder. Keep it private and back it up.
- Set a strong `SECRET_KEY` environment variable before deployment. The built-in development key is not suitable for production.
- The camera scanner requires browser camera permission and a secure context (localhost is supported). If the CDN is unavailable, manual barcode entry still works.
- Product lookup needs internet access. Open Food Facts data is community-contributed and may be missing or inaccurate.
- Missing nutrient values remain unavailable; they are not silently treated as zero.
- The profile warnings are simple educational flags, not a medically validated recommendation engine. The app cannot guarantee allergen safety or diagnose/treat health conditions.
- This version does not claim to implement trained PyTorch models, OCR, an AI chatbot, medical validation or PDF export. Those are future modules.

## Main routes
`/api/register`, `/api/login`, `/api/logout`, `/api/me`, `/api/profile`, `/api/product/<barcode>`, `/api/scans`, `/api/history`, `/api/dashboard`.


## Pro upgrade notes
- Added `datasets/ingredient_screening_122.json`, a 122-term ingredient screening vocabulary. It is not a list of 122 toxic ingredients.
- Barcode lookup now returns screening matches and checks declared user allergy terms when signed in. Missing ingredient data is treated as unknown.
- Profile supports height, weight and activity level.
- Added local-food photo capture with user-confirmed food category and generic per-100 g estimates. This is not yet a trained image-recognition model.
- Refreshed the UI with layered aurora gradients, glass-like cards and stronger visual contrast.

### Windows setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. Camera access works on localhost or HTTPS.


## Consumption decision and portion guide
The scanner now presents a transparent rule-based **YES / NO / UNKNOWN** screening result. It distinguishes likely beverages (ml) from solid foods (g), uses a listed serving size when a compatible unit is available, and otherwise shows a generic starting serving guide (200 ml for beverages or 30 g for solids). The user can adjust the amount and the nutrition panel scales per-100 g/ml values accordingly. Portion unit is saved with each journal entry.

A **NO** result is used for a possible match against an allergy saved in the profile or declared allergen data. **UNKNOWN** is shown when key product information is missing. A **YES** result means only that no saved-allergy match was found and sufficient label fields were returned; it is not a medical clearance or a guarantee of safety. High sugar/sodium flags are informational and do not alone establish that a food is unsafe. Recommendations are educational portion guides, not personalized medical prescriptions. Verify packaging and consult a qualified professional for medical dietary needs.


## Consumption decision engine update
See `documentation/CONSUMPTION_DECISION_ENGINE.md` for the EDIBLE / NOT EDIBLE and DRINKABLE / NOT DRINKABLE screening logic, portion estimation, profile use and limitations. Existing profile fields and account data are preserved.
