QUESTIONS = [
("Why can valid JSON still be rejected?", ["It may violate the application's schema", "JSON is always trusted", "It cannot"], 0),
("Why verify an evidence quote?", ["To ensure it came from the review", "To make outputs longer", "To expose secrets"], 0),
("Why calculate totals in Python?", ["Models can make arithmetic/grounding errors", "Models refuse numbers", "It saves disk space"], 0),
("What if Q&A cites an unseen ID?", ["Reject it", "Accept it", "Invent its review"], 0),
]
WRITTEN = ["Explain why API keys must stay out of Git.", "What makes review text untrusted data?", "When does a cached classification become stale?", "Why do 12 correct examples not prove complete accuracy?"]

def score_choices(answers):
    """Validate four zero-based quiz choices; written answers are mentor-reviewed."""
    if len(answers) != len(QUESTIONS) or any(not isinstance(a, int) or a < 0 or a >= len(QUESTIONS[i][1]) for i, a in enumerate(answers)):
        raise ValueError("answers must be one valid choice per question")
    return sum(answer == QUESTIONS[i][2] for i, answer in enumerate(answers))
