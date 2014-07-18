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
    is_slave_ready = sa.Column(sa.Boolean, default=False)

    def __repr__(self):
        return "Snapshot(table_name=%r, name=%r)" % (
            self.table_name,
            self.name
        )
