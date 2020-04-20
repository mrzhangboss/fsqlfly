import sqlalchemy as sa
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()


class Base(_Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=sa.func.now())
    updated_at = Column(DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    is_hidden = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    def as_dict(self):
        return {x for x in vars(self) if x != '_sa_instance_state'}


class User(Base):
    __tablename__ = 'user'
    name = Column(String(20))


class Book(Base):
    __tablename__ = 'book'
    name = Column(String(20))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    user = relationship('User', backref="books")


engine = sa.create_engine('sqlite://', echo=True)
DBSession = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
session = DBSession()
new_user = User(id=5, name='Bob')
session.add(new_user)
session.commit()
book1 = Book(name='test1', user=new_user)
session.add(book1)
book2 = Book(name='test2', user=new_user)
session.add(book2)
session.commit()
# 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
user = session.query(User).filter(User.id == 5).one()
print('books', [x.as_dict() for x in user.books])
print(user.as_dict())

session.close()
