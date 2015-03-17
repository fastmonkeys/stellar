from sqlalchemy import create_engine


def get_conn(url):
    engine = create_engine(url, echo=False)
    return engine.connect()
