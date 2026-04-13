"""FastAPI application for the todo system."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.models import TodoCreate, TodoItem, TodoUpdate
from app.storage import TodoStorage

# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="A simple todo application with in-memory storage",
    version="0.1.0",
)

# Initialize storage
storage = TodoStorage()

# Get the static directory path
static_dir = Path(__file__).parent.parent / "static"

# Mount static files directory for CSS and JS
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root() -> FileResponse:
    """Serve the frontend HTML page."""
    index_path = static_dir / "index.html"
    return FileResponse(index_path)


@app.get("/api/todos", response_model=list[TodoItem])
async def list_todos() -> list[TodoItem]:
    """List all todo items."""
    return storage.list_all()


@app.get("/api/todos/{todo_id}", response_model=TodoItem)
async def get_todo(todo_id: str) -> TodoItem:
    """Get a specific todo item by ID."""
    todo = storage.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/api/todos", response_model=TodoItem, status_code=201)
async def create_todo(data: TodoCreate) -> TodoItem:
    """Create a new todo item."""
    return storage.create(data)


@app.put("/api/todos/{todo_id}", response_model=TodoItem)
async def update_todo(todo_id: str, data: TodoUpdate) -> TodoItem:
    """Update a todo item."""
    updated_todo = storage.update(todo_id, data)
    if updated_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo


@app.delete("/api/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: str) -> None:
    """Delete a todo item."""
    if not storage.delete(todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")


@app.patch("/api/todos/{todo_id}/toggle", response_model=TodoItem)
async def toggle_todo(todo_id: str) -> TodoItem:
    """Toggle the completed status of a todo item."""
    updated_todo = storage.toggle_completed(todo_id)
    if updated_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo


@app.delete("/api/todos", status_code=204)
async def clear_all_todos() -> None:
    """Delete all todo items."""
    storage.clear_all()


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "todo_count": str(len(storage))}
