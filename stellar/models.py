import sqlalchemy as sa
from datetime import datetime

from sqlalchemy.orm import relationship, backref
from decimal import Decimal
from database import Base, db

class Snapshot(Base):
    __tablename__ = 'snapshot'
    id = sa.Column(sa.Integer, sa.Sequence('snapshot_id_seq'), primary_key=True)
    table_name = sa.Column(sa.String(255))
    table_hash = sa.Column(sa.String(32))
    project_name = sa.Column(sa.String(255))
    name = sa.Column(sa.String(255))
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)