def average_score(scores):
    values = [float(score) for score in scores if score is not None]
    return sum(values) / len(values) if values else 0.0
