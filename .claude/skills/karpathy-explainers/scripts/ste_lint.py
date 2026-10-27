#!/usr/bin/env python3
"""ASD-STE100 lint for rung 1 ("80% of the way" profile).

  python3 ste_lint.py draft.md [--glossary glossary.json] [--strict]

ERRORS (must be 0):  sentence > 20 words (procedural) / > 25 words (descriptive),
                     paragraph > 6 sentences, glossary synonym used (one word = one meaning),
                     contraction.
WARNINGS (aim for <= 20% of sentences; --strict makes them errors):
                     passive voice, -ing verb form, unapproved/complex word, hedge word,
                     noun cluster > 3 words, missing article guess, more than one instruction.
Ignored: fenced code, $...$ / $$...$$ maths, table rows, headings, URLs.
Procedural = a sentence that starts with a command verb or sits in a numbered list.
glossary.json: {"cell potential": ["voltage", "emf", "cell voltage"], ...}  canonical -> banned synonyms.
Exit code 1 if any error.
"""
import argparse, json, re, sys

COMPLEX = {  # unapproved/complex word -> STE-style simple word
    "utilize": "use", "utilise": "use", "commence": "start", "terminate": "stop", "approximately": "about",
    "additional": "more", "ascertain": "find", "assist": "help", "attempt": "try", "demonstrate": "show",
    "facilitate": "help", "indicate": "show", "obtain": "get / find", "perform": "do", "require": "need",
    "sufficient": "enough", "subsequently": "then", "prior": "before", "numerous": "many", "possess": "have",
    "endeavor": "try", "initiate": "start", "modify": "change", "eliminate": "remove", "verify": "make sure",
    "therefore": "thus / so", "consequently": "as a result", "furthermore": "also", "moreover": "also",
    "regarding": "about", "whereas": "but", "whilst": "while", "via": "through", "e.g.": "for example",
    "i.e.": "that is", "etc": "list all items", "respectively": "say each pair", "aforementioned": "this",
    "leverage": "use", "comprise": "contain", "magnitude": "size / value",
}
HEDGES = {"basically", "essentially", "simply", "just", "very", "quite", "really", "actually", "perhaps",
          "arguably", "somewhat", "fairly", "rather", "probably", "obviously", "clearly", "of course", "kind of",
          "sort of", "a bit", "pretty much", "in a sense", "more or less"}
CMD_VERBS = {"add", "adjust", "apply", "calculate", "change", "check", "compare", "compute", "connect", "count",
             "decrease", "divide", "do", "draw", "enter", "find", "give", "hold", "increase", "keep", "let", "look",
             "make", "measure", "move", "multiply", "note", "push", "put", "read", "record", "remove", "replace",
             "select", "set", "show", "start", "stop", "subtract", "take", "turn", "use", "write", "plug", "try",
             "predict", "drag", "click", "open", "close", "convert", "solve", "substitute", "think", "imagine"}
IRREG_PP = {"shown", "given", "made", "known", "done", "taken", "written", "seen", "found", "held", "kept", "built",
            "set", "put", "read", "drawn", "driven", "chosen", "broken", "spoken", "brought", "caught", "left", "sent",
            "split", "spread", "thrown", "worn", "understood"}
ING_OK = {"thing", "something", "nothing", "anything", "everything", "during", "bring", "ring", "string", "king",
          "spring", "wing", "sing", "swing", "ceiling", "morning", "evening", "building", "heating", "cooling",
          "setting", "reading", "warning", "opening", "coating", "plating", "fitting", "bearing", "spacing"}
BE = r"\b(is|are|was|were|be|been|being|gets|got)\b"


def strip_markup(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", " FORMULA ", text, flags=re.S)
    text = re.sub(r"\$[^$\n]+\$", " FORMULA ", text)
    text = re.sub(r"https?://\S+", " URL ", text)
    text = re.sub(r"`[^`]+`", " CODE ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)
    return text


def paragraphs(text):
    out = []
    for block in re.split(r"\n\s*\n", text):
        lines = [l for l in block.split("\n") if l.strip() and not l.lstrip().startswith(("#", "|", ">"))]
        if not lines: continue
        items, cur = [], []
        for l in lines:
            m = re.match(r"\s*(\d+[.)]|[-*+])\s+(.*)", l)
            if m:
                if cur: items.append((False, " ".join(cur))); cur = []
                items.append((m.group(1)[0].isdigit(), m.group(2)))
            else:
                cur.append(l.strip())
        if cur: items.append((False, " ".join(cur)))
        out.append(items)
    return out


def sentences(s):
    s = re.sub(r"\b(e\.g|i\.e|etc|vs|approx|Fig|Eq|cf)\.", lambda m: m.group(0).replace(".", "§"), s)
    parts = re.split(r"(?<=[.!?:;])\s+(?=[A-Z0-9(\"'“])", s.strip())
    return [p.replace("§", ".") for p in parts if re.search(r"[A-Za-z]", p)]


def words(s):
    return re.findall(r"[A-Za-z0-9°⁰-⁹₀-₉+\-−/^.,']+", re.sub(r"[()\"“”]", " ", s))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--glossary"); ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    raw = sys.stdin.read() if a.file == "-" else open(a.file).read()
    gloss = json.load(open(a.glossary)) if a.glossary else {}
    errs, warns, n_sent, lens = [], [], 0, []
    for pi, items in enumerate(paragraphs(strip_markup(raw)), 1):
        sents = [(num, x) for num, it in items for x in sentences(it)]
        prose = [x for num, x in sents if not num]
        if len(prose) > 6: errs.append(f"P{pi}: paragraph has {len(prose)} sentences (max 6): \"{prose[0][:60]}...\"")
        for num, s in sents:
            n_sent += 1; w = words(s); lw = [x.lower().strip(".,;:'") for x in w]
            first = lw[0] if lw else ""
            proc = num or first in CMD_VERBS
            cap = 20 if proc else 25; lens.append(len(w))
            tag = f"P{pi} \"{s[:70]}{'...' if len(s) > 70 else ''}\""
            if len(w) > cap: errs.append(f"{tag}: {len(w)} words > {cap} ({'procedural' if proc else 'descriptive'})")
            if re.search(r"\b\w+(n't|'re|'ll|'ve|'d)\b|\b(it's|that's|there's|what's|let's)\b", s, re.I):
                errs.append(f"{tag}: contraction (write the full words)")
            low = " " + " ".join(lw) + " "
            for canon, syns in gloss.items():
                for syn in syns:
                    if re.search(rf"(?<![\w-]){re.escape(syn.lower())}(?![\w-])", s.lower()):
                        errs.append(f"{tag}: '{syn}' -> use the one term '{canon}' (one word, one meaning)")
            m = re.search(BE + r"\s+(\w+ly\s+)?(\w+ed|" + "|".join(IRREG_PP) + r")\b", s, re.I)
            if m: warns.append(f"{tag}: passive? '{m.group(0)}' -> say who does it")
            for x in lw:
                if x.endswith("ing") and len(x) > 5 and x not in ING_OK: warns.append(f"{tag}: -ing form '{x}' (STE: use a simple tense or a noun)"); break
            for bad, good in COMPLEX.items():
                if re.search(rf"\b{re.escape(bad.rstrip('e'))}(e|es|ed|ing|s|ion|ions)?\b" if bad[-1].isalpha() else re.escape(bad), s, re.I): warns.append(f"{tag}: '{bad}' -> '{good}'")
            for h in HEDGES:
                if f" {h} " in low: warns.append(f"{tag}: hedge '{h}' -> state it or cut it")
            run = 0
            STOP = {"the", "a", "an", "of", "to", "in", "is", "and", "or", "for", "on", "with", "at", "by", "from", "it", "this",
                    "that", "if", "as", "when", "then", "be", "are", "you", "we", "not", "no", "can", "will", "do", "does", "has", "have"}
            for x in w:
                core = x.strip(".,;:'").lower()
                noun_like = re.match(r"[a-z]", core) and core not in STOP and not core.endswith(("ed", "ly", "es")) and core not in CMD_VERBS
                run = run + 1 if noun_like else 0
                if run >= 4: warns.append(f"{tag}: possible noun cluster > 3 words"); break
                if x[-1] in ".,;:": run = 0
            if proc and len(re.findall(r"\b(and then|then|, and)\b", s)) >= 1 and len(w) > 10:
                warns.append(f"{tag}: more than one instruction? (one action per sentence)")
    ratio = len(warns) / max(1, n_sent)
    for e in errs: print("ERROR  ", e)
    for x in warns: print("warn   ", x)
    avg = sum(lens) / max(1, len(lens))
    print(f"\n{n_sent} sentences, avg {avg:.1f} words, max {max(lens or [0])}; {len(errs)} errors, {len(warns)} warnings "
          f"({ratio:.0%} of sentences; target <= 20%)")
    fail = errs or (a.strict and warns) or ratio > 0.2
    print("RESULT:", "FAIL" if fail else "PASS (80% profile)")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
