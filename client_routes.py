"""
client_routes.py — Espace CLIENT
Routes : /shop  /cart  /cart/add  /cart/remove  /commande  /mes-commandes
Thème : violet / purple
"""

import json
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from .database import get_db
from .models import Stock, Commande, CommandeItem

router = APIRouter(prefix="", tags=["client"])


# ─────────────────────────────────────────────
#  STYLES CLIENT  (violet / purple)
# ─────────────────────────────────────────────

CLIENT_STYLE = """
<style>
  *, *::before, *::after { box-sizing: border-box; }
  :root {
    --accent:   #a855f7;
    --accent2:  #7c3aed;
    --dark-bg:  #0f0f1a;
    --card-bg:  #1a1a2e;
    --text:     #f1f5f9;
    --muted:    #64748b;
  }
  body { background: var(--dark-bg); color: var(--text);
         font-family: 'Inter', sans-serif; margin: 0; }
  h1, h2 { color: var(--accent); font-weight: 800; }
  /* SIDEBAR */
  .sidebar {
    position: fixed; width: 250px; height: 100vh; left: 0; top: 0;
    background: linear-gradient(160deg, #0f0f1a 0%, #2d1b69 100%);
    border-right: 1px solid rgba(168,85,247,0.2);
    padding: 36px 20px; z-index: 1000;
    box-shadow: 4px 0 20px rgba(0,0,0,0.5);
  }
  .sidebar-brand {
    color: #c084fc; font-size: 1.8rem; font-weight: 900;
    letter-spacing: 2px; text-align: center; margin-bottom: 8px;
    text-shadow: 0 0 15px rgba(192,132,252,0.5);
    border-bottom: 1px solid rgba(168,85,247,0.3); padding-bottom: 16px;
  }
  .sidebar-user {
    text-align: center; font-size: 12px; color: var(--muted); margin-bottom: 28px;
  }
  .sidebar a {
    display: block; color: #cbd5e1; padding: 12px 18px;
    text-decoration: none; border-radius: 12px; margin-bottom: 8px;
    transition: 0.25s; background: rgba(255,255,255,0.03); font-weight: 600;
  }
  .sidebar a:hover {
    background: rgba(168,85,247,0.15); color: #fff;
    transform: translateX(6px);
    box-shadow: 0 0 10px rgba(168,85,247,0.3);
  }
  .sidebar a.active {
    background: rgba(168,85,247,0.25); color: #c084fc;
    border-left: 3px solid #a855f7;
  }
  .sidebar .logout { color: #f87171 !important; margin-top: auto; }
  .main { margin-left: 268px; padding: 40px; min-height: 100vh; }
  /* CARDS */
  .card {
    background: var(--card-bg); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 24px; transition: 0.3s;
  }
  .card:hover { border-color: rgba(168,85,247,0.4); }
  /* GRID PRODUITS */
  .products-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 20px; margin-top: 24px;
  }
  .product-card {
    background: var(--card-bg); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px; padding: 22px; transition: 0.3s;
    display: flex; flex-direction: column; gap: 10px;
  }
  .product-card:hover {
    border-color: var(--accent); transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(168,85,247,0.2);
  }
  .product-name { font-size: 16px; font-weight: 700; }
  .product-rayon {
    font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
    color: var(--muted);
  }
  .product-price { font-size: 22px; font-weight: 800; color: #c084fc; }
  .product-stock { font-size: 12px; color: var(--muted); }
  .btn-add {
    width: 100%; padding: 11px; background: var(--accent); color: #fff;
    border: none; border-radius: 12px; font-weight: 700; cursor: pointer;
    transition: 0.25s; font-size: 14px;
  }
  .btn-add:hover { background: var(--accent2); box-shadow: 0 0 15px rgba(168,85,247,0.4); }
  /* PANIER */
  .cart-badge {
    background: #a855f7; color: white; border-radius: 50%;
    width: 22px; height: 22px; font-size: 11px; font-weight: 800;
    display: inline-flex; align-items: center; justify-content: center;
    margin-left: 8px;
  }
  /* FILTRES */
  .filter-bar {
    display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 24px;
  }
  .filter-btn {
    padding: 8px 18px; border-radius: 100px; border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.03); color: #94a3b8; font-size: 13px;
    cursor: pointer; transition: 0.25s; text-decoration: none;
  }
  .filter-btn:hover, .filter-btn.active {
    background: rgba(168,85,247,0.2); border-color: #a855f7; color: #c084fc;
  }
  /* COMMANDE STATUT */
  .badge {
    display: inline-block; padding: 4px 12px; border-radius: 100px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
  }
  .badge-wait    { background: rgba(251,191,36,0.15); color: #fbbf24; }
  .badge-ok      { background: rgba(34,197,94,0.15);  color: #22c55e; }
  .badge-transit { background: rgba(59,130,246,0.15); color: #60a5fa; }
  .badge-done    { background: rgba(100,116,139,0.15); color: #94a3b8; }
  .badge-cancel  { background: rgba(239,68,68,0.15);  color: #f87171; }
  /* BOUTONS GÉNÉRAUX */
  .btn-primary {
    display: inline-block; padding: 13px 28px;
    background: var(--accent); color: white; border: none;
    border-radius: 13px; font-weight: 700; cursor: pointer;
    text-decoration: none; transition: 0.25s; font-size: 15px;
  }
  .btn-primary:hover {
    background: var(--accent2); box-shadow: 0 0 20px rgba(168,85,247,0.4);
    transform: translateY(-2px); color: white;
  }
  .btn-outline {
    display: inline-block; padding: 11px 24px;
    border: 1px solid rgba(255,255,255,0.15); color: #94a3b8;
    border-radius: 12px; text-decoration: none; font-size: 14px;
    transition: 0.25s;
  }
  .btn-outline:hover { border-color: var(--accent); color: #c084fc; }
  input, select, textarea {
    background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.1);
    color: #f1f5f9; border-radius: 12px; padding: 12px 16px;
    font-size: 14px; outline: none; width: 100%; transition: 0.25s;
    margin-bottom: 16px;
  }
  input:focus, select:focus, textarea:focus {
    border-color: var(--accent); box-shadow: 0 0 0 3px rgba(168,85,247,0.15);
  }
  label { font-size: 12px; text-transform: uppercase;
          letter-spacing: 1px; color: #94a3b8; display: block; margin-bottom: 6px; }
  table { width: 100%; border-collapse: collapse; }
  th { padding: 14px 16px; color: var(--accent); font-size: 12px;
       text-transform: uppercase; letter-spacing: 1px; text-align: left; }
  td { padding: 16px; border-bottom: 1px solid rgba(255,255,255,0.04);
       vertical-align: middle; }
  tr:last-child td { border-bottom: none; }
</style>
"""


def client_sidebar(request: Request, active: str = "shop"):
    nom = request.session.get("user_nom", "Visiteur")
    links = [
        ("shop",         "/shop",            "🛍️ Catalogue"),
        ("cart",         "/cart",            "🛒 Mon Panier"),
        ("commandes",    "/mes-commandes",   "📦 Mes Commandes"),
    ]
    items = ""
    for key, href, label in links:
        cls = "active" if key == active else ""
        items += f'<a href="{href}" class="{cls}">{label}</a>'
    return f"""
    <div class="sidebar">
      <div class="sidebar-brand">🛒 SDE</div>
      <div class="sidebar-user">👤 {nom}</div>
      {items}
      <br><br>
      <a href="/logout" class="logout">🚪 Déconnexion</a>
    </div>"""


def page_wrap(sidebar_html: str, body: str, title: str = "SDE — Espace Client") -> str:
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
  {CLIENT_STYLE}
</head>
<body>
  {sidebar_html}
  <div class="main">{body}</div>
</body>
</html>"""


# ─────────────────────────────────────────────
#  HELPERS PANIER (stocké en session JSON)
# ─────────────────────────────────────────────

def get_cart(request: Request) -> dict:
    raw = request.session.get("cart", "{}")
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return {}


def save_cart(request: Request, cart: dict):
    request.session["cart"] = json.dumps(cart)


def cart_count(request: Request) -> int:
    return sum(item["quantite"] for item in get_cart(request).values())


# ─────────────────────────────────────────────
#  CATALOGUE  GET /shop
# ─────────────────────────────────────────────

@router.get("/shop", response_class=HTMLResponse)
def shop(request: Request, rayon: str = "", db: Session = Depends(get_db)):
    if not request.session.get("user_id") or request.session.get("profil") != "CLIENT":
        return RedirectResponse("/login")

    query = db.query(Stock).filter(Stock.quantite > 0)
    if rayon:
        query = query.filter(Stock.rayon == rayon)
    produits = query.order_by(Stock.rayon, Stock.produit).all()

    # Rayons disponibles pour filtres
    rayons = [r[0] for r in db.query(Stock.rayon).distinct().all()]

    filter_buttons = '<a href="/shop" class="filter-btn' + (' active' if not rayon else '') + '">Tout</a>'
    for r in sorted(rayons):
        active = " active" if r == rayon else ""
        filter_buttons += f'<a href="/shop?rayon={r}" class="filter-btn{active}">{r.capitalize()}</a>'

    cards = ""
    for p in produits:
        cards += f"""
        <div class="product-card">
          <div>
            <div class="product-name">{p.produit.capitalize()}</div>
            <div class="product-rayon">{p.rayon}</div>
          </div>
          <div class="product-price">{int(p.prix):,} FCFA</div>
          <div class="product-stock">📦 Stock : {p.quantite} unités</div>
          <form method="POST" action="/cart/add">
            <input type="hidden" name="produit_id" value="{p.id}">
            <input type="hidden" name="quantite" value="1">
            <button type="submit" class="btn-add">+ Ajouter au panier</button>
          </form>
        </div>"""

    if not cards:
        cards = '<p style="color:#64748b; grid-column: 1/-1; text-align:center; padding:60px 0;">Aucun produit trouvé.</p>'

    count = cart_count(request)
    badge = f'<span class="cart-badge">{count}</span>' if count > 0 else ""

    body = f"""
    <header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:32px;">
      <div>
        <h1>🛍️ Catalogue</h1>
        <p style="color:#64748b;">{len(produits)} produit(s) disponible(s)</p>
      </div>
      <a href="/cart" class="btn-primary">🛒 Panier{badge}</a>
    </header>
    <div class="filter-bar">{filter_buttons}</div>
    <div class="products-grid">{cards}</div>"""

    return page_wrap(client_sidebar(request, "shop"), body, "SDE — Catalogue")


# ─────────────────────────────────────────────
#  AJOUTER AU PANIER  POST /cart/add
# ─────────────────────────────────────────────

@router.post("/cart/add")
def cart_add(
    request: Request,
    produit_id: int = Form(...),
    quantite: int = Form(1),
    db: Session = Depends(get_db),
):
    if not request.session.get("user_id") or request.session.get("profil") != "CLIENT":
        return RedirectResponse("/login")

    produit = db.query(Stock).filter(Stock.id == produit_id).first()
    if not produit:
        return RedirectResponse("/shop")

    cart = get_cart(request)
    key = str(produit_id)
    if key in cart:
        cart[key]["quantite"] += quantite
    else:
        cart[key] = {
            "id": produit.id,
            "nom": produit.produit,
            "rayon": produit.rayon,
            "prix": int(produit.prix),
            "quantite": quantite,
        }
    save_cart(request, cart)
    return RedirectResponse("/shop", status_code=303)


# ─────────────────────────────────────────────
#  RETIRER DU PANIER  POST /cart/remove
# ─────────────────────────────────────────────

@router.post("/cart/remove")
def cart_remove(request: Request, produit_id: str = Form(...)):
    if not request.session.get("user_id") or request.session.get("profil") != "CLIENT":
        return RedirectResponse("/login")
    cart = get_cart(request)
    cart.pop(str(produit_id), None)
    save_cart(request, cart)
    return RedirectResponse("/cart", status_code=303)


# ─────────────────────────────────────────────
#  MON PANIER  GET /cart
# ─────────────────────────────────────────────

@router.get("/cart", response_class=HTMLResponse)
def view_cart(request: Request):
    if not request.session.get("user_id") or request.session.get("profil") != "CLIENT":
        return RedirectResponse("/login")

    cart = get_cart(request)

    if not cart:
        body = """
        <div style="text-align:center; padding:80px 0;">
          <div style="font-size:5rem; margin-bottom:20px;">🛒</div>
          <h2 style="color:#64748b; font-weight:400;">Votre panier est vide</h2>
          <a href="/shop" class="btn-primary" style="margin-top:24px; display:inline-block;">
            Aller au catalogue
          </a>
        </div>"""
        return page_wrap(client_sidebar(request, "cart"), body, "Panier vide")

    rows = ""
    total_global = 0
    for key, item in cart.items():
        sous_total = item["prix"] * item["quantite"]
        total_global += sous_total
        rows += f"""
        <tr>
          <td>
            <strong>{item['nom'].capitalize()}</strong><br>
            <small style="color:#64748b;">{item['rayon']}</small>
          </td>
          <td>{item['prix']:,} FCFA</td>
          <td>
            <form method="POST" action="/cart/update" style="display:inline;">
              <input type="hidden" name="produit_id" value="{key}">
              <input type="number" name="quantite" value="{item['quantite']}"
                     min="1" style="width:80px; margin:0;"
                     onchange="this.form.submit()">
            </form>
          </td>
          <td style="color:#c084fc; font-weight:700;">{sous_total:,} FCFA</td>
          <td>
            <form method="POST" action="/cart/remove">
              <input type="hidden" name="produit_id" value="{key}">
              <button type="submit" style="background:rgba(239,68,68,0.15);color:#f87171;
                border:none;border-radius:8px;padding:6px 14px;cursor:pointer;">✕</button>
            </form>
          </td>
        </tr>"""

    body = f"""
    <header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:32px;">
      <h1>🛒 Mon Panier</h1>
      <a href="/shop" class="btn-outline">← Continuer les achats</a>
    </header>
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>PRODUIT</th><th>PRIX UNIT.</th><th>QTÉ</th><th>SOUS-TOTAL</th><th></th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    <div style="display:flex; justify-content:flex-end; margin-top:24px; align-items:center; gap:32px;">
      <div>
        <span style="color:#64748b; font-size:14px;">TOTAL</span>
        <div style="font-size:32px; font-weight:800; color:#c084fc;">{total_global:,} FCFA</div>
      </div>
      <a href="/commande" class="btn-primary" style="font-size:16px; padding:16px 36px;">
        ✅ Passer la commande
      </a>
    </div>"""

    return page_wrap(client_sidebar(request, "cart"), body, "Mon Panier")


# ─────────────────────────────────────────────
#  MISE À JOUR QUANTITÉ  POST /cart/update
# ─────────────────────────────────────────────

@router.post("/cart/update")
def cart_update(
    request: Request,
    produit_id: str = Form(...),
    quantite: int = Form(...),
):
    if not request.session.get("user_id") or request.session.get("profil") != "CLIENT":
        return RedirectResponse("/login")
    cart = get_cart(request)
    if str(produit_id) in cart:
        if quantite > 0:
            cart[str(produit_id)]["quantite"] = quantite
        else:
            cart.pop(str(produit_id), None)
    save_cart(request, cart)
    return RedirectResponse("/cart", status_code=303)


# ─────────────────────────────────────────────
#  PASSER UNE COMMANDE  GET + POST /commande
# ─────────────────────────────────────────────

@router.get("/commande", response_class=HTMLResponse)
def commande_form(request: Request):
    if not request.session.get("user_id") or request.session.get("profil") != "CLIENT":
        return RedirectResponse("/login")

    cart = get_cart(request)
    if not cart:
        return RedirectResponse("/shop")

    total = sum(i["prix"] * i["quantite"] for i in cart.values())
    recap = "".join(
        f'<li style="padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.04);">'
        f'<span style="color:#c084fc;">{i["nom"].capitalize()}</span>'
        f' × {i["quantite"]} = <strong>{i["prix"]*i["quantite"]:,} FCFA</strong></li>'
        for i in cart.values()
    )

    body = f"""
    <h1>✅ Finaliser la commande</h1>
    <div style="display:grid; grid-template-columns:1fr 380px; gap:28px; margin-top:28px;">
      <!-- FORMULAIRE -->
      <div class="card">
        <h2 style="font-size:18px; margin-bottom:24px;">📍 Informations de livraison</h2>
        <form method="POST" action="/commande">
          <label>Adresse de livraison *</label>
          <textarea name="adresse" rows="3" placeholder="Quartier, rue, repère…" required></textarea>
          <label>Notes ou instructions (optionnel)</label>
          <textarea name="notes" rows="2" placeholder="Ex: Livrer après 17h…"></textarea>
          <button type="submit" class="btn-primary" style="width:100%; font-size:16px; padding:16px; margin-top:8px;">
            🚀 Confirmer la commande — {total:,} FCFA
          </button>
        </form>
      </div>
      <!-- RÉCAP PANIER -->
      <div class="card" style="align-self:start;">
        <h2 style="font-size:16px; margin-bottom:16px;">📋 Récapitulatif</h2>
        <ul style="list-style:none; padding:0; margin:0;">{recap}</ul>
        <div style="margin-top:20px; padding-top:16px; border-top:1px solid rgba(255,255,255,0.08);">
          <strong style="font-size:20px; color:#c084fc;">Total : {total:,} FCFA</strong>
        </div>
      </div>
    </div>"""

    return page_wrap(client_sidebar(request, "cart"), body)


@router.post("/commande")
def commande_submit(
    request: Request,
    adresse: str = Form(...),
    notes:   str = Form(""),
    db: Session = Depends(get_db),
):
    if not request.session.get("user_id") or request.session.get("profil") != "CLIENT":
        return RedirectResponse("/login")

    cart = get_cart(request)
    if not cart:
        return RedirectResponse("/shop")

    total = sum(i["prix"] * i["quantite"] for i in cart.values())

    commande = Commande(
        client_id=request.session["user_id"],
        total=total,
        adresse_livraison=adresse.strip(),
        notes=notes.strip() or None,
        statut="EN_ATTENTE",
    )
    db.add(commande)
    db.flush()

    for item in cart.values():
        db.add(CommandeItem(
            commande_id=commande.id,
            produit_nom=item["nom"],
            rayon=item["rayon"],
            quantite=item["quantite"],
            prix_unitaire=item["prix"],
            total=item["prix"] * item["quantite"],
        ))

    db.commit()

    # Vider le panier
    save_cart(request, {})

    return RedirectResponse(f"/commande/succes/{commande.id}", status_code=303)


# ─────────────────────────────────────────────
#  PAGE SUCCÈS  GET /commande/succes/{id}
# ─────────────────────────────────────────────

@router.get("/commande/succes/{commande_id}", response_class=HTMLResponse)
def commande_succes(request: Request, commande_id: int):
    if not request.session.get("user_id") or request.session.get("profil") != "CLIENT":
        return RedirectResponse("/login")

    body = f"""
    <div style="text-align:center; padding:80px 40px; max-width:600px; margin:auto;">
      <div style="font-size:6rem; margin-bottom:24px;">🎉</div>
      <h1 style="font-size:2.5rem;">Commande confirmée !</h1>
      <p style="color:#94a3b8; font-size:18px; margin:16px 0 36px;">
        Votre commande <strong style="color:#c084fc;">#CMD-{commande_id:04d}</strong>
        a bien été enregistrée.<br>Vous serez contacté pour la livraison.
      </p>
      <div style="display:flex; gap:16px; justify-content:center;">
        <a href="/mes-commandes" class="btn-primary">📦 Suivre mes commandes</a>
        <a href="/shop" class="btn-outline">🛍️ Continuer mes achats</a>
      </div>
    </div>"""

    return page_wrap(client_sidebar(request, "commandes"), body, "Commande confirmée !")


# ─────────────────────────────────────────────
#  MES COMMANDES  GET /mes-commandes
# ─────────────────────────────────────────────

STATUT_BADGE = {
    "EN_ATTENTE":   ("badge-wait",    "⏳ En attente"),
    "CONFIRMEE":    ("badge-ok",      "✅ Confirmée"),
    "EN_LIVRAISON": ("badge-transit", "🚚 En livraison"),
    "LIVREE":       ("badge-done",    "📬 Livrée"),
    "ANNULEE":      ("badge-cancel",  "❌ Annulée"),
}


@router.get("/mes-commandes", response_class=HTMLResponse)
def mes_commandes(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id") or request.session.get("profil") != "CLIENT":
        return RedirectResponse("/login")

    commandes = (
        db.query(Commande)
        .filter(Commande.client_id == request.session["user_id"])
        .order_by(Commande.date_commande.desc())
        .all()
    )

    if not commandes:
        body = """
        <h1>📦 Mes Commandes</h1>
        <div style="text-align:center; padding:80px 0;">
          <div style="font-size:4rem; margin-bottom:16px;">📭</div>
          <h2 style="color:#64748b; font-weight:400;">Aucune commande pour le moment</h2>
          <a href="/shop" class="btn-primary" style="margin-top:24px; display:inline-block;">
            Faire mes premiers achats
          </a>
        </div>"""
        return page_wrap(client_sidebar(request, "commandes"), body)

    cards = ""
    for c in commandes:
        cls, label = STATUT_BADGE.get(c.statut, ("badge-wait", c.statut))
        date_str = c.date_commande.strftime("%d/%m/%Y à %H:%M")
        items_html = "".join(
            f'<li style="color:#94a3b8; font-size:13px;">• {i.produit_nom.capitalize()} ×{i.quantite} — {i.total:,} FCFA</li>'
            for i in c.items
        )
        cards += f"""
        <div class="card" style="margin-bottom:16px;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <strong style="color:#c084fc;">CMD-{c.id:04d}</strong>
              <span style="color:#64748b; font-size:13px; margin-left:12px;">{date_str}</span>
            </div>
            <span class="badge {cls}">{label}</span>
          </div>
          <ul style="list-style:none; padding:0; margin:12px 0;">{items_html}</ul>
          <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.06); padding-top:12px; margin-top:4px;">
            <span style="color:#64748b; font-size:13px;">📍 {c.adresse_livraison or '—'}</span>
            <strong style="font-size:18px; color:#c084fc;">{c.total:,} FCFA</strong>
          </div>
        </div>"""

    body = f"""
    <header style="display:flex; justify-content:space-between; align-items:center; margin-bottom:32px;">
      <h1>📦 Mes Commandes</h1>
      <a href="/shop" class="btn-primary">🛍️ Nouvel achat</a>
    </header>
    {cards}"""

    return page_wrap(client_sidebar(request, "commandes"), body, "Mes Commandes")
