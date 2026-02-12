from app.db.database import get_db


class NoteRepository:
    def insert_note(self, chat_id: int, note_text: str, created_at: str) -> int:
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO notes (chat_id, note_text, created_at) VALUES (?, ?, ?)",
                (chat_id, note_text, created_at),
            )
            conn.commit()
            return int(cursor.lastrowid)
