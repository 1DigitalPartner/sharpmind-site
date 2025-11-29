from __future__ import annotations
from . import render_posts as rp
from pathlib import Path

def main():
    rp.render_all()
    # se esistono questi builder, eseguili; altrimenti ignora
    for mod_name, fn in [
        ("build_tools_page", "build_tools_page"),
        ("build_homepage",   "build_homepage"),
    ]:
        try:
            mod = __import__(f"scripts.{mod_name}", fromlist=[fn])
            getattr(mod, fn)()
            print(f"✔ {fn.replace('_',' ').title()} generata.")
        except Exception as e:
            # non bloccare la build se non presenti
            print(f"ℹ Skippata {fn}: {e}")

if __name__ == "__main__":
    main()
