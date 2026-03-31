from pydantic import BaseModel
from typing import Optional
from datetime import timedelta

class MediaItem(BaseModel):
    user_id: str
    title: str
    media_type: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    author_or_director: Optional[str] = None
    release_year: Optional[int] = None
    total_seasons: Optional[int] = 1
    total_episodes: Optional[int] = None
    total_pages: Optional[int] = None
    status: Optional[str] = 'pendiente'
    current_season: Optional[int] = 1
    current_episode: Optional[int] = 0
    current_page: Optional[int] = 0
    movie_progress: Optional[str] = None # Formato "HH:MM:SS"
    rating: Optional[float] = None
    is_favorite: Optional[bool] = False

class Note(BaseModel):
    user_id: str
    media_id: Optional[str] = None # Puede ir ligada a una serie o estar suelta
    title: Optional[str] = None
    content: str
    color: Optional[str] = "#ffffff"
    is_pinned: Optional[bool] = False