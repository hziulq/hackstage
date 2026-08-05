from flask import Blueprint, jsonify, request

bp = Blueprint("hello", __name__, url_prefix="/api")


@bp.get("/hello")
def hello():
    """挨拶(動作確認用)
    ---
    get:
      summary: 挨拶を返す(認証不要)
      parameters:
        - in: query
          name: name
          required: false
          schema:
            type: string
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: "hello, world!"
    """
    name = request.args.get("name", "world")
    return jsonify({"message": f"hello, {name}!"})
