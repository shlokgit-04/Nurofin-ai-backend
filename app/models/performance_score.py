from sqlalchemy import Column, Integer, Float, String, ForeignKey
from app.db.base_class import Base


class PerformanceScore(Base):
    __tablename__ = "performancescore"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    quarter_id = Column(Integer, ForeignKey("quarter.id"), nullable=False)
    period_type = Column(String, nullable=True)
    period_start = Column(String, nullable=True)
    period_end = Column(String, nullable=True)
    completed_tasks = Column(Integer, default=0)
    total_assigned = Column(Integer, default=0)
    completion_pct = Column(Float, default=0.0)
    on_time_count = Column(Integer, default=0)
    late_count = Column(Integer, default=0)
    avg_delay_hours = Column(Float, default=0.0)
    transferred_out = Column(Integer, default=0)
    transferred_in = Column(Integer, default=0)
    reopened_count = Column(Integer, default=0)
    bug_count = Column(Integer, default=0)
    estimated_hours_total = Column(Float, default=0.0)
    actual_hours_total = Column(Float, default=0.0)
    productivity_score = Column(Float, default=0.0)
    consistency_score = Column(Float, default=0.0)
    collaboration_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
