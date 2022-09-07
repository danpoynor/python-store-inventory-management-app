"""Models for the application."""
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Brand(Base):
    """Brand class."""

    __tablename__ = 'brands'
    brand_id = Column(Integer, primary_key=True, unique=True)
    brand_name = Column('brand_name', String)

    def __repr__(self):
        """Representation of the object.

        Returns a string representation of an object.
        """
        return f'name: {self.product_name} quantity: {self.product_quantity} price: {self.product_price} date_updated: {self.date_updated}'


class Product(Base):
    """Product class."""

    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True, unique=True)
    product_name = Column('product_name', String)
    product_quantity = Column('product_quantity', Integer)
    product_price = Column('product_price', Integer)
    # date_updated to be stored as a DateTime object instead of just Date
    date_updated = Column('date_updated', DateTime)
    brand_id = Column(Integer, ForeignKey('brands.brand_id'))

    def __repr__(self):
        """Representation of the object.

        Returns a string representation of an object.
        """
        return f'name: {self.product_name} quantity: {self.product_quantity} price: {self.product_price} date_updated: {self.date_updated}'
