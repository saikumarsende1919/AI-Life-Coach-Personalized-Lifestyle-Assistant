# src/workflow.py
from typing import Dict
from src.agent import Agent
from src.memory import Memory
import time

class WorkflowRunner:
    """
    Minimal loop agent / workflow orchestrator.
    For demo: runs the agent for a user snapshot and returns the result.
    In a real hackathon you can expand to scheduled loops or A/B simulation.
    """
    def __init__(self):
        self.memory = Memory()
        self.agent = Agent(self.memory)

    def run_once(self, snapshot: Dict) -> Dict:
        # run orchestrator and return results
        return self.agent.run(snapshot)

    def run_batch(self, snapshots: list):
        results = {}
        for s in snapshots:
            uid = s.get('user_id', 'unknown')
            results[uid] = self.run_once(s)
            # small delay to simulate scheduling / traces
            time.sleep(0.05)
        return results
