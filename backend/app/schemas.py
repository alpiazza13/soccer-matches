from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.models import Match, Team, Competition
from pydantic import EmailStr

class TeamSchema(BaseModel):
    """Data structure for Teams."""
    id: int = Field(alias=Team.external_id.key)
    name: str
    short_name: str| None = None
    tla: str| None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class CompetitionSchema(BaseModel):
    """Data structure for Competitions."""
    id: int = Field(alias=Competition.external_id.key)
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ScoreValues(BaseModel):
    """Sub-structure for actual score numbers."""
    home: int | None = None
    away: int | None = None
    model_config = ConfigDict(from_attributes=True, extra='allow')

class ScoreSchema(BaseModel):
    """Structured score data with 'extra=allow' for API flexibility."""
    winner: str | None = None
    duration: str
    fullTime: ScoreValues
    halfTime: ScoreValues | None = None

    # if the API adds new fields, Pydantic will still accept them in _extract_match_info and store them in the object
    model_config = ConfigDict(from_attributes=True, extra='allow')

class MatchSchema(BaseModel):
    """
    The master structure for a Match. 
    Nests Team and Competition schemas for full type-safety.
    """
    match_id: int = Field(alias=Match.external_id.key) # use external_id from DB as match_id
    status: str
    utc_date: datetime
    home_team: TeamSchema
    away_team: TeamSchema
    competition: CompetitionSchema
    score: ScoreSchema

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserMatchResponse(BaseModel):
    user_id: int
    match_id: int
    is_done: bool

    model_config = ConfigDict()