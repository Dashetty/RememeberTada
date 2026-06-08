#!/usr/bin/env python3
"""
Run a medication reminder task from the command line.
Used by PythonAnywhere's scheduled tasks feature.

Usage:
    python run_task.py morning
    python run_task.py night
"""
import sys
import reminder


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("morning", "night"):
        print("Usage: python run_task.py <morning|night>")
        sys.exit(1)

    timing = sys.argv[1]
    result = reminder.run_reminder(timing)
    print(result["message"])


if __name__ == "__main__":
    main()
