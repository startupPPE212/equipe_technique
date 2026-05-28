"""
fournisseur_routes.py — Espace FOURNISSEUR
Routes : /fournisseur  /fournisseur/produits  /fournisseur/ajouter-produit
         /fournisseur/commandes-b2b
Thème : orange / amber
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from .database import get_db
from .models import ProduitFournisseur, CommandeB2B, User

router = APIRouter(prefix="/fournisseur", tags=["fournisseur"])


# ─────────────────────────────────────────────
#  STYLES FOURNISSEUR  (orange / amber)
# ─────────────────────────────────────────────

FOURN_STYLE = """
<style>
  *, *::before, *::after { box-sizing: border-box; }
  :root {
    --accent:  #f97316;
    --accent2: #ea580c;
    --gold:    #fbbf24;
    --dark-bg: #0f0a00;
    --card-bg: #1c1400;
    --text:    #fef3c7;
    --muted:   #92400e;
  }
  body { background: var(--dark-bg); color: var(--text);
         font-family: 'Inter', sans-serif; margin: 0; }
  h1, h2 { color: var(--accent); font-weight: 800; }
  /* SIDEBAR */
  .sidebar {
    position: fixed; width: 250px; height: 100vh; left: 0; top: 0;
    background: linear-gradient(160deg, #0f0a00 0%, #431407 100%);
    border-right: 1px solid rgba(249,115,22,0.2);
    padding: 36px 20px; z-index: 1000;
    box-shadow: 4px 0 20px rgba(0,0,0,0.5);
  }
  .sidebar-brand {
    color: #fb923c; font-size: 1.8rem; font-weight: 900;
    letter-spacing: 2px; text-align: center; margin-bottom: 8px;
    text-shadow: 0 0 15px rgba(251,146,60,0.5);
    border-bottom: 1px solid rgba(249,115,22,0.3); padding-bottom: 16px;
  }
  .sidebar-user {
    text-align: center; font-size: 12px; color: #78350f; margin-bottom: 28px;
  }
  .sidebar a {
    display: block; color: #d97706; padding: 12px 18px;
    text-decoration: none; border-radius: 12px; margin-bottom: 8px;
    transition: 0.25s; background: rgba(255,255,255,0.02); font-weight: 600;
  }
  .sidebar a:hover {
    background: rgba(249,115,22,0.15); color: #fff;
    transform: translateX(6px);
    box-shadow: 0 0 10px rgba(249,115,22,0.3);
  }
  .sidebar a.active {
    background: rgba(249,115,22,0.2); color: #fb923c;
    border-left: 3px solid #f97316;
  }
  .sidebar .logout { color: #f87171 !important; }
  .main { margin-left: 268px; padding: 40px; min-height: 100vh; }
  /* CARDS */
  .card {
    background: var(--card-bg); border: 1px solid rgba(249,115,22,0.1);
    border-radius: 20px; padding: 24px; transition: 0.3s;
  }
  .card:hover { border-color: rgba(249,115,22,0.4); }
  /* STAT CARDS */
  .stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 32px; }
  .stat-card {
    background: rgba(249,115,22,0.06); border: 1px solid rgba(249,115,22,0.15);
    border-radius: 18px; padding: 24px; position: relative; overflow: hidden;
  }
  .stat-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #92400e; }
  .stat-value { font-size: 28px; font-weight: 800; color: #fef3c7; margin-top: 4px; }
  .stat-icon { position: absolute; right: 16px; bottom: 16px; font-size: 36px; opacity: 0.4; }
  /* TABLE */
  table { width: 100%; border-collapse: collapse; }
  th { padding: 14px 16px; color: var(--accent); font-size: 12px;
       text-transform: uppercase; letter-spacing: 1px; text-align: left; }
  td { padding: 16px; border-bottom: 1px solid rgba(249,115,22,0.07); vertical-align: middle; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(249,115,22,0.04); }
  /* BOUTONS */
  .btn-primary {
    display: inline-block; padding: 12px 26px;
    background: var(--accent); color: white; border: none;
    border-radius: 12px; font-weight: 700; cursor: pointer;
    text-decoration: none; transition: 0.25s; font-size: 14px;
  }
  .btn-primary:hover {
    background: var(--accent2); box-shadow: 0 0 20px rgba(249,115,22,0.4);
    transform: translateY(-2px); color: white;
  }
  .btn-outline {
    display: inline-block; padding: 10px 22px;
    border: 1px solid rgba(249,115,22,0.3); color: #d97706;
    border-radius: 12px; text-decoration: none; font-size: 13px; transition: 0.25s;
  }
  .btn-outline:hover { border-color: var(--accent); color: #fb923c; }
  .btn-danger {
    display: inline-block; padding: 8px 16px;
    background: rgba(239,68,68,0.1); color: #f87171; border: none;
    border-radius: 10px; cursor: pointer; font-size: 13px; transition: 0.25s;
  }
  .btn-danger:hover { background: rgba(239,68,68,0.2); }
  /* FORM */
  input, select, textarea {
    background: rgba(0,0,0,0.4); border: 1px solid rgba(249,115,22,0.2);
    color: #fef3c7; border-radius: 12px; padding: 12px 16px;
    font-size: 14px; outline: none; width: 100%; transition: 0.25s;
    margin-bottom: 16px;
  }
  input:focus, select:focus, textarea:focus {
    border-color: var(--accent); box-shadow: 0 0 0 3px rgba(249,115,22,0.15);
  }
  select option { background: #1c1400; }
  label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px;
          color: #92400e; display: block; margin-bottom: 6px; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .two-col > div { margin: 0; }
  /* BADGES STATUT */
  .badge {
    display: inline-block; padding: 4px 12px;
    border-radius: 100px; font-size: 11px; font-weight: 700;
  }
  .badge-wait    { background: rgba(251,191,36,0.15); color: #fbbf24; }
  .badge-ok      { background: rgba(34,197,94,0.15);  color: #22c55e; }
  .badge-done    { background: rgba(100,116,139,0.15); color: #94a3b8; }
  .badge-cancel  { background: rgba(239,68,68,0.15);  color: #f87171; }
  /* DISPONIBILITÉ */
  .dot-on  { display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;margin-right:6px; }
  .dot-off { display:inline-block;width:8px;height:8px;border-radius:50%;background:#64748b;margin-right:6px; }
</style>
"""


def fourn_sidebar(request: Request, active: str = "dashboard") -> str:
    nom = request.session.get("user_nom", "Fournisseur")
    links = [
        ("dashboard",   "/fournisseur",                  "📊 Tableau de bord"),
        ("produits",    "/fournisseur/produits",          "📦 Mon Catalogue"),
        ("ajouter",     "/fournisseur/ajouter-produit",   "➕ Ajouter un produit"),
        ("commandes",   "/fournisseur/commandes-b2b",     "🤝 Commandes B2B"),
    ]
    items = ""
    for key, href, label in links:
        cls = "active" if key == active else ""
        items += f'<a href="{href}" class="{cls}">{label}</a>'
    return f"""
    <div class="sidebar">
      <div class="sidebar-brand">🏭 SDE</div>
      <div class="sidebar-user">👤 {nom}</div>
      {items}
      <br><br>
      <a href="/logout" class="logout">🚪 Déconnexion</a>
    </div>"""


def page_wrap(sidebar_html: str, body: str, title: str = "SDE — Espace Fournisseur") -> str:
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
  {FOURN_STYLE}
</head>
<body>
  {sidebar_html}
  <div class="main">{body}</div>
</body>
</html>"""


def require_fourn(request: Request):
    """Vérifie que l'utilisateur est bien un FOURNISSEUR connecté."""
    return (
        request.session.get("user_id") and
        request.session.get("profil") == "FOURNISSEUR"
    )


# ─────────────────────────────────────────────
#  TABLEAU DE BORD  GET /fournisseur
# ─────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    if not require_fourn(request):
        return RedirectResponse("/login")

    fourn_id = request.session["user_id"]

    produits = db.query(ProduitFournisseur).filter(
        ProduitFournisseur.fournisseur_id == fourn_id
    ).all()

    commandes = db.query(CommandeB2B).filter(
        CommandeB2B.fournisseur_id == fourn_id
    ).all()

    nb_produits    = len(produits)
    nb_disponibles = sum(1 for p in produits if p.is_disponible)
    nb_commandes   = len(commandes)
    ca_estime      = sum(
        c.prix_total for c in commandes if c.statut in ("CONFIRMEE", "LIVREE")
    )

    # Dernières commandes (5)
    recentes = sorted(commandes, key=lambda c: c.date_commande, reverse=True)[:5]
    rows_cmd = ""
    for c in recentes:
        date_str = c.date_commande.strftime("%d/%m/%Y")
        entreprise = db.query(User).filter(User.id == c.entreprise_id).first()
        ent_nom = f"{entreprise.prenom} {entreprise.nom}" if entreprise else "—"
        badge_cls = {
            "EN_ATTENTE": "badge-wait", "CONFIRMEE": "badge-ok",
            "LIVREE": "badge-done",     "ANNULEE": "badge-cancel"
        }.get(c.statut, "badge-wait")
        rows_cmd += f"""
        <tr>
          <td style="color:#fb923c; font-weight:600;">#B2B-{c.id:04d}</td>
          <td>{ent_nom}</td>
          <td>{c.produit.nom if c.produit else '—'}</td>
          <td>{c.quantite:,}</td>
          <td style="color:#fbbf24;">{c.prix_total:,.0f} FCFA</td>
          <td><span class="badge {badge_cls}">{c.statut}</span></td>
          <td style="color:#92400e; font-size:12px;">{date_str}</td>
        </tr>"""

    table_cmd = f"""
    <div class="card" style="margin-top:32px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <h2 style="font-size:17px; margin:0;">🤝 Dernières commandes reçues</h2>
        <a href="/fournisseur/commandes-b2b" class="btn-outline">Voir tout</a>
      </div>
      <table>
        <thead>
          <tr><th>#</th><th>ENTREPRISE</th><th>PRODUIT</th><th>QTÉ</th><th>MONTANT</th><th>STATUT</th><th>DATE</th></tr>
        </thead>
        <tbody>{rows_cmd or '<tr><td colspan="7" style="color:#92400e; text-align:center; padding:30px;">Aucune commande</td></tr>'}</tbody>
      </table>
    </div>""" if recentes else ""

    body = f"""
    <header style="margin-bottom:36px;">
      <h1>📊 Tableau de bord Fournisseur</h1>
      <p style="color:#92400e;">Gérez votre catalogue et suivez vos commandes B2B</p>
    </header>
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-label">Produits catalogués</div>
        <div class="stat-value">{nb_produits}</div>
        <div class="stat-icon">📦</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Disponibles à la vente</div>
        <div class="stat-value">{nb_disponibles}</div>
        <div class="stat-icon">✅</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Commandes B2B reçues</div>
        <div class="stat-value">{nb_commandes}</div>
        <div class="stat-icon">🤝</div>
      </div>
    </div>
    <div style="display:flex; gap:16px; margin-bottom:24px;">
      <a href="/fournisseur/ajouter-produit" class="btn-primary">➕ Ajouter un produit</a>
      <a href="/fournisseur/produits" class="btn-outline">📦 Voir mon catalogue</a>
    </div>
    {table_cmd}"""

    return page_wrap(fourn_sidebar(request, "dashboard"), body)


# ─────────────────────────────────────────────
#  CATALOGUE  GET /fournisseur/produits
# ─────────────────────────────────────────────

@router.get("/produits", response_class=HTMLResponse)
def liste_produits(request: Request, db: Session = Depends(get_db)):
    if not require_fourn(request):
        return RedirectResponse("/login")

    produits = db.query(ProduitFournisseur).filter(
        ProduitFournisseur.fournisseur_id == request.session["user_id"]
    ).order_by(ProduitFournisseur.date_ajout.desc()).all()

    rows = ""
    for p in produits:
        dot = '<span class="dot-on"></span>Disponible' if p.is_disponible \
              else '<span class="dot-off"></span>Indisponible'
        rows += f"""
        <tr>
          <td><strong>{p.nom}</strong><br><small style="color:#92400e;">{p.categorie or '—'}</small></td>
          <td style="color:#fbbf24; font-weight:700;">{p.prix_gros:,.0f} FCFA / {p.unite}</td>
          <td>{p.quantite_disponible:,} {p.unite}</td>
          <td>min. {p.quantite_minimum} {p.unite}</td>
          <td style="font-size:13px;">{dot}</td>
          <td style="font-size:12px; color:#92400e;">{p.date_ajout.strftime('%d/%m/%Y')}</td>
          <td style="display:flex; gap:8px;">
            <a href="/fournisseur/modifier-produit/{p.id}" class="btn-outline" style="padding:6px 12px; font-size:12px;">✏️</a>
            <form method="POST" action="/fournisseur/toggle-produit/{p.id}" style="display:inline;">
              <button type="submit" class="btn-outline" style="padding:6px 12px; font-size:12px;">
                {'🔴' if p.is_disponible else '🟢'}
              </button>
            </form>
            <form method="POST" action="/fournisseur/supprimer-produit/{p.id}" style="display:inline;"
                  onsubmit="return confirm('Supprimer ce produit ?')">
              <button type="submit" class="btn-danger" style="padding:6px 12px;">🗑️</button>
            </form>
          </td>
        </tr>"""

    if not rows:
        rows = '<tr><td colspan="7" style="color:#92400e; text-align:center; padding:50px;">Aucun produit. <a href="/fournisseur/ajouter-produit" style="color:#f97316;">Ajoutez-en un !</a></td></tr>'

    body = f"""
    <header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:32px;">
      <h1>📦 Mon Catalogue</h1>
      <a href="/fournisseur/ajouter-produit" class="btn-primary">➕ Nouveau produit</a>
    </header>
    <div class="card" style="overflow:auto;">
      <table>
        <thead>
          <tr>
            <th>PRODUIT</th><th>PRIX GROS</th><th>STOCK DISPO</th>
            <th>QTÉ MIN</th><th>STATUT</th><th>DATE</th><th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""

    return page_wrap(fourn_sidebar(request, "produits"), body, "Mon Catalogue")


# ─────────────────────────────────────────────
#  AJOUTER PRODUIT  GET + POST /fournisseur/ajouter-produit
# ─────────────────────────────────────────────

@router.get("/ajouter-produit", response_class=HTMLResponse)
def ajouter_produit_form(request: Request):
    if not require_fourn(request):
        return RedirectResponse("/login")

    body = f"""
    <h1>➕ Ajouter un produit</h1>
    <div class="card" style="max-width:680px; margin-top:28px;">
      <form method="POST" action="/fournisseur/ajouter-produit">
        <label>Nom du produit *</label>
        <input type="text" name="nom" placeholder="Ex : Riz long grain 50kg" required>

        <div class="two-col">
          <div>
            <label>Catégorie</label>
            <select name="categorie">
              <option value="">— Sélectionner —</option>
              <option>Alimentation</option>
              <option>Boissons</option>
              <option>Électroménager</option>
              <option>Vêtements & Textile</option>
              <option>Hygiène & Beauté</option>
              <option>Fournitures scolaires</option>
              <option>Jouets</option>
              <option>Accessoires maison</option>
              <option>Boucherie / Poissonnerie</option>
              <option>Fruits & Légumes</option>
              <option>Autre</option>
            </select>
          </div>
          <div>
            <label>Unité de vente</label>
            <select name="unite">
              <option value="unité">Unité</option>
              <option value="kg">Kilogramme (kg)</option>
              <option value="litre">Litre</option>
              <option value="carton">Carton</option>
              <option value="sac">Sac</option>
              <option value="pièce">Pièce</option>
              <option value="fardeau">Fardeau</option>
            </select>
          </div>
        </div>

        <label>Description (optionnel)</label>
        <textarea name="description" rows="3" placeholder="Caractéristiques, origine, conditionnement…"></textarea>

        <div class="two-col">
          <div>
            <label>Prix de gros (FCFA / unité) *</label>
            <input type="number" name="prix_gros" min="1" placeholder="Ex : 45000" required>
          </div>
          <div>
            <label>Quantité disponible *</label>
            <input type="number" name="quantite_disponible" min="0" placeholder="Ex : 1000" required>
          </div>
        </div>

        <label>Quantité minimale de commande *</label>
        <input type="number" name="quantite_minimum" min="1" placeholder="Ex : 10" value="10" required>

        <button type="submit" class="btn-primary" style="width:100%; font-size:16px; padding:15px; margin-top:8px;">
          ✅ Publier dans le catalogue
        </button>
      </form>
    </div>"""

    return page_wrap(fourn_sidebar(request, "ajouter"), body)


@router.post("/ajouter-produit")
def ajouter_produit_submit(
    request: Request,
    nom:                 str   = Form(...),
    categorie:           str   = Form(""),
    description:         str   = Form(""),
    prix_gros:           float = Form(...),
    quantite_disponible: int   = Form(...),
    quantite_minimum:    int   = Form(10),
    unite:               str   = Form("unité"),
    db: Session = Depends(get_db),
):
    if not require_fourn(request):
        return RedirectResponse("/login")

    db.add(ProduitFournisseur(
        fournisseur_id=request.session["user_id"],
        nom=nom.strip(),
        categorie=categorie or None,
        description=description.strip() or None,
        prix_gros=prix_gros,
        quantite_disponible=quantite_disponible,
        quantite_minimum=quantite_minimum,
        unite=unite,
        is_disponible=True,
    ))
    db.commit()
    return RedirectResponse("/fournisseur/produits", status_code=303)


# ─────────────────────────────────────────────
#  MODIFIER PRODUIT  GET + POST
# ─────────────────────────────────────────────

@router.get("/modifier-produit/{produit_id}", response_class=HTMLResponse)
def modifier_produit_form(request: Request, produit_id: int, db: Session = Depends(get_db)):
    if not require_fourn(request):
        return RedirectResponse("/login")

    p = db.query(ProduitFournisseur).filter(
        ProduitFournisseur.id == produit_id,
        ProduitFournisseur.fournisseur_id == request.session["user_id"]
    ).first()

    if not p:
        return RedirectResponse("/fournisseur/produits")

    body = f"""
    <h1>✏️ Modifier : {p.nom}</h1>
    <div class="card" style="max-width:680px; margin-top:28px;">
      <form method="POST" action="/fournisseur/modifier-produit/{p.id}">
        <label>Nom du produit *</label>
        <input type="text" name="nom" value="{p.nom}" required>
        <label>Catégorie</label>
        <input type="text" name="categorie" value="{p.categorie or ''}">
        <label>Description</label>
        <textarea name="description" rows="3">{p.description or ''}</textarea>
        <div class="two-col">
          <div>
            <label>Prix de gros (FCFA) *</label>
            <input type="number" name="prix_gros" value="{p.prix_gros}" required>
          </div>
          <div>
            <label>Quantité disponible *</label>
            <input type="number" name="quantite_disponible" value="{p.quantite_disponible}" required>
          </div>
        </div>
        <div class="two-col">
          <div>
            <label>Quantité minimale</label>
            <input type="number" name="quantite_minimum" value="{p.quantite_minimum}">
          </div>
          <div>
            <label>Unité</label>
            <input type="text" name="unite" value="{p.unite}">
          </div>
        </div>
        <button type="submit" class="btn-primary" style="width:100%; padding:14px; margin-top:8px;">
          💾 Enregistrer les modifications
        </button>
      </form>
    </div>"""

    return page_wrap(fourn_sidebar(request, "produits"), body)


@router.post("/modifier-produit/{produit_id}")
def modifier_produit_submit(
    request: Request, produit_id: int,
    nom: str = Form(...), categorie: str = Form(""),
    description: str = Form(""), prix_gros: float = Form(...),
    quantite_disponible: int = Form(...), quantite_minimum: int = Form(10),
    unite: str = Form("unité"),
    db: Session = Depends(get_db),
):
    if not require_fourn(request):
        return RedirectResponse("/login")

    p = db.query(ProduitFournisseur).filter(
        ProduitFournisseur.id == produit_id,
        ProduitFournisseur.fournisseur_id == request.session["user_id"]
    ).first()

    if p:
        p.nom = nom.strip()
        p.categorie = categorie or None
        p.description = description.strip() or None
        p.prix_gros = prix_gros
        p.quantite_disponible = quantite_disponible
        p.quantite_minimum = quantite_minimum
        p.unite = unite
        db.commit()

    return RedirectResponse("/fournisseur/produits", status_code=303)


# ─────────────────────────────────────────────
#  TOGGLE DISPONIBILITÉ  POST /fournisseur/toggle-produit/{id}
# ─────────────────────────────────────────────

@router.post("/toggle-produit/{produit_id}")
def toggle_produit(request: Request, produit_id: int, db: Session = Depends(get_db)):
    if not require_fourn(request):
        return RedirectResponse("/login")

    p = db.query(ProduitFournisseur).filter(
        ProduitFournisseur.id == produit_id,
        ProduitFournisseur.fournisseur_id == request.session["user_id"]
    ).first()
    if p:
        p.is_disponible = not p.is_disponible
        db.commit()
    return RedirectResponse("/fournisseur/produits", status_code=303)


# ─────────────────────────────────────────────
#  SUPPRIMER PRODUIT  POST /fournisseur/supprimer-produit/{id}
# ─────────────────────────────────────────────

@router.post("/supprimer-produit/{produit_id}")
def supprimer_produit(request: Request, produit_id: int, db: Session = Depends(get_db)):
    if not require_fourn(request):
        return RedirectResponse("/login")

    p = db.query(ProduitFournisseur).filter(
        ProduitFournisseur.id == produit_id,
        ProduitFournisseur.fournisseur_id == request.session["user_id"]
    ).first()
    if p:
        db.delete(p)
        db.commit()
    return RedirectResponse("/fournisseur/produits", status_code=303)


# ─────────────────────────────────────────────
#  COMMANDES B2B REÇUES  GET /fournisseur/commandes-b2b
# ─────────────────────────────────────────────

STATUT_BADGE = {
    "EN_ATTENTE": ("badge-wait",   "⏳ En attente"),
    "CONFIRMEE":  ("badge-ok",     "✅ Confirmée"),
    "LIVREE":     ("badge-done",   "📬 Livrée"),
    "ANNULEE":    ("badge-cancel", "❌ Annulée"),
}


@router.get("/commandes-b2b", response_class=HTMLResponse)
def commandes_b2b(request: Request, db: Session = Depends(get_db)):
    if not require_fourn(request):
        return RedirectResponse("/login")

    commandes = db.query(CommandeB2B).filter(
        CommandeB2B.fournisseur_id == request.session["user_id"]
    ).order_by(CommandeB2B.date_commande.desc()).all()

    rows = ""
    for c in commandes:
        cls, label = STATUT_BADGE.get(c.statut, ("badge-wait", c.statut))
        ent = db.query(User).filter(User.id == c.entreprise_id).first()
        ent_nom = f"{ent.prenom} {ent.nom}" if ent else "—"
        ent_type = ent.type_entreprise or "" if ent else ""
        rows += f"""
        <tr>
          <td style="color:#fb923c; font-weight:600;">#B2B-{c.id:04d}</td>
          <td><strong>{ent_nom}</strong><br><small style="color:#92400e;">{ent_type}</small></td>
          <td>{c.produit.nom if c.produit else '—'}</td>
          <td>{c.quantite:,}</td>
          <td style="color:#fbbf24; font-weight:700;">{c.prix_total:,.0f} FCFA</td>
          <td><span class="badge {cls}">{label}</span></td>
          <td style="color:#92400e; font-size:12px;">{c.date_commande.strftime('%d/%m/%Y')}</td>
          <td>
            <form method="POST" action="/fournisseur/confirmer-b2b/{c.id}" style="display:inline;">
              <button type="submit" class="btn-outline" style="padding:6px 12px; font-size:12px;"
                      {'disabled' if c.statut != 'EN_ATTENTE' else ''}>✅ Confirmer</button>
            </form>
          </td>
        </tr>"""

    if not rows:
        rows = '<tr><td colspan="8" style="color:#92400e; text-align:center; padding:50px;">Aucune commande reçue pour l\'instant.</td></tr>'

    body = f"""
    <header style="margin-bottom:32px;">
      <h1>🤝 Commandes B2B</h1>
      <p style="color:#92400e;">Commandes passées par les entreprises sur vos produits</p>
    </header>
    <div class="card" style="overflow:auto;">
      <table>
        <thead>
          <tr>
            <th>#</th><th>ENTREPRISE</th><th>PRODUIT</th>
            <th>QTÉ</th><th>MONTANT</th><th>STATUT</th><th>DATE</th><th>ACTION</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""

    return page_wrap(fourn_sidebar(request, "commandes"), body, "Commandes B2B")


@router.post("/confirmer-b2b/{commande_id}")
def confirmer_b2b(request: Request, commande_id: int, db: Session = Depends(get_db)):
    if not require_fourn(request):
        return RedirectResponse("/login")

    c = db.query(CommandeB2B).filter(
        CommandeB2B.id == commande_id,
        CommandeB2B.fournisseur_id == request.session["user_id"]
    ).first()

    if c and c.statut == "EN_ATTENTE":
        c.statut = "CONFIRMEE"
        db.commit()

    return RedirectResponse("/fournisseur/commandes-b2b", status_code=303)
