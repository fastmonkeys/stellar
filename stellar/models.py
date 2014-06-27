import sqlalchemy as sa
from datetime import datetime
from database import Base


class Snapshot(Base):
    __tablename__ = 'snapshot'
    id = sa.Column(sa.Integer, sa.Sequence('snapshot_id_seq'), primary_key=True)
    table_name = sa.Column(sa.String(255), nullable=False)
    table_hash = sa.Column(sa.String(32), nullable=False)
    project_name = sa.Column(sa.String(255), nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
