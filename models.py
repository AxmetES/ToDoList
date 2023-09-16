from sqlalchemy import Integer, String, Column, DateTime, func

from db import Base, engine


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    task = Column(String)
    created_at = Column(DateTime, default=func.now())


Base.metadata.create_all(engine)