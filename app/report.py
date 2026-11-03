from collections import Counter

def insights(reviews, analyses):
    verified = [analyses[r.id] for r in reviews if r.id in analyses]
    sentiments, topics = Counter(x["sentiment"] for x in verified), Counter(t for x in verified for t in x["topics"])
    total, analyzed = len(reviews), len(verified)
    return {"analysis_derived": True, "coverage":{"analyzed":analyzed,"total":total,"failed_or_pending":total-analyzed},
      "sentiment_distribution": {s:{"count":sentiments[s],"percent":round(100*sentiments[s]/analyzed,2) if analyzed else 0} for s in ("positive","negative","neutral","mixed")},
      "topic_frequency":dict(topics), "mixed_review_count":sentiments["mixed"],
      "top_complaint_themes":[t for t,_ in topics.most_common(3)], "cited_example_ids":[r.id for r in reviews if r.id in analyses][:5]}
