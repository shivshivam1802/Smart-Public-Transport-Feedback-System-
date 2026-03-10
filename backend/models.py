from sqlalchemy import Column, Integer, String, Float, Text
from .database import Base

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    sentiment = Column(String)   # positive / negative
    issues = Column(String)      # comma-separated: delay,overcrowding,cleanliness,staff,safety,infrastructure
    latitude = Column(Float)
    longitude = Column(Float)
    cluster = Column(Integer)    # DBSCAN cluster id; -1 = noise
