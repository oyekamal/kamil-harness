#!/usr/bin/env python3
"""SkillsMP search helper — find community AI skills for hard/unknown tasks.

Usage:
    python3 skillsmp_search.py "automate browser form filling"
    python3 skillsmp_search.py "data extraction" --limit 5
    python3 skillsmp_search.py "SEO analysis" --occupation software-developers
"""
import json
import os
import sys
import urllib.request
import urllib.parse

API_BASE = "https://skillsmp.com/api/v1/skills/search"
API_KEY = os.environ.get("SKILLSMP_API_KEY", "")


def search(query: str, limit: int = 3, occupation: str = "", category: str = "") -> dict:
    params = {"q": query, "limit": limit, "sortBy": "stars"}
    if occupation:
        params["occupation"] = occupation
    if category:
        params["category"] = category

    url = f"{API_BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"success": False, "error": {"code": e.code, "message": e.reason}}
    except Exception as e:
        return {"success": False, "error": {"code": "NETWORK_ERROR", "message": str(e)}}


def format_results(data: dict) -> str:
    if not data.get("success"):
        err = data.get("error", {})
        return f"SkillsMP error {err.get('code')}: {err.get('message')}"

    skills = data.get("data", {}).get("skills", []) or data.get("skills", [])
    if not skills:
        return "No skills found."

    lines = []
    for s in skills:
        name = s.get("name", "?")
        author = s.get("author", "")
        stars = s.get("stars", 0)
        desc = (s.get("description") or "")[:120]
        skill_url = s.get("skillUrl", "")
        github_url = s.get("githubUrl", "")
        lines.append(f"★{stars}  {author}/{name} — {desc}")
        lines.append(f"     page: {skill_url}")
        lines.append(f"     code: {github_url}")
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--occupation", default="")
    parser.add_argument("--category", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not API_KEY:
        print("SKILLSMP_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    result = search(args.query, args.limit, args.occupation, args.category)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_results(result))
