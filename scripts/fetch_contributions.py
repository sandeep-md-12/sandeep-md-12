"""Fetch the public contribution calendar and write data/contributions.json.

Uses GitHub's public HTML endpoint (no token needed):
    https://github.com/users/<username>/contributions
"""
import datetime as dt
import json
import os
import re
import sys
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "sandeep-md-12")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "contributions.json")


def fetch_days(username):
    url = f"https://github.com/users/{username}/contributions"
    r = requests.get(url, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Counts live in <tool-tip for="<cell id>">N contributions on ...</tool-tip>
    tips = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"\s*(\d+|No) contribution", tip.get_text())
        if tip.get("for") and m:
            tips[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1))

    days = {}
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        date = cell["data-date"]
        count = tips.get(cell.get("id"))
        if count is None:  # fall back to the intensity level if tooltip is missing
            count = int(cell.get("data-level", 0))
        days[date] = count
    if not days:
        sys.exit("No contribution cells found - GitHub markup may have changed.")
    return OrderedDict(sorted(days.items()))


def summarize(days):
    dates = list(days)
    counts = list(days.values())
    today = dt.date.fromisoformat(dates[-1])

    # current streak (today is allowed to be 0 without breaking it)
    cur, i = 0, len(counts) - 1
    if counts[i] == 0:
        i -= 1
    while i >= 0 and counts[i] > 0:
        cur += 1
        i -= 1

    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)

    best_date = max(days, key=days.get)
    monthly = OrderedDict()
    for d, c in days.items():
        monthly[d[:7]] = monthly.get(d[:7], 0) + c

    return {
        "username": USERNAME,
        "generated": today.isoformat(),
        "total": sum(counts),
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": {"date": best_date, "count": days[best_date]},
        "monthly": monthly,
        "days": days,
    }


def main():
    data = summarize(fetch_days(USERNAME))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=1)
    print(f"{data['total']} contributions, streak {data['current_streak']}, "
          f"longest {data['longest_streak']} -> {OUT}")


if __name__ == "__main__":
    main()
