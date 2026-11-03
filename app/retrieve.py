import re
STOP = {"the","a","an","is","are","what","how","why","about","with","and","of","to","in","for","on","did","do"}
def tokens(text): return set(re.findall(r"[a-z0-9]+", text.casefold())) - STOP
def retrieve(question, reviews, limit=5):
    query = tokens(question)
    ranked = sorted(((len(query & tokens(r.text)), r) for r in reviews), key=lambda x:(x[0],x[1].id), reverse=True)
    return [r for score,r in ranked if score][:limit]
