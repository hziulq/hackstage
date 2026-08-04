from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.dragon import Dragon
from app.schemas.dragon import dragon_schema, dragons_schema

dragon_bp = Blueprint("dragon", __name__)


@dragon_bp.route("", methods=["GET"])
def get_dragons():
    dragons = Dragon.query.all()
    return jsonify(dragons_schema.dump(dragons)), 200


@dragon_bp.route("/<int:dragon_id>", methods=["GET"])
def get_dragon(dragon_id):
    dragon = Dragon.query.get_or_404(dragon_id)
    return jsonify(dragon_schema.dump(dragon)), 200


@dragon_bp.route("", methods=["POST"])
def create_dragon():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        data = dragon_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    dragon = Dragon(
        name=data["name"],
        element=data["element"],
        level=data.get("level", 1),
    )
    db.session.add(dragon)
    db.session.commit()

    return jsonify(dragon_schema.dump(dragon)), 201


@dragon_bp.route("/<int:dragon_id>", methods=["PUT"])
def update_dragon(dragon_id):
    dragon = Dragon.query.get_or_404(dragon_id)
    json_data = request.get_json()

    try:
        data = dragon_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    for key, value in data.items():
        setattr(dragon, key, value)

    db.session.commit()
    return jsonify(dragon_schema.dump(dragon)), 200


@dragon_bp.route("/<int:dragon_id>", methods=["DELETE"])
def delete_dragon(dragon_id):
    dragon = Dragon.query.get_or_404(dragon_id)
    db.session.delete(dragon)
    db.session.commit()
    return jsonify({"message": "deleted"}), 200