

"""
Velora Agent — Scheduling Core
Handles secure, persistent task scheduling, triggering, and audit-logged execution.
"""

import json
import threading
import time
from datetime import datetime, timedelta
from uuid import uuid4
from config.audit_logger import log_event

SCHEDULE_FILE = "velora_schedule.json"

def load_schedule():
    try:
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_schedule(data):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def schedule_task(task_name, run_time, repeat_interval=None, metadata=None):
    schedule = load_schedule()
    task_id = str(uuid4())
    schedule[task_id] = {
        "task": task_name,
        "run_time": run_time,
        "repeat_interval": repeat_interval,
        "metadata": metadata or {},
        "last_run": None
    }
    save_schedule(schedule)
    log_event("task_scheduled", {"task_id": task_id, "task": task_name, "run_time": run_time})
    return task_id

def run_task(task_id, task_details):
    now = datetime.utcnow().isoformat()
    log_event("task_executed", {
        "task_id": task_id,
        "task": task_details["task"],
        "timestamp": now,
        "metadata": task_details["metadata"]
    })

    # Placeholder for task execution logic
    # In production, map task names to callable functions securely.
    print(f"Executing task: {task_details['task']}")

    schedule = load_schedule()
    if task_id in schedule:
        schedule[task_id]["last_run"] = now
        if schedule[task_id]["repeat_interval"]:
            next_run = datetime.fromisoformat(schedule[task_id]["run_time"]) + timedelta(
                seconds=schedule[task_id]["repeat_interval"])
            schedule[task_id]["run_time"] = next_run.isoformat()
        save_schedule(schedule)

def monitor_schedule():
    while True:
        schedule = load_schedule()
        now = datetime.utcnow()

        for task_id, details in list(schedule.items()):
            run_time = datetime.fromisoformat(details["run_time"])
            if details["last_run"] is None or now >= run_time:
                run_task(task_id, details)
        time.sleep(10)

def start_scheduler():
    thread = threading.Thread(target=monitor_schedule, daemon=True)
    thread.start()
    log_event("scheduler_started", {"timestamp": datetime.utcnow().isoformat()})

if __name__ == "__main__":
    start_scheduler()