from pydantic import BaseModel

class DashboardSummary(BaseModel):
    activeProjects: int
    completedProjects: int
    todayTasks: int
    overdueTasks: int
    todayMeetings: int
    highPriorityTasks: int
