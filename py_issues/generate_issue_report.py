#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, timezone

REPO = sys.argv[1] if len(sys.argv) > 1 else "OWNER/REPO"
SINCE = sys.argv[2] if len(sys.argv) > 2 else "2026-01-01"  # YYYY-MM-DD
OUT_CSV = sys.argv[3] if len(sys.argv) > 3 else "closed_issues.csv"

# GraphQL: closed issues since date, with labels, stateReason, and closing PRs (if any)
QUERY = r"""
query($owner:String!, $name:String!, $cursor:String, $since:DateTime!) {
  repository(owner:$owner, name:$name) {
    issues(first:100, after:$cursor, states:CLOSED, orderBy:{field:UPDATED_AT, direction:DESC}, filterBy:{since:$since}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number
        title
        url
        createdAt
        closedAt
        stateReason
        labels(first:50) { nodes { name } }
        closingIssuesReferences(first:10) {
          nodes {
            __typename
            ... on PullRequest { number url mergedAt state title }
          }
        }
      }
    }
  }
}
"""

def gh_graphql(query: str, variables: dict) -> dict:
    # Use: gh api graphql -f query='...' -f variables='...'
    cmd = [
        "gh", "api", "graphql",
        "-f", f"query={query}",
        "-f", f"variables={json.dumps(variables)}",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or res.stdout.strip())
    return json.loads(res.stdout)

def classify(issue: dict) -> str:
    labels = [n["name"] for n in (issue.get("labels", {}).get("nodes") or [])]
    state_reason = issue.get("stateReason")  # e.g. COMPLETED, NOT_PLANNED, REOPENED (varies)
    closing_prs = issue.get("closingIssuesReferences", {}).get("nodes") or []

    # 1) Explicit not planned (if repo uses it)
    if state_reason == "NOT_PLANNED":
        return "not_planned"

    # 2) Resolution labels (if you use them)
    if any(l.lower().startswith("resolution:") for l in labels):
        # you can return the exact resolution label if you want:
        # return next(l for l in labels if l.lower().startswith("resolution:"))
        return "has_resolution_label"

    # 3) Closed via PR linkage
    if len(closing_prs) > 0:
        return "fixed_via_pr"

    return "manual_or_unknown"

def iso_to_dt(s: str):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None

def main():
    if "/" not in REPO:
        print("Usage: export_closed_issues.py OWNER/REPO [SINCE=YYYY-MM-DD] [OUT=closed_issues.csv]")
        sys.exit(2)

    owner, name = REPO.split("/", 1)
    since_dt = datetime.fromisoformat(SINCE).replace(tzinfo=timezone.utc)

    rows = []
    cursor = None
    total = 0

    while True:
        data = gh_graphql(QUERY, {
            "owner": owner,
            "name": name,
            "cursor": cursor,
            "since": since_dt.isoformat(),
        })
        issues = data["data"]["repository"]["issues"]["nodes"]
        page = data["data"]["repository"]["issues"]["pageInfo"]

        for it in issues:
            total += 1
            labels = [n["name"] for n in (it.get("labels", {}).get("nodes") or [])]
            closing_prs = it.get("closingIssuesReferences", {}).get("nodes") or []

            created = iso_to_dt(it.get("createdAt"))
            closed = iso_to_dt(it.get("closedAt"))
            days_to_close = ""
            if created and closed:
                days_to_close = f"{(closed - created).total_seconds() / 86400.0:.2f}"

            resolution = classify(it)

            rows.append({
                "number": it["number"],
                "title": it["title"].replace("\n", " ").strip(),
                "url": it["url"],
                "createdAt": it.get("createdAt", ""),
                "closedAt": it.get("closedAt", ""),
                "daysToClose": days_to_close,
                "stateReason": it.get("stateReason") or "",
                "labels": "|".join(labels),
                "closingPRs": "|".join(str(pr.get("number")) for pr in closing_prs if pr),
                "resolution": resolution,
            })

        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]

    # write CSV
    import csv
    fields = ["number","title","url","createdAt","closedAt","daysToClose","stateReason","labels","closingPRs","resolution"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    # quick summary to stdout
    from collections import Counter
    c = Counter(r["resolution"] for r in rows)
    print(f"Repo: {REPO}")
    print(f"Closed issues since {SINCE}: {len(rows)}")
    for k, v in c.most_common():
        print(f"  {k:18s} {v}")

    print(f"\nWrote: {OUT_CSV}")

if __name__ == "__main__":
    main()
