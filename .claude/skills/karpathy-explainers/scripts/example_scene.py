"""Example scene for explainer_video.py: half-life in three beats (~20 s).

Copy this file, keep the pattern:
  - one idea per beat, narration in STE100 style (short, active, one term per thing)
  - each beat redraws the earlier state (call the earlier draw at t=T) and adds ONE new thing
  - every number on screen is computed from model(), never typed by hand
  - claims + source on every beat, so the script.md is a checklist
"""
from explainer_video import Beat, C, seg

TITLE = "Half-life"
SRC = "OpenStax Chemistry 2e, sec. 21.3 (half-life, first-order decay)"


def model(t, n0=100.0, half=5.0):          # single source of truth for every number
    return n0 * 0.5 ** (t / half)


def frame(p, k):                            # shared axes, drawn on with progress k; keep y < 620 (caption band)
    p.text("Half-life", 60, 50, 40, C["fg"], k, bold=True)
    return p.axes(140, 130, 900, 400, (0, 20), (0, 100), "time (years)", "atoms left (%)",
                  xticks=(0, 5, 10, 15, 20), yticks=(0, 25, 50, 100), progress=k)


def b1(p, t, T):
    m = frame(p, seg(t, 0, 1.0))
    p.math(r"$N = N_0 \left(\dfrac{1}{2}\right)^{t / t_{1/2}}$", 1080, 120, 40, C["yellow"], seg(t, 1.0, 1.8), "r")
    p.plot(m, model, 0, 20, C["blue"], progress=seg(t, 1.5, T - 0.5))


def b2(p, t, T):
    b1(p, 99, 99)
    m = frame(p, 1)
    for i, tt in enumerate((5, 10, 15), start=1):       # numbered steps: one half-life each
        k = seg(t, 0.4 + 1.2 * (i - 1), 1.4 + 1.2 * (i - 1))
        x0, y0 = m(tt - 5, model(tt - 5)); x1, y1 = m(tt, model(tt))
        p.arrow(x0 + 12, y0 - 40, x1 - 6, y1 - 40, C["teal"], 3, k, num=i)  # offset above the curve: arrows never cross labels
        p.dot(x1, y1, 8, C["yellow"], k)
        p.text(f"{model(tt):.1f} %", x1 + 14, y1 + 22, 24, C["yellow"], k)  # label below-right of its dot


def b3(p, t, T):
    b2(p, 99, 99)
    k = seg(t, 0.3, 1.2)
    p.box(700, 200, 380, 110, "Each step halves\nwhat is left.", C["green"], k, fill=C["green"], size=28)


BEATS = [
    Beat(say="Each atom has the same chance to decay in each year. So the number of atoms falls along this curve.",
         draw=b1, claims=["N = N0 (1/2)^(t / t_half) for first-order decay"], source=SRC),
    Beat(say="Look at one half-life: five years. After step one, half is left. After step two, one quarter is left.",
         draw=b2, claims=["t_half = 5 years (example value)", "50.0 % at 5 y, 25.0 % at 10 y, 12.5 % at 15 y"], source=SRC),
    Beat(say="The time for each half does not change. That is why we can use one number, the half-life.",
         draw=b3, claims=["half-life is constant for first-order decay"], source=SRC),
]
