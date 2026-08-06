from flask import jsonify
 
 
def error_response(code, message, fields=None, status=400):
    """design.md §7 のエラー契約に合わせた統一フォーマット。
 
    {"error": {"code": "...", "message": "...", "fields": {...}}}
    """
    body = {"error": {"code": code, "message": message}}
    if fields:
        body["error"]["fields"] = fields
    return jsonify(body), status
