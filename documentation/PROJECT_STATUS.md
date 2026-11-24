# Implementation status — NutriScan AI Pro

## Implemented in this build
- [x] Flask application and responsive premium dashboard UI
- [x] Registration, login and logout with hashed passwords
- [x] SQLite users, profiles and per-user scan records
- [x] Open Food Facts barcode product lookup
- [x] Manual barcode entry and optional browser camera scanner
- [x] Manual portion weight input in grams with live per-portion nutrition calculation
- [x] Nutrition dashboard totals from saved scan weights
- [x] Recent scans, searchable history, individual deletion and clear-history action
- [x] Profile preferences and simple educational flags
- [x] Missing nutrient values remain unavailable

## Planned / not implemented
- [ ] OCR extraction from uploaded nutrition labels
- [ ] Trained CNN / PyTorch model
- [ ] BERT fine-tuning or validated ingredient classifier
- [ ] AI nutrition assistant backed by a language model
- [ ] Healthier alternatives recommendation engine
- [ ] Product comparison workspace
- [ ] PDF nutrition report export
- [ ] Production deployment hardening, CSRF protection, rate limiting and database migration strategy

The app is an educational student project. It is not medical advice and cannot guarantee allergen safety.
