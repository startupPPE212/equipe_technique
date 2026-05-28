"""
migrate.py — Migration complète
Ajoute toutes les colonnes manquantes à la table users et aux autres tables.
Idempotent : sûr à relancer plusieurs fois.
"""

from sqlalchemy import text, inspect


def run_migrations(engine):
    inspector = inspect(engine)
    existing  = inspector.get_table_names()

    with engine.connect() as conn:

        # ── TABLE users ────────────────────────────────────────
        if "users" in existing:
            cols = [c["name"] for c in inspector.get_columns("users")]

            # Colonnes à ajouter : (nom, type SQL, valeur par défaut pour les lignes existantes)
            user_cols = [
                ("sexe",               "TEXT",     "''"),
                ("telephone",          "TEXT",     "''"),
                ("profil",             "TEXT",     "'ENTREPRISE'"),
                ("type_entreprise",    "TEXT",     "NULL"),
                ("date_creation",      "DATETIME", "datetime('now')"),
                ("is_active",          "BOOLEAN",  "1"),
                ("is_verified",        "BOOLEAN",  "1"),   # comptes existants = vérifiés
                ("verification_token", "TEXT",     "NULL"),
                ("token_expires_at",   "DATETIME", "NULL"),
                ("password_hash",      "TEXT",     "''"),
            ]

            for col, col_type, default in user_cols:
                if col not in cols:
                    print(f"🔧 Ajout de users.{col}")
                    conn.execute(text(
                        f"ALTER TABLE users ADD COLUMN {col} {col_type}"
                    ))
                    if default != "NULL":
                        conn.execute(text(
                            f"UPDATE users SET {col} = {default} WHERE {col} IS NULL"
                        ))
                    conn.commit()

            # Migrer hashed_password → password_hash si nécessaire
            if "hashed_password" in cols and "password_hash" in [c["name"] for c in inspector.get_columns("users")]:
                print("🔧 Migration hashed_password → password_hash")
                conn.execute(text(
                    "UPDATE users SET password_hash = hashed_password "
                    "WHERE password_hash = '' AND hashed_password IS NOT NULL"
                ))
                conn.commit()

        # ── TABLE ventes ───────────────────────────────────────
        if "ventes" in existing:
            cols = [c["name"] for c in inspector.get_columns("ventes")]
            if "date_vente" not in cols:
                print("🔧 Ajout de ventes.date_vente")
                conn.execute(text("ALTER TABLE ventes ADD COLUMN date_vente DATETIME"))
                conn.execute(text("UPDATE ventes SET date_vente = datetime('now') WHERE date_vente IS NULL"))
                conn.commit()

        # ── TABLE vente_items ──────────────────────────────────
        if "vente_items" in existing:
            cols = [c["name"] for c in inspector.get_columns("vente_items")]
            for col, typ in [
                ("rayon","TEXT"),("produit","TEXT"),
                ("quantite","INTEGER"),("prix_unitaire","INTEGER"),("total","INTEGER")
            ]:
                if col not in cols:
                    print(f"🔧 Ajout de vente_items.{col}")
                    conn.execute(text(f"ALTER TABLE vente_items ADD COLUMN {col} {typ}"))
                    conn.commit()

        # ── TABLE stocks ───────────────────────────────────────
        if "stocks" in existing:
            cols = [c["name"] for c in inspector.get_columns("stocks")]
            if "quantite" not in cols:
                print("🔧 Ajout de stocks.quantite")
                conn.execute(text("ALTER TABLE stocks ADD COLUMN quantite INTEGER DEFAULT 0"))
                conn.commit()

    print("🚀 Migrations terminées — base de données à jour.")
