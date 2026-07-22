from pydantic import BaseModel
from typing import Optional

class DashboardSummary(BaseModel):
    activeProjects: int
    completedProjects: int
    totalTasks: int = 0
    completedTasks: int = 0
    todayTasks: int
    overdueTasks: int
    todayMeetings: int
    highPriorityTasks: int
    pendingInvitations: int = 0
    meetingsNeedingMOM: int = 0
    pendingApprovals: int = 0
    upcomingDeadlines: int = 0
    recentActivity: list = []
