import csv, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from app.models import Review, validate_review
from app.ingest import import_reviews
from app.classify import validate_classification, classify_review, classifier_messages
from app.provider import FakeProvider, ProviderError, HTTPSProvider
from app.cache import valid_cached
from app.report import insights
from app.retrieve import retrieve
from app.qa import ask, ABSTENTION
from app.selfcheck import score_choices

R = Review("R001", "Fest", "Loved the DJs but the queue was terrible.", "2026-01-15")
def good(**over):
    d={"review_id":"R001","sentiment":"mixed","topics":["sound","queue"],"evidence_quote":"queue was terrible","short_reason":"Praise and a queue complaint."}; d.update(over); return json.dumps(d)

class VibeCheckTests(unittest.TestCase):
    def test_01_valid_review(self): self.assertEqual(validate_review(R.to_dict()).id,"R001")
    def test_02_duplicate_id(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.json"; p.write_text(json.dumps([R.to_dict(),R.to_dict()])); a,b=import_reviews(p); self.assertEqual((len(a),len(b)),(1,1))
    def test_03_bad_date(self):
        with self.assertRaises(ValueError): validate_review({**R.to_dict(),"created_at":"nope"})
    def test_04_empty_text(self):
        with self.assertRaises(ValueError): validate_review({**R.to_dict(),"text":""})
    def test_05_csv_utf8(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.csv"; p.write_text("id,event,text,created_at\nR9,Fest,café music was lovely,2026-01-01\n",encoding="utf-8"); self.assertEqual(len(import_reviews(p)[0]),1)
    def test_06_valid_classifier_json(self): self.assertEqual(validate_classification(good(),R)["sentiment"],"mixed")
    def test_07_bad_json(self):
        with self.assertRaises(ValueError): validate_classification("{",R)
    def test_08_wrong_id(self):
        with self.assertRaises(ValueError): validate_classification(good(review_id="R2"),R)
    def test_09_invented_quote(self):
        with self.assertRaises(ValueError): validate_classification(good(evidence_quote="invented"),R)
    def test_10_invalid_label(self):
        with self.assertRaises(ValueError): validate_classification(good(sentiment="wonderful"),R)
    def test_11_bad_topics(self):
        with self.assertRaises(ValueError): validate_classification(good(topics=["queue","queue"]),R)
    def test_12_too_many_topics(self):
        with self.assertRaises(ValueError): validate_classification(good(topics=["queue","sound","food","staff"]),R)
    def test_13_fake_classify(self): self.assertEqual(classify_review(R,FakeProvider([good()]))["review_id"],"R001")
    def test_14_cache_unchanged(self):
        x=validate_classification(good(),R, "m"); self.assertTrue(valid_cached({"R001":x},R,"m"))
    def test_15_cache_changed_source(self):
        x=validate_classification(good(),R,"m"); other=Review("R001","Fest","Different text entirely here.","2026-01-15"); self.assertIsNone(valid_cached({"R001":x},other,"m"))
    def test_16_zero_denominator(self): self.assertEqual(insights([],{})["sentiment_distribution"]["positive"]["percent"],0)
    def test_17_missing_analysis(self): self.assertEqual(insights([R],{})["coverage"]["failed_or_pending"],1)
    def test_18_mixed_report(self): self.assertEqual(insights([R],{"R001":validate_classification(good(),R)})["mixed_review_count"],1)
    def test_19_retrieve(self): self.assertEqual(retrieve("queue problems",[R])[0].id,"R001")
    def test_20_qa_unknown_citation(self):
        with self.assertRaises(ValueError): ask("queue",[R],FakeProvider([json.dumps({"answer":"bad","cited_review_ids":["R99"]})]))
    def test_21_qa_abstains_without_retrieval(self): self.assertEqual(ask("astronomy",[R],FakeProvider([]))["answer"],ABSTENTION)
    def test_22_qa_valid(self):
        out=ask("queue",[R],FakeProvider([json.dumps({"answer":"One review mentions a queue [R001].","cited_review_ids":["R001"]})])); self.assertEqual(out["retrieved_ids"],["R001"])
    def test_23_injection_is_data(self): self.assertIn("untrusted_review",classifier_messages(R)[1]["content"])
    def test_24_https_required(self):
        with self.assertRaises(ProviderError): HTTPSProvider("http://bad.test","m","k")
    def test_25_no_key_in_messages(self): self.assertNotIn("secret",str(classifier_messages(R)))
    def test_26_http_429_retries(self):
        response = json.dumps({"choices":[{"message":{"content":"ok"}}]}).encode()
        class Reply:
            def read(self): return response
            def __enter__(self): return self
            def __exit__(self,*args): return False
        with patch("app.provider.urlopen", side_effect=[HTTPError("x",429,"rate",{},None), Reply()]) as call, patch("app.provider.time.sleep"):
            self.assertEqual(HTTPSProvider("https://provider.test/x","m","k").call_model([]),"ok"); self.assertEqual(call.call_count,2)
    def test_27_timeout_failure(self):
        with patch("app.provider.urlopen", side_effect=TimeoutError):
            with patch("app.provider.time.sleep"):
                with self.assertRaises(ProviderError): HTTPSProvider("https://provider.test/x","m","k",retries=0).call_model([])
    def test_28_selfcheck_validation_and_scoring(self):
        self.assertEqual(score_choices([0,0,0,0]),4)
        with self.assertRaises(ValueError): score_choices([0])
    def test_29_export_count_matches(self):
        report=insights([R],{"R001":validate_classification(good(),R)})
        self.assertEqual(report["coverage"]["analyzed"],len(["R001"]))

if __name__ == "__main__": unittest.main()
