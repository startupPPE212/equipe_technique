from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
 
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    sexe = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profil = Column(String, nullable=False)  # 'CLIENT', 'FOURNISSEUR', 'ENTREPRISE'
    date_creation = Column(DateTime, default=datetime.now)
     
class Vente(Base):
    __tablename__ = "ventes"
 
    id = Column(Integer, primary_key=True, index=True)
    age = Column(String)
    sexe = Column(String)
    total = Column(Integer)
    date_vente = Column(DateTime, default=datetime.now)
    
    items = relationship("VenteItem", back_populates="vente")
 
 
class VenteItem(Base):
    __tablename__ = "vente_items"
 
    id = Column(Integer, primary_key=True, index=True)
    vente_id = Column(Integer, ForeignKey("ventes.id"))
    rayon = Column(String)
    produit = Column(String)
    quantite = Column(Integer)
    prix_unitaire = Column(Integer)
    total = Column(Integer)
   
 
    vente = relationship("Vente", back_populates="items")
 
class Stock(Base):
    __tablename__ = "stocks"
 
    id = Column(Integer, primary_key=True, index=True)
    rayon = Column(String)
    produit = Column(String, index=True)
    prix = Column(Float)
    quantite = Column(Integer, default=0)
 
    __table_args__ = (
        UniqueConstraint('produit', name='uq_stock_produit'),
    )

