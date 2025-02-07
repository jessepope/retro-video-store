from app import db
from app.models.customer import Customer
from app.models.video import Video
from app.models.rental import Rental
from flask import Blueprint, jsonify, request, abort, make_response

from app.routes.video_routes import check_for_valid_input

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

def validate_customer_input(request_body):
    '''ensure all input from request body is a correct 
    and valid data type, abort and return 400 error 
    message if the data is not valid'''
    for key, value in request_body.items():
        if type(value) is not str:
            abort(make_response({"Invalid Input": f"The {key} value must be a string."}, 400))
    return None

@customers_bp.route("", methods=["GET"])
def get_customers():
    sort_query = request.args.get("sort")
    if sort_query == "asc":
        customers = Customer.query.order_by(Customer.name).all()
    elif sort_query == "desc":
        customers = Customer.query.order_by(Customer.name.desc()).all()
    else:
        customers = Customer.query.all()

    response_body = [customer.to_dict() for customer in customers]
    return jsonify(response_body), 200

@customers_bp.route("/<customer_id>", methods=["GET"])
def get_single_customer(customer_id):
    if customer_id.isdigit() == False:
        return jsonify(None), 400
    
    customer = Customer.query.get(customer_id)

    if customer is None:
        return jsonify({'message': f'Customer {customer_id} was not found'}), 404

    response_body = customer.to_dict()

    return jsonify(response_body), 200

@customers_bp.route("/<customer_id>/rentals", methods=["GET"])
def get_customer_rentals(customer_id):
    if customer_id.isdigit() == False:
        return jsonify(None), 400
    
    customer = Customer.query.get(customer_id)

    if customer is None:
        return jsonify({'message': f'Customer {customer_id} was not found'}), 404

    rentals = Rental.query.filter_by(customer_id=customer_id, checked_in=False)
    
    response_body = []

    for rental in rentals:
        video = Video.query.get(rental.video_id)
        response_body.append(
        {
        "release_date": video.release_date,
        "title": video.title,
        "due_date": rental.due_date,
    })

    return jsonify(response_body), 200


@customers_bp.route("", methods=["POST"])
def post_new_customer():
    request_body = request.get_json()

    list_of_attributes = ["name", "postal_code", "phone"]

    check_for_valid_input(request_body, list_of_attributes)
    validate_customer_input(request_body)

    new_customer = Customer(name=request_body["name"],
    postal_code=request_body["postal_code"],
    phone=request_body["phone"])

    db.session.add(new_customer)
    db.session.commit()

    response_body = {
        "id": new_customer.id
    }
    return jsonify(response_body), 201

@customers_bp.route("/<customer_id>", methods=["PUT"])
def update_customer(customer_id):
    customer = Customer.query.get(customer_id)
    
    if customer is None:
        return jsonify({'message': f'Customer {customer_id} was not found'}), 404

    request_body = request.get_json()

    list_of_attributes = ["name", "postal_code", "phone"]
    
    check_for_valid_input(request_body, list_of_attributes)

    validate_customer_input(request_body)

    customer.name = request_body["name"]
    customer.postal_code = request_body["postal_code"]
    customer.phone = request_body["phone"]

    db.session.commit()

    response_body = customer.to_dict()

    return jsonify(response_body), 200

@customers_bp.route("/<customer_id>", methods=["DELETE"])
def delete_customer(customer_id):

    customer = Customer.query.get(customer_id)

    if customer is None:
        return jsonify({'message': f'Customer {customer_id} was not found'}), 404
    
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({
        'id': customer.id
        }), 200

