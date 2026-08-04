from flask import Blueprint, jsonify, request

bp = Blueprint("hello", __name__, url_prefix="/api")


@bp.get("/hello")
def hello():
    name = request.args.get("name", "world")
    return jsonify({"message": f"hello, {name}!"})
