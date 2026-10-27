# Step 1: the fact sheet (do this before ANY rung)

All four rungs render ONE fact sheet. The fact sheet is written in plain prose, with no style
limits, and every number in it comes from code. This is the "render step" rule: think first,
style later. It is also the reason the rungs never disagree with each other.

## Template

```markdown
# Fact sheet: <topic>
Primary source(s): <book + section/page, or paper, or official doc URL>. Secondary: <...>

## Core statement
<the equation / rule / mechanism, in its standard form, and any equivalent forms>

## Symbols (one line each: symbol | meaning | unit | typical value)

## Conditions and sign conventions
<when it holds, temperature/assumptions, which direction is positive, what is included/excluded>

## The direction rule(s)
<"when X goes up, Y goes down", stated so a learner can predict>

## Worked numbers (computed by the script below, not by hand)
| inputs | output | source value (if the source prints one) |

## Misconceptions (what learners and models get wrong)
## Limits (where it stops being accurate)
## Three surprising claims to spot-check against the primary source
## Glossary (one term per concept; banned synonyms) -> glossary.json for ste_lint.py
```

Compute the worked numbers in a tiny Python script and paste its output. Reuse the same
function as `model()` in rung 3 and in the rung-4 scene, so one formula feeds every rung.

---

## Worked example: the Nernst equation

This is a sample finished fact sheet (the Nernst Dial, OpenStax Chemistry 2e ch. 17). Use it
as the bar for "what a finished fact sheet looks like", not as text to paste.

Primary source: OpenStax *Chemistry 2e*, section 17.4 "Potential, Free Energy, and Equilibrium".
Constants: CODATA 2018 (R = 8.314462618 J mol⁻¹ K⁻¹, F = 96485.33212 C mol⁻¹).

**Core statement.** E_cell = E°_cell − (RT / nF) ln Q.
At 298.15 K this becomes E_cell = E°_cell − (0.05916 V / n) log₁₀ Q
(often printed as 0.0592 V). The 0.0592 goes with **log₁₀**, the RT/nF goes with **ln**.

**Symbols.** E_cell: cell potential under the actual conditions, V. E°_cell: standard cell
potential (all activities 1, usually 25 °C), V. R: gas constant. T: temperature in **kelvin**.
n: moles of electrons transferred in the balanced reaction (no unit). F: Faraday constant.
Q: reaction quotient, products over reactants, each raised to its coefficient; pure solids and
liquids are left out; strictly activities, approximated by molarity or pressure in atm/bar.

**Direction rule.** When Q increases, E_cell decreases. Each ×10 in Q lowers E_cell by
0.0592/n V at 25 °C. When Q < 1, E_cell > E°_cell.

**Equilibrium link.** At equilibrium Q = K and E_cell = 0 (the cell is "dead"), so
E°_cell = (RT / nF) ln K. A dead battery has E_cell = 0, not E°_cell = 0.

**Worked numbers** (Daniell cell, Zn(s) | Zn²⁺ || Cu²⁺ | Cu(s), E° = 1.10 V, n = 2,
Q = [Zn²⁺]/[Cu²⁺], 25 °C), from
`E = 1.10 - 0.0591593/2 * log10(Q)`:

| Q | 0.01 | 0.1 | 1 | 10 | 100 | 1000 |
|---|---|---|---|---|---|---|
| E_cell (V) | 1.159 | 1.130 | 1.100 | 1.070 | 1.041 | 1.011 |

K for this cell = 10^(2 × 1.10 / 0.05916) ≈ 1.5 × 10³⁷.

**Misconceptions.** (1) Mixing 0.0592 with ln (wrong by ×2.303). (2) Q inverted (reactants over
products), which flips the direction rule. (3) n taken from one half-reaction's coefficient
instead of the electrons cancelled in the balanced equation. (4) Putting Zn(s) or Cu(s) in Q.
(5) Using °C for T. (6) Thinking the potential falls in proportion to Q; it falls with log Q, so
a ×1000 change in Q moves a Daniell cell only ~0.089 V. (7) Thinking E°=0 means no voltage: a
concentration cell has E° = 0 V but a non-zero E_cell when the two concentrations differ.

**Limits.** Concentration stands in for activity only in dilute solution. The 0.0592 form is
for 25 °C only. E° itself changes slightly with temperature; the simple form ignores that.

**Three surprising claims to spot-check.** (a) ×10 in Q changes E by only 29.6 mV when n = 2.
(b) At equilibrium E_cell = 0 V, and E° fixes K. (c) Same metal, two concentrations, still a voltage.

**Glossary.** "cell potential" (ban: voltage, emf, cell voltage); "standard cell potential" (ban:
standard voltage); "reaction quotient" (ban: concentration ratio); "electrons transferred" (ban:
electron number, charge number).
