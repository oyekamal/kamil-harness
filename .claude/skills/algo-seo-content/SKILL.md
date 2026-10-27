---
name: "algo-seo-content"
description: "Execute content SEO strategy from keyword research through content planning, writing, and on-page optimization. Use this skill when the user needs to create SEO-optimized content, perform keyword research, identify content gaps, or improve existing content rankings — even if they say 'content strategy', 'keyword research', or 'how to rank for this topic'."
metadata:
  category: "SEO Content Strategy"
  tags: ["seo", "content-strategy", "keyword-research", "on-page-seo"]
---

# Content SEO Strategy

## Overview

Content SEO is the systematic process of creating and optimizing content to match search intent and rank organically. The pipeline: keyword research → intent mapping → content creation → on-page optimization → performance monitoring. Success depends on intent match, not keyword density.

## When to Use

**Trigger conditions:**
- Planning new content to capture organic search traffic
- Optimizing existing underperforming content
- Conducting keyword research and content gap analysis

**When NOT to use:**
- When the issue is technical (page speed, crawlability) — use technical SEO
- When the issue is off-page (backlinks, authority) — use backlink analysis

## The Iron Law

```
CONTENT MUST MATCH SEARCH INTENT
A perfectly optimized page targeting the wrong intent will NOT rank.
Four intent types:
1. Informational — wants to learn ("how to", "what is")
2. Navigational — wants a specific site ("github login")
3. Commercial — comparing options ("best CRM 2025")
4. Transactional — wants to buy/do ("buy iPhone 16 case")
Check SERP results to determine actual intent before writing.
```

## Algorithm

### Phase 1: Keyword Research
- Gather seed keywords from brainstorming, competitor analysis, and tools (Ahrefs, SEMrush, Google Keyword Planner)
- Group related keywords by intent and topic (keyword clustering)

### Phase 2: SERP Analysis
- Check top 10 results for each cluster — identify intent, content format (guide/list/comparison), and depth
- Find keywords competitors rank for that you don't (content gap analysis)

### Phase 3: Content Brief
Define before writing:
- Target keyword (primary)
- Search intent (informational/commercial/transactional/navigational)
- Content format (how-to guide / comparison / list / pillar page)
- Target word count benchmark (from SERP analysis)
- Required subtopics (from SERP — what the top 3 results all cover)

### Phase 4: On-Page Optimization
- Title tag: keyword front-loaded, under 60 chars
- Meta description: includes keyword, benefit-focused, under 155 chars
- H1: matches intent, contains primary keyword
- H2/H3 structure: cover all key subtopics
- Internal links: 3-5 links to related content
- Image alt text: descriptive, keyword where natural

### Phase 5: Verification
- Does title contain primary keyword?
- Does intent match SERP?
- Are all key subtopics covered?
- Are there internal links to related content?

## Output Format

```json
{
  "content_brief": {
    "primary_keyword": "...",
    "intent": "informational",
    "format": "how-to guide",
    "target_word_count": 2000,
    "subtopics": ["...", "..."]
  },
  "optimization": {
    "title": "...",
    "meta_description": "...",
    "h2_structure": ["...", "..."],
    "internal_links": 5
  },
  "metadata": {
    "search_volume": 2400,
    "keyword_difficulty": 35
  }
}
```

## Key Gotchas

- **Keyword density is dead**: Write naturally. Forced keyword insertion hurts readability.
- **Search volume ≠ traffic**: A #1 ranking for a 10K volume keyword won't bring 10K visits. CTR varies.
- **Content freshness**: Some queries demand fresh content (e.g., "best laptop 2025"). Outdated content drops.
- **Cannibalization**: Multiple pages targeting the same keyword compete with each other.
- **E-E-A-T**: For YMYL topics (health, finance), Google requires Experience, Expertise, Authority, Trust.

| Edge Case | Guidance |
|-----------|----------|
| Zero search volume keyword | May be worth targeting if topically relevant (emerging topic) |
| KD > 80 for new site | Target long-tail variants first |
| Mixed intent SERP | Create content matching dominant intent |
