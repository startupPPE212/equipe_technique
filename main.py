from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.responses import StreamingResponse
import plotly.express as px
import pandas as pd
from collections import defaultdict
import csv
import matplotlib.pyplot as plt
import io
import base64
from fastapi.responses import HTMLResponse
from io import StringIO
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np
from .database import SessionLocal, get_db
from .database import engine, SessionLocal
from .models import Base, Vente, VenteItem, Stock
from fastapi import Form
from sqlalchemy import func
from collections import defaultdict
from datetime import datetime, timedelta
from collections import defaultdict
from sklearn.linear_model import LogisticRegression 
from .models import Vente
import os
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Depends
from fastapi import HTTPException
import secrets
import hashlib  
from .models import User
from .migrate import run_migrations
from .auth import router as auth_router
from .client_routes import router as client_router
from .fournisseur_routes import router as fournisseur_router

app = FastAPI()

Base.metadata.create_all(bind=engine)
run_migrations(engine)

app.include_router(auth_router)
app.include_router(client_router)
app.include_router(fournisseur_router)


SECRET_KEY_FIXE = os.getenv("SECRET_KEY", "ma_cle_secrete_super_longue_et_introuvable_12345")


#-------------COULEUR PRINCIPALE-----------------

COMMON_STYLE = """
<style>
    :root {
        --neon-blue: #00d4ff;
        --neon-green: #22c55e; /* Vert Fluo */
        --dark-bg: #0f172a;
        --card-bg: #1e293b;
        --text-light: #f8fafc;
    }
    body {
        background-color: var(--dark-bg) !important;
        color: var(--text-light) !important;
        font-family: 'Inter', sans-serif;
        margin: 0;
    }
    h1, h2 {
        color: var(--neon-blue);
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.4);
        font-weight: 800;
    }
    
    /* 🔥 LA NOUVELLE CLASSE VERT FLUO */
    .text-vert-fluo {
        color: var(--neon-green) !important;
        text-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
        font-weight: bold;
    }

    /* 🌊 VOLET DE GAUCHE : DÉGRADÉ BLEU ET DESIGN ÉPURÉ */
    .sidebar {
        position: fixed; width: 260px; height: 100vh;
        background: linear-gradient(160deg, #0f172a 0%, #1e3a8a 100%); /* Dégradé Bleu */
        border-right: 1px solid rgba(0, 212, 255, 0.2);
        padding: 40px 20px;
        box-shadow: 4px 0 15px rgba(0,0,0,0.5);
        z-index: 1000;
    }
    /* ⚡ TITRE FLUO DU VOLET */
    .sidebar-brand {
        color: #00ffff; /* Cyan pur */
        font-size: 2rem;
        font-weight: 900;
        letter-spacing: 3px;
        text-align: center;
        margin-bottom: 40px;
        text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff; /* Effet Néon intense */
        border-bottom: 2px solid rgba(0, 255, 255, 0.3);
        padding-bottom: 15px;
    }
    .sidebar a {
        display: block; color: #cbd5e1; padding: 14px 20px;
        text-decoration: none; border-radius: 12px;
        margin-bottom: 10px; transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.03);
        font-weight: 600;
    }
    .sidebar a:hover {
        background: rgba(0, 212, 255, 0.15);
        color: #ffffff;
        transform: translateX(8px);
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }
    
    .main-content { margin-left: 280px; padding: 40px; }
    .container-fluid-custom { padding: 40px; max-width: 1200px; margin: auto; }
    
    .card {
        background: var(--card-bg); border: 1px solid #334155;
        border-radius: 20px; color: white;
    }
    .btn-neon {
        background: var(--neon-blue); color: #020617;
        border: none; padding: 12px 24px; border-radius: 12px;
        font-weight: bold; transition: 0.3s; text-decoration: none; display: inline-block;
    }
    .btn-neon:hover { box-shadow: 0 0 20px rgba(0, 212, 255, 0.6); color: #020617; }
</style>
"""

# --------------SIDEBAR GLOBALE---------

def sidebar(request: Request):
    session = request.session
    user_name = session.get("user_name", "Utilisateur")
    user_role = session.get("user_role", "CLIENT") # Valeur par défaut
    
    # Rendu des boutons en fonction du profil utilisateur
    menu_buttons = ""
    
    if user_role == "ENTREPRISE":
        menu_buttons = """
            <a href="/" class="menu-btn">🏠 Accueil Dashboard</a>
            <a href="/client" class="menu-btn">➕ Nouvelle Vente</a>
            <a href="/stats" class="menu-btn">📈 Statistiques</a>
            <a href="/prediction" class="menu-btn">🔮 Prédictions IA</a>
            <a href="/stocks" class="menu-btn">📦 Gestion Stock</a>
            <a href="/entreprise/achats-gros" class="menu-btn">🤝 Acheter aux Fournisseurs</a>
        """
    elif user_role == "CLIENT":
        menu_buttons = """
            <a href="/shop" class="menu-btn">🛒 Boutique en Ligne</a>
            <a href="/commandes/mes-achats" class="menu-btn">📦 Mes Commandes</a>
            <a href="/panier-virtuel" class="menu-btn">🧾 Mon Panier</a>
        """
    elif user_role == "FOURNISSEUR":
        menu_buttons = """
            <a href="/fournisseur/dashboard" class="menu-btn">📊 Mes Ventes en Gros</a>
            <a href="/fournisseur/deposer-lot" class="menu-btn">📦 Proposer un Grand Lot</a>
            <a href="/fournisseur/offres" class="menu-btn">📋 Catalogue Grossiste</a>
        """

    return f"""
    <div class="sidebar">
        <div class="sidebar-brand">💎 SDE PLATFORM</div>
        <div class="text-center mb-4">
            <span class="text-vert-fluo" style="font-size:14px;">👤 {user_name}</span><br>
            <span class="badge bg-primary" style="font-size:11px;">{user_role}</span>
        </div>
        
        <div class="menu-buttons">
            {menu_buttons}
        </div>

        <div style="margin-top:auto; padding-bottom:20px;">
            <a href="/logout" style="color:#f87171; text-decoration:none; font-size:14px;">🚪 Déconnexion</a>
        </div>
    </div>
    """

#-------------SECURITE GLOBALE------------------
# RÈGLE STARLETTE : dernier add_middleware = outermost = s'exécute EN PREMIER sur chaque requête.
# SessionMiddleware doit donc être ajouté EN DERNIER pour parser le cookie avant auth_middleware.

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    PUBLIC_ROUTES = ["/login", "/register", "/welcome", "/static",
                     "/resend-verification", "/verify-email", "/compte-supprime"]
    if any(path.startswith(r) for r in PUBLIC_ROUTES):
        return await call_next(request)
    session = getattr(request, "session", None)
    if session is None or not session.get("user_id"):
        return RedirectResponse("/login")
    return await call_next(request)

# ⚠️  Ajouté APRÈS @app.middleware → devient outermost → parse le cookie en premier ✓
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY_FIXE,
    max_age=86400,
    same_site="lax",
    https_only=False,
    session_cookie="sde_session",
)


#------------CHECK ADMIN-----------------

def check_admin(request: Request):
    if not request.session.get("admin"):
        raise HTTPException(status_code=401)

#-----------FONCTIONS PREDICTIONS-----------------
def calcul_prediction(ventes):

    def convertir_age(age):
        mapping = {
            "12-18": 15, "18-25": 22, "19-25": 22,
            "26-39": 32, "40+": 45, "40-55": 47, "55+": 60
        }
        return mapping.get(age, None)

    data = []

    for v in ventes:
        age_num = convertir_age(v.age)

        if age_num is not None and v.sexe and v.total:
            data.append({
                "age": age_num,
                "sexe": 1 if v.sexe == "Homme" else 0,
                "total": v.total
            })

    if len(data) < 3:
        return None

    df = pd.DataFrame(data)

    X = df[["age", "sexe"]]
    y = df["total"]

    model = LinearRegression()
    model.fit(X, y)

    # Profil test (modifiable plus tard avec filtres)
    prediction = model.predict([[32, 1]])[0]

    return round(prediction, 0)

  #--------------FONCTION POUR RETROUVER LE PRIX ET LE RAYON-------------------
  
def get_info_produit(nom_produit):
    """Cherche le rayon et le prix d'un produit depuis le dictionnaire ARTICLES"""
    for rayon, produits in ARTICLES.items():
        if nom_produit in produits:
            return rayon, produits[nom_produit] # Retourne (rayon, prix)
    return "Inconnu", 0  

    
# ---------------- DATABASE CONNECTION ----------------

from sqlalchemy.orm import Session

def get_db():
    """
    Fonction de dépendance qui crée une session de base de données 
    pour chaque requête et la ferme une fois la requête terminée.
    """
    db = SessionLocal()
    try:
        yield db  # FastAPI utilisera cet objet 'db' dans tes routes
    finally:
        db.close()
#----------------- PROFIL CORRESPONDANT----------------


# ---------------- PRODUITS COMPLETS ----------------
ARTICLES = {

    "electromenager": {
        "frigo": 250000, "micro-ondes": 60000, "machine a laver": 180000,
        "ventilateur": 20000, "climatiseur": 220000, "mixeur": 15000,
        "cuisiniere": 90000, "bouilloire": 12000, "aspirateur": 80000,
        "grille-pain": 10000, "four": 70000, "blender": 25000,
        "fer a repasser": 15000, "chauffe-eau": 120000
    },

    "hightech": {
        "telephone": 150000, "ordinateur": 400000, "tablette": 120000,
        "ecouteurs": 5000, "chargeur": 3000, "smartwatch": 35000,
        "camera": 90000, "imprimante": 70000, "routeur": 20000,
        "clavier": 10000, "souris": 5000, "ecran": 120000,
        "ps5": 450000, "casque gamer": 25000
    },

    "alimentation": {
        "riz": 15000, "pates": 12000, "huile": 18000,
        "sucre": 10000, "lait": 800, "banane": 500,
        "tomate": 300, "viande": 2500, "poisson": 2000,
        "farine": 9000, "haricot": 6000, "mais": 4000,
        "sel": 500, "cafe": 2000
    },

    "boissons": {
        "eau": 500, "coca": 700, "fanta": 700,
        "jus": 1200, "cafe": 1000, "the": 500,
        "biere": 1500, "energy": 2000, "sprite": 700,
        "lait": 800, "vin": 15000, "whisky": 25000
    },

    "produits entretien": {
        "savon lessive": 2000, "eau javel": 1500, "detergent": 2500,
        "balai": 3000, "serpillere": 1500, "desinfectant": 2000,
        "nettoyant vitre": 1800, "eponge": 500, "papier toilette": 2000,
        "liquide vaisselle": 1200
    },

    "cosmetiques": {
        "savon": 500, "parfum": 15000, "creme": 8000,
        "rouge a levres": 3000, "shampooing": 2500,
        "deodorant": 2000, "lotion": 4000,
        "maquillage": 12000, "huile cheveux": 3500,
        "gel douche": 2000, "fond de teint": 7000
    },

    "fournitures scolaires": {
        "cahier": 500, "stylo": 200, "crayon": 100,
        "regle": 300, "sac": 5000,
        "calculatrice": 4000, "gomme": 100,
        "colle": 500, "trousse": 1500,
        "livre": 3000, "ardoise": 2500
    },

    "jouets": {
        "poupee": 3000, "voiture": 2000, "lego": 15000,
        "ballon": 1000, "jeu societe": 8000,
        "peluche": 4000, "robot": 20000,
        "puzzle": 3000, "drone": 25000,
        "console mini": 30000, "train electrique": 35000
    },

    "accessoire maison": {
        "rideau": 5000, "tapis": 8000, "horloge": 6000,
        "lampe": 7000, "coussin": 3000,
        "decoration mur": 4000, "vase": 3500,
        "table basse": 25000, "chaise": 10000,
        "etagere": 15000, "miroir": 12000
    },

    "ustensile cuisine": {
        "couteau": 2000, "casserole": 8000, "poele": 6000,
        "cuillere": 500, "fourchette": 500, "assiette": 1000,
        "verre": 800, "planche a decouper": 2000,
        "passoire": 2500, "ouvre boite": 1500
    },

    "fruits et legumes": {
        "banane": 500, "pomme": 800, "orange": 600,
        "tomate": 300, "oignon": 400, "carotte": 300,
        "chou": 1000, "poivron": 700, "salade": 500,
        "ananas": 1500
    },

    "boucherie/poissonnerie": {
        "boeuf": 3000, "poulet": 2500, "porc": 2800,
        "poisson": 2000, "crevette": 3500, "crabe": 4000,
        "saucisse": 1500, "foie": 2000, "agneau": 3500,
        "thon": 3000
    },

    "layette": {
        "body bebe": 2000, "pyjama bebe": 3500, "chaussons": 1500,
        "bonnet": 1200, "biberon": 2500, "tetine": 1000,
        "poussette": 45000, "lit bebe": 80000, "couverture": 5000,
        "couche": 6000, "lingette": 3000, "chauffe biberon": 15000,
        "sac a langer": 12000, "veilleuse": 7000, "jouet bebe": 4000
    }
}
#---------------REMPLISSAGE DB----------------

@app.get("/force-init-db")
def force_init(db: Session = Depends(get_db)):
    # Insérez ici la boucle 'for rayon, produits in ARTICLES.items()...' du script ci-dessus
    # Puis faites db.commit()
    return {"status": "Database populated"}

# ---------------- HOME ----------------

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    profil = request.session.get("profil") or request.session.get("user_role", "")
    if not request.session.get("admin") and profil != "ENTREPRISE":
        return RedirectResponse("/login")
    
    # --- CALCULS DES DONNÉES ---
    ventes = db.query(Vente).all()
    nb_ventes = len(ventes)
    ca_total = sum(v.total or 0 for v in ventes)
    
    # 1. Panier Moyen
    panier_moyen = ca_total / nb_ventes if nb_ventes > 0 else 0

    # 2. Top Produit et Top Rayon
    produit_stats = defaultdict(int)
    rayon_stats = defaultdict(int)
    
    for v in ventes:
        for item in v.items:
            produit_stats[item.produit] += item.quantite
            rayon_stats[item.rayon] += item.quantite
    
    top_produit = max(produit_stats, key=produit_stats.get) if produit_stats else "N/A"
    top_rayon = max(rayon_stats, key=rayon_stats.get) if rayon_stats else "N/A"

    return f"""
    <html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {COMMON_STYLE}
        <style>
            .stat-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px; }}
            .stat-card {{
                background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px; padding: 25px; text-align: left; backdrop-filter: blur(10px);
                transition: 0.3s; position: relative; overflow: hidden;
            }}
            .stat-card:hover {{ border-color: var(--neon-green); transform: translateY(-5px); background: rgba(34, 197, 94, 0.08); }}
            .stat-label {{ font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; display: block; margin-bottom: 10px; }}
            .stat-value {{ font-size: 28px; font-weight: 800; color: #ffffff; display: block; }}
            .stat-icon {{ position: absolute; right: 20px; bottom: 20px; font-size: 40px; }}
        </style>
        <title>Dashboard | 💎SDE ADMIN</title>
    </head>
    <body>
        {sidebar(request)}
        <div class="main-content">
            <header class="mb-5">
                <h1 style="font-size: 38px;">🏪 Vue d'ensemble</h1>
                <p>Statistiques clés de votre activité commerciale.</p>
            </header>

            <div class="stat-grid">
                <div class="stat-card">
                    <span class="stat-label text-vert-fluo">Chiffre d'Affaires</span>
                    <span class="stat-value">{ca_total:,} FCFA</span>
                    <span class="stat-icon">💰</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label text-vert-fluo">Panier Moyen</span>
                    <span class="stat-value">{int(panier_moyen):,} FCFA</span>
                    <span class="stat-icon">📈</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label text-vert-fluo">Ventes Totales</span>
                    <span class="stat-value">{nb_ventes}</span>
                    <span class="stat-icon">🛒</span>
                </div>
                <div class="stat-card">
                    <span class="stat-label text-vert-fluo">Rayon Leader</span>
                    <span class="stat-value" style="font-size: 22px;">{top_rayon.upper()}</span>
                    <span class="stat-icon">🏆</span>
                </div>
            </div>

            <div class="mt-4 p-3" style="background: rgba(255,255,255,0.03); border-radius: 15px; border: 1px solid rgba(255,255,255,0.05);">
                <span class="text-vert-fluo" style="font-size: 15px;">🌟 <b>Produit Star :</b> {top_produit}</span>
            </div>
        </div>
    </body>
    </html>
    """

# ---------------- CLIENT ----------------

@app.get("/client", response_class=HTMLResponse)
def page_client(request: Request):
    return f"""
    <html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {COMMON_STYLE}
        <style>
            .client-card {{
                max-width: 500px;
                margin: 50px auto;
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 30px;
                padding: 40px;
                backdrop-filter: blur(20px);
            }}
            select, input {{
                background: rgba(0,0,0,0.3) !important;
                border: 1px solid rgba(255,255,255,0.2) !important;
                color: white !important;
                border-radius: 12px !important;
                padding: 12px !important;
            }}
            .btn-start {{
                background: #60a5fa; color: #000; border: none;
                padding: 15px; border-radius: 12px; font-weight: 800;
                width: 100%; margin-top: 20px; transition: 0.3s;
            }}
            .btn-start:hover {{ background: #93c5fd; transform: scale(1.02); }}
        </style>
    </head>
    <body>
        {sidebar(request)}
        <div class="main-content text-center">
            <div class="client-card">
                <h1 class="mb-4" style="color: #60a5fa;">👤 Nouveau Client</h1>
                <form action="/rayon" method="get">
                    <div class="mb-4 text-start">
                        <label class="form-label">Tranche d'âge</label>
                        <select name="age" class="form-select">
                            <option value="18-25">18 - 25 ans</option>
                            <option value="26-39">26 - 39 ans</option>
                            <option value="40-55">40 - 55 ans</option>
                            <option value="55+">55 ans et plus</option>
                        </select>
                    </div>
                    <div class="mb-4 text-start">
                        <label class="form-label">Sexe</label>
                        <select name="sexe" class="form-select">
                            <option value="Homme">Homme</option>
                            <option value="Femme">Femme</option>
                        </select>
                    </div>
                    <button type="submit" class="btn-start">COMMENCER LA VENTE</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

# ---------------- SAVE CLIENT ----------------
@app.post("/save-client")
def save_client(request: Request, age: str = Form(...), sexe: str = Form(...)):
    request.session["age"] = age
    request.session["sexe"] = sexe
    request.session["panier"] = []
    return RedirectResponse("/rayon", status_code=302)


# ---------------- RAYON ----------------

@app.get("/rayon", response_class=HTMLResponse)
def rayon(request: Request, age: str, sexe: str, db: Session = Depends(get_db)):

    # ✅ stockage session ICI 
    request.session["age"] = age
    request.session["sexe"] = sexe

    # ✅ Source unique : table Stock — plus aucune dépendance à ARTICLES
    rayons_db = sorted({row[0] for row in db.query(Stock.rayon).distinct().all()})

    boutons = ""
    for r in rayons_db:
        boutons += f"""
        <button name="rayon" value="{r}" class="btn btn-outline-primary m-1" style="text-transform:capitalize;">
            {r}
        </button>
        """

    return f"""
    <html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {COMMON_STYLE}
    </head>
    <body>
        <div class="container text-center" style="padding-top: 100px;">
            <h1 class="mb-5">🏪 CHOISIR UN RAYON</h1>
            <form action="/articles" method="get">
                <input type="hidden" name="age" value="{age}">
                <input type="hidden" name="sexe" value="{sexe}">
                <div class="d-flex flex-wrap justify-content-center">
                    {boutons}
                </div>
            </form>
            <br>
            <a href="/client" class="btn btn-neon">⬅ Retour aux informations client</a>
        </div>
    </body>
    </html
    """


# ---------------- ARTICLES ----------------

@app.get("/articles", response_class=HTMLResponse)
def articles(request: Request, age: str, sexe: str, rayon: str):

    panier = request.session.get("panier", [])

    # 🔥 récupération ventes pour recommandation
    db = SessionLocal()
    ventes = db.query(Vente).all()

    last_product = panier[-1].get('produit') if panier else None
    reco = recommend_advanced(ventes, panier, age, sexe) if panier else []

    # ✅ Source unique : table Stock — les noms et prix sont ceux de la DB
    stocks_rayon = db.query(Stock).filter(Stock.rayon == rayon).all()
    # Dictionnaire {nom_produit: prix} lu depuis la DB
    produits_rayon = {s.produit: int(s.prix) for s in stocks_rayon}

    items = ""
    for p, prix in produits_rayon.items():
        items += f"""
        <div class="col-md-4">
            <div class="card mb-3" style="border-radius:12px;">
                <div class="card-body text-center">

                    <h5 class="card-title">{p.capitalize()}</h5>

                    <p style="color:green;font-weight:bold;">
                        {prix:,} FCFA
                    </p>

                    <form action="/ajouter-panier" method="post">
                        <input type="hidden" name="produit" value="{p}">
                        <input type="hidden" name="rayon" value="{rayon}">
                        <input type="hidden" name="age" value="{age}">
                        <input type="hidden" name="sexe" value="{sexe}">

                        <input type="number" name="qte_{p}" value="1" min="1"
                               class="form-control mb-2">

                        <button class="btn btn-warning w-100">
                            Ajouter au panier
                        </button>
                    </form>

                </div>
            </div>
        </div>
        """

    # ---------------- RECOMMANDATIONS ----------------
    
    reco_html = ""

    if reco:
        for p, s in reco:
            # On doit retrouver le rayon et le prix du produit recommandé
            r_origine = "Inconnu"
            prix_reco = 0
            for r_nom, p_liste in ARTICLES.items():
                if p in p_liste:
                    r_origine = r_nom
                    prix_reco = p_liste[p]
                    break

            reco_html += f"""
            <div class="col-md-3">
                <div class="card border-success mb-3 shadow-sm" style="border-radius:12px;">
                    <div class="card-body text-center">
                        <h6 class="text-success">💡 Suggestion</h6>
                        <h5 class="card-title">{p}</h5>
                        <p class="text-muted" style="font-size:0.9rem;">{prix_reco} FCFA</p>

                        <form action="/ajouter-panier" method="post">
                            <input type="hidden" name="produit" value="{p}">
                            <input type="hidden" name="rayon" value="{r_origine}">
                            <input type="hidden" name="age" value="{age}">
                            <input type="hidden" name="sexe" value="{sexe}">

                            <div class="input-group input-group-sm mb-2">
                                <span class="input-group-text">Qté</span>
                                <input type="number" name="qte_{p}" value="1" min="1" class="form-control">
                            </div>

                            <button class="btn btn-success btn-sm w-100">
                                + Ajouter au panier
                            </button>
                        </form>
                    </div>
                </div>
            </div>
            """
    else:
        reco_html = "<p class='text-center text-muted'>Ajoutez un produit pour voir les suggestions.</p>"

    # ---------------- PAGE ----------------
    return f"""
    <html>
    <head>
        <title>Articles</title>

        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        
        {COMMON_STYLE}

        <style>
            .product-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 25px;
            }}

            h2 {{
                font-weight:bold;
            }}
        </style>
    </head>

    <body>

    <div class="container mt-4">

        <h2 class="text-center">🛒 Rayon : {rayon}</h2>

        <!-- PRODUITS -->
        <div class="row mt-4">
            {items}
        </div>

        <!-- RECOMMANDATIONS -->
        <h4 class="mt-5 text-center">🧠 Suggestions pour vous</h4>

        <div class="row mt-3">
            {reco_html}
        </div>

        <!-- ACTIONS -->
        <div class="text-center mt-4">
            <a href="/rayon?age={age}&sexe={sexe}" class="btn btn-secondary">
                ⬅ Retour
            </a>

            <a href="/panier" class="btn btn-success">
                🧾 Voir panier ({len(panier)})
            </a>
        </div>

    </div>

    </body>
    </html>
    """



# ---------------- AJOUT PANIER ----------------

@app.post("/ajouter-panier")
async def ajouter_panier(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    produit = form.get("produit")
    rayon = form.get("rayon")
    age = form.get("age")
    sexe = form.get("sexe")
    qte = int(form.get(f"qte_{produit}") or 1)

    # --- VÉRIFICATION STOCK ---
    stock = db.query(Stock).filter(Stock.produit == produit).first()
    if stock is None:
        # Produit inconnu — ne devrait pas arriver si le flux passe par /articles
        # On crée une entrée neutre à prix 0 pour ne pas bloquer
        stock = Stock(rayon=rayon, produit=produit, prix=0, quantite=100)
        db.add(stock)
        db.commit()
        db.refresh(stock)

    if qte > stock.quantite:
        return RedirectResponse(
            f"/vente-impossible?produit={produit}&demande={qte}&dispo={stock.quantite}",
            status_code=302
        )

    # ✅ Prix lu exclusivement depuis la DB — jamais depuis ARTICLES
    prix_unitaire = int(stock.prix)

    panier = request.session.get("panier", [])
    panier.append({
        "produit": produit,
        "rayon": rayon,
        "prix": prix_unitaire,
        "quantite": qte
    })
    request.session["panier"] = panier

    return RedirectResponse(
        f"/articles?age={age}&sexe={sexe}&rayon={rayon}",
        status_code=302
    )


# ---------------- PANIER ----------------

@app.get("/panier", response_class=HTMLResponse)
def voir_panier(request: Request):
    panier = request.session.get("panier", [])
    
    # On récupère les infos dans la SESSION
    age = request.session.get("age", "Inconnu")
    sexe = request.session.get("sexe", "Inconnu")
    
    total = sum(float(item.get('prix', 0)) * item.get('quantite', 1) for item in panier)

    return f"""
    <html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {COMMON_STYLE}
        <style>
            .receipt-container {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 40px;
                max-width: 600px;
                margin: auto;
                backdrop-filter: blur(15px);
            }}
            .receipt-line {{
                display: flex;
                justify-content: space-between;
                border-bottom: 1px dashed rgba(255,255,255,0.1);
                padding: 15px 0;
            }}
            .total-section {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #60a5fa;
            }}
            .btn-validate {{
                background: linear-gradient(45deg, #2563eb, #3b82f6);
                color: white; border: none; padding: 15px; border-radius: 12px;
                width: 100%; font-weight: bold; font-size: 18px; transition: 0.3s;
                text-decoration: none; display: block; text-align: center;
            }}
            .btn-reset {{
                background: rgba(239, 68, 68, 0.1);
                color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2);
                padding: 10px; border-radius: 12px; width: 100%; margin-top: 15px;
                transition: 0.3s; font-weight: 600;
            }}
        </style>
    </head>
    <body>
        {sidebar(request)}
        <div class="main-content">
            <div class="receipt-container">
                <h2 class="text-center mb-4" style="color: #60a5fa;">🧾 Récapitulatif</h2>
                <p class="text-center text-muted">Client: {sexe}, {age} ans</p>
               
                {"".join([f'<div class="receipt-line"><span>{i.get("produit")} (x{i.get("quantite")})</span><b>{int(i.get("prix", 0)) * i.get("quantite"):,} FCFA</b></div>' for i in panier])}
                <div class="total-section d-flex justify-content-between align-items-center">
                    <span style="font-size: 20px;">TOTAL</span>
                    <span style="font-size: 28px; font-weight: 800; color: #ffffff;">{total:,} FCFA</span>
                </div>

                <form action="/confirm" method="post" class="mt-4">
                    <button type="submit" class="btn-validate">Confirmer la vente</button>
                </form>

                <form action="/recommencer" method="post">
                    <button type="submit" class="btn-reset">🔄 Recommencer le panier</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

# ---------------- CONFIRM ----------------

@app.post("/confirm", response_class=HTMLResponse)
def confirm(request: Request, db: Session = Depends(get_db)):
    panier = request.session.get("panier", [])
    age = request.session.get("age", "inconnu")
    sexe = request.session.get("sexe", "inconnu")

    total = 0
    vente = Vente(age=age, sexe=sexe, total=0)

    for i in panier:
        # ✅ Prix lu exclusivement depuis la DB Stock
        stock_ref = db.query(Stock).filter(Stock.produit == i["produit"]).first()
        prix = int(stock_ref.prix) if stock_ref else i.get("prix", 0)
        qte = i["quantite"]
        total_produit = prix * qte
        total += total_produit

        item = VenteItem(
            rayon=i["rayon"],
            produit=i["produit"],
            quantite=qte,
            prix_unitaire=prix,
            total=total_produit
        )
        vente.items.append(item)

        # --- DÉDUCTION STOCK ---
        stock = db.query(Stock).filter(Stock.produit == i["produit"]).first()
        if stock:
            stock.quantite = max(0, stock.quantite - qte)
        else:
            # Créer l'entrée stock si elle n'existe pas (init à 100 - qte vendue)
            nouveau_stock = Stock(
                rayon=i["rayon"],
                produit=i["produit"],
                prix=prix,
                quantite=max(0, 100 - qte)
            )
            db.add(nouveau_stock)

    vente.total = total
    db.add(vente)
    db.commit()
    db.refresh(vente) # Pour être sûr de récupérer l'ID généré par la DB

    # C'est ICI qu'on définit la variable pour l'injecter dans le HTML
    vente_id = vente.id 

    request.session.pop("panier", None)
    request.session.pop("age", None)
    request.session.pop("sexe", None)

    return f"""
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap" rel="stylesheet">
        <style>
            body {{
                background-color: #0f172a;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                font-family: 'Inter', sans-serif;
                overflow: hidden;
            }}
            .confirm-container {{
                text-align: center;
                animation: fadeIn 0.8s ease-out;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .neon-title {{
                font-size: 5rem; /* Plus grand */
                font-weight: 900;
                color: #60a5fa;
                text-transform: uppercase;
                letter-spacing: 8px;
                text-shadow: 0 0 15px rgba(96, 165, 250, 0.7), 
                             0 0 30px rgba(37, 99, 235, 0.5), 
                             0 0 60px rgba(37, 99, 235, 0.3);
                margin-bottom: 60px;
                line-height: 1.1;
            }}
            .btn-group {{
                display: flex;
                gap: 25px;
                justify-content: center;
            }}
            .btn-custom {{
                padding: 18px 35px;
                font-size: 1.2rem;
                font-weight: 700;
                border-radius: 12px; /* Look plus moderne/tech que l'arrondi total */
                text-decoration: none;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .btn-detail {{
                background: rgba(30, 41, 59, 0.5);
                color: #cbd5e1;
                border: 2px solid #334155;
            }}
            .btn-detail:hover {{
                background: #334155;
                color: #ffffff;
                border-color: #60a5fa;
                transform: scale(1.05);
            }}
            .btn-new {{
                background: #2563eb;
                color: white;
                border: 2px solid #2563eb;
                box-shadow: 0 0 20px rgba(37, 99, 235, 0.4);
            }}
            .btn-new:hover {{
                background: #1d4ed8;
                box-shadow: 0 0 35px rgba(37, 99, 235, 0.6);
                transform: scale(1.05);
            }}
        </style>
    </head>
    <body>
        <div class="confirm-container">
            <div class="neon-title">VENTE<br>CONFIRMÉE</div>
            
            <div class="btn-group">
                <a href="/vente/{vente_id}" class="btn-custom btn-detail">
                    <span>🔎</span> VOIR DÉTAILS
                </a>
                <a href="/" class="btn-custom btn-new">
                    <span>➕</span> NOUVELLE VENTE
                </a>
            </div>
        </div>
    </body>
    </html>
    """    
#-----------------RECOMMENCER--------------

@app.post("/recommencer")
def recommencer_panier(request: Request):
    # On vide uniquement le panier, on peut garder le client si on veut
    request.session["panier"] = []
    return RedirectResponse("/client", status_code=303)


# ================= VENTE IMPOSSIBLE =================

@app.get("/vente-impossible", response_class=HTMLResponse)
def vente_impossible(produit: str, demande: int, dispo: int):
    return f"""
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap" rel="stylesheet">
        {COMMON_STYLE}
        <style>
            .vi-wrapper {{
                display: flex; align-items: center; justify-content: center;
                min-height: 100vh; flex-direction: column; text-align: center;
                padding: 40px;
            }}
            .vi-card {{
                background: rgba(0, 10, 30, 0.8);
                border: 2px solid rgba(0, 212, 255, 0.3);
                border-radius: 28px;
                padding: 60px 80px;
                max-width: 700px;
                backdrop-filter: blur(20px);
                box-shadow: 0 0 60px rgba(0, 212, 255, 0.08);
                animation: fadeIn 0.7s ease-out;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .vi-icon {{ font-size: 5rem; margin-bottom: 20px; }}
            .vi-title {{
                font-size: 2.2rem; font-weight: 900;
                color: #00d4ff;
                text-shadow: 0 0 20px rgba(0, 212, 255, 0.9),
                             0 0 40px rgba(0, 212, 255, 0.5),
                             0 0 80px rgba(0, 212, 255, 0.3);
                letter-spacing: 3px; text-transform: uppercase;
                margin-bottom: 15px;
            }}
            .vi-subtitle {{
                font-size: 1.1rem; color: #94a3b8;
                margin-bottom: 35px; line-height: 1.7;
            }}
            .vi-stats {{
                display: flex; gap: 30px; justify-content: center;
                margin-bottom: 40px;
            }}
            .vi-stat-box {{
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px; padding: 20px 30px;
                min-width: 140px;
            }}
            .vi-stat-label {{
                font-size: 11px; text-transform: uppercase;
                letter-spacing: 2px; color: #64748b; display: block; margin-bottom: 8px;
            }}
            .vi-stat-value {{
                font-size: 2rem; font-weight: 900;
            }}
            .vi-stat-value.red {{ color: #f87171; text-shadow: 0 0 10px rgba(248,113,113,0.5); }}
            .vi-stat-value.blue {{ color: #00d4ff; text-shadow: 0 0 10px rgba(0,212,255,0.5); }}
            .vi-btn {{
                display: inline-block; text-decoration: none;
                padding: 16px 40px; border-radius: 14px; font-weight: 800;
                font-size: 1rem; transition: all 0.3s; margin: 8px;
            }}
            .vi-btn-back {{
                background: rgba(0, 212, 255, 0.15);
                color: #00d4ff; border: 2px solid rgba(0, 212, 255, 0.4);
            }}
            .vi-btn-back:hover {{
                background: rgba(0, 212, 255, 0.25);
                box-shadow: 0 0 25px rgba(0,212,255,0.4);
                color: #00d4ff;
            }}
            .vi-btn-stock {{
                background: rgba(34, 197, 94, 0.15);
                color: #22c55e; border: 2px solid rgba(34, 197, 94, 0.4);
            }}
            .vi-btn-stock:hover {{
                background: rgba(34, 197, 94, 0.25);
                box-shadow: 0 0 25px rgba(34,197,94,0.4);
                color: #22c55e;
            }}
        </style>
    </head>
    <body>
        {sidebar(request)}
        <div class="main-content">
            <div class="vi-wrapper">
                <div class="vi-card">
                    <div class="vi-icon">⚠️</div>
                    <div class="vi-title">Vente Impossible</div>
                    <div class="vi-subtitle">
                        Produit en manque — La quantité demandée dépasse le stock disponible 
                        pour <b style="color:#fff;">« {produit.upper()} »</b>
                    </div>
                    <div class="vi-stats">
                        <div class="vi-stat-box">
                            <span class="vi-stat-label">Demandé</span>
                            <span class="vi-stat-value red">{demande}</span>
                        </div>
                        <div class="vi-stat-box">
                            <span class="vi-stat-label">Disponible</span>
                            <span class="vi-stat-value blue">{dispo}</span>
                        </div>
                    </div>
                    <div>
                        <a href="javascript:history.back()" class="vi-btn vi-btn-back">
                            ⬅ Modifier la quantité
                        </a>
                        <a href="/stocks" class="vi-btn vi-btn-stock">
                            📦 Voir les stocks
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


# ================= GESTION STOCK =================

def init_stocks_si_vide(db: Session):
    """Initialise tous les produits ARTICLES à 100 unités.
    Utilise INSERT OR IGNORE (on_conflict_do_nothing) pour éviter toute erreur
    de contrainte UNIQUE, même si des produits portent le même nom dans plusieurs rayons."""
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert

    vus = set()  # Evite les doublons intra-ARTICLES (cafe, banane, lait…)
    for rayon, produits in ARTICLES.items():
        for produit, prix in produits.items():
            if produit in vus:
                continue
            vus.add(produit)
            stmt = sqlite_insert(Stock.__table__).values(
                rayon=rayon,
                produit=produit,
                prix=float(prix),
                quantite=100
            ).on_conflict_do_nothing(index_elements=["produit"])
            db.execute(stmt)
    db.commit()


@app.get("/stocks", response_class=HTMLResponse)
def gestion_stocks(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin") and request.session.get("profil","") != "ENTREPRISE" and request.session.get("user_role","") != "ENTREPRISE":
        return RedirectResponse("/login")

    # Initialise les stocks si c'est la première visite
    init_stocks_si_vide(db)

    stocks = db.query(Stock).order_by(Stock.rayon, Stock.produit).all()

    # Regrouper par rayon
    rayons_dict = defaultdict(list)
    for s in stocks:
        rayons_dict[s.rayon].append(s)

    alerte_count = sum(1 for s in stocks if s.quantite <= 10)

    # ✅ Dropdown modal : rayons issus uniquement de la DB
    tous_rayons_options = sorted(set(list(rayons_dict.keys())))
    options_rayon_html = "".join(
        f'<option value="{r}">{r.capitalize()}</option>' for r in tous_rayons_options
    )

    # ---- HTML des rayons ----
    rayons_html = ""
    for rayon, items in sorted(rayons_dict.items()):
        rows = ""
        for s in items:
            alert_class = "stock-alerte" if s.quantite <= 10 else ""
            badge = '<span class="badge-alerte">⚠ Réapprovisionnement requis</span>' if s.quantite <= 10 else ""
            rows += f"""
            <tr class="{alert_class}" id="row-{s.id}">
                <td class="prod-name">{s.produit.capitalize()}</td>
                <td class="prod-qty">
                    <span class="qty-bubble {'qty-low' if s.quantite <= 10 else ''}">{s.quantite}</span>
                    {badge}
                </td>
                <td class="prod-prix">{int(s.prix):,} FCFA</td>
                <td class="prod-actions">
                    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                        <form action="/stocks/reapprovisionner" method="post"
                              style="display:flex;gap:8px;align-items:center;">
                            <input type="hidden" name="produit_id" value="{s.id}">
                            <input type="number" name="qte_ajout" value="50" min="1"
                                   class="input-qty" placeholder="Qté">
                            <button type="submit" class="btn-reappro">+ Réappro.</button>
                        </form>
                        <form action="/stocks/supprimer-article" method="post"
                              onsubmit="return confirm('Supprimer «{s.produit.capitalize()}» ? Cette action est irréversible.')">
                            <input type="hidden" name="produit_id" value="{s.id}">
                            <button type="submit" class="btn-suppr-article">🗑 Supprimer</button>
                        </form>
                    </div>
                </td>
            </tr>
            """
        rayons_html += f"""
        <div class="rayon-section" id="rayon-block-{rayon}">
            <div class="rayon-title-bar">
                <span class="rayon-title">📂 {rayon.upper()}</span>
                <form action="/stocks/supprimer-rayon" method="post"
                      onsubmit="return confirm('Supprimer TOUT le rayon «{rayon.upper()}» et ses {len(items)} article(s) ? Cette action est irréversible.')">
                    <input type="hidden" name="rayon" value="{rayon}">
                    <button type="submit" class="btn-suppr-rayon">🗑 Supprimer le rayon</button>
                </form>
            </div>
            <table class="stock-table">
                <thead>
                    <tr>
                        <th>Produit</th>
                        <th>Quantité</th>
                        <th>Prix unitaire</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """

    alerte_banner = f"""
        <div class="alerte-banner">
            ⚠️ <b>{alerte_count} produit(s)</b> sous le seuil de 10 unités — réapprovisionnement recommandé
        </div>
    """ if alerte_count > 0 else ""

    return f"""
    <html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {COMMON_STYLE}
        <style>
            .stock-header {{ margin-bottom: 35px; }}
            .stock-header h1 {{ font-size: 2.4rem; }}

            .alerte-banner {{
                background: rgba(234, 179, 8, 0.12);
                border: 1px solid rgba(234, 179, 8, 0.4);
                color: #fcd34d;
                border-radius: 14px; padding: 14px 22px;
                margin-bottom: 30px; font-size: 15px;
            }}

            .rayon-section {{
                margin-bottom: 40px;
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 20px; overflow: hidden;
            }}
            .rayon-title-bar {{
                display: flex; justify-content: space-between; align-items: center;
                background: rgba(0, 212, 255, 0.07);
                border-bottom: 1px solid rgba(0, 212, 255, 0.15);
                padding: 12px 20px;
            }}
            .rayon-title {{
                font-size: 1rem; font-weight: 800;
                color: var(--neon-blue);
                letter-spacing: 2px; text-transform: uppercase;
            }}
            .btn-suppr-rayon {{
                background: rgba(239, 68, 68, 0.1);
                color: #f87171;
                border: 1px solid rgba(239, 68, 68, 0.3);
                padding: 7px 16px; border-radius: 10px;
                font-weight: 700; font-size: 12px;
                cursor: pointer; transition: 0.3s; white-space: nowrap;
            }}
            .btn-suppr-rayon:hover {{
                background: rgba(239, 68, 68, 0.25);
                box-shadow: 0 0 12px rgba(239,68,68,0.35);
            }}
            .btn-suppr-article {{
                background: rgba(239, 68, 68, 0.08);
                color: #f87171;
                border: 1px solid rgba(239, 68, 68, 0.25);
                padding: 7px 14px; border-radius: 10px;
                font-weight: 700; font-size: 12px;
                cursor: pointer; transition: 0.3s; white-space: nowrap;
            }}
            .btn-suppr-article:hover {{
                background: rgba(239, 68, 68, 0.22);
                box-shadow: 0 0 10px rgba(239,68,68,0.3);
            }}
            .stock-table {{ width: 100%; border-collapse: collapse; }}
            .stock-table thead tr {{
                background: rgba(255,255,255,0.04);
                border-bottom: 1px solid rgba(255,255,255,0.08);
            }}
            .stock-table th {{
                padding: 12px 20px; font-size: 12px;
                text-transform: uppercase; letter-spacing: 1.5px;
                color: #64748b; font-weight: 700; text-align: left;
            }}
            .stock-table td {{
                padding: 14px 20px;
                border-bottom: 1px solid rgba(255,255,255,0.04);
                color: #cbd5e1; vertical-align: middle;
            }}
            .stock-table tr:last-child td {{ border-bottom: none; }}
            .stock-table tr:hover {{ background: rgba(255,255,255,0.03); }}

            .stock-alerte {{ background: rgba(239, 68, 68, 0.05) !important; }}
            .stock-alerte:hover {{ background: rgba(239, 68, 68, 0.08) !important; }}

            .qty-bubble {{
                display: inline-block; padding: 4px 14px;
                border-radius: 100px; font-weight: 800; font-size: 0.95rem;
                background: rgba(34, 197, 94, 0.15);
                color: #22c55e;
            }}
            .qty-low {{
                background: rgba(239, 68, 68, 0.15) !important;
                color: #f87171 !important;
                animation: pulse-red 2s infinite;
            }}
            @keyframes pulse-red {{
                0%, 100% {{ box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }}
                50% {{ box-shadow: 0 0 0 6px rgba(239,68,68,0); }}
            }}
            .badge-alerte {{
                display: inline-block; margin-left: 10px;
                font-size: 11px; padding: 3px 10px;
                background: rgba(239, 68, 68, 0.15);
                color: #f87171; border-radius: 100px;
                border: 1px solid rgba(239, 68, 68, 0.3);
                font-weight: 600;
            }}

            .input-qty {{
                width: 90px; background: rgba(0,0,0,0.3) !important;
                border: 1px solid rgba(255,255,255,0.15) !important;
                color: white !important; border-radius: 10px !important;
                padding: 8px 12px !important; font-size: 14px;
                transition: 0.3s;
            }}
            .input-qty:focus {{ border-color: var(--neon-blue) !important; outline: none; }}

            .btn-reappro {{
                background: rgba(0, 212, 255, 0.12);
                color: var(--neon-blue);
                border: 1px solid rgba(0, 212, 255, 0.35);
                padding: 8px 18px; border-radius: 10px;
                font-weight: 700; font-size: 13px;
                cursor: pointer; transition: 0.3s; white-space: nowrap;
            }}
            .btn-reappro:hover {{
                background: rgba(0, 212, 255, 0.22);
                box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
            }}

            /* Bouton Ajouter article (haut droite) */
            .btn-add-product-top {{
                background: linear-gradient(135deg, #22c55e, #16a34a);
                color: white; border: none;
                padding: 14px 22px; border-radius: 14px;
                font-weight: 800; font-size: 15px;
                cursor: pointer; white-space: nowrap;
                box-shadow: 0 4px 20px rgba(34, 197, 94, 0.35);
                transition: 0.3s; display: flex; align-items: center; gap: 10px;
                flex-shrink: 0; margin-top: 6px;
            }}
            .btn-add-product-top:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 28px rgba(34, 197, 94, 0.5);
            }}

            /* Modal Ajouter produit */
            .modal-overlay {{
                display: none; position: fixed; inset: 0;
                background: rgba(0,0,0,0.7); z-index: 2000;
                align-items: center; justify-content: center;
                backdrop-filter: blur(5px);
            }}
            .modal-overlay.active {{ display: flex; }}
            .modal-card {{
                background: #1e293b; border: 1px solid rgba(0,212,255,0.2);
                border-radius: 24px; padding: 40px; width: 100%; max-width: 480px;
                animation: fadeIn 0.3s ease-out;
            }}
            @keyframes fadeIn {{
                from {{ opacity:0; transform:scale(0.95); }}
                to {{ opacity:1; transform:scale(1); }}
            }}
            .modal-card h3 {{ color: var(--neon-blue); font-size: 1.4rem; margin-bottom: 24px; }}
            .modal-input {{
                width: 100%; background: rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.15);
                color: white; border-radius: 12px;
                padding: 12px 16px; margin-bottom: 16px;
                font-size: 15px; transition: 0.3s;
            }}
            .modal-input:focus {{ border-color: var(--neon-blue); outline: none; }}
            .modal-input option {{ background: #1e293b; }}
            .btn-modal-submit {{
                width: 100%; background: linear-gradient(90deg, #00d4ff, #0080ff);
                color: #020617; border: none; padding: 14px;
                border-radius: 12px; font-weight: 800;
                font-size: 16px; cursor: pointer; transition: 0.3s; margin-top: 8px;
            }}
            .btn-modal-submit:hover {{ box-shadow: 0 0 25px rgba(0,212,255,0.5); }}
            .btn-modal-cancel {{
                width: 100%; background: transparent;
                color: #64748b; border: 1px solid rgba(255,255,255,0.1);
                padding: 12px; border-radius: 12px;
                font-weight: 600; cursor: pointer; transition: 0.3s; margin-top: 8px;
            }}
            .btn-modal-cancel:hover {{ color: #cbd5e1; border-color: rgba(255,255,255,0.2); }}
        </style>
    </head>
    <body>
        {sidebar(request)}
        <div class="main-content">
            <div class="stock-header" style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <h1>📦 Gestion des Stocks</h1>
                    <p>Suivi en temps réel des quantités disponibles. Seuil d'alerte : <b style="color:#f87171;">10 unités</b>.</p>
                </div>
                <button class="btn-add-product-top" onclick="document.getElementById('modalAjout').classList.add('active')">
                    ➕ Ajouter un article
                </button>
            </div>

            {alerte_banner}
            {rayons_html}
        </div>

        <!-- MODAL AJOUTER PRODUIT -->
        <div class="modal-overlay" id="modalAjout">
            <div class="modal-card">
                <h3>➕ Nouveau Produit</h3>
                <form action="/stocks/ajouter-produit" method="post">
                    <select name="rayon" class="modal-input" required id="selectRayon">
                        <option value="" disabled selected>-- Choisir un rayon --</option>
                        {options_rayon_html}
                        <option value="autre">🆕 Nouveau rayon...</option>
                    </select>
                    <input type="text" name="nouveau_rayon" class="modal-input"
                           placeholder="Nom du nouveau rayon (si applicable)" style="display:none;" id="inputNvRayon">
                    <input type="text" name="produit" class="modal-input"
                           placeholder="Nom du produit" required>
                    <input type="number" name="prix" class="modal-input"
                           placeholder="Prix unitaire (FCFA)" min="1" required>
                    <input type="number" name="quantite" class="modal-input"
                           placeholder="Quantité initiale" min="1" value="100" required>
                    <button type="submit" class="btn-modal-submit">💾 Enregistrer le produit</button>
                    <button type="button" class="btn-modal-cancel"
                            onclick="document.getElementById('modalAjout').classList.remove('active')">
                        Annuler
                    </button>
                </form>
            </div>
        </div>

        <script>
            document.getElementById('selectRayon').addEventListener('change', function() {{
                document.getElementById('inputNvRayon').style.display =
                    this.value === 'autre' ? 'block' : 'none';
            }});
        </script>
    </body>
    </html>
    """


# ================= RÉAPPROVISIONNEMENT =================

@app.post("/stocks/reapprovisionner")
def reapprovisionner(request: Request, produit_id: int = Form(...), qte_ajout: int = Form(...), db: Session = Depends(get_db)):
    if not request.session.get("admin") and request.session.get("profil","") != "ENTREPRISE" and request.session.get("user_role","") != "ENTREPRISE":
        return RedirectResponse("/login")
    stock = db.query(Stock).filter(Stock.id == produit_id).first()
    if stock:
        stock.quantite += qte_ajout
        db.commit()
    return RedirectResponse("/stocks", status_code=302)


# ================= AJOUTER PRODUIT =================

@app.post("/stocks/ajouter-produit")
def ajouter_produit_stock(
    request: Request,
    rayon: str = Form(...),
    nouveau_rayon: str = Form(""),
    produit: str = Form(...),
    prix: float = Form(...),
    quantite: int = Form(...),
    db: Session = Depends(get_db)
):
    if not request.session.get("admin") and request.session.get("profil","") != "ENTREPRISE" and request.session.get("user_role","") != "ENTREPRISE":
        return RedirectResponse("/login")

    rayon_final = nouveau_rayon.strip().lower() if rayon == "autre" and nouveau_rayon.strip() else rayon

    # Vérifier si le produit existe déjà
    existant = db.query(Stock).filter(Stock.produit == produit.lower()).first()
    if not existant:
        nouveau = Stock(
            rayon=rayon_final,
            produit=produit.lower(),
            prix=prix,
            quantite=quantite
        )
        db.add(nouveau)
        db.commit()
    return RedirectResponse("/stocks", status_code=302)


# ================= SUPPRIMER UN ARTICLE =================

@app.post("/stocks/supprimer-article")
def supprimer_article(
    request: Request,
    produit_id: int = Form(...),
    db: Session = Depends(get_db)
):
    if not request.session.get("admin") and request.session.get("profil","") != "ENTREPRISE" and request.session.get("user_role","") != "ENTREPRISE":
        return RedirectResponse("/login")
    stock = db.query(Stock).filter(Stock.id == produit_id).first()
    if stock:
        db.delete(stock)
        db.commit()
    return RedirectResponse("/stocks", status_code=302)


# ================= SUPPRIMER UN RAYON ENTIER =================

@app.post("/stocks/supprimer-rayon")
def supprimer_rayon(
    request: Request,
    rayon: str = Form(...),
    db: Session = Depends(get_db)
):
    if not request.session.get("admin") and request.session.get("profil","") != "ENTREPRISE" and request.session.get("user_role","") != "ENTREPRISE":
        return RedirectResponse("/login")
    # Supprime TOUS les articles du rayon d'un coup
    db.query(Stock).filter(Stock.rayon == rayon).delete()
    db.commit()
    return RedirectResponse("/stocks", status_code=302)


# ======================= PAGE UPDATE =======================

@app.get("/update", response_class=HTMLResponse)
def page_update(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("admin") and request.session.get("profil","") != "ENTREPRISE" and request.session.get("user_role","") != "ENTREPRISE":
        return RedirectResponse("/login")

    stocks = db.query(Stock).order_by(Stock.rayon, Stock.produit).all()

    # Regrouper par rayon
    rayons_dict = defaultdict(list)
    for s in stocks:
        rayons_dict[s.rayon].append(s)

    # Construire les sections par rayon
    sections_html = ""
    for rayon, items in sorted(rayons_dict.items()):
        rows_html = ""
        for s in items:
            rows_html += f"""
            <tr>
                <td>
                    <form action="/update/article-nom" method="post" class="inline-form">
                        <input type="hidden" name="produit_id" value="{s.id}">
                        <input type="text" name="nouveau_nom" value="{s.produit.capitalize()}"
                               class="update-input">
                        <button type="submit" class="btn-update-blue" title="Modifier le nom">
                            ✏️ Renommer
                        </button>
                    </form>
                </td>
                <td>
                    <form action="/update/article-prix" method="post" class="inline-form">
                        <input type="hidden" name="produit_id" value="{s.id}">
                        <input type="number" name="nouveau_prix" value="{int(s.prix)}"
                               min="1" class="update-input update-input-sm">
                        <span style="color:#64748b; font-size:12px;">FCFA</span>
                        <button type="submit" class="btn-update-green" title="Modifier le prix">
                            💰 Maj prix
                        </button>
                    </form>
                </td>
                <td style="color:#64748b; font-size:13px; min-width:90px;">{s.quantite} unités</td>
            </tr>
            """

        sections_html += f"""
        <div class="update-section">
            <div class="update-rayon-bar">
                <span class="update-rayon-label">📂 {rayon.upper()}</span>
                <form action="/update/rayon-nom" method="post" class="inline-form">
                    <input type="hidden" name="ancien_nom" value="{rayon}">
                    <input type="text" name="nouveau_nom" value="{rayon.capitalize()}"
                           class="update-input update-input-rayon">
                    <button type="submit" class="btn-update-orange" title="Renommer ce rayon">
                        🗂 Renommer le rayon
                    </button>
                </form>
            </div>
            <table class="update-table">
                <thead>
                    <tr>
                        <th>Nom de l'article</th>
                        <th>Prix unitaire</th>
                        <th>Stock actuel</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """

    toast_html = ""
    msg = request.query_params.get("msg")
    if msg:
        color = "#22c55e" if "succès" in msg.lower() or "mis" in msg.lower() else "#f87171"
        toast_html = f"""
        <div id="toast-notif" style="
            position:fixed; top:28px; right:28px; z-index:9999;
            background: rgba(15,23,42,0.97);
            border: 1px solid {color};
            border-radius: 16px; padding: 16px 26px;
            color:{color}; font-weight:700; font-size:15px;
            box-shadow: 0 0 24px {color}44;
            animation: fadeInRight 0.4s ease-out;">
            ✅ {msg}
        </div>
        <style>
        @keyframes fadeInRight {{
            from {{ opacity:0; transform:translateX(30px); }}
            to {{ opacity:1; transform:translateX(0); }}
        }}
        </style>
        <script>
            setTimeout(() => {{
                const t = document.getElementById('toast-notif');
                if (t) t.style.display = 'none';
            }}, 3500);
        </script>
        """

    return f"""
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap"
              rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
              rel="stylesheet">
        {COMMON_STYLE}
        <style>
            /* ---- SECTIONS ---- */
            .update-section {{
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 20px; overflow: hidden;
                margin-bottom: 36px;
            }}
            .update-rayon-bar {{
                display: flex; align-items: center; justify-content: space-between;
                flex-wrap: wrap; gap: 12px;
                background: rgba(251,146,60,0.07);
                border-bottom: 1px solid rgba(251,146,60,0.2);
                padding: 14px 22px;
            }}
            .update-rayon-label {{
                font-weight: 900; font-size: 0.95rem;
                letter-spacing: 2px; text-transform: uppercase;
                color: #fb923c;
            }}

            /* ---- TABLE ---- */
            .update-table {{ width:100%; border-collapse:collapse; }}
            .update-table thead tr {{
                background: rgba(255,255,255,0.04);
                border-bottom: 1px solid rgba(255,255,255,0.08);
            }}
            .update-table th {{
                padding: 11px 20px; font-size: 11px;
                text-transform: uppercase; letter-spacing: 1.5px;
                color: #64748b; font-weight: 700; text-align: left;
            }}
            .update-table td {{
                padding: 13px 20px;
                border-bottom: 1px solid rgba(255,255,255,0.04);
                vertical-align: middle;
            }}
            .update-table tr:last-child td {{ border-bottom: none; }}
            .update-table tr:hover {{ background: rgba(255,255,255,0.025); }}

            /* ---- INPUTS ---- */
            .inline-form {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
            .update-input {{
                background: rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.12);
                color: #f1f5f9; border-radius: 10px;
                padding: 8px 13px; font-size: 14px;
                transition: 0.25s; min-width: 160px;
            }}
            .update-input:focus {{
                border-color: var(--neon-blue); outline: none;
                box-shadow: 0 0 0 3px rgba(0,212,255,0.15);
            }}
            .update-input-sm  {{ min-width: 100px; max-width: 130px; }}
            .update-input-rayon {{ min-width: 180px; }}

            /* ---- BOUTONS ---- */
            .btn-update-blue, .btn-update-green, .btn-update-orange {{
                border: none; border-radius: 10px;
                padding: 8px 16px; font-weight: 700; font-size: 13px;
                cursor: pointer; transition: 0.3s; white-space: nowrap;
            }}
            .btn-update-blue {{
                background: rgba(0,212,255,0.12); color: #00d4ff;
                border: 1px solid rgba(0,212,255,0.3);
            }}
            .btn-update-blue:hover {{
                background: rgba(0,212,255,0.22);
                box-shadow: 0 0 14px rgba(0,212,255,0.35);
            }}
            .btn-update-green {{
                background: rgba(34,197,94,0.12); color: #22c55e;
                border: 1px solid rgba(34,197,94,0.3);
            }}
            .btn-update-green:hover {{
                background: rgba(34,197,94,0.22);
                box-shadow: 0 0 14px rgba(34,197,94,0.35);
            }}
            .btn-update-orange {{
                background: rgba(251,146,60,0.12); color: #fb923c;
                border: 1px solid rgba(251,146,60,0.3);
            }}
            .btn-update-orange:hover {{
                background: rgba(251,146,60,0.22);
                box-shadow: 0 0 14px rgba(251,146,60,0.35);
            }}

            /* ---- HEADER ---- */
            .update-page-header {{ margin-bottom: 36px; }}
            .update-page-header h1 {{ font-size: 2.3rem; }}
            .update-page-header p {{ color: #64748b; font-size: 15px; }}

            /* ---- VIDE ---- */
            .empty-state {{
                text-align:center; padding: 80px 20px; color: #334155;
            }}
            .empty-state span {{ font-size: 3.5rem; display:block; margin-bottom: 16px; }}
        </style>
    </head>
    <body>
        {sidebar(request)}
        {toast_html}
        <div class="main-content">
            <div class="update-page-header">
                <h1>✏️ Update — Modification du catalogue</h1>
                <p>
                    Modifiez ici le nom et le prix de chaque article, ou renommez un rayon entier.
                    Les changements sont appliqués instantanément dans toute l'application.
                </p>
            </div>

            {"".join([sections_html]) if stocks else
             '<div class="empty-state"><span>📭</span>Aucun article en base — ajoutez des produits depuis Gestion Stock.</div>'}
        </div>
    </body>
    </html>
    """


# ---- UPDATE : Nom article ----
@app.post("/update/article-nom")
def update_article_nom(
    request: Request,
    produit_id: int = Form(...),
    nouveau_nom: str = Form(...),
    db: Session = Depends(get_db)
):
    stock = db.query(Stock).filter(Stock.id == produit_id).first()
    if stock:
        stock.produit = nouveau_nom.strip().lower()
        db.commit()
    return RedirectResponse(f"/update?msg=Article+mis+à+jour+avec+succès", status_code=302)


# ---- UPDATE : Prix article ----
@app.post("/update/article-prix")
def update_article_prix(
    request: Request,
    produit_id: int = Form(...),
    nouveau_prix: float = Form(...),
    db: Session = Depends(get_db)
):
    stock = db.query(Stock).filter(Stock.id == produit_id).first()
    if stock:
        stock.prix = nouveau_prix
        db.commit()
    return RedirectResponse(f"/update?msg=Prix+mis+à+jour+avec+succès", status_code=302)


# ---- UPDATE : Nom rayon ----
@app.post("/update/rayon-nom")
def update_rayon_nom(
    request: Request,
    ancien_nom: str = Form(...),
    nouveau_nom: str = Form(...),
    db: Session = Depends(get_db)
):
    nouveau = nouveau_nom.strip().lower()
    # Mettre à jour tous les articles de ce rayon
    db.query(Stock).filter(Stock.rayon == ancien_nom).update({"rayon": nouveau})
    db.commit()
    return RedirectResponse(f"/update?msg=Rayon+renommé+avec+succès", status_code=302)


#----------------DETAIL VENTE-----------

@app.get("/vente/{vente_id}", response_class=HTMLResponse)
def detail_vente(vente_id: int, db: Session = Depends(get_db)):
    vente = db.query(Vente).filter(Vente.id == vente_id).first()

    if not vente:
        return "<body style='background:#0f172a; color:white;'><h2>Vente introuvable</h2></body>"

    # Construction du tableau aligné
    items_rows = "".join([
        f"""
        <div class="row-item">
            <span class="cell-name">{item.produit} <small style="color:#64748b">({item.rayon})</small></span>
            <span class="cell-qty">{item.quantite}</span>
            <span class="cell-price">{item.prix_unitaire:,}</span>
            <span class="cell-subtotal">{item.total:,} FCFA</span>
        </div>
        """ for item in vente.items
    ])

    return f"""
    <html>
    <head>
        <style>
            body {{ background: #0f172a; color: #cbd5e1; font-family: 'Inter', sans-serif; padding: 60px; }}
            .main-content {{ max-width: 800px; margin: 0 auto; }}
            
            h1 {{ color: white; font-size: 2.2rem; margin-bottom: 5px; }}
            .subtitle {{ color: #60a5fa; margin-bottom: 40px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }}
            
            .client-bar {{ padding: 15px 0; border-bottom: 1px solid #1e293b; margin-bottom: 30px; color: #94a3b8; }}
            .client-bar b {{ color: white; }}

            /* Système d'alignement par colonnes */
            .header-table {{ display: flex; padding: 10px 0; color: #64748b; font-weight: bold; font-size: 0.8rem; text-transform: uppercase; border-bottom: 1px solid #334155; }}
            .row-item {{ display: flex; padding: 20px 0; border-bottom: 1px solid #1e293b; align-items: center; }}
            
            .cell-name {{ flex: 2; font-weight: 500; color: white; }}
            .cell-qty {{ flex: 0.4; text-align: center; }}
            .cell-price {{ flex: 1; text-align: right; }}
            .cell-subtotal {{ flex: 1; text-align: right; color: #60a5fa; font-weight: bold; }}

            .total-final {{ text-align: right; padding-top: 30px; font-size: 2.5rem; color: white; font-weight: 900; }}
            .total-final span {{ color: #60a5fa; }}

            .nav-buttons {{ margin-top: 60px; display: flex; gap: 30px; }}
            .nav-link {{ color: #94a3b8; text-decoration: none; border-bottom: 1px solid transparent; transition: 0.3s; }}
            .nav-link:hover {{ color: white; border-bottom-color: #60a5fa; }}
        </style>
    </head>
    <body>
        <div class="main-content">
            <h1>DÉTAILS VENTE</h1>
            <div class="subtitle">Récapitulatif Officiel #{vente.id}</div>
            
            <div class="client-bar">
                PROFIL : <b>{vente.sexe}</b> &nbsp;|&nbsp; TRANCHE D'ÂGE : <b>{vente.age} ANS</b>
            </div>

            <div class="header-table">
                <span class="cell-name">Produit</span>
                <span class="cell-qty">Qté</span>
                <span class="cell-price">Prix Unit.</span>
                <span class="cell-subtotal">Total</span>
            </div>

            {items_rows}

            <div class="total-final">
                TOTAL : <span>{vente.total:,} FCFA</span>
            </div>

            <div class="nav-buttons">
                <a href="/vente" class="nav-link">🧾 Liste des ventes</a>
                <a href="/" class="nav-link" style="color: #60a5fa;">➕ Nouvelle vente client</a>
            </div>
        </div>
    </body>
    </html>
    """
    
 #-------------MINI MOTEUR IA---------------
 
def mini_model_business(ventes):

    if not ventes:
        return {
            "trend_rayon": None,
            "growth_score": 0,
            "insight": "Aucune donnée disponible"
        }

    rayon_count = defaultdict(int)
    total_ventes = len(ventes)

    for v in ventes:
        if v.items:
            for item in v.items:
                rayon_count[item.rayon] += 1

    trend_rayon = max(rayon_count, key=rayon_count.get)

    growth_score = rayon_count[trend_rayon] / total_ventes

    if growth_score > 0.5:
        insight = f"🔥 Forte domination du rayon {trend_rayon}"
    elif growth_score > 0.3:
        insight = f"📈 Rayon {trend_rayon} en croissance"
    else:
        insight = f"⚠️ Marché fragmenté, aucun rayon dominant"

    return {
        "trend_rayon": trend_rayon,
        "growth_score": round(growth_score, 2),
        "insight": insight
    }
    
    
 #--------------MOTEUR DE RECOMMANDATION IA---------------
 
def recommend_products(ventes, age, sexe):

   def convertir_age(age):
       mapping = {
           "12-18": 15, "18-25": 22, "19-25": 22,
           "26-39": 32, "40+": 45, "40-55": 47, "55+": 60
       }
       return mapping.get(age, None)

   target_age = convertir_age(age)
   if target_age is None:
       target_age = 32  # Valeur par défaut si âge inconnu
   target_sexe = 1 if sexe == "Homme" else 0

   produit_score = defaultdict(float)

   for v in ventes:
       age_v = convertir_age(v.age)
       sexe_v = 1 if v.sexe == "Homme" else 0

       if age_v is None:
          continue

        # 🔥 similarité profil
       age_diff = abs(target_age - age_v)
       sexe_match = 1 if sexe_v == target_sexe else 0

       score = (1 / (1 + age_diff)) + sexe_match

       if v.items:
          for item in v.items:
              produit_score[item.produit] += score * item.quantite

   if not produit_score:
       return []

    # tri
   recommandations = sorted(produit_score.items(), key=lambda x: x[1], reverse=True)

   return recommandations[:5]  # top 5 produits
   
   
 #-----------RECOMMANDATION ASSOCIE IA---------------

def recommend_smart(ventes, panier):

    if not panier:
        return []

    produits_panier = [p['produit'] for p in panier]

    association = defaultdict(int)

    for v in ventes:
        produits = [item.produit for item in v.items]

        # 🔥 vérifier si au moins 1 produit du panier est présent
        if any(p in produits for p in produits_panier):

            for p in produits:

                # ❌ ne pas recommander déjà acheté
                if p not in produits_panier:

                    # 🔥 pondération (plus fort si plusieurs produits match)
                    score = sum(1 for x in produits_panier if x in produits)

                    association[p] += score

    if not association:
        return []

    recommandations = sorted(association.items(), key=lambda x: x[1], reverse=True)

    return recommandations[:5]
    
#--------------RECOMMANDATION AVANCE IA----------------

def recommend_advanced(ventes, panier, age, sexe):

    if not panier:
        return []

    def convertir_age(age):
        if age == "12-18":
            return 15
        elif age == "19-25":
            return 22
        elif age == "26-39":
            return 32
        elif age == "40+":
            return 45
        return 0

    target_age = convertir_age(age)
    target_sexe = 1 if sexe == "Homme" else 0

    produits_panier = [p['produit'] for p in panier]

    scores = defaultdict(float)

    for v in ventes:

        age_v = convertir_age(v.age)
        sexe_v = 1 if v.sexe == "Homme" else 0

        # 🔥 similarité profil
        age_diff = abs(target_age - age_v)
        sexe_match = 1 if sexe_v == target_sexe else 0

        profil_score = (1 / (1 + age_diff)) + sexe_match

        produits = [item.produit for item in v.items]

        if any(p in produits for p in produits_panier):

            for item in v.items:
                if item.produit not in produits_panier:

                    scores[item.produit] += profil_score * item.quantite

    if not scores:
        return []

    recommandations = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return recommandations[:5]

#--------------STATISTIQUE--------------

@app.get("/stats", response_class=HTMLResponse)
def stats(period: str = "all", db: Session = Depends(get_db)):
    ventes = db.query(Vente).all()
    ai = mini_model_business(ventes)
    now = datetime.utcnow()

    # ---------------- FILTRE TEMPS ----------------
    if period == "day":
        ventes = [v for v in ventes if v.date_achat and v.date_achat.date() == now.date()]
    elif period == "week":
        ventes = [v for v in ventes if v.date_achat and v.date_achat >= now - timedelta(days=7)]
    elif period == "month":
        ventes = [v for v in ventes if v.date_achat and v.date_achat >= now - timedelta(days=30)]

    # ---------------- KPI ----------------
    ca_total = sum(v.total or 0 for v in ventes)
    total_ventes = len(ventes)
    panier_moyen = ca_total / total_ventes if total_ventes > 0 else 0

    # ---------------- STATS ----------------
    produit_stats = defaultdict(int)
    rayon_stats = defaultdict(float)

    for v in ventes:
        if v.items:
            for item in v.items:
                produit_stats[item.produit] += item.quantite or 0
                rayon_stats[item.rayon] += item.total or 0

    # ---------------- TOP ----------------
    top_produits = sorted(produit_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    top_rayons = sorted(rayon_stats.items(), key=lambda x: x[1], reverse=True)[:3]

    # ---------------- DATAFRAME ----------------
    # C'est ici que l'erreur se produisait : alignement strict requis
    df_rayon = pd.DataFrame({
        "rayon": list(rayon_stats.keys()), 
        "total": list(rayon_stats.values())
    })

    df_prod = pd.DataFrame({
        "produit": list(produit_stats.keys()), 
        "quantite": list(produit_stats.values())
    })

    # ---------------- GRAPHIQUES ----------------
    
    # 📊 CONFIGURATION DIAGRAMME CAMEMBERT (VIVIDE)
    chart_rayon = px.pie(
        df_rayon, names="rayon", values="total",
        color_discrete_sequence=px.colors.qualitative.Vivid,
        hole=0.4
    )
    chart_rayon.update_layout(
        showlegend=True,
        legend=dict(font=dict(color="#7dd3fc"), orientation="h", yanchor="bottom", y=-0.2),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=30, l=10, r=10)
    )

    # 📊 CONFIGURATION DIAGRAMME EN BANDES (PRO)
    chart_prod = px.bar(
        df_prod, x="produit", y="quantite",
        labels={'produit': 'Produits', 'quantite': 'Unités Vendues'}
    )
    chart_prod.update_traces(marker_color='#00d4ff', marker_line_color='#f8fafc', marker_line_width=1.5)
    chart_prod.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#7dd3fc"),
        xaxis=dict(showgrid=False, title_font=dict(size=14)),
        yaxis=dict(showgrid=True, gridcolor="#334155", title_font=dict(size=14))
    )

    # ---------------- HTML ----------------
    return f"""
    <html>
    <head>
        <title>Dashboard | SDE Admin</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {COMMON_STYLE}
    </head>
    <body>
        <div class="sidebar">
            <h2>🛒 SDE Admin</h2>
            <hr style="border-color:#334155;">
            <a href="/">🏠 Menu Principal</a>
            <hr style="border-color:#334155;">
            <a href="/vente">🧾 Ventes</a>
            <a href="/produits">📦 Produits</a>
            <a href="/clients">👥 Clients</a>
        </div>

        <div class="main-content">
            <h1>📊 Statistiques Globales</h1>
            
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card p-4 text-center">
                        <h2>💰 Chiffre d'Affaires</h2>
                        <div class="value mb-2" style="color: #00FF00;">{ca_total:,.0f} FCFA</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card p-4 text-center">
                        <h2>🧾 Nombre de Ventes</h2>
                        <div class="value mb-2" style="color: #00FF00;">{total_ventes}</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card p-4 text-center">
                        <h2>🛒 Panier Moyen</h2>
                        <div class="value mb-2" style="color: #00FF00;">{panier_moyen:.0f} FCFA</div>
                    </div>
                </div>
            </div>

            <div class="row mt-4 g-4">
                <div class="col-md-8">
                    <div class="card p-3">{chart_prod.to_html(full_html=False)}</div>
                </div>
                <div class="col-md-4">
                    <div class="card p-4">
                        <h2>🧠 Insight IA</h2>
                        <p class="text-vert-fluo" style="font-size:1.1rem; line-height:1.6;">{ai["insight"]}</p>
                        <hr style="border-color:#334155;">
                        <div class="text-white mb-2">Score de croissance</div>
                        <div class="value mb-3" style="color: #00FF00;">{ai["growth_score"] * 100:.1f}%</div>
                        <div style="background:rgba(0,212,255,0.06); border-left:3px solid #00d4ff;
                                    border-radius:0 12px 12px 0; padding:14px 16px; margin-top:6px;">
                            <p style="font-size:0.82rem; color:#94a3b8; margin:0; line-height:1.7;">
                                💡 <b style="color:#cbd5e1;">Comment lire ce score ?</b><br>
                                Le score de croissance mesure la concentration des ventes sur un seul rayon.
                                Au-delà de <b style="color:#00d4ff;">60 %</b>, un rayon domine nettement le marché.
                                En dessous de <b style="color:#fcd34d;">30 %</b>, les ventes sont bien réparties —
                                signe d'une clientèle diversifiée. Utilisez cet indicateur pour orienter
                                vos décisions de réassort et de mise en avant des produits.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="card p-3">
                        {chart_rayon.to_html(full_html=False)}
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card p-4">
                        <h2>🏆 Top Rayons</h2>
                        {''.join([f"<div class='d-flex justify-content-between border-bottom py-2'><span>{r}</span><b>{t:,.0f} FCFA</b></div>" for r,t in top_rayons])}
                        <div style="background:rgba(34,197,94,0.06); border-left:3px solid #22c55e;
                                    border-radius:0 12px 12px 0; padding:14px 16px; margin-top:20px;">
                            <p style="font-size:0.82rem; color:#94a3b8; margin:0; line-height:1.7;">
                                📊 <b style="color:#cbd5e1;">Lecture du classement</b><br>
                                Ce classement reflète le <b style="color:#22c55e;">chiffre d'affaires cumulé</b>
                                généré par rayon sur l'ensemble de l'historique des ventes.
                                Un rayon en tête indique une forte demande client — pensez à maintenir
                                son stock en priorité et à surveiller les ruptures pour ne pas
                                manquer de ventes potentielles.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
          
 #------------DAHSBOARD VENTE----------
 
@app.get("/vente", response_class=HTMLResponse)
def liste_ventes(db: Session = Depends(get_db)):
    ventes = db.query(Vente).order_by(Vente.id.desc()).all()
    cards = ""
    for v in ventes:
        cards += f"""
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-body p-4">
                    <h5 class="card-title" style="color:var(--neon-blue);">🧾 Vente #{v.id}</h5>
                    <p class="mb-1">👤 Client : <b>{v.age} ans | {v.sexe}</b></p>
                    <p>💰 Montant : <b style="color:#16a34a; font-size:1.2rem;">{v.total} FCFA</b></p>
                    <a href="/vente/{v.id}" class="btn btn-outline-primary btn-sm w-100">Détails de la transaction</a>
                </div>
            </div>
        </div>
        """

    return f"""
    <html>
    <head>
        <title>Ventes | SDE</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {COMMON_STYLE}
    </head>
    <body>
        <div class="container-fluid-custom">
            <div class="d-flex justify-content-between align-items-center mb-5">
                <h1>🧾 Historique des Ventes</h1>
                
            </div>
            <div class="row">{cards}
                <a href="/stats" class="btn btn-neon">⬅ Retour dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """
    
 #------------ DASHBOARD PRODUIT--------  
 
@app.get("/produits", response_class=HTMLResponse)
def produits(db: Session = Depends(get_db)):
    ventes = db.query(Vente).all()
    produits_dict = defaultdict(int)
    for v in ventes:
        if v.items:
            for i in v.items:
                produits_dict[i.produit] += i.quantite or 0
    top = sorted(produits_dict.items(), key=lambda x: x[1], reverse=True)

    cards = "".join([f"""
        <div class="col-md-3 mb-4">
            <div class="card p-4 text-center">
                <h5 class="mb-3" style="color: #00BFFF;">📦 {p}</h5>
                <div class="value" style="color:white;">{q}</div>
                <small class="mb-2" style="color: #00FF00; font-weight: bold;">Unités vendues</small>
            </div>
        </div>
        """ for p, q in top])

    return f"""
    <html>
    <head>
        <title>Produits | SDE</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {COMMON_STYLE}
    </head>
    <body>
        <div class="container-fluid-custom">
            <div class="d-flex justify-content-between align-items-center mb-5">
                <h1>📦 Performance Produits</h1>
                <a href="/stats" class="btn btn-neon">⬅ Retour dashboard</a>
            </div>
            <div class="row">{cards}</div>
        </div>
    </body>
    </html>
    """
 #-------------DASHBOARD CLIENT--------
 
@app.get("/clients", response_class=HTMLResponse)
def clients(db: Session = Depends(get_db)):
    ventes = db.query(Vente).all()
    sexe_data = defaultdict(float)
    age_data = defaultdict(float)
    for v in ventes:
        sexe_data[v.sexe] += v.total or 0
        age_data[v.age] += v.total or 0

    sexe_cards = "".join([f"""
        <div class="col-md-6 mb-3">
            <div class="card p-4 text-center">
                <h4 style="color: white;">🚻 {s}</h4>
                <div class="value" style="color: #16a34a; font-weight: bold;">
    {t:,.0f} FCFA</div>
            </div>
        </div>
        """ for s, t in sexe_data.items()])

    age_cards = "".join([f"""
        <div class="col-md-3 mb-3">
            <div class="card p-3 text-center">
                <h6>🎂 {a} ans</h6>
                <div style="font-size:1.2rem; font-weight:bold; color:#16a34a;">{t:,.0f}</div>
            </div>
        </div>
        """ for a, t in age_data.items()])

    return f"""
    <html>
    <head>
        <title>Analyse Clients | SDE</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {COMMON_STYLE}
    </head>
    <body>
        <div class="container-fluid-custom">
            <div class="d-flex justify-content-between align-items-center mb-5">
                <h1>👥 Analyse de la Clientèle</h1>
                <a href="/stats" class="btn btn-neon">⬅ Retour dashboard</a>
            </div>
            
            <h3 class="mb-4,">Répartition par Sexe (CA)</h3>
            <div class="row">{sexe_cards}</div>

            <h3 class="mb-4">Répartition par Tranche d'Âge</h3>
            <div class="row">{age_cards}</div>
        </div>
    </body>
    </html>
    """

 #------------PREDICTIONS---------------

@app.get("/prediction", response_class=HTMLResponse)
def prediction(request: Request, db: Session = Depends(get_db)):
    ventes = db.query(Vente).all()
    
    # Récupération des données de session
    panier = request.session.get("panier", [])
    age_session = request.session.get("age", "26-39")
    sexe_session = request.session.get("sexe", "Femme")

    # --- LOGIQUE IA ---
    reco = recommend_products(ventes, age_session, sexe_session)
    
    data = []
    def convertir_age(age):
        mapping = {
            "12-18": 15, "18-25": 22, "19-25": 22,
            "26-39": 32, "40+": 45, "40-55": 47, "55+": 60
        }
        return mapping.get(age, 32)

    for v in ventes:
        if v.items:
            for item in v.items:
                data.append({
                    "age": convertir_age(v.age),
                    "sexe": 1 if v.sexe == "Homme" else 0,
                    "rayon": item.rayon
                })

    df = pd.DataFrame(data)
    if df.empty:
        return f"{sidebar(request)}<div class='main-content'><h3>Pas assez de données pour l'analyse.</h3></div>"

    X = df[["age", "sexe"]]
    y = df["rayon"]

    # LogisticRegression nécessite au minimum 2 classes différentes dans les données
    if y.nunique() < 2:
        best_rayon = y.iloc[0]
        best_score = 1.0
        level = "DONNÉES INSUFFISANTES ⚠️"
        results = [(best_rayon, 1.0)]
        graph_html = "<p style='color:#94a3b8;'>Pas assez de variété dans les données pour générer un graphique.</p>"
    else:
        try:
            model = LogisticRegression(max_iter=200)
            model.fit(X, y)
            client_actuel = [[convertir_age(age_session), 1 if sexe_session == "Homme" else 0]]
            proba = model.predict_proba(client_actuel)[0]
            classes = model.classes_
            results = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)
            best_rayon, best_score = results[0]
            level = "TRÈS FIABLE 🔥" if best_score > 0.6 else "MOYENNEMENT FIABLE ⚠️"
            df_plot = pd.DataFrame(results, columns=["rayon", "proba"])
            fig = px.bar(df_plot, x="rayon", y="proba",
                         color="proba", color_continuous_scale='Viridis',
                         labels={'rayon': 'Rayons', 'proba': 'Probabilité'})
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#f8fafc"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#334155"),
                margin=dict(t=10, b=10, l=10, r=10),
                height=350
            )
            graph_html = fig.to_html(full_html=False)
        except Exception:
            best_rayon = y.mode()[0]
            best_score = 0.0
            level = "DONNÉES INSUFFISANTES ⚠️"
            results = [(best_rayon, 1.0)]
            graph_html = "<p style='color:#94a3b8;'>Graphique indisponible — données insuffisantes.</p>"

    # --- ÉLÉMENTS HTML ---
    prob_cards = "".join([
        f"""<div class="d-flex justify-content-between align-items-center p-3 mb-2" 
                 style="background:rgba(255,255,255,0.03); border-radius:12px; border-left:4px solid #00d4ff;">
            <span style="font-weight:600;">{r}</span>
            <span class="text-vert-fluo">{p*100:.1f}%</span>
        </div>""" for r, p in results[:4]
    ])

    return f"""
    <html>
    <head>
        <title>IA Predictions | SDE LUXE</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {COMMON_STYLE}
    </head>
    <body>
        {sidebar(request)}

        <div class="main-content">
            <div class="d-flex justify-content-between align-items-center mb-5">
                <h1>🔮 Prédictions Intelligence Artificielle</h1>
                <a href="/stats" class="btn-neon">⬅ Retour Dashboard</a>
            </div>

            <div class="card p-5 mb-5" style="border: 2px solid #00d4ff; background: linear-gradient(145deg, #1e293b, #0f172a); box-shadow: 0 0 30px rgba(0, 212, 255, 0.15);">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h4 class="text-vert-fluo mb-3" style="letter-spacing:2px;">CIBLE DÉTECTÉE</h4>
                        <div style="font-size: 1.5rem; line-height: 1.8;">
                            Le client (Profil: <span class="text-vert-fluo">{sexe_session}</span>, <span class="text-vert-fluo">{age_session} ans</span>) 
                            se dirigera probablement vers le rayon : <br>
                            <span style="font-size: 3rem; font-weight: 900; color: #fff; text-shadow: 0 0 15px rgba(255,255,255,0.3);">
                                🛒 {best_rayon.upper()}
                            </span>
                        </div>
                    </div>
                    <div class="col-md-4 text-center">
                        <div class="p-3" style="border-radius:20px; background: rgba(34, 197, 94, 0.1); border: 1px solid var(--neon-green);">
                            <div style="font-size: 0.9rem; opacity: 0.8;">INDICE DE CONFIANCE</div>
                            <div style="font-size: 2.5rem; font-weight: 800;" class="text-vert-fluo">{best_score*100:.1f}%</div>
                            <div style="font-size: 0.8rem; font-weight: bold;">{level}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-md-7">
                    <div class="card p-4 h-100">
                        <h3 class="text-vert-fluo mb-4" style="font-size:1.2rem;">📊 Analyse des Probabilités</h3>
                        {graph_html}
                    </div>
                </div>

                <div class="col-md-5">
                    <div class="card p-4 h-100">
                        <h3 class="text-vert-fluo mb-4" style="font-size:1.2rem;">🏆 Top Rayons Potentiels</h3>
                        {prob_cards}
                        <p class="mt-4" style="font-size:0.85rem; opacity:0.5; font-style:italic;">
                            * Ces prédictions sont générées en temps réel via une régression logistique basée sur votre historique de ventes.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
#------------RECEPTIONNAIRE-------------------

@app.post("/add")
def add_to_cart(request: Request, rayon: str = Form(...), produit: str = Form(...), quantite: int = Form(...), db: Session = Depends(get_db)):
    # ✅ Prix lu depuis la DB Stock
    stock_ref = db.query(Stock).filter(Stock.produit == produit).first()
    prix = int(stock_ref.prix) if stock_ref else 0
    
    panier = request.session.get("panier", [])
    
    # 2. On ajoute l'article avec la quantité choisie
    panier.append({
        "rayon": rayon,
        "produit": produit,
        "quantite": quantite, # <--- C'est ici que la quantité est enregistrée
        "prix": prix
    })
    
    request.session["panier"] = panier
    return RedirectResponse(url="/prediction", status_code=303)
     
#-------------EXPORT CSV---------------
   
@app.get("/export")
def export_csv(db: Session = Depends(get_db)):

    ventes = db.query(Vente).all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Age", "Sexe", "Produit", "Rayon", "Quantité", "Prix", "Total"])

    for v in ventes:
        for item in v.items:
            writer.writerow([
                v.id,
                v.age,
                v.sexe,
                item.produit,
                item.rayon,
                item.quantite,
                item.prix_unitaire,
                item.total
            ])

    output.seek(0)

    return StreamingResponse(output, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ventes.csv"})

 #----------------LOGIN--------------------
 


# Routes /register et /login gérées par auth.py

# Routes /login et /register gérées par auth.py

# POST /login géré par auth.py (auth_router)

# GET /logout géré par auth.py (auth_router)

#------------HISTORIQUE----------------------

@app.get("/admin/historique", response_class=HTMLResponse)
def voir_historique(request: Request, db: Session = Depends(get_db)):
    # 1. Vérification de sécurité (Admin seulement)
    if not request.session.get("admin") and request.session.get("profil","") != "ENTREPRISE" and request.session.get("user_role","") != "ENTREPRISE":
        return RedirectResponse("/login")
    
    # 2. Récupération des ventes regroupées (Parent -> Vente)
    # On utilise .options(joinedload(Vente.items)) si tu veux optimiser, 
    # mais SQLAlchemy gère les relations automatiquement ici.
    ventes = db.query(Vente).order_by(Vente.date_vente.desc()).all()

    # 3. Préparation du contenu principal
    main_body = ""
    
    if not ventes:
        # MESSAGE EN GRAND, GRAS ET FLUO BLEU SI VIDE
        main_body = f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 70vh; flex-direction: column; text-align: center;">
            <h1 style="font-size: 5rem; margin-bottom: 10px;">AUCUNE VENTE</h1>
            <h2 style="font-size: 2rem; color: var(--neon-blue); text-transform: uppercase; letter-spacing: 5px;">Le registre est vide</h2>
            <br><br>
            <a href="/admin" class="btn-neon">RETOUR AU DASHBOARD</a>
        </div>
        """
    else:
        # Construction du tableau des ventes
        rows = ""
        for v in ventes:
            date_str = v.date_vente.strftime("%d/%m/%Y %H:%M")
            
            # On liste les articles du panier pour cette vente
            items_html = "<ul style='list-style: none; padding: 0; margin: 0;'>"
            for item in v.items:
                items_html += f"""
                <li style='margin-bottom: 5px; border-left: 2px solid var(--neon-green); padding-left: 10px;'>
                    <span class='text-vert-fluo'>{item.produit}</span> 
                    <span style='color: #94a3b8;'> (x{item.quantite})</span> 
                    <span style='float: right; color: #cbd5e1;'>{item.total:,} F</span>
                </li>"""
            items_html += "</ul>"

            rows += f"""
            <tr style="border-bottom: 1px solid rgba(0, 212, 255, 0.1); transition: 0.3s;">
                <td style="padding: 20px; vertical-align: top;">
                    <span style="color: var(--neon-blue); font-weight: bold;">{date_str}</span><br>
                    <small style="color: #64748b;">ID: #{v.id}</small>
                </td>
                <td style="padding: 20px; vertical-align: top;">
                    <span class="text-vert-fluo">{v.sexe}</span><br>
                    <span style="font-size: 0.85em; color: #94a3b8;">Tranche: {v.age}</span>
                </td>
                <td style="padding: 20px;">{items_html}</td>
                <td style="padding: 20px; text-align: right; vertical-align: middle;">
                    <strong style="color: var(--neon-blue); font-size: 1.2rem; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);">
                        {v.total:,} FCFA
                    </strong>
                </td>
            </tr>
            """

        main_body = f"""
        <div class="container-fluid-custom">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
                <h1>📜 Historique des Transactions</h1>
                <a href="/client" class="btn-neon"><i class="fas fa-plus"></i> Nouvelle Vente</a>
            </div>

            <div class="card" style="overflow: hidden;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: rgba(0, 212, 255, 0.05); text-align: left;">
                            <th style="padding: 15px; color: var(--neon-blue);">DATE</th>
                            <th style="padding: 15px; color: var(--neon-blue);">CLIENT</th>
                            <th style="padding: 15px; color: var(--neon-blue);">PANIER (DÉTAILS)</th>
                            <th style="padding: 15px; color: var(--neon-blue); text-align: right;">TOTAL TRANSACTION</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
        """

    # 4. Assemblage final avec tes composants sidebar() et COMMON_STYLE
    full_html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SDE ADMIN - Historique</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        {COMMON_STYLE}
        <style>
            /* Petites corrections locales pour le tableau */
            tbody tr:hover {{
                background: rgba(255, 255, 255, 0.02);
            }}
            .main-content {{
                background-image: radial-gradient(circle at top right, rgba(0, 212, 255, 0.05), transparent);
                min-height: 100vh;
            }}
        </style>
    </head>
    <body>
        {sidebar(request)}
        <div class="main-content">
            {main_body}
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=full_html)
    
#----------------WELCOME-----------------

@app.get("/welcome", response_class=HTMLResponse)
def welcome():
    return """
    <html>
    <head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
    body {
        margin:0;
        height:100vh;
        display:flex;
        justify-content:center;
        align-items:center;
        background: radial-gradient(circle at top, #1e3a8a, #020617);
        color:white;
        text-align:center;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        overflow:hidden;
    }

    .hero-content {
        max-width: 900px;
        padding: 20px;
        animation: fadeIn 1.2s ease-out;
    }

    @keyframes fadeIn {
        from { opacity:0; transform:scale(0.95); }
        to { opacity:1; transform:scale(1); }
    }

    h1 {
        font-size: 64px; /* Grand message bien mis en valeur */
        margin-bottom: 25px;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, #93c5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }

    p {
        color:#94a3b8;
        font-size: 20px;
        margin-bottom: 40px;
        line-height: 1.6;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Le fameux bouton */
    .btn-dashboard {
        display: inline-block;
        text-decoration: none;
        padding: 20px 50px;
        font-size: 20px;
        font-weight: bold;
        text-transform: uppercase;
        border-radius: 50px;
        background: #3b82f6;
        color: white !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }

    .btn-dashboard:hover {
        transform: translateY(-5px);
        background: #2563eb;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.6);
        border-color: rgba(255,255,255,0.2);
    }

    .features-grid {
        display:flex; 
        gap:20px; 
        justify-content:center;
        margin-bottom: 50px;
    }

    .feature-tag {
        padding:12px 24px; 
        background:rgba(255,255,255,0.05); 
        border: 1px solid rgba(255,255,255,0.1);
        border-radius:100px;
        font-size: 14px;
        color: #60a5fa;
        backdrop-filter: blur(5px);
    }

    </style>
    </head>

    <body>

        <div class="hero-content">
            <h1>🚀 Dashboard Intelligent</h1>

            <p>
                La plateforme d'analyse de vente de nouvelle génération. 
                Pilotez votre supermarché avec des données précises et des prédictions IA.
            </p>

            <div class="features-grid">
                <div class="feature-tag">📊 Stats Temps Réel</div>
                <div class="feature-tag">🔮 Prédictions IA</div>
                <div class="feature-tag">🛒 Flux de Ventes</div>
            </div>

            <a href="/" class="btn-dashboard">
                ACCÉDER AU DASHBOARD
            </a>
        </div>

    </body>
    </html>
    """

