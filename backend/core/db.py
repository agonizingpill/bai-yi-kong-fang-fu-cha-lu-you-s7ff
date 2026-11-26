from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine, inspect, text

from core.config import DATABASE_URL

metadata = MetaData()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def ensure_runtime_columns():
    """Add columns introduced after the initial snapshot on persistent volumes.

    metadata.create_all creates missing tables but does not ALTER existing ones.
    The benchmark database is normally fresh; this keeps a named development
    volume working as well.
    """
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    statements = []
    if 'return_forecasts' in tables:
        columns = {column['name'] for column in inspector.get_columns('return_forecasts')}
        if 'status' not in columns:
            statements.append(
                "ALTER TABLE return_forecasts "
                "ADD COLUMN status VARCHAR(32) NOT NULL DEFAULT '有效'"
            )
    if not statements:
        return
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


@contextmanager
def transaction():
    with engine.begin() as conn:
        yield conn
