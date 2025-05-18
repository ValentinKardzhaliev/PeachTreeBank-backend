from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from passlib.hash import bcrypt
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    transactions = relationship("Transaction", back_populates="owner")

    def set_password(self, password):
        self.hashed_password = bcrypt.hash(password)

    def check_password(self, password):
        return bcrypt.verify(password, self.hashed_password)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    from_account = Column(String)
    to_account = Column(String)
    amount = Column(Float)
    status = Column(String, default="yellow")

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="transactions")