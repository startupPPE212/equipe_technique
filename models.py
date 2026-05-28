"""
models.py — Version 2
Ajouts par rapport à v1 :
  - User.verification_token  : token UUID pour confirmer l'email
  - User.is_verified         : True après clic sur le lien
  - User.token_expires_at    : expiration du token (24h)
Les autres modèles sont inchangés.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, UniqueConstraint, Text, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id               = Column(Integer, primary_key=True, index=True)
    nom              = Column(String,  nullable=False)
    prenom           = Column(String,  nullable=False)
    sexe             = Column(String,  nullable=False)
    telephone        = Column(String,  nullable=False)
    email            = Column(String,  unique=True, index=True, nullable=False)
    password_hash    = Column(String,  nullable=False)
    profil           = Column(String,  nullable=False)       # CLIENT | FOURNISSEUR | ENTREPRISE
    type_entreprise  = Column(String,  nullable=True)
    date_creation    = Column(DateTime, default=datetime.now)
    is_active        = Column(Boolean,  default=True)

    # ── Vérification e-mail ──────────────────────────
    is_verified        = Column(Boolean,  default=False)
    verification_token = Column(String,   nullable=True, unique=True)
    token_expires_at   = Column(DateTime, nullable=True)

    # Relations
    commandes            = relationship("Commande",           back_populates="client",
                                        foreign_keys="Commande.client_id")
    produits_fournisseur = relationship("ProduitFournisseur", back_populates="fournisseur")


class Commande(Base):
    __tablename__ = "commandes"
    id                = Column(Integer, primary_key=True, index=True)
    client_id         = Column(Integer, ForeignKey("users.id"))
    statut            = Column(String,  default="EN_ATTENTE")
    total             = Column(Integer, default=0)
    date_commande     = Column(DateTime, default=datetime.now)
    adresse_livraison = Column(Text,    nullable=True)
    notes             = Column(Text,    nullable=True)
    client = relationship("User", back_populates="commandes", foreign_keys=[client_id])
    items  = relationship("CommandeItem", back_populates="commande", cascade="all, delete-orphan")


class CommandeItem(Base):
    __tablename__ = "commande_items"
    id            = Column(Integer, primary_key=True, index=True)
    commande_id   = Column(Integer, ForeignKey("commandes.id"))
    produit_nom   = Column(String,  nullable=False)
    rayon         = Column(String,  nullable=True)
    quantite      = Column(Integer, nullable=False)
    prix_unitaire = Column(Integer, nullable=False)
    total         = Column(Integer, nullable=False)
    commande = relationship("Commande", back_populates="items")


class ProduitFournisseur(Base):
    __tablename__ = "produits_fournisseur"
    id                  = Column(Integer, primary_key=True, index=True)
    fournisseur_id      = Column(Integer, ForeignKey("users.id"))
    nom                 = Column(String,  nullable=False)
    categorie           = Column(String,  nullable=True)
    description         = Column(Text,    nullable=True)
    prix_gros           = Column(Float,   nullable=False)
    quantite_disponible = Column(Integer, default=0)
    quantite_minimum    = Column(Integer, default=10)
    unite               = Column(String,  default="unité")
    date_ajout          = Column(DateTime, default=datetime.now)
    is_disponible       = Column(Boolean,  default=True)
    fournisseur = relationship("User", back_populates="produits_fournisseur")


class CommandeB2B(Base):
    __tablename__ = "commandes_b2b"
    id             = Column(Integer, primary_key=True, index=True)
    entreprise_id  = Column(Integer, ForeignKey("users.id"))
    fournisseur_id = Column(Integer, ForeignKey("users.id"))
    produit_id     = Column(Integer, ForeignKey("produits_fournisseur.id"))
    quantite       = Column(Integer, nullable=False)
    prix_total     = Column(Float,   nullable=False)
    statut         = Column(String,  default="EN_ATTENTE")
    date_commande  = Column(DateTime, default=datetime.now)
    notes          = Column(Text,    nullable=True)
    entreprise  = relationship("User",               foreign_keys=[entreprise_id])
    fournisseur = relationship("User",               foreign_keys=[fournisseur_id])
    produit     = relationship("ProduitFournisseur", foreign_keys=[produit_id])


class Vente(Base):
    __tablename__ = "ventes"
    id         = Column(Integer, primary_key=True, index=True)
    age        = Column(String)
    sexe       = Column(String)
    total      = Column(Integer)
    date_vente = Column(DateTime, default=datetime.now)
    items = relationship("VenteItem", back_populates="vente")


class VenteItem(Base):
    __tablename__ = "vente_items"
    id            = Column(Integer, primary_key=True, index=True)
    vente_id      = Column(Integer, ForeignKey("ventes.id"))
    rayon         = Column(String)
    produit       = Column(String)
    quantite      = Column(Integer)
    prix_unitaire = Column(Integer)
    total         = Column(Integer)
    vente = relationship("Vente", back_populates="items")


class Stock(Base):
    __tablename__ = "stocks"
    id       = Column(Integer, primary_key=True, index=True)
    rayon    = Column(String)
    produit  = Column(String, index=True)
    prix     = Column(Float)
    quantite = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint('produit', name='uq_stock_produit'),)
