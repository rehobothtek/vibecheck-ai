import json
from pathlib import Path
from app.ingest import import_reviews
from app.provider import HTTPSProvider, ProviderError
from app.classify import classify_review
from app.cache import load_cache, save_cache, valid_cached
from app.report import insights
from app.qa import ask
from app.selfcheck import QUESTIONS, WRITTEN

DATA = Path("data/synthetic_reviews.csv"); CACHE = Path("data/results/analyses.json")
def provider(): return HTTPSProvider()
def load(): return import_reviews(DATA)[0]
def self_check():
    score=0; rationales=[]
    for prompt, choices, right in QUESTIONS:
        print("\n"+prompt); [print(f" {i+1}. {c}") for i,c in enumerate(choices)]
        while True:
            answer=input("Choice: ").strip()
            if answer.isdigit() and 1 <= int(answer) <= len(choices): break
            print("Enter a listed number.")
        score += int(answer)-1 == right
    for q in WRITTEN:
        text=input("\n"+q+"\nYour explanation (mentor reviews this): ").strip()
        if text: rationales.append({"question":q,"rationale":text})
    print(f"Score: {score}/{len(QUESTIONS)}. Written answers are intentionally not auto-graded.")
    Path("data/results/self_check.json").parent.mkdir(parents=True,exist_ok=True); Path("data/results/self_check.json").write_text(json.dumps({"score":score,"rationales":rationales},indent=2),encoding="utf-8")
def run():
    reviews=load(); cache=load_cache(CACHE)
    while True:
        print("\nVibeCheck AI | 1 Import 2 List 3 Analyze 4 Details 5 Insights 6 Ask 7 Export 8 Self-Check 0 Quit")
        choice=input("> ").strip()
        if choice=="0": return
        if choice=="1":
            path=input("CSV/JSON path (blank for sample): ").strip() or str(DATA)
            try: reviews,rejected=import_reviews(path); print(f"Accepted {len(reviews)}; rejected {len(rejected)}: {rejected}")
            except ValueError as exc: print(f"Import failed: {exc}")
        elif choice=="2": [print(f"{r.id}: {r.text}") for r in reviews]
        elif choice=="3":
            try:
                p=provider(); ok=failed=skipped=0
                for r in reviews:
                    if valid_cached(cache,r,p.model): skipped+=1; continue
                    try: cache[r.id]=classify_review(r,p); ok+=1
                    except (ValueError,ProviderError) as exc: print(f"{r.id} failed: {exc}"); failed+=1
                save_cache(CACHE,cache); print(f"Succeeded {ok}, failed {failed}, skipped {skipped}")
            except ProviderError as exc: print(f"Provider configuration/error: {exc}")
        elif choice=="4": print(json.dumps(cache,indent=2))
        elif choice=="5": print(json.dumps(insights(reviews,cache),indent=2))
        elif choice=="6":
            try: print(json.dumps(ask(input("Question: "),reviews,provider()),indent=2))
            except (ProviderError,ValueError) as exc: print(f"Q&A failed: {exc}")
        elif choice=="7":
            out={"report":insights(reviews,cache),"reviews":[r.to_dict() for r in reviews],"validated_analyses":cache}
            Path("data/results").mkdir(parents=True,exist_ok=True); Path("data/results/export_report.json").write_text(json.dumps(out,indent=2),encoding="utf-8"); print("Exported data/results/export_report.json")
        elif choice=="8": self_check()
        else: print("Invalid choice; please choose 0–8.")
if __name__ == "__main__": run()
