"""In-memory storage for todo items."""

from datetime import datetime
from typing import Iterator

from app.models import TodoItem, TodoCreate, TodoUpdate


class TodoStorage:
    """In-memory storage for todo items."""

    def __init__(self) -> None:
        """Initialize an empty storage."""
        self._todos: dict[str, TodoItem] = {}

    def create(self, data: TodoCreate) -> TodoItem:
        """Create a new todo item."""
        todo = TodoItem(**data.model_dump())
        self._todos[todo.id] = todo
        return todo

    def get(self, todo_id: str) -> TodoItem | None:
        """Get a todo item by ID."""
        return self._todos.get(todo_id)

    def list_all(self) -> list[TodoItem]:
        """List all todo items."""
        return list(self._todos.values())

    def update(self, todo_id: str, data: TodoUpdate) -> TodoItem | None:
        """Update a todo item."""
        todo = self._todos.get(todo_id)
        if todo is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        updated_todo = todo.model_copy(update=update_data)
        self._todos[todo_id] = updated_todo
        return updated_todo

    def delete(self, todo_id: str) -> bool:
        """Delete a todo item."""
        return self._todos.pop(todo_id, None) is not None

    def toggle_completed(self, todo_id: str) -> TodoItem | None:
        """Toggle the completed status of a todo item."""
        todo = self._todos.get(todo_id)
        if todo is None:
            return None

        updated_todo = todo.model_copy(
            update={"completed": not todo.completed, "updated_at": datetime.utcnow()}
        )
        self._todos[todo_id] = updated_todo
        return updated_todo

    def clear_all(self) -> int:
        """Clear all todo items. Returns the number of items cleared."""
        count = len(self._todos)
        self._todos.clear()
        return count

    def __iter__(self) -> Iterator[TodoItem]:
        """Iterate over all todo items."""
        return iter(self._todos.values())

    def __len__(self) -> int:
        """Return the number of todo items."""
        return len(self._todos)
