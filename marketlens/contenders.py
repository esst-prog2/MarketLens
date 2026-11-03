"""Contenders measured side by side on one walk-forward replay.

A contender has a name, fit(rows) and predict(rows). Both receive only the
sessions up to and including the reference session, so no contender can see an
outcome. predict returns records shaped like forecasting.predict: per symbol a
five-session call (direction, optional confidence) and a next-session close
estimate. A contender without an answer for a horizon leaves that field None.
"""
from .core import ASSETS, direction
from .forecasting import evaluate, fit_model, predict
from .market_data import require_contiguous, target_session


def call(rows, symbol, horizon, direction=None, confidence=None, estimate=None):
    current = rows[-1]
    return {"symbol": symbol, "date": current["date"], "price": current[symbol], "horizon": horizon,
            "due": target_session(current["date"], horizon), "direction": direction,
            "confidence": confidence, "estimate": estimate}


class Contender:
    name = "contender"

    def fit(self, rows):
        """Baselines learn nothing; a model refits on the sessions it is given."""

    def predict(self, rows):
        raise NotImplementedError


class AlwaysUp(Contender):
    name = "always-up"

    def predict(self, rows):
        return [call(rows, s, 5, direction="Up") for s in ASSETS]


class Momentum(Contender):
    name = "momentum-20"

    def predict(self, rows):
        return [call(rows, s, 5, direction=direction(rows[-1][s]-rows[-21][s])) for s in ASSETS]


class LastClose(Contender):
    name = "last-close"

    def predict(self, rows):
        return [call(rows, s, 1, estimate=rows[-1][s]) for s in ASSETS]


class Logistic(Contender):
    """The app's model: retrained at every cutoff, keeping the last usable one."""
    name = "logistic (calibrated-linear-v2)"

    def __init__(self, trainer=fit_model):
        self.trainer, self.model = trainer, None

    def fit(self, rows):
        try:
            self.model = self.trainer(rows)
        except ValueError:
            pass  # Not enough history yet; like the app, keep the previous model.

    def predict(self, rows):
        return predict(self.model, rows) if self.model else []


CONTENDERS = (AlwaysUp, Momentum, LastClose, Logistic)


def replay(contenders, rows, start):
    """Walk forward from rows[start]; return each contender's evaluated calls."""
    require_contiguous(rows)
    calls = {c.name: [] for c in contenders}
    for i in range(start, len(rows)):
        past = rows[:i+1]
        for contender in contenders:
            contender.fit(past)
            for record in contender.predict(past):
                ahead = i + record["horizon"]
                if ahead >= len(rows):
                    continue  # Outcome lies beyond the sample: pending, not scored.
                if rows[ahead]["date"] != record["due"]:
                    raise ValueError("Due session does not match the replay calendar.")
                calls[contender.name].append(evaluate(record, rows[ahead][record["symbol"]]))
    return calls


def answered(record):
    return record["direction"] is not None if record["horizon"] == 5 else record["estimate"] is not None


def leaderboard(calls):
    """Score every contender only on the observations all answering contenders share."""
    def mean(values):
        return sum(values)/len(values) if values else None
    keyed = {name: {(r["date"], r["symbol"], r["horizon"]): r for r in records if answered(r)}
             for name, records in calls.items()}
    shared = {}
    for horizon in (5, 1):
        sets = [{k for k in keys if k[2] == horizon} for keys in keyed.values()]
        sets = [s for s in sets if s]
        shared[horizon] = set.intersection(*sets) if sets else set()
    board = []
    for name, keys in keyed.items():
        calls5 = [keys[k] for k in sorted(shared[5]) if k in keys]
        calls1 = [keys[k] for k in sorted(shared[1]) if k in keys]
        confident = calls5 and all(r["confidence"] is not None for r in calls5)
        board.append({"name": name, "calls": len(calls5), "accuracy": mean([r["correct"] for r in calls5]),
                      "brier": mean([(r["confidence"]-r["correct"])**2 for r in calls5]) if confident else None,
                      "estimates": len(calls1), "mae": mean([r["error"] for r in calls1]),
                      "mape": mean([r["ape"] for r in calls1])})
    return board
