import json
from .retrieve import retrieve

ABSTENTION = "Insufficient evidence in the supplied reviews"
def qa_messages(question, records):
    evidence = "\n".join(f"[{r.id}] {r.text}" for r in records)
    return [{"role":"system","content":"Answer ONLY from supplied evidence. Return JSON only with answer and cited_review_ids. Cite IDs in [R001] form. If unsupported, answer exactly: Insufficient evidence in the supplied reviews, with no citations."}, {"role":"user","content":f"Question: {question}\nEvidence:\n{evidence}"}]
def ask(question, reviews, provider):
    records = retrieve(question, reviews)
    if not records: return {"answer":ABSTENTION,"cited_review_ids":[],"retrieved_ids":[]}
    try: answer = json.loads(provider.call_model(qa_messages(question, records)))
    except (json.JSONDecodeError, Exception) as exc:
        if exc.__class__.__name__ == "ProviderError": raise
        return {"answer":ABSTENTION,"cited_review_ids":[],"retrieved_ids":[r.id for r in records]}
    allowed = {r.id for r in records}
    if not isinstance(answer, dict) or set(answer) != {"answer","cited_review_ids"} or not isinstance(answer["answer"], str) or not isinstance(answer["cited_review_ids"], list) or any(x not in allowed for x in answer["cited_review_ids"]):
        raise ValueError("Q&A response violates evidence contract")
    if not answer["cited_review_ids"] and answer["answer"] != ABSTENTION: raise ValueError("unsupported Q&A answer must abstain")
    answer["retrieved_ids"] = [r.id for r in records]; return answer
