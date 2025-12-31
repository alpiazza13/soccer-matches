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
    score: Dict[str, Any]  # Keeps the complex score JSON intact

    model_config = ConfigDict(from_attributes=True)