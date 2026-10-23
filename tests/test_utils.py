from interview_coach.utils import average_score

def test_average_score():
    assert average_score([6, 8, 10]) == 8

def test_empty_average():
    assert average_score([]) == 0.0
