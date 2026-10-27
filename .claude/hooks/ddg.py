#!/usr/bin/env python3
"""ddg.py "query" [n]  -> title | url | snippet   (live DuckDuckGo via ddgs)"""
import sys
from ddgs import DDGS
q = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
for r in DDGS().text(q, max_results=n):
    print(f"{r['title']}\n  {r['href']}\n  {r['body'][:220]}\n")
