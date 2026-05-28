"""
auth.py — Version 2
Nouvelles fonctionnalités :
  • Envoi d'e-mail de confirmation à l'inscription
  • Route /verify-email/{token} pour activer le compte
  • Route /resend-verification pour renvoyer le lien
  • Route GET/POST /mon-compte/supprimer pour supprimer son compte
"""

import hashlib, secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, Commande, CommandeItem, ProduitFournisseur, CommandeB2B
# Import conditionnel du service e-mail (nécessite email_service.py dans /app/)
try:
    from .email_service import (
        send_verification_email,
        send_deletion_email,
        send_resend_verification_email,
    )
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False
    print("⚠️  email_service.py non trouvé — les e-mails sont désactivés.")
    print("   Ajoutez email_service.py dans votre dossier app/ pour activer.")
    def send_verification_email(to, prenom, token):
        print(f"[EMAIL SIMULÉ] Vérification → {to}  token={token}")
        return False
    def send_deletion_email(to, prenom):
        print(f"[EMAIL SIMULÉ] Suppression → {to}")
        return False
    def send_resend_verification_email(to, prenom, token):
        print(f"[EMAIL SIMULÉ] Renvoi vérif → {to}  token={token}")
        return False

router = APIRouter()

TOKEN_EXPIRY_HOURS = 24


# ─── Utilitaires mot de passe ────────────────────────────────
def hash_password(password: str) -> str:
    salt   = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, hashed = stored.split(":", 1)
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except Exception:
        return False


# ─── Styles communs auth ─────────────────────────────────────
AUTH_STYLE = """
<style>
  *,*::before,*::after{box-sizing:border-box;}
  :root{--blue:#00d4ff;--dark:#0f172a;--card:#1e293b;}
  body{margin:0;min-height:100vh;
    background:radial-gradient(ellipse at top left,#1e3a8a 0%,#0f172a 60%);
    font-family:'Inter',sans-serif;color:#f8fafc;
    display:flex;align-items:center;justify-content:center;}
  .auth-wrap{width:100%;max-width:540px;padding:20px;}
  .auth-card{background:rgba(30,41,59,0.9);border:1px solid rgba(255,255,255,0.08);
    border-radius:28px;padding:48px 44px;backdrop-filter:blur(20px);
    box-shadow:0 25px 60px rgba(0,0,0,0.5);}
  .brand{font-size:2rem;font-weight:900;letter-spacing:3px;text-align:center;
    color:#00d4ff;text-shadow:0 0 20px rgba(0,212,255,0.5);margin-bottom:6px;}
  .sub-brand{text-align:center;color:#64748b;font-size:13px;margin-bottom:36px;}
  label{display:block;font-size:12px;text-transform:uppercase;letter-spacing:1px;
    color:#94a3b8;margin-bottom:6px;}
  input,select{width:100%;background:rgba(0,0,0,0.4);
    border:1px solid rgba(255,255,255,0.12);color:#f8fafc;border-radius:12px;
    padding:13px 16px;font-size:15px;outline:none;transition:0.25s;margin-bottom:18px;}
  input:focus,select:focus{border-color:#00d4ff;box-shadow:0 0 0 3px rgba(0,212,255,0.15);}
  select option{background:#1e293b;}
  .btn-submit{width:100%;padding:15px;background:linear-gradient(135deg,#00d4ff,#0ea5e9);
    color:#020617;border:none;border-radius:14px;font-size:16px;font-weight:800;
    letter-spacing:1px;cursor:pointer;transition:0.3s;margin-top:8px;text-transform:uppercase;}
  .btn-submit:hover{transform:translateY(-2px);box-shadow:0 12px 30px rgba(0,212,255,0.4);}
  .btn-danger{width:100%;padding:15px;background:rgba(239,68,68,0.15);color:#f87171;
    border:1px solid rgba(239,68,68,0.3);border-radius:14px;font-size:16px;font-weight:800;
    cursor:pointer;transition:0.3s;margin-top:8px;}
  .btn-danger:hover{background:rgba(239,68,68,0.25);box-shadow:0 0 20px rgba(239,68,68,0.3);}
  .divider{display:flex;align-items:center;gap:12px;margin:24px 0;}
  .divider::before,.divider::after{content:'';flex:1;height:1px;background:rgba(255,255,255,0.1);}
  .divider span{color:#475569;font-size:13px;white-space:nowrap;}
  .link-alt{text-align:center;font-size:14px;color:#64748b;}
  .link-alt a{color:#00d4ff;text-decoration:none;font-weight:600;}
  .error-msg{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);
    color:#fca5a5;border-radius:12px;padding:12px 16px;font-size:14px;margin-bottom:20px;}
  .success-msg{background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);
    color:#86efac;border-radius:12px;padding:12px 16px;font-size:14px;margin-bottom:20px;}
  .info-msg{background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.25);
    color:#7dd3fc;border-radius:12px;padding:12px 16px;font-size:14px;margin-bottom:20px;}
  .profil-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:18px;}
  .profil-card{border:2px solid rgba(255,255,255,0.1);border-radius:16px;padding:16px 8px;
    text-align:center;cursor:pointer;transition:0.25s;background:rgba(255,255,255,0.03);
    position:relative;}
  .profil-card input[type=radio]{position:absolute;opacity:0;width:0;height:0;margin:0;}
  .profil-card .icon{font-size:28px;display:block;margin-bottom:6px;}
  .profil-card .label{font-size:11px;font-weight:700;letter-spacing:1px;color:#94a3b8;}
  .profil-card:has(input:checked){border-color:#00d4ff;background:rgba(0,212,255,0.1);
    box-shadow:0 0 20px rgba(0,212,255,0.2);}
  .profil-card:has(input:checked) .label{color:#00d4ff;}
  .two-col{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  .two-col>div{margin:0;}
  #type_entreprise_group{display:none;}
  .warn-box{background:rgba(251,191,36,0.1);border:1px solid rgba(251,191,36,0.3);
    color:#fde68a;border-radius:14px;padding:16px;font-size:14px;margin-bottom:20px;
    line-height:1.6;}
</style>"""


def _page(title, content, wide=False):
    max_w = "620px" if wide else "540px"
    return f"""<!DOCTYPE html><html lang="fr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
{AUTH_STYLE}<style>.auth-wrap{{max-width:{max_w};}}</style>
</head><body>{content}</body></html>"""


# ═══════════════════════════════════════════════════════════
#  INSCRIPTION  GET /register
# ═══════════════════════════════════════════════════════════

@router.get("/register", response_class=HTMLResponse)
def register_page(error: str = ""):
    err = f'<div class="error-msg">⚠️ {error}</div>' if error else ""
    content = f"""
    <div class="auth-wrap">
    <div class="auth-card">
      <div class="brand">💎 SDE</div>
      <div class="sub-brand">Smart Distribution Engine — Créer votre compte</div>
      {err}
      <form method="POST" action="/register">
        <label>Choisissez votre profil *</label>
        <div class="profil-grid">
          <label class="profil-card"><input type="radio" name="profil" value="CLIENT" required>
            <span class="icon">🛒</span><span class="label">CLIENT</span></label>
          <label class="profil-card"><input type="radio" name="profil" value="FOURNISSEUR">
            <span class="icon">🏭</span><span class="label">FOURNISSEUR</span></label>
          <label class="profil-card"><input type="radio" name="profil" value="ENTREPRISE">
            <span class="icon">🏢</span><span class="label">ENTREPRISE</span></label>
        </div>
        <div id="type_entreprise_group">
          <label>Type d'établissement *</label>
          <select name="type_entreprise" id="type_entreprise">
            <option value="">— Sélectionner —</option>
            <option value="SUPERMARCHE">🏪 Supermarché</option>
            <option value="MARCHE">🥬 Marché</option>
            <option value="ALIMENTATION">🛍️ Alimentation / Épicerie</option>
            <option value="BOUTIQUE_VETEMENTS">👗 Boutique Vêtements</option>
            <option value="RESTAURANT">🍽️ Restaurant</option>
            <option value="SECRETARIAT">📋 Secrétariat / Bureau</option>
            <option value="AUTRE">🔧 Autre</option>
          </select>
        </div>
        <div class="two-col">
          <div><label>Prénom *</label><input type="text" name="prenom" placeholder="Jean" required></div>
          <div><label>Nom *</label><input type="text" name="nom" placeholder="Dupont" required></div>
        </div>
        <div class="two-col">
          <div><label>Sexe *</label>
            <select name="sexe" required>
              <option value="">— Sélectionner —</option>
              <option>Homme</option><option>Femme</option><option>Autre</option>
            </select></div>
          <div><label>Téléphone *</label>
            <input type="tel" name="telephone" placeholder="+237 6XX XXX XXX" required></div>
        </div>
        <label>Adresse e-mail *</label>
        <input type="email" name="email" placeholder="vous@exemple.com" required>
        <div class="two-col">
          <div><label>Mot de passe *</label>
            <input type="password" name="password" placeholder="••••••••" required minlength="6"></div>
          <div><label>Confirmer *</label>
            <input type="password" name="confirm_password" placeholder="••••••••" required></div>
        </div>
        <button type="submit" class="btn-submit">✨ Créer mon compte</button>
      </form>
      <div class="divider"><span>Déjà inscrit ?</span></div>
      <div class="link-alt"><a href="/login">→ Se connecter</a></div>
    </div></div>
    <script>
      document.querySelectorAll('input[name="profil"]').forEach(r => {{
        r.addEventListener('change', function() {{
          const g = document.getElementById('type_entreprise_group');
          const s = document.getElementById('type_entreprise');
          if(this.value==='ENTREPRISE'){{g.style.display='block';s.required=true;}}
          else{{g.style.display='none';s.required=false;s.value='';}}
        }});
      }});
    </script>"""
    return _page("Créer un compte — SDE", content, wide=True)


# ═══════════════════════════════════════════════════════════
#  INSCRIPTION  POST /register
# ═══════════════════════════════════════════════════════════

@router.post("/register")
def register(
    request: Request,
    nom: str = Form(...), prenom: str = Form(...),
    sexe: str = Form(...), telephone: str = Form(...),
    email: str = Form(...), password: str = Form(...),
    confirm_password: str = Form(...), profil: str = Form(...),
    type_entreprise: str = Form(""),
    db: Session = Depends(get_db),
):
    if password != confirm_password:
        return RedirectResponse("/register?error=Les+mots+de+passe+ne+correspondent+pas", 303)
    if profil not in ("CLIENT", "FOURNISSEUR", "ENTREPRISE"):
        return RedirectResponse("/register?error=Profil+invalide", 303)
    if profil == "ENTREPRISE" and not type_entreprise:
        return RedirectResponse("/register?error=Veuillez+choisir+un+type+d'établissement", 303)
    if db.query(User).filter(User.email == email.lower().strip()).first():
        return RedirectResponse("/register?error=Cet+email+est+déjà+utilisé", 303)

    token   = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)

    user = User(
        nom=nom.strip(), prenom=prenom.strip(), sexe=sexe,
        telephone=telephone.strip(), email=email.lower().strip(),
        password_hash=hash_password(password), profil=profil,
        type_entreprise=type_entreprise if profil == "ENTREPRISE" else None,
        is_active=True, is_verified=False,
        verification_token=token, token_expires_at=expires,
    )
    db.add(user)
    db.commit()

    # Envoi de l'e-mail de confirmation
    send_verification_email(user.email, user.prenom, token)

    return RedirectResponse(f"/register/confirmer?email={user.email}", 303)


@router.get("/register/confirmer", response_class=HTMLResponse)
def register_confirm(email: str = ""):
    content = f"""
    <div class="auth-wrap">
    <div class="auth-card" style="text-align:center;">
      <div style="font-size:5rem;margin-bottom:20px;">📧</div>
      <div class="brand">Vérifiez votre e-mail</div>
      <div class="success-msg" style="margin-top:24px;">
        Un lien de confirmation a été envoyé à<br>
        <strong style="color:#00d4ff;">{email}</strong>
      </div>
      <p style="color:#94a3b8;font-size:14px;line-height:1.7;">
        Ouvrez votre boîte mail et cliquez sur le lien pour
        <strong>activer votre compte</strong>.<br>
        Le lien expire dans <strong>24 heures</strong>.
      </p>
      <div class="divider"><span>Pas reçu l'e-mail ?</span></div>
      <form method="POST" action="/resend-verification">
        <input type="hidden" name="email" value="{email}">
        <button type="submit" class="btn-submit" style="background:rgba(0,212,255,0.15);
          color:#00d4ff;border:1px solid rgba(0,212,255,0.3);">
          🔄 Renvoyer le lien
        </button>
      </form>
    </div></div>"""
    return _page("Vérifiez votre e-mail", content)


# ═══════════════════════════════════════════════════════════
#  VÉRIFICATION E-MAIL  GET /verify-email/{token}
# ═══════════════════════════════════════════════════════════

@router.get("/verify-email/{token}", response_class=HTMLResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()

    # Token introuvable
    if not user:
        content = """<div class="auth-wrap"><div class="auth-card" style="text-align:center;">
          <div style="font-size:4rem;margin-bottom:16px;">❌</div>
          <div class="brand" style="color:#f87171;">Lien invalide</div>
          <div class="error-msg" style="margin-top:20px;">
            Ce lien de vérification est invalide ou a déjà été utilisé.
          </div>
          <div class="link-alt" style="margin-top:20px;">
            <a href="/login">→ Se connecter</a> &nbsp;|&nbsp;
            <a href="/register">Créer un compte</a>
          </div>
        </div></div>"""
        return _page("Lien invalide", content)

    # Token expiré
    if user.token_expires_at and datetime.now() > user.token_expires_at:
        content = f"""<div class="auth-wrap"><div class="auth-card" style="text-align:center;">
          <div style="font-size:4rem;margin-bottom:16px;">⏰</div>
          <div class="brand" style="color:#fbbf24;">Lien expiré</div>
          <div class="error-msg" style="margin-top:20px;">
            Ce lien a expiré (valable 24h). Demandez-en un nouveau.
          </div>
          <form method="POST" action="/resend-verification" style="margin-top:20px;">
            <input type="hidden" name="email" value="{user.email}">
            <button type="submit" class="btn-submit">🔄 Renvoyer un lien</button>
          </form>
        </div></div>"""
        return _page("Lien expiré", content)

    # ✅ Activation
    user.is_verified          = True
    user.verification_token   = None
    user.token_expires_at     = None
    db.commit()

    # Connecter automatiquement
    _set_session(request=None, user=user, session=None)

    content = f"""<div class="auth-wrap"><div class="auth-card" style="text-align:center;">
      <div style="font-size:5rem;margin-bottom:16px;">🎉</div>
      <div class="brand">Compte activé !</div>
      <div class="success-msg" style="margin-top:20px;">
        Bienvenue <strong>{user.prenom}</strong> !<br>
        Votre compte est maintenant actif.
      </div>
      <a href="/login" class="btn-submit" style="display:block;text-decoration:none;
        text-align:center;margin-top:24px;padding:15px;">
        🚀 Se connecter maintenant
      </a>
    </div></div>"""
    return _page("Compte activé !", content)


# ═══════════════════════════════════════════════════════════
#  RENVOYER LE LIEN  POST /resend-verification
# ═══════════════════════════════════════════════════════════

@router.post("/resend-verification")
def resend_verification(email: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if user and not user.is_verified:
        token              = secrets.token_urlsafe(32)
        user.verification_token = token
        user.token_expires_at   = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        db.commit()
        send_resend_verification_email(user.email, user.prenom, token)
    # Toujours rediriger vers la même page (ne pas révéler si l'email existe)
    return RedirectResponse(f"/register/confirmer?email={email}", 303)


# ═══════════════════════════════════════════════════════════
#  CONNEXION  GET + POST /login
# ═══════════════════════════════════════════════════════════

@router.get("/login", response_class=HTMLResponse)
def login_page(error: str = "", info: str = ""):
    err  = f'<div class="error-msg">⚠️ {error}</div>' if error else ""
    inf  = f'<div class="info-msg">ℹ️ {info}</div>'   if info  else ""
    content = f"""
    <div class="auth-wrap">
    <div class="auth-card">
      <div class="brand">💎 SDE</div>
      <div class="sub-brand">Smart Distribution Engine</div>
      {err}{inf}
      <form method="POST" action="/login">
        <label>Adresse e-mail</label>
        <input type="email" name="email" placeholder="vous@exemple.com" required autofocus>
        <label>Mot de passe</label>
        <input type="password" name="password" placeholder="••••••••" required>
        <button type="submit" class="btn-submit">🔐 Se connecter</button>
      </form>
      <div class="divider"><span>Pas encore de compte ?</span></div>
      <div class="link-alt"><a href="/register">→ Créer un compte gratuitement</a></div>
    </div></div>"""
    return _page("Connexion — SDE", content)


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...), password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user or not verify_password(password, user.password_hash):
        return RedirectResponse("/login?error=Email+ou+mot+de+passe+incorrect", 303)
    if not user.is_active:
        return RedirectResponse("/login?error=Compte+désactivé", 303)

    # Compte non vérifié → renvoyer vers la page de confirmation
    if not user.is_verified:
        return RedirectResponse(
            f"/login?error=Compte+non+vérifié.+Consultez+vos+e-mails."
            f"&info=Vous+pouvez+demander+un+nouveau+lien+sur+la+page+de+confirmation",
            303
        )

    _set_session(request, user)
    return RedirectResponse(_redirect_for(user.profil), 303)


# ═══════════════════════════════════════════════════════════
#  DÉCONNEXION  GET /logout
# ═══════════════════════════════════════════════════════════

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", 303)


# ═══════════════════════════════════════════════════════════
#  SUPPRESSION DU COMPTE  GET + POST /mon-compte/supprimer
# ═══════════════════════════════════════════════════════════

@router.get("/mon-compte/supprimer", response_class=HTMLResponse)
def delete_account_page(request: Request, error: str = ""):
    if not request.session.get("user_id"):
        return RedirectResponse("/login")
    nom = request.session.get("user_nom", "utilisateur")
    err = f'<div class="error-msg">⚠️ {error}</div>' if error else ""
    content = f"""
    <div class="auth-wrap">
    <div class="auth-card">
      <div class="brand" style="color:#f87171;">⚠️ Supprimer le compte</div>
      <div class="sub-brand">Cette action est irréversible</div>
      {err}
      <div class="warn-box">
        🗑️ Vous êtes sur le point de supprimer définitivement le compte de
        <strong>{nom}</strong>.<br><br>
        Toutes vos données seront effacées :<br>
        commandes, historique, catalogue, informations personnelles.<br><br>
        <strong>Cette action ne peut pas être annulée.</strong>
      </div>
      <form method="POST" action="/mon-compte/supprimer">
        <label>Confirmez avec votre mot de passe *</label>
        <input type="password" name="password" placeholder="Votre mot de passe actuel" required>
        <button type="submit" class="btn-danger">🗑️ Supprimer définitivement mon compte</button>
      </form>
      <div class="divider"><span>Vous avez changé d'avis ?</span></div>
      <div class="link-alt"><a href="/">← Retour à l'accueil</a></div>
    </div></div>"""
    return _page("Supprimer mon compte", content)


@router.post("/mon-compte/supprimer")
def delete_account(
    request: Request,
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse("/login")

    # Vérification du mot de passe
    if not verify_password(password, user.password_hash):
        return RedirectResponse("/mon-compte/supprimer?error=Mot+de+passe+incorrect", 303)

    # Sauvegarder infos pour l'e-mail AVANT suppression
    email_backup  = user.email
    prenom_backup = user.prenom

    # Suppression en cascade des données liées
    for commande in db.query(Commande).filter(Commande.client_id == user_id).all():
        db.query(CommandeItem).filter(CommandeItem.commande_id == commande.id).delete()
        db.delete(commande)

    db.query(ProduitFournisseur).filter(
        ProduitFournisseur.fournisseur_id == user_id
    ).delete()

    db.query(CommandeB2B).filter(
        (CommandeB2B.entreprise_id == user_id) |
        (CommandeB2B.fournisseur_id == user_id)
    ).delete()

    db.delete(user)
    db.commit()

    # Vider la session
    request.session.clear()

    # E-mail de confirmation de suppression
    send_deletion_email(email_backup, prenom_backup)

    return RedirectResponse("/compte-supprime", 303)


@router.get("/compte-supprime", response_class=HTMLResponse)
def compte_supprime():
    content = """
    <div class="auth-wrap">
    <div class="auth-card" style="text-align:center;">
      <div style="font-size:5rem;margin-bottom:20px;">👋</div>
      <div class="brand" style="color:#94a3b8;">Compte supprimé</div>
      <div class="success-msg" style="margin-top:24px;">
        Votre compte a bien été supprimé.<br>
        Un e-mail de confirmation vous a été envoyé.
      </div>
      <p style="color:#64748b;font-size:14px;margin:20px 0;">
        Merci d'avoir utilisé SDE Platform.<br>
        Vous pouvez créer un nouveau compte à tout moment.
      </p>
      <a href="/register" class="btn-submit" style="display:block;text-decoration:none;
        text-align:center;padding:15px;">Créer un nouveau compte</a>
    </div></div>"""
    return _page("Compte supprimé", content)


# ═══════════════════════════════════════════════════════════
#  HELPERS INTERNES
# ═══════════════════════════════════════════════════════════

def _set_session(request, user, session=None):
    s = session or (request.session if request else {})
    if not s and not request:
        return
    sess = request.session if request else s
    sess["user_id"]   = user.id
    sess["user_nom"]  = f"{user.prenom} {user.nom}"
    sess["profil"]    = user.profil
    sess["user_role"] = user.profil
    sess["user_name"] = f"{user.prenom} {user.nom}"
    if user.profil == "ENTREPRISE":
        sess["admin"] = True
    else:
        sess.pop("admin", None)


def _redirect_for(profil: str) -> str:
    return {"CLIENT": "/shop", "FOURNISSEUR": "/fournisseur", "ENTREPRISE": "/"}.get(profil, "/login")
