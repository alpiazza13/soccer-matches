from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

class TeamSchema(BaseModel):
    """Data structure for Teams."""
    id: int
    name: str
    short_name: Optional[str] = None
    tla: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CompetitionSchema(BaseModel):
    """Data structure for Competitions."""
    id: int
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)

class ScoreValues(BaseModel):
    """Sub-structure for actual score numbers."""
    home: Optional[int] = None
    away: Optional[int] = None
    model_config = ConfigDict(extra='allow')

class ScoreSchema(BaseModel):
    """Structured score data with 'extra=allow' for API flexibility."""
    winner: Optional[str] = None
    duration: str
    fullTime: ScoreValues
    halfTime: Optional[ScoreValues] = None
    
    # if the API adds new fields, Pydantic will still accept them in _extract_match_info and store them in the object
    model_config = ConfigDict(extra='allow')

class MatchSchema(BaseModel):
    """
    The master structure for a Match. 
    Nests Team and Competition schemas for full type-safety.
    """
    match_id: int
    status: str
    utc_date: datetime
    home_team: TeamSchema
    away_team: TeamSchema
    competition: CompetitionSchema
    score: ScoreSchema

    model_config = ConfigDict(from_attributes=True)