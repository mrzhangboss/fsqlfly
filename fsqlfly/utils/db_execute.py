from sqlalchemy import create_engine


def execute(sql, url, *args) -> list:
    engine = create_engine(url)
    with engine.connect() as con:
        rs = con.execute(sql, *args)
        return list(rs)
