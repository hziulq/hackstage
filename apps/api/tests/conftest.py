import pytest
from app import create_app
from app.extensions import db as _db
from app.extensions import limiter
from app.models.user import User
from sqlalchemy.orm import scoped_session, sessionmaker


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture(autouse=True)
def db_session(app):
    """各テストをSAVEPOINTで囲み、テスト後に必ずロールバックする(research.md §2)。

    開発用DB(dbサービス)に接続するが、テストで作成したデータは実際にはコミットされない。
    """
    with app.app_context():
        connection = _db.engine.connect()
        outer_transaction = connection.begin()

        session_factory = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
        test_session = scoped_session(session_factory)

        original_session = _db.session
        _db.session = test_session

        yield test_session

        _db.session = original_session
        test_session.remove()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture(autouse=True)
def reset_limiter(app):
    """Flask-Limiterのインメモリストレージをテストごとにリセットする(research.md §3)。"""
    with app.app_context():
        limiter.reset()
    yield


@pytest.fixture
def client(app):
    return app.test_client()


def create_user(email, password="correct-horse", display_name="テスト利用者"):
    """テスト用利用者を作成して返す(data-model.mdのテスト用利用者の形に従う)。"""
    user = User(email=email, display_name=display_name)
    user.set_password(password)
    _db.session.add(user)
    _db.session.commit()
    return user
