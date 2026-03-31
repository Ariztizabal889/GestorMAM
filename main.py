import os
import html
from typing import Optional, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, Field
from supabase import create_client, Client
# Ya no necesitamos load_dotenv en producción, pero lo dejamos por si acaso

# 1. CONFIGURACIÓN (Optimizada para Render)
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    # Este print aparecerá en los Logs de Render si algo falla
    print("❌ ERROR: SUPABASE_URL o SUPABASE_KEY no configuradas en Environment")
    raise ValueError("Faltan variables de entorno")

supabase: Client = create_client(url, key)
app = FastAPI(title="Gestor de Entretenimiento API Pro")

# 2. CORS (Vital para que GitHub Pages pueda hablar con Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RUTA DE BIENVENIDA (Para evitar el "Not Found" al entrar a la URL)
@app.get("/")
async def root():
    return {"status": "online", "message": "API de GestorMAM funcionando"}

# 3. MODELOS DE DATOS
class MediaItem(BaseModel):
    user_id: str
    title: str
    media_type: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    author_or_director: Optional[str] = None
    release_year: Optional[int] = None
    total_seasons: Optional[int] = 1
    total_episodes: Any = None
    total_pages: Optional[int] = None
    status: Optional[str] = "pendiente"
    current_season: Optional[int] = 1
    current_episode: Optional[int] = 0
    current_page: Optional[int] = 0
    rating: Optional[float] = None
    is_favorite: Optional[bool] = False

    @validator('title', 'description', 'cover_image_url')
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            return html.escape(v)
        return v

class NoteItem(BaseModel):
    user_id: str
    media_id: Optional[str] = None
    title: Optional[str] = None
    content: str
    color: Optional[str] = "#ffffff"
    is_pinned: Optional[bool] = False

    @validator('title', 'content')
    def sanitize_notes(cls, v):
        if isinstance(v, str):
            return html.escape(v)
        return v

# 4. RUTAS PARA MEDIA_ITEMS (BIBLIOTECA)
@app.get("/media/usuario/{user_id}")
async def obtener_biblioteca(user_id: str):
    try:
        res = supabase.table("media_items").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
        return {"datos": res.data}
    except Exception as e:
        print(f"Error en GET media_items: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener biblioteca")

@app.post("/media/")
async def crear_contenido(item: MediaItem):
    try:
        res = supabase.table("media_items").insert(item.dict()).execute()
        return {"mensaje": "Contenido creado", "datos": res.data}
    except Exception as e:
        print(f"Error en POST media_items: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/media/{item_id}")
async def actualizar_contenido(item_id: str, item: MediaItem):
    try:
        datos = {k: v for k, v in item.dict().items() if v is not None}
        # Nota: updated_at se suele manejar en Supabase con triggers, 
        # pero esto asegura que se marque el cambio
        res = supabase.table("media_items").update(datos).eq("id", item_id).execute()
        return {"mensaje": "Actualizado", "datos": res.data}
    except Exception as e:
        print(f"Error en PUT media_items: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/media/{item_id}")
async def borrar_contenido(item_id: str):
    try:
        supabase.table("media_items").delete().eq("id", item_id).execute()
        return {"mensaje": "Eliminado"}
    except Exception as e:
        print(f"Error en DELETE media_items: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 5. RUTAS PARA NOTAS
@app.get("/notas/usuario/{user_id}")
async def obtener_notas(user_id: str):
    try:
        res = supabase.table("notes").select("*").eq("user_id", user_id).order("is_pinned", desc=True).execute()
        return {"datos": res.data}
    except Exception as e:
        print(f"Error en GET notes: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener notas")

@app.post("/notas/")
async def crear_nota(nota: NoteItem):
    try:
        res = supabase.table("notes").insert(nota.dict()).execute()
        return {"mensaje": "Nota creada", "datos": res.data}
    except Exception as e:
        print(f"Error en POST notes: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/notas/{nota_id}")
async def borrar_nota(nota_id: str):
    try:
        supabase.table("notes").delete().eq("id", nota_id).execute()
        return {"mensaje": "Nota eliminada"}
    except Exception as e:
        print(f"Error en DELETE notes: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/notas/{nota_id}")
async def actualizar_nota(nota_id: str, nota: NoteItem):
    try:
        datos_nota = {k: v for k, v in nota.dict().items() if v is not None}
        res = supabase.table("notes").update(datos_nota).eq("id", nota_id).execute()
        return {"mensaje": "Nota actualizada", "datos": res.data}
    except Exception as e:
        print(f"DEBUG ERROR PUT NOTAS: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar la nota")
