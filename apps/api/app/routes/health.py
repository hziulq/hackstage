from flask import Blueprint, jsonify

bp = Blueprint("health", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    """ヘルスチェック
    ---
    get:
      summary: ヘルスチェック(認証不要)
      responses:
        200:
          description: 正常
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: ok
    """
    return jsonify({"status": "ok"})
