# main.py (project root)
import json
import os
from src.workflow import WorkflowRunner

DATA_PATH = os.path.join('data', 'sample_user_data.json')

def load_sample():
    print("Loading JSON from:", DATA_PATH)
    with open(DATA_PATH, 'r') as f:
        data = json.load(f)
        print("Loaded JSON:", data)
        return data


def pretty_print(results: dict):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(results)

if __name__ == '__main__':
    print("AI Life OS — Minimal demo")
    runner = WorkflowRunner()
    sample = load_sample()
    print("Running agent for sample user:", sample.get('user_id'))
    res = runner.run_once(sample)
    pretty_print(res)
    # show memory store content
    from src.memory import Memory
    mem = Memory()
    print("\nMemory summary for user:")
    print(json.dumps(mem.get_all(sample.get('user_id')), indent=2))
