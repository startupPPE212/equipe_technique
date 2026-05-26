"""
migrate.py — Migration de base de données
Ajoute les colonnes/tables manquantes sans détruire les données existantes.
À appeler UNE FOIS au démarrage depuis main.py : run_migrations(engine)
"""

from sqlalchemy import text, inspect


def run_migrations(engine):
    """
    Vérifie l'état réel de la base et corrige les écarts avec les modèles.
    Toutes les opérations sont idempotentes (sûres à relancer plusieurs fois).
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    with engine.connect() as conn:

        # ──────────────────────────────────────────────────
        # TABLE : ventes  — ajouter date_vente si manquant
        # ──────────────────────────────────────────────────
        if "ventes" in existing_tables:
            cols_ventes = [c["name"] for c in inspector.get_columns("ventes")]

            if "date_vente" not in cols_ventes:
                print("🔧 Migration : ajout de ventes.date_vente")
                conn.execute(text(
                    "ALTER TABLE ventes ADD COLUMN date_vente DATETIME"
                ))
                # Remplir les lignes existantes avec la date du jour
                conn.execute(text(
                    "UPDATE ventes SET date_vente = datetime('now') WHERE date_vente IS NULL"
                ))
                conn.commit()
                print("✅  ventes.date_vente ajouté.")

        # ──────────────────────────────────────────────────
        # TABLE : vente_items  — vérifications défensives
        # ──────────────────────────────────────────────────
        if "vente_items" in existing_tables:
            cols_vi = [c["name"] for c in inspector.get_columns("vente_items")]
            for col, col_type in [
                ("rayon",         "TEXT"),
                ("produit",       "TEXT"),
                ("quantite",      "INTEGER"),
                ("prix_unitaire", "INTEGER"),
                ("total",         "INTEGER"),
            ]:
                if col not in cols_vi:
                    print(f"🔧 Migration : ajout de vente_items.{col}")
                    conn.execute(text(
                        f"ALTER TABLE vente_items ADD COLUMN {col} {col_type}"
                    ))
                    conn.commit()

        # ──────────────────────────────────────────────────
        # TABLE : stocks  — vérifications défensives
        # ──────────────────────────────────────────────────
        if "stocks" in existing_tables:
            cols_s = [c["name"] for c in inspector.get_columns("stocks")]
            if "quantite" not in cols_s:
                print("🔧 Migration : ajout de stocks.quantite")
                conn.execute(text(
                    "ALTER TABLE stocks ADD COLUMN quantite INTEGER DEFAULT 0"
                ))
                conn.commit()

        # ──────────────────────────────────────────────────
        # NOUVELLES TABLES  (créées par create_all, mais on
        # s'assure qu'elles existent avant toute requête)
        # Les tables users, commandes, commande_items,
        # produits_fournisseur, commandes_b2b sont gérées
        # automatiquement par Base.metadata.create_all().
        # ──────────────────────────────────────────────────

    print("🚀 Migrations terminées — base de données à jour.")
