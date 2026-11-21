from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    order: int


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    category_id: int
    category_name: Optional[str] = None
    difficulty_level: str
    difficulty_score: int
    target_muscles: List[str] = []
    video_url: Optional[str] = None


class SkillDetailOut(SkillOut):
    description: Optional[str] = None
    technique_instructions: Optional[str] = None
    common_mistakes: Optional[str] = None
    prerequisites: List[str] = []
    progresses_to: List[str] = []


class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    target_muscles: List[str] = []
    related_skill_id: Optional[int] = None


class WorkoutExerciseOut(BaseModel):
    id: int
    exercise_id: int
    exercise_name: str
    section: str
    sets: int
    reps: str
    rest_seconds: int
    video_url: Optional[str] = None


class WorkoutOut(BaseModel):
    id: int
    title: str
    estimated_duration_minutes: int
    order_in_program: int
    exercises: List[WorkoutExerciseOut] = []


class ProgramOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    experience_level: str
    duration_weeks: int
    days_per_week: int
    workouts: List[WorkoutOut] = []


class RankOut(BaseModel):
    id: int
    name: str
    order: int
    badge_color: str
    min_xp: int


class LeaderboardEntryOut(BaseModel):
    username: str
    rank_name: str
    badge_color: str
    xp: int
    verified_skills: int


class CommunityPostOut(BaseModel):
    id: int
    username: str
    content: str
    post_type: str
    created_at: datetime
    likes_count: int = 0


class WorkoutLogCreate(BaseModel):
    workout_id: int
    duration_minutes: Optional[int] = 30
    notes: Optional[str] = ""


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
