# Smart Meeting Scheduler

A small web app that finds overlapping free time for meeting participants. The FastAPI backend checks availability during a 9:00 AM to 5:00 PM workday, and the browser interface displays the matching windows.

## Requirements

- Python 3.8 or later
- An internet connection to load Tailwind CSS from its CDN

## Run Locally

Install the backend dependencies and start the API:

```powershell
py -m pip install fastapi uvicorn
py -m uvicorn main:app --reload
```

Open `index.html` in a browser. The page sends requests to `http://127.0.0.1:8000`. Interactive API documentation is available at <http://127.0.0.1:8000/docs>.

## API

`POST /api/schedule` accepts a date, meeting duration in minutes, and participants with their busy periods. Times use the `YYYY-MM-DD HH:MM` format.

```json
{
  "users": [
    {
      "name": "Alice",
      "busy_slots": [
        { "start": "2026-10-01 10:00", "end": "2026-10-01 11:30" }
      ]
    },
    {
      "name": "Bob",
      "busy_slots": [
        { "start": "2026-10-01 11:00", "end": "2026-10-01 12:00" }
      ]
    }
  ],
  "date": "2026-10-01",
  "duration_minutes": 45
}
```

The response contains common free-time windows that are at least the requested duration:

```json
{
  "options": [
    { "start": "09:00 AM", "end": "10:00 AM" },
    { "start": "12:00 PM", "end": "05:00 PM" }
  ]
}

```