from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import os #link to the os.environ.get to retrieve the uri link
from datetime import date
from sqlalchemy import Column, select
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') #used to hide sensitive information 



class Base(DeclarativeBase):
    pass

db= SQLAlchemy(model_class= Base)
ma=Marshmallow()

db.init_app(app)
ma.init_app(app)


service_mechanics = db.Table(
    "service_mechanics",
    Base.metadata,
    Column("ticket_id", db.ForeignKey("service_tickets.id")),
    Column("mechanic_id", db.ForeignKey("mechanics.id"))
)

class Customers(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(80), nullable=False)##VARCHAR IN SQL BUT STR IN PYTHON
    email: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20))

class Service_tickets(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(17), nullable=False, unique=True)
    service_date: Mapped[date] = mapped_column(nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(1500), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))

class Mechanics(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(80), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False ) # requried for contact purpose 
    salary: Mapped[float] = mapped_column(db.Float(7), nullable=False)


# Schema 
##each model needs a schema

class CustomersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers

class Service_ticketsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service_tickets

class MechanicsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics


###This allow you serach and get single or Multiple customers or attribute hance the singular and pural commands
customer_schema = CustomersSchema()
customers_schema = CustomersSchema(many=True)

service_ticket_schema = Service_ticketsSchema()
service_tickets_schema = Service_ticketsSchema(many=True)

mechanic_schema = MechanicsSchema()
mechanics_schema = MechanicsSchema(many=True)

#Routes
#@ is the wrapper of the funtions, it acts as the mailman to the server.

@app.route("/customers", methods =['POST'])
def create_customer():
    try: # validation error, this type of error handling, handles commands that isnt recognizable 
        customer_data = customer_schema.load(request.json) # command this is to load only validate information
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customers(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer) # add to session
    db.session.commit() #upload info to database

    return jsonify("Customer has been added our database."), 201



@app.route("/customers", methods =['GET'])
def get_customers():
    query = select(Customers)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers), 200






@app.route ("/customers/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customers, customer_id )

    return customer_schema.jsonify(customer), 200



@app.route("/customers/<int:customer_id>", methods =['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customers, customer_id)

    if customer == None:
        return jsonify ({"message": "invalid id"}), 400
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in customer_data.items():
        if value:
            setattr(customer, field, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200




@app.route("/customers/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customers, customer_id)

    if customer == None:
        return jsonify({"message": "invalid id"}), 400

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"User at ID {customer_id}  has been deleted "})



if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)