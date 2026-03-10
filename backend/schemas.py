from pydantic import BaseModel

class FeedbackCreate(BaseModel):
    text: str
    latitude: float
    longitude: float

class FeedbackResponse(BaseModel):
    id: int
    message: str
    sentiment: str
    issues: list[str]

class AnalyticsSummary(BaseModel):
    total_feedback: int
    by_sentiment: dict
    by_issue: dict

class ClusterSummary(BaseModel):
    cluster_id: int
    count: int
    center_lat: float
    center_lon: float
    top_issues: list[str]
