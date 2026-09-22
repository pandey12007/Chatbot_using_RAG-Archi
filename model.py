from sqlalchemy import String , Integer , Column
from database import Base

class IncidentQuery(Base):
    __tablename__ = "incident_query"
    
    id = Column(Integer,primary_key=True,index=True)
    query = Column(String,nullable=False)
    incident_id = Column(String,nullable=False)
    category = Column(String,nullable=False)
    subcategory = Column(String,nullable=False)
    severity = Column(String,nullable=False)
    solution = Column(String,nullable=False)
    
    