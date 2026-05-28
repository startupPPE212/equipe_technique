"""
=============================================================================
  PATCH D'INTÉGRATION — main.py
  Ce fichier explique précisément quelles lignes ajouter / modifier dans
  votre main.py existant pour activer les 3 profils.
  Copier-coller les blocs ci-dessous aux endroits indiqués.
=============================================================================
"""

# ═══════════════════════════════════════════════════════════
#  ÉTAPE 1 — IMPORTS  (ajouter juste après les imports actuels)
# ═══════════════════════════════════════════════════════════
"""
Ajouter ces lignes APRÈS la dernière ligne d'import :

from .auth               import router as auth_router
from .client_routes      import router as client_router
from .fournisseur_routes import router as fournisseur_router
"""

# ═══════════════════════════════════════════════════════════
#  ÉTAPE 2 — ENREGISTREMENT DES ROUTERS
#  (ajouter juste après  app = FastAPI()  )
# ═══════════════════════════════════════════════════════════
"""
app.include_router(auth_router)
app.include_router(client_router)
app.include_router(fournisseur_router)
"""

# ═══════════════════════════════════════════════════════════
#  ÉTAPE 3 — REMPLACER le middleware d'authentification
#  Chercher  async def auth_middleware  et remplacer tout le bloc
# ═══════════════════════════════════════════════════════════
"""
@app.middleware("http")
async def auth_middleware(request: Request, call_next):

    path = request.url.path

    # Routes publiques (aucune vérification)
    PUBLIC_ROUTES = [
        "/login", "/register",           # auth
        "/admin-login", "/welcome",       # existant
        "/static",                        # assets statiques
    ]
    if any(path.startswith(r) for r in PUBLIC_ROUTES):
        return await call_next(request)

    session = getattr(request, "session", None)
    if session is None:
        return await call_next(request)

    profil = session.get("profil")

    # ── Routes CLIENT  ────────────────────────────────────────
    CLIENT_ROUTES = ["/shop", "/cart", "/commande", "/mes-commandes"]
    if any(path.startswith(r) for r in CLIENT_ROUTES):
        if profil != "CLIENT":
            return RedirectResponse("/login")
        return await call_next(request)

    # ── Routes FOURNISSEUR  ───────────────────────────────────
    if path.startswith("/fournisseur"):
        if profil != "FOURNISSEUR":
            return RedirectResponse("/login")
        return await call_next(request)

    # ── Routes ENTREPRISE / ADMIN  ────────────────────────────
    # Rétro-compatible : on lit toujours session["admin"]
    if not session.get("admin"):
        return RedirectResponse("/login")

    return await call_next(request)
"""

# ═══════════════════════════════════════════════════════════
#  ÉTAPE 4 — ROUTE  /  (dashboard ENTREPRISE)
#  Remplacer le début de la route GET "/" pour accepter aussi
#  le profil ENTREPRISE en plus du flag admin.
# ═══════════════════════════════════════════════════════════
"""
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    # Compatible ancien flag + nouveau profil
    if not request.session.get("admin") and request.session.get("profil") != "ENTREPRISE":
        return RedirectResponse("/login")
    # ... reste du code inchangé ...
"""

# ═══════════════════════════════════════════════════════════
#  ÉTAPE 5 — PAGE /admin  (optionnel — page d'accueil ENTREPRISE)
#  Ajouter cette route si elle n'existe pas déjà, pour rediriger
#  vers le dashboard principal après la connexion.
# ═══════════════════════════════════════════════════════════
"""
@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request):
    if not request.session.get("admin"):
        return RedirectResponse("/login")
    return RedirectResponse("/")
"""

# ═══════════════════════════════════════════════════════════
#  ÉTAPE 6 — SUPPRIMER l'ancienne route /logout de main.py
#  Elle est maintenant gérée dans auth.py (GET /logout).
#  Si vous laissez les deux, FastAPI utilisera la dernière
#  enregistrée — supprimez celle de main.py pour éviter
#  les conflits.
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
#  ÉTAPE 7 — MISE À JOUR models.py
#  Remplacer votre fichier models.py par le nouveau fourni.
#  Puis relancer  Base.metadata.create_all(bind=engine)
#  (déjà fait au démarrage de l'app) pour créer les nouvelles
#  tables : users, commandes, commande_items,
#           produits_fournisseur, commandes_b2b
# ═══════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════
#  RÉSUMÉ FINAL DES FICHIERS
# ═══════════════════════════════════════════════════════════
"""
Arborescence finale du projet :

votre_app/
├── __init__.py
├── database.py          ← inchangé
├── models.py            ← REMPLACÉ  (+ User, Commande, ProduitFournisseur, CommandeB2B)
├── auth.py              ← NOUVEAU   (register, login, logout)
├── client_routes.py     ← NOUVEAU   (shop, cart, commande, mes-commandes)
├── fournisseur_routes.py← NOUVEAU   (dashboard, catalogue, commandes-b2b)
├── main.py              ← MODIFIÉ   (imports, routers, middleware)
└── populate_db.py       ← inchangé


Flux utilisateur après intégration :

  /register  →  crée le compte
      ↓ selon profil choisi
  CLIENT     →  /shop  (catalogue, panier, commandes)
  FOURNISSEUR→  /fournisseur  (catalogue gros, commandes B2B)
  ENTREPRISE →  /  (dashboard actuel — inchangé)

  /login  →  reconnexion directe vers le bon espace
  /logout →  vide la session et retourne à /login
"""
