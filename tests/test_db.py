import pytest
from sqlalchemy import text

from app.db.session import engine

def test_connection():
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_pgvector_installed():
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector' ")
        ).first()
    assert row is not None