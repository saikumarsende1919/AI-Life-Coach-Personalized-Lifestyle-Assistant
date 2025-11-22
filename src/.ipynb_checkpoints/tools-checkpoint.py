# src/tools.py
from typing import Dict, List

class EmailTool:
    """Very small email stub for demo. Collects sent messages in-memory."""
    def __init__(self):
        self.sent = []

    def send(self, to_email: str, subject: str, body: str) -> Dict:
        rec = {"to": to_email, "subject": subject, "body": body}
        self.sent.append(rec)
        # return status for orchestrator
        return {"status": "ok", "record": rec}

class CalendarTool:
    """Calendar stub: stores created events in-memory."""
    def __init__(self):
        self.events = []

    def create_event(self, user_id: str, title: str, start_time: str, duration_min: int = 30) -> Dict:
        ev = {"user": user_id, "title": title, "start": start_time, "duration": duration_min}
        self.events.append(ev)
        return {"status": "ok", "event": ev}

def summarize_plan(plan_items: List[str]) -> str:
    """Small helper to render human-friendly plan text."""
    return " • ".join(plan_items)
