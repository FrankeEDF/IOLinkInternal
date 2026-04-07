#!/usr/bin/env python3
"""
Fetch all GitHub issues from FrankeEDF/IOLink and save each as a markdown file
in a subdirectory named _<issue_number>.
"""

import os
import subprocess
import json
import re
import sys


REPO = "FrankeEDF/IOLink"
OUTPUT_BASE = os.path.dirname(os.path.abspath(__file__))


def safe_filename(text: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", text)


def fetch_issues() -> list:
    """Fetch all issues (open + closed) using gh CLI."""
    result = subprocess.run(
        [
            "gh", "issue", "list",
            "--repo", REPO,
            "--state", "all",
            "--limit", "1000",
            "--json", "number,title,author,createdAt,state,body,comments,labels,closedAt",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"Error fetching issues:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def format_issue(issue: dict) -> str:
    lines = []

    title = issue.get("title", "")
    lines.append(f"# {title}")
    lines.append("")

    author = issue.get("author", {}).get("login", "unknown")
    created = issue.get("createdAt", "")
    state = issue.get("state", "").upper()
    labels = [lbl.get("name", "") for lbl in issue.get("labels", [])]

    lines.append(f"- Author: {author}")
    lines.append(f"- Created: {created}")
    lines.append(f"- State: {state}")
    if labels:
        lines.append(f"- Labels: {', '.join(labels)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    body = issue.get("body") or ""
    body = body.replace("\r\n", "\n").strip()
    if body:
        lines.append(body)
        lines.append("")

    comments = issue.get("comments", [])
    if comments:
        lines.append("## Comments")
        lines.append("")
        for comment in comments:
            c_author = comment.get("author", {}).get("login", "unknown")
            c_created = comment.get("createdAt", "")
            lines.append(f"### {c_author} ({c_created})")
            lines.append("")
            c_body = comment.get("body") or ""
            c_body = c_body.replace("\r\n", "\n").strip()
            lines.append(c_body)
            lines.append("")

    return "\n".join(lines)


def main():
    print(f"Fetching issues from {REPO} ...")
    issues = fetch_issues()
    print(f"Found {len(issues)} issues.")

    for issue in issues:
        number = issue["number"]
        title = issue.get("title", f"issue_{number}")

        dir_name = f"_{number}"
        dir_path = os.path.join(OUTPUT_BASE, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        filename = f"{safe_filename(title)}.md"
        file_path = os.path.join(dir_path, filename)

        content = format_issue(issue)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  [{number}] {title} -> {os.path.relpath(file_path)}")

    print(f"\nDone. Issues saved to: {OUTPUT_BASE}")


if __name__ == "__main__":
    main()
