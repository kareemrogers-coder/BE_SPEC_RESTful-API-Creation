### Lesson 3: Assignment RESTful API Creation

###### Beginning the creation of a RESTful API

**Task:**

1. Install flask-marshmallow, and marshmallow-sqlalchemy.
```py
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
```
2. Create Schemas for your Customer model (hint: use the SQLAlchemyAutoSchema to construct a schema from the model itself).
```py
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') #used to hide sensitive information 

class Base(DeclarativeBase):
    pass

db= SQLAlchemy(model_class= Base)
ma=Marshmallow()

db.init_app(app)
ma.init_app(app)
```
**Implement CRUD for your Customer:**

- /customers POST: Create Customer
```py
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
```
- /customers GET: Get all customers:

```py
@app.route("/customers", methods =['GET'])
def get_customers():
    query = select(Customers)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers), 200
```


- /customers/<id> GET: Get customer belonging to id:

```py
@app.route ("/customers/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customers, customer_id )

    return customer_schema.jsonify(customer), 200
```


- /customers/<id> PUT: Update Customer:

```py
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
```

- /customers/<id> DELETE: Delete Customer:

```py
@app.route("/customers/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customers, customer_id)

    if customer == None:
        return jsonify({"message": "invalid id"}), 400

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"User at ID {customer_id}  has been deleted "})
```