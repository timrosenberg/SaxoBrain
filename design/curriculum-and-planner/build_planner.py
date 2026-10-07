"""Planner prototype: template-planner.html + data2.json (curriculum + whole catalog) -> planner-prototype.html."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(HERE, f)
t = open(P("template-planner.html"), encoding="utf-8").read()
d = json.load(open(P("data2.json"), encoding="utf-8"))
open(P("planner-prototype.html"), "w", encoding="utf-8").write(t.replace("/*DATA*/", json.dumps(d, ensure_ascii=False, separators=(",", ":"))))
print("planner-prototype.html written")
