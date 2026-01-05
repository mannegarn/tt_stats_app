from datetime import datetime
from pathlib import Path
import json

from src.config import (
    RAW_EVENTS_DIR,
)
from src.utils.helper_logic import (
    get_event_count_from_file,
    get_event_date_status,
    is_senior_event,
)


def get_raw_events_summary(raw_events_dir: Path) -> str:
    """
    Get a summary of the raw events data stored in the given directory.

    Args:
        raw_events_dir (Path): The directory containing the raw events data.

    Returns:
        events_markdown: A summary of the raw events data.
    """

    events_markdown = "# Raw Events Data Summary\n\n"

    events_files = sorted(raw_events_dir.glob("events_*.json"))

    total_events = 0
    excluded_events = 0
    senior_events = 0
    total_ongoing = 0
    total_completed = 0
    total_future = 0

    for event_file in events_files:
        year = int(event_file.stem.split("_")[1])
        event_count = get_event_count_from_file(raw_events_dir, event_file.name)
        total_events += event_count
        events_markdown += f"- {year}: {event_count} events\n"

        with open(event_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            continue

        events_list = data[0].get("rows", [])

        for event in events_list:
            event_name = event.get("EventName")
            if not event_name or not is_senior_event(event_name):
                excluded_events += 1
                continue
            senior_events += 1

            event_status = get_event_date_status(event)
            if event_status == "future":
                total_future += 1
            elif event_status == "ongoing":
                total_ongoing += 1
            elif event_status == "completed":
                total_completed += 1

    events_markdown += "\n### 📈 Senior vs Excluded Breakdown\n"
    events_markdown += "| Category | Count | Percentage |\n"
    events_markdown += "| :--- | :--- | :--- |\n"
    events_markdown += f"| **Total Raw Events** | {total_events} | 100% |\n"
    events_markdown += f"| **Excluded (Youth/Para)** | {excluded_events} | {(excluded_events/total_events)*100:.1f}% |\n"
    events_markdown += f"| **Senior Events** | {senior_events} | {(senior_events/total_events)*100:.1f}% |\n"

    events_markdown += "\n### 📅 Senior Event Status\n"
    events_markdown += "| Status | Count |\n"
    events_markdown += "| :--- | :--- |\n"
    events_markdown += f"| ✅ Completed | {total_completed} |\n"
    events_markdown += f"| 📡 Ongoing | {total_ongoing} |\n"
    events_markdown += f"| ⏳ Future | {total_future} |\n"
    events_markdown += f"| Total | {senior_events} |\n"

    return events_markdown


if __name__ == "__main__":

    generated_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw_data_report = [
        "# 🗃️ tt_stats_app Raw Data Report",
        f"*Generated on: {generated_on}*",
        "\n---",
    ]

    raw_data_report.append(get_raw_events_summary(RAW_EVENTS_DIR))

    report_path = Path("data/RAW_DATA_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(raw_data_report))

    print(f"✅ Report updated at {report_path} on {generated_on}")
