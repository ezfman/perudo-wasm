from perudo import Perudo


p = Perudo()


def test_faces():
    p.bet = {
        "count": 1,
        "face": 2,
    }

    assert not p._validate_bet({"count": 1, "face": 2})
    assert p._validate_bet({"count": 1, "face": 3})
    assert p._validate_bet({"count": 1, "face": 4})
    assert p._validate_bet({"count": 1, "face": 5})
    assert p._validate_bet({"count": 1, "face": 6})
    assert p._validate_bet({"count": 1, "face": 1})
