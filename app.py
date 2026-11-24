from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3, requests, os, re, json, unicodedata
from datetime import datetime, date
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / 'nutriscan.db'
OFF_URL = 'https://world.openfoodfacts.org/api/v2/product/{barcode}.json'
app = Flask(__name__, static_folder='frontend', static_url_path='')
app.secret_key = os.getenv('SECRET_KEY', 'change-this-secret-key-before-deployment')
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS profiles (
          user_id INTEGER PRIMARY KEY, age INTEGER, height_cm REAL, weight_kg REAL, activity TEXT DEFAULT 'Moderate', diet TEXT DEFAULT 'Not specified',
          allergies TEXT DEFAULT '', conditions TEXT DEFAULT '', goal TEXT DEFAULT 'Balanced nutrition',
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS scans (
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, barcode TEXT NOT NULL,
          product_name TEXT NOT NULL, brand TEXT, image TEXT, weight_g REAL NOT NULL,
          nutrition_json TEXT NOT NULL, portion_unit TEXT NOT NULL DEFAULT 'g', scanned_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        ''')
        scan_cols={r['name'] for r in con.execute('PRAGMA table_info(scans)').fetchall()}
        if 'portion_unit' not in scan_cols: con.execute("ALTER TABLE scans ADD COLUMN portion_unit TEXT NOT NULL DEFAULT 'g'")
        cols={r['name'] for r in con.execute('PRAGMA table_info(profiles)').fetchall()}
        for col,decl in [('height_cm','REAL'),('weight_kg','REAL'),('activity',"TEXT DEFAULT 'Moderate'")]:
            if col not in cols: con.execute(f'ALTER TABLE profiles ADD COLUMN {col} {decl}')


def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'error': 'Please sign in to continue.'}), 401
        return fn(*args, **kwargs)
    return wrapped


@app.get('/')
def home():
    return send_from_directory('frontend', 'index.html')

@app.get('/api/health')
def health():
    return jsonify({'status': 'ok', 'app': 'NutriScan AI Pro'})

@app.post('/api/register')
def register():
    data = request.get_json(silent=True) or {}
    name, email, password = (str(data.get(k, '')).strip() for k in ('name','email','password'))
    if len(name) < 2 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email) or len(password) < 8:
        return jsonify({'error': 'Enter a name, valid email and password with at least 8 characters.'}), 400
    try:
        with db() as con:
            cur = con.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)', (name,email.lower(),generate_password_hash(password)))
            uid = cur.lastrowid
            con.execute('INSERT INTO profiles(user_id) VALUES(?)', (uid,))
        session['user_id'] = uid
        session['user_name'] = name
        return jsonify({'user': {'name': name, 'email': email.lower()}}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'An account with this email already exists. Please sign in.'}), 409

@app.post('/api/login')
def login():
    data = request.get_json(silent=True) or {}
    email, password = str(data.get('email','')).strip().lower(), str(data.get('password',''))
    with db() as con:
        user = con.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Incorrect email or password.'}), 401
    session.clear(); session['user_id'] = user['id']; session['user_name'] = user['name']
    return jsonify({'user': {'name': user['name'], 'email': user['email']}})

@app.post('/api/logout')
def logout():
    session.clear(); return jsonify({'ok': True})

@app.get('/api/me')
@login_required
def me():
    with db() as con:
        u = con.execute('SELECT name,email FROM users WHERE id=?', (session['user_id'],)).fetchone()
    return jsonify({'user': dict(u)})

@app.get('/api/profile')
@login_required
def get_profile():
    with db() as con:
        row = con.execute('SELECT age,height_cm,weight_kg,activity,diet,allergies,conditions,goal FROM profiles WHERE user_id=?', (session['user_id'],)).fetchone()
    return jsonify(dict(row) if row else {})

@app.put('/api/profile')
@login_required
def save_profile():
    d = request.get_json(silent=True) or {}
    age = d.get('age')
    try: age = int(age) if age not in (None,'') else None
    except (TypeError,ValueError): return jsonify({'error':'Age must be a number.'}),400
    if age is not None and not 1 <= age <= 120: return jsonify({'error':'Enter a valid age.'}),400
    def number(key, lo, hi):
        v=d.get(key)
        if v in (None, ''): return None
        try: v=float(v)
        except (TypeError, ValueError): raise ValueError(key)
        if not lo <= v <= hi: raise ValueError(key)
        return v
    try:
        height=number('height_cm',50,250); weight=number('weight_kg',2,400)
    except ValueError as e:
        return jsonify({'error':'Enter a valid '+e.args[0].replace('_',' ')+'.'}),400
    with db() as con:
        con.execute('''INSERT INTO profiles(user_id,age,height_cm,weight_kg,activity,diet,allergies,conditions,goal) VALUES(?,?,?,?,?,?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET age=excluded.age,height_cm=excluded.height_cm,weight_kg=excluded.weight_kg,activity=excluded.activity,diet=excluded.diet,allergies=excluded.allergies,conditions=excluded.conditions,goal=excluded.goal''',
        (session['user_id'],age,height,weight,str(d.get('activity','Moderate')),str(d.get('diet','Not specified')),str(d.get('allergies','')),str(d.get('conditions','')),str(d.get('goal','Balanced nutrition'))))
    return jsonify({'ok':True})

def get_profile_for_current_user():
    uid=session.get('user_id')
    if not uid: return {}
    with db() as con:
        row=con.execute('SELECT age,height_cm,weight_kg,activity,diet,allergies,conditions,goal FROM profiles WHERE user_id=?',(uid,)).fetchone()
    return dict(row) if row else {}


def ingredient_screen(ingredients, allergens, profile=None):
    """Transparent ingredient-term screening; this is not a toxicity test."""
    profile=profile or {}
    path=BASE/'datasets'/'ingredient_screening_122.json'
    data=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'records':[]}
    normalized=re.sub(r'\s+',' ',unicodedata.normalize('NFKC',(ingredients or '').lower()))
    hits=[]
    for item in data['records']:
        term=item['name'].lower()
        if len(term)>1 and re.search(r'(?<![a-z0-9])'+re.escape(term)+r'(?![a-z0-9])',normalized): hits.append(item)
    allergen_text=(allergens or '').lower()
    allergies=[x.strip().lower() for x in str(profile.get('allergies') or '').split(',') if x.strip()]
    allergy_hits=[a for a in allergies if a in allergen_text or a in normalized]
    message=('Potential profile allergy match: '+', '.join(allergy_hits)+'. Verify the physical label and seek qualified allergy advice before consuming.') if allergy_hits else ('Ingredient terms matched the screening dictionary. Review each note; a match does not mean the product is toxic.') if hits else ('No screening terms matched. This is not proof of safety.') if ingredients else 'Ingredient declaration unavailable. Safety cannot be assessed from this barcode record.'
    return {'dictionary_size':len(data.get('records',[])),'matched_count':len(hits),'matches':hits[:30],'user_allergy_matches':allergy_hits,'ingredient_data_available':bool(ingredients),'status':'review' if hits or allergy_hits else ('unknown' if not ingredients else 'no_match'),'message':message}


def normalize_off_product(p, barcode=None):
    """Normalize an Open Food Facts product for both barcode and name search."""
    n = p.get('nutriments') or {}
    category_text = ' '.join([
        str(p.get('categories') or ''), str(p.get('product_name') or ''),
        str(p.get('quantity') or ''), *map(str, p.get('categories_tags') or [])
    ]).lower()
    is_drink = bool(re.search(
        r'\b(beverage|drink|juice|water|milk|soda|cola|coffee|tea|nectar|smoothie|shake|lassi|buttermilk)\b',
        category_text
    )) or bool(re.search(
        r'\b\d+(?:\.\d+)?\s*(?:ml|cl|liters?|litres?)\b',
        str(p.get('quantity') or '').lower()
    ))
    suffix = '100ml' if is_drink else '100g'

    def val(*keys):
        for key in keys:
            try:
                if n.get(key) is not None:
                    return float(n[key])
            except (TypeError, ValueError):
                pass
        return None

    def nutrient(base, *fallback):
        return val(base + '_' + suffix, *fallback)

    salt = nutrient('salt', 'salt_100g', 'salt_100ml')
    sodium = nutrient('sodium', 'sodium_100g', 'sodium_100ml')
    if sodium is None and salt is not None:
        sodium = salt * 393.4

    return {
        'barcode': str(barcode or p.get('code') or ''),
        'name': p.get('product_name') or p.get('product_name_en') or 'Unnamed product',
        'brand': p.get('brands') or 'Brand not listed',
        'image': p.get('image_url') or p.get('image_front_url'),
        'quantity': p.get('quantity'), 'serving_size': p.get('serving_size'),
        'categories': p.get('categories') or '',
        'categories_tags': p.get('categories_tags') or [],
        'food_groups_tags': p.get('food_groups_tags') or [],
        'product_type': 'beverage' if is_drink else ('food' if p.get('categories') or p.get('categories_tags') else 'unknown'),
        'ingredients': p.get('ingredients_text') or p.get('ingredients_text_en'),
        'allergens': p.get('allergens') or p.get('allergens_tags'),
        'per_100g': {
            'energy_kcal': nutrient('energy-kcal', 'energy-kcal_value', 'energy-kcal_100g', 'energy-kcal_100ml'),
            'fat_g': nutrient('fat', 'fat_100g', 'fat_100ml'),
            'saturated_fat_g': nutrient('saturated-fat', 'saturated-fat_100g', 'saturated-fat_100ml'),
            'carbohydrates_g': nutrient('carbohydrates', 'carbohydrates_100g', 'carbohydrates_100ml'),
            'sugars_g': nutrient('sugars', 'sugars_100g', 'sugars_100ml'),
            'fiber_g': nutrient('fiber', 'fiber_100g', 'fiber_100ml'),
            'protein_g': nutrient('proteins', 'proteins_100g', 'proteins_100ml'),
            'salt_g': salt, 'sodium_mg': sodium
        },
        'ingredient_screening': ingredient_screen(
            p.get('ingredients_text') or p.get('ingredients_text_en'),
            p.get('allergens'), get_profile_for_current_user()
        ),
        'source': 'Open Food Facts',
        'source_note': 'Community-contributed data. Verify the physical package. Nutrients are per 100 ' + ('ml' if is_drink else 'g') + '.'
    }


OFF_FIELDS = 'code,product_name,product_name_en,brands,image_url,image_front_url,ingredients_text,ingredients_text_en,allergens,nutriments,quantity,serving_size,categories,categories_tags,food_groups_tags'
OFF_HEADERS = {'User-Agent': 'NutriScanAI/1.1 (student project; product lookup)'}


@app.get('/api/product/<barcode>')
def product(barcode):
    if not barcode.isdigit() or not (8 <= len(barcode) <= 14):
        return jsonify({'error': 'Enter a valid 8–14 digit barcode.'}), 400
    try:
        r = requests.get(OFF_URL.format(barcode=barcode), params={'fields': OFF_FIELDS}, headers=OFF_HEADERS, timeout=20)
        if r.status_code == 404:
            return jsonify({'error': 'Barcode not found in Open Food Facts.'}), 404
        r.raise_for_status()
        payload = r.json()
    except requests.Timeout:
        return jsonify({'error': 'Product lookup timed out. Check your internet connection and try again.'}), 504
    except requests.RequestException:
        return jsonify({'error': 'Open Food Facts is temporarily unavailable. Please retry or search by product name.'}), 503
    except ValueError:
        return jsonify({'error': 'The product database returned an unreadable response. Please retry.'}), 502
    if payload.get('status') != 1 or not payload.get('product'):
        return jsonify({'error': 'Barcode not listed in Open Food Facts.'}), 404
    return jsonify(normalize_off_product(payload['product'], barcode))


@app.get('/api/product-search')
def product_search():
    """Search Open Food Facts by product name; return explicit candidates only."""
    query = str(request.args.get('q', '')).strip()
    if len(query) < 2:
        return jsonify({'error': 'Enter at least 2 characters to search.'}), 400
    if len(query) > 100:
        return jsonify({'error': 'Search text is too long.'}), 400

    endpoints = [
        ('https://world.openfoodfacts.org/cgi/search.pl', {
            'search_terms': query, 'search_simple': 1, 'action': 'process',
            'json': 1, 'page_size': 12, 'fields': OFF_FIELDS
        }),
        ('https://world.openfoodfacts.org/api/v2/search', {
            'search_terms': query, 'page_size': 12, 'fields': OFF_FIELDS
        })
    ]
    last_error = None
    for url, params in endpoints:
        try:
            response = requests.get(url, params=params, headers=OFF_HEADERS, timeout=15)
            if response.status_code == 404:
                continue
            response.raise_for_status()
            payload = response.json()
            raw_products = payload.get('products') or []
            results, seen = [], set()
            for item in raw_products:
                name = str(item.get('product_name') or item.get('product_name_en') or '').strip()
                if not name:
                    continue
                code = str(item.get('code') or '').strip()
                key = code or (name.lower() + '|' + str(item.get('brands') or '').lower())
                if key in seen:
                    continue
                seen.add(key)
                results.append(normalize_off_product(item, code))
                if len(results) >= 10:
                    break
            if results:
                return jsonify({'query': query, 'count': len(results), 'results': results, 'source': 'Open Food Facts'})
        except requests.Timeout:
            last_error = 'Product search timed out. Please try again.'
        except (requests.RequestException, ValueError):
            last_error = 'Product search is temporarily unavailable. Please try again.'
    if last_error:
        return jsonify({'error': last_error}), 503
    return jsonify({'query': query, 'count': 0, 'results': [], 'source': 'Open Food Facts'})

@app.get('/api/ingredient-dictionary')
def ingredient_dictionary():
    data=json.loads((BASE/'datasets'/'ingredient_screening_122.json').read_text(encoding='utf-8'))
    return jsonify({'count':data['record_count'],'note':data['important_note'],'categories':{k:sum(1 for x in data['records'] if x['category']==k) for k in sorted({x['category'] for x in data['records']})}})

@app.post('/api/ingredient-screen')
def screen_ingredients_api():
    d=request.get_json(silent=True) or {}
    return jsonify(ingredient_screen(str(d.get('ingredients','')),str(d.get('allergens','')),get_profile_for_current_user()))

@app.post('/api/scans')
@login_required
def save_scan():
    import json
    d=request.get_json(silent=True) or {}; p=d.get('product') or {}; weight=d.get('amount', d.get('weight_g')); unit=str(d.get('unit','g')).lower()
    if unit not in ('g','ml'): return jsonify({'error':'Portion unit must be grams (g) or millilitres (ml).'}),400
    try: weight=float(weight)
    except (TypeError,ValueError): return jsonify({'error':'Enter food weight in grams.'}),400
    if not 0 < weight <= 5000: return jsonify({'error':'Weight must be between 0 and 5000 grams.'}),400
    if not p.get('barcode') or not isinstance(p.get('per_100g'),dict): return jsonify({'error':'A valid product is required.'}),400
    with db() as con:
        cur=con.execute('INSERT INTO scans(user_id,barcode,product_name,brand,image,weight_g,nutrition_json,portion_unit,scanned_at) VALUES(?,?,?,?,?,?,?,?,?)',
        (session['user_id'],str(p['barcode']),str(p.get('name','Unnamed product')),str(p.get('brand','')),p.get('image'),weight,json.dumps(p.get('per_100g',{})),unit,datetime.now().isoformat(timespec='seconds')))
    return jsonify({'id':cur.lastrowid,'ok':True}),201

@app.get('/api/history')
@login_required
def history():
    import json
    with db() as con: rows=con.execute('SELECT * FROM scans WHERE user_id=? ORDER BY scanned_at DESC LIMIT 200',(session['user_id'],)).fetchall()
    return jsonify({'scans':[{'id':r['id'],'barcode':r['barcode'],'name':r['product_name'],'brand':r['brand'],'image':r['image'],'weight_g':r['weight_g'],'portion_unit':r['portion_unit'],'nutrition':json.loads(r['nutrition_json']),'scanned_at':r['scanned_at']} for r in rows]})

@app.delete('/api/history/<int:scan_id>')
@login_required
def delete_scan(scan_id):
    with db() as con: cur=con.execute('DELETE FROM scans WHERE id=? AND user_id=?',(scan_id,session['user_id']))
    if not cur.rowcount: return jsonify({'error':'Scan not found.'}),404
    return jsonify({'ok':True})

@app.delete('/api/history')
@login_required
def clear_history():
    with db() as con: con.execute('DELETE FROM scans WHERE user_id=?',(session['user_id'],))
    return jsonify({'ok':True})

@app.get('/api/dashboard')
@login_required
def dashboard():
    import json
    uid=session['user_id']; today=date.today().isoformat()
    with db() as con:
        total=con.execute('SELECT COUNT(*) n FROM scans WHERE user_id=?',(uid,)).fetchone()['n']
        rows=con.execute('SELECT * FROM scans WHERE user_id=? AND substr(scanned_at,1,10)=? ORDER BY scanned_at DESC',(uid,today)).fetchall()
        recent=con.execute('SELECT id,product_name,brand,weight_g,portion_unit,scanned_at FROM scans WHERE user_id=? ORDER BY scanned_at DESC LIMIT 5',(uid,)).fetchall()
    totals={k:0.0 for k in ['energy_kcal','protein_g','carbohydrates_g','fat_g']}; available={k:False for k in totals}
    for r in rows:
        n=json.loads(r['nutrition_json']); factor=r['weight_g']/100
        for k in totals:
            if n.get(k) is not None: totals[k]+=float(n[k])*factor; available[k]=True
    return jsonify({'total_scans':total,'today_scans':len(rows),'today':{k:(round(v,1) if available[k] else None) for k,v in totals.items()},'recent':[dict(x) for x in recent]})

if __name__=='__main__':
    init_db(); app.run(host='127.0.0.1',port=5000,debug=True)
else:
    init_db()
