from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List

app = FastAPI(title="Smart Meeting Scheduler API")

# Enable CORS so our frontend index.html file can talk to our backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas for API Input ---
class BusySlot(BaseModel):
    start: str  # Format: "YYYY-MM-DD HH:MM"
    end: str    # Format: "YYYY-MM-DD HH:MM"

class UserInput(BaseModel):
    name: str
    busy_slots: List[BusySlot]

class ScheduleRequest(BaseModel):
    users: List[UserInput]
    date: str          # Format: "YYYY-MM-DD"
    duration_minutes: int

# --- Scheduler Logic ---
def get_working_limits(date_str: str, start_hour=9, end_hour=17):
    day = datetime.strptime(date_str, "%Y-%m-%d")
    start = day.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end = day.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    return start, end

def get_free_slots(user: UserInput, date_str: str) -> List[tuple]:
    work_start, work_end = get_working_limits(date_str)
    
    # Parse and sort busy slots
    parsed_slots = []
    for slot in user.busy_slots:
        try:
            s_dt = datetime.strptime(slot.start, "%Y-%m-%d %H:%M")
            e_dt = datetime.strptime(slot.end, "%Y-%m-%d %H:%M")
            if s_dt.date() == work_start.date():
                parsed_slots.append((s_dt, e_dt))
        except ValueError:
            continue
            
    parsed_slots.sort()
    
    free_slots = []
    current_time = work_start

    for busy_start, busy_end in parsed_slots:
        if busy_start > current_time:
            free_slots.append((current_time, busy_start))
        current_time = max(current_time, busy_end)

    if current_time < work_end:
        free_slots.append((current_time, work_end))

    return free_slots

def intersect_slots(slots_a, slots_b):
    intersection = []
    i, j = 0, 0
    while i < len(slots_a) and j < len(slots_b):
        start_a, end_a = slots_a[i]
        start_b, end_b = slots_b[j]

        overlap_start = max(start_a, start_b)
        overlap_end = min(end_a, end_b)

        if overlap_start < overlap_end:
            intersection.append((overlap_start, overlap_end))

        if end_a < end_b:
            i += 1
        else:
            j += 1
    return intersection

# --- API Endpoint ---
@post_route := app.post("/api/schedule")
def schedule_meeting(payload: ScheduleRequest):
    if not payload.users:
        return {"options": []}

    # Start with the first user's free slots
    common_free = get_free_slots(payload.users[0], payload.date)

    # Successively intersect with other users
    for user in payload.users[1:]:
        user_free = get_free_slots(user, payload.date)
        common_free = intersect_slots(common_free, user_free)

    # Filter by duration
    duration = timedelta(minutes=payload.duration_minutes)
    valid_slots = []
    for start, end in common_free:
        if (end - start) >= duration:
            valid_slots.append({
                "start": start.strftime("%I:%M %p"),
                "end": end.strftime("%I:%M %p")
            })

    return {"options": valid_slots}