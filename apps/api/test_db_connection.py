# DragonDB接続確認テスト用
from app import create_app
from app.extensions import db
from app.models.dragon import Dragon

app = create_app()

with app.app_context():
    db.create_all()
    print("テーブル作成: OK")

    d = Dragon(name="ファフニール", element="fire", level=50)
    db.session.add(d)
    db.session.commit()

    dragons = Dragon.query.all()
    print("登録件数:", len(dragons))
    for d in dragons:
        print(d)