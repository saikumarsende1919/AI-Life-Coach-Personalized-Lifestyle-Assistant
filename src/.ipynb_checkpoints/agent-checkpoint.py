# src/agent.py
from typing import Dict
from src.memory import Memory
from src.tools import EmailTool, CalendarTool, summarize_plan

class Agent:
    """
    Minimal multi-capability agent that coordinates simple sub-policies:
    - health advice
    - finance check
    - learning coach
    - productivity scheduling
    Saves interventions to Memory and uses stub tools for actions.
    """
    def __init__(self, memory: Memory):
        self.memory = memory
        self.email = EmailTool()
        self.calendar = CalendarTool()

    # ------------------------------------------------------------
    # HEALTH POLICY
    # ------------------------------------------------------------
    def health_policy(self, user_id: str, snapshot: Dict) -> Dict:
        steps = snapshot.get('steps_last_7_days', 0)
        sleep = snapshot.get('sleep_hours_avg', 7)

        plan = []
        risk = 'low'

        if steps < 2000 or sleep < 5.5:
            risk = 'high'
            plan = [
                'Walk 20 minutes daily',
                'Follow a sleep-winddown routine',
                'Track sleep for 2 weeks'
            ]
        elif steps < 5000 or sleep < 6.5:
            risk = 'medium'
            plan = ['Increase steps by 20%', 'Keep regular bedtime']
        else:
            plan = ['Maintain current routine']

        return {
            "domain": "health",
            "risk": risk,
            "plan": plan,
            "message": f"Health plan: {summarize_plan(plan)}"
        }

    # ------------------------------------------------------------
    # FINANCE POLICY (FIXED)
    # ------------------------------------------------------------
    def finance_policy(self, user_id, finance_data):
        expenses = finance_data.get('monthly_expenses', 0)
        subs = finance_data.get('subscriptions', [])

        # FIX: allow integer monthly_expenses
        if isinstance(expenses, (int, float)):
            expenses = [expenses]

        total = sum(expenses) if expenses else 0

        alert = None
        if total > 40000:
            alert = "High spending detected"

        plan = ["No urgent action", "Review subscriptions monthly"]

        return {
            "domain": "finance",
            "total": total,
            "alert": alert,
            "plan": plan,
            "message": f"Finance plan: {plan[0]} • {plan[1]}"
        }

    # ------------------------------------------------------------
    # LEARNING POLICY
    # ------------------------------------------------------------
    def learning_policy(self, user_id: str, snapshot: Dict) -> Dict:
        scores = snapshot.get('quiz_scores', [])
        avg = sum(scores) / len(scores) if scores else 0
        last_active = snapshot.get('last_active_days', 999)

        risk = 'low'
        plan = []

        if avg < 40 or last_active > 7:
            risk = 'high'
            plan = ['Daily 15-min micro-lesson', 'Practice quiz every 3 days']
        elif avg < 60 or last_active > 3:
            risk = 'medium'
            plan = ['3 micro-lessons per week', 'Weekly practice quiz']
        else:
            plan = ['Keep current pace']

        return {
            "domain": "learning",
            "risk": risk,
            "plan": plan,
            "message": f"Learning plan: {summarize_plan(plan)}"
        }

    # ------------------------------------------------------------
    # PRODUCTIVITY POLICY (FULLY FIXED)
    # ------------------------------------------------------------
    def productivity_policy(self, user_id: str, snapshot: Dict) -> Dict:
        tasks = snapshot.get('tasks', [])

        # FIX: Convert string tasks → dict tasks
        normalized_tasks = []
        for t in tasks:
            if isinstance(t, str):
                normalized_tasks.append({
                    "title": t,
                    "priority": 5,
                    "start_time": "TBD"
                })
            else:
                normalized_tasks.append(t)

        tasks = normalized_tasks

        if not tasks:
            return {
                "domain": "productivity",
                "scheduled": None,
                "message": "No tasks to schedule"
            }

        # choose highest-priority
        top = sorted(tasks, key=lambda t: t.get('priority', 5))[0]

        ev = self.calendar.create_event(
            user_id,
            top.get('title', 'Task'),
            top.get('start_time', 'TBD')
        )

        return {
            "domain": "productivity",
            "scheduled": ev,
            "message": f"Scheduled: {top.get('title')}"
        }

    # ------------------------------------------------------------
    # MAIN ORCHESTRATOR
    # ------------------------------------------------------------
    def run(self, user_snapshot: Dict) -> Dict:
        user_id = user_snapshot.get('user_id', 'anonymous')
        meta = user_snapshot.get('meta', {})
        responses = {}

        # Health
        h = self.health_policy(user_id, user_snapshot.get('health', {}))
        self.memory.save_event(user_id, 'health', h)
        responses['health'] = h

        # Finance
        f = self.finance_policy(user_id, user_snapshot.get('finance', {}))
        self.memory.save_event(user_id, 'finance', f)
        responses['finance'] = f

        # Learning
        l = self.learning_policy(user_id, user_snapshot.get('learning', {}))
        self.memory.save_event(user_id, 'learning', l)
        responses['learning'] = l

        # Productivity
        p = self.productivity_policy(user_id, user_snapshot.get('productivity', {}))
        self.memory.save_event(user_id, 'productivity', p)
        responses['productivity'] = p

        # Send email only for high-risk
        critical = []
        if h.get('risk') == 'high':
            critical.append('health')
        if l.get('risk') == 'high':
            critical.append('learning')

        if critical:
            subj = "AI Life OS — Recommended Actions"
            body_lines = [
                f"- {d.title()}: {responses[d]['message']}" for d in critical
            ]
            body = f"Hi {meta.get('name','User')},\n\nI detected issues in: {', '.join(critical)}.\n\nRecommendations:\n" + "\n".join(body_lines)

            email_to = meta.get('email', 'user@example.com')
            self.email.send(email_to, subj, body)

            self.memory.save_event(user_id, 'email_sent',
                                   {"to": email_to, "subject": subj})

        # Save combined summary
        self.memory.save_event(user_id, 'daily_summary', responses)
        return responses
