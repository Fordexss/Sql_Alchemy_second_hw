from datetime import datetime

from flask import Flask, json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///shop.db', echo=True)
DeclarativeBase = declarative_base()
Session = sessionmaker(bind=engine)

products_clients_association = Table(
    'products_clients_association',
    DeclarativeBase.metadata,
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('client_id', Integer, ForeignKey('clients.id'))
)


class ProductType(DeclarativeBase):
    __tablename__ = 'product_types'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    products = relationship('Product', back_populates='type')


class Product(DeclarativeBase):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    type_id = Column(Integer, ForeignKey('product_types.id'))

    type = relationship('ProductType', back_populates='products')
    deliveries = relationship('Delivery', back_populates='product')
    sales = relationship('Sale', back_populates='product')
    clients = relationship('Client', secondary=products_clients_association, back_populates='products')


class Delivery(DeclarativeBase):
    __tablename__ = 'deliveries'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    quantity = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))

    product = relationship('Product', back_populates='deliveries')


class Sale(DeclarativeBase):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    quantity = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))

    product = relationship('Product', back_populates='sales')


class Client(DeclarativeBase):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    products = relationship('Product', secondary=products_clients_association, back_populates='clients')


DeclarativeBase.metadata.create_all(engine)

with Session() as session:
    type1 = ProductType(name='Електроніка')
    type2 = ProductType(name='Одяг')
    session.add_all([type1, type2])
    session.commit()

    product1 = Product(name='Смартфон', quantity=50, type=type1)
    product2 = Product(name='Футболка', quantity=100, type=type2)
    session.add_all([product1, product2])
    session.commit()

    delivery1 = Delivery(quantity=20, product=product1)
    delivery2 = Delivery(quantity=50, product=product2)
    session.add_all([delivery1, delivery2])
    session.commit()

    sale1 = Sale(quantity=10, product=product1)
    sale2 = Sale(quantity=30, product=product2)
    session.add_all([sale1, sale2])
    session.commit()

    client1 = Client(name='Іванов Максим', email='ivanov@gmail.com')
    client2 = Client(name='Петров Володимир', email='petrov@gmail.com')
    session.add_all([client1, client2])
    session.commit()

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_main():
    return "Ласкаво просимо на головну сторінку!"


@app.route('/product_types', methods=['GET'])
def get_product_types():
    try:
        with Session() as session:
            product_types = session.query(ProductType).all()
            result = [{'id': pt.id, 'name': pt.name, 'products': [p.name for p in pt.products]} for pt in product_types]
        response = app.response_class(
            response=json.dumps(result, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as e:
        print("Помилка у /product_types:", str(e))
        raise


@app.route('/products', methods=['GET'])
def get_products():
    try:
        with Session() as session:
            products = session.query(Product).options(joinedload(Product.type)).all()
            result = [{'id': p.id, 'name': p.name, 'quantity': p.quantity, 'type': p.type.name} for p in products]
        response = app.response_class(
            response=json.dumps(result, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as e:
        print("Помилка у /products:", str(e))
        raise


@app.route('/deliveries', methods=['GET'])
def get_deliveries():
    try:
        with Session() as session:
            deliveries = session.query(Delivery).all()
            result = [{'id': d.id, 'date': d.date, 'quantity': d.quantity, 'product_id': d.product_id} for d in
                      deliveries]
        response = app.response_class(
            response=json.dumps(result, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as e:
        print("Помилка у /deliveries:", str(e))
        raise


@app.route('/sales', methods=['GET'])
def get_sales():
    try:
        with Session() as session:
            sales = session.query(Sale).all()
            result = [{'id': s.id, 'date': s.date, 'quantity': s.quantity, 'product_id': s.product_id} for s in sales]
        response = app.response_class(
            response=json.dumps(result, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as e:
        print("Помилка у /sales:", str(e))
        raise


@app.route('/clients', methods=['GET'])
def get_clients():
    try:
        with Session() as session:
            clients = session.query(Client).all()
            result = [{'id': c.id, 'name': c.name, 'email': c.email, 'products': [p.name for p in c.products]} for c in
                      clients]
        response = app.response_class(
            response=json.dumps(result, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as e:
        print("Помилка у /clients:", str(e))
        raise
