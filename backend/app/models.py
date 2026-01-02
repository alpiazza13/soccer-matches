from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, unique=True, index=True) # ID from the Football API
    name = Column(String, nullable=False)
    short_name = Column(String)
    tla = Column(String(3)) # The 3-letter code (e.g., ARS)

    # Relationship: A team can play in many matches as home or away
    matches_as_home = relationship("Match", foreign_keys="[Match.home_team_id]", back_populates="home_team")
    matches_as_away = relationship("Match", foreign_keys="[Match.away_team_id]", back_populates="away_team")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, unique=True, index=True)
    utc_date = Column(DateTime, nullable=False)
    status = Column(String) # e.g., FINISHED, TIMED, SCHEDULED
    
    # Foreign Keys
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    competition_id = Column(Integer, ForeignKey("competitions.id"))
    user_matches = relationship("UserMatch", back_populates="match")
    
    # Scores stored as JSON for flexibility
    score = Column(JSON) # e.g., {"fullTime": {"home": 2, "away": 1}}
    
    competition = relationship("Competition", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="matches_as_home")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="matches_as_away")

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class Competition(Base):
    __tablename__ = "competitions"
    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True)
    name = Column(String)
    code = Column(String)

    matches = relationship("Match", back_populates="competition")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # This allows us to say `user.user_matches` to see their tracked games
    user_matches = relationship("UserMatch", back_populates="user")

class UserMatch(Base):
    """
    The 'Join' table that tracks if a specific user has finished a specific match.
    """
    __tablename__ = "user_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    is_done = Column(Boolean, default=False)
    notes = Column(String, nullable=True) # Optional: for future 'take notes' feature
    last_updated = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    user = relationship("User", back_populates="user_matches")
    match = relationship("Match", back_populates="user_matches")