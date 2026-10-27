# Rung 2: diagrams that a reader can check

A diagram makes structure visible: flows, parts, states, cause and effect, order of events.
It also *looks* authoritative even when it is wrong. So every diagram in this skill ships with
three things: real labels, numbered arrows, and a list of its own weak spots.

## Pick the form

| The content is... | Draw | Tool |
|---|---|---|
| A process in order (A causes B, then C) | flowchart, numbered arrows | SVG (template) or Mermaid `flowchart LR` |
| Messages between actors over time | sequence diagram | Mermaid `sequenceDiagram` (autonumber) |
| A physical setup (cell, circuit, apparatus) | labelled schematic | hand-written SVG |
| States and transitions | state diagram | Mermaid `stateDiagram-v2` |
| How one quantity changes another | a plot with the direction marked | SVG or the rung-3 canvas |
| A hierarchy / parts of a whole | tree or nested boxes | Mermaid `flowchart TB` |
| A nuanced trade-off, "it depends" | NO diagram; use text or a table | rung 1 |

## Rules

1. **Every box carries its real name** ("Zn anode", "salt bridge"), never "Component A".
2. **Every arrow is numbered** in the order events happen, and its label says *what* moves
   ("2. e⁻ through wire"), not "flows".
3. **Arrow direction is a claim.** Check each one against the source (e.g. electron flow vs
   conventional current, which way ions move). Write the source next to the diagram.
4. **One colour = one meaning**, reused in every rung (e.g. yellow = the quantity you solve for).
   Never encode meaning in colour alone; also label it.
5. **≤ 9 boxes.** If you need more, split into two diagrams.
6. **Mark what you are unsure of.** Dashed stroke + class `uncertain` + `data-why`.
7. **After the diagram, list its 3 weakest points**, in this form:
   ```
   Weak spots in this diagram:
   1. <label/arrow> — <why it may be wrong or simplified> — <how to check it>
   ```
   Honest examples: "arrow 3 shows net ion flow; real ions move both ways", "the box sizes are
   not to scale", "label 'E°' assumes 25 °C". Do not list fake weaknesses to fill the slots.
8. Text ≥ 13 px, high contrast, a `<title>` and `<desc>` (the alt text).

## SVG: start from the template

`references/diagram-template.svg` already follows the conventions. Copy it, rename nodes, move
boxes. Then check and LOOK:

```bash
python3 scripts/diagram_check.py my.svg --png my.png     # lint + render via cairosvg
# then open my.png with the Read tool. Check: overlaps, cut-off labels, arrow heads, reading order.
```

## Mermaid

Number edges in the label: `A[Zn anode] -->|1. e⁻ leave Zn| B[External wire]`.
For sequences, add `autonumber`. Do not use `click` or HTML labels.

```bash
python3 scripts/diagram_check.py flow.mmd --png flow.png  # renders offline with headless Chromium
```

The checker uses a local `mermaid.min.js` (`$MERMAID_JS`, or
`~/.cache/karpathy-explainers/mermaid.min.js`). If neither exists, it prints the one-line `curl`
that fetches it.

## Verification checklist (rung 2)

- [ ] `diagram_check.py` says PASS, and you looked at the PNG
- [ ] every label is the real name from the source; every number on it matches the fact sheet
- [ ] every arrow direction checked against the source (write which page)
- [ ] arrows numbered 1..N in the true order of events
- [ ] the weak-spots list is present and specific
- [ ] the same colours and terms as rung 1 (same glossary)
