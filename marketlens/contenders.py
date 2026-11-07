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

    def __init__(self, symbols=ASSETS):
        self.symbols = tuple(symbols)

    def fit(self, rows):
        """Baselines learn nothing; a model refits on the sessions it is given."""

    def predict(self, rows):
        raise NotImplementedError


class AlwaysUp(Contender):
    name = "always-up"

    def predict(self, rows):
        return [call(rows, s, 5, direction="Up") for s in self.symbols]


class Momentum(Contender):
    name = "momentum-20"

    def predict(self, rows):
        return [call(rows, s, 5, direction=direction(rows[-1][s]-rows[-21][s])) for s in self.symbols]


class LastClose(Contender):
    name = "last-close"

    def predict(self, rows):
        return [call(rows, s, 1, estimate=rows[-1][s]) for s in self.symbols]


class Logistic(Contender):
    """The app's model: retrained at every cutoff, keeping the last usable one."""
    name = "logistic (calibrated-linear-v2)"

    def __init__(self, symbols=ASSETS, trainer=fit_model):
        super().__init__(symbols)
        self.trainer, self.model = trainer, None

    def fit(self, rows):
        try:
            self.model = self.trainer(rows, None if self.symbols == tuple(ASSETS) else self.symbols)
        except ValueError:
            pass  # Not enough history yet; like the app, keep the previous model.

    def predict(self, rows):
        return predict(self.model, rows) if self.model else []


CONTENDERS = (AlwaysUp, Momentum, LastClose, Logistic)


def replay(contenders, rows, start, symbols=ASSETS):
    """Walk forward from rows[start]; return each contender's evaluated calls."""
    require_contiguous(rows, symbols)
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
    """An evaluated call this contender actually made for its horizon."""
    if record.get("actual_close") is None:
        return False
    return record["direction"] is not None if record["horizon"] == 5 else record["estimate"] is not None


def mean(values):
    return sum(values)/len(values) if values else None


def shared(calls):
    """Evaluated calls by contender and key, and the keys all answering contenders share per horizon."""
    keyed = {name: {(r["date"], r["symbol"], r["horizon"]): r for r in records if answered(r)}
             for name, records in calls.items()}
    common = {}
    for horizon in (5, 1):
        sets = [{k for k in keys if k[2] == horizon} for keys in keyed.values()]
        sets = [s for s in sets if s]
        common[horizon] = set.intersection(*sets) if sets else set()
    return keyed, common


def leaderboard(calls):
    """Score every contender only on the observations all answering contenders share."""
    keyed, shared_keys = shared(calls)
    board = []
    for name, keys in keyed.items():
        calls5 = [keys[k] for k in sorted(shared_keys[5]) if k in keys]
        calls1 = [keys[k] for k in sorted(shared_keys[1]) if k in keys]
        confident = calls5 and all(r["confidence"] is not None for r in calls5)
        board.append({"name": name, "calls": len(calls5), "accuracy": mean([r["correct"] for r in calls5]),
                      "brier": mean([(r["confidence"]-r["correct"])**2 for r in calls5]) if confident else None,
                      "estimates": len(calls1), "mae": mean([r["error"] for r in calls1]),
                      "mape": mean([r["ape"] for r in calls1])})
    return board


def by_session(keyed, keys, score):
    """Per reference session, the mean of score(record) over its shared symbols."""
    sessions = {}
    for key in keys:
        sessions.setdefault(key[0], []).append(score(keyed[key]))
    return [(day, mean(values)) for day, values in sorted(sessions.items())]


def edge(calls, model, minimum=30, block=5):
    """The model against the best other contender, per horizon, with an approximate 95% range.

    Differences are averaged per reference session, then over blocks of five
    consecutive sessions, so overlapping five-session targets are not counted as
    independent. A verdict needs the whole range on one side of zero.
    """
    keyed, keys = shared(calls)
    board = {b["name"]: b for b in leaderboard(calls)}
    result = {}
    for horizon, field, sign in ((5, "accuracy", 1), (1, "mae", -1)):
        rivals = [n for n in calls if n != model and board[n][field] is not None]
        if board[model][field] is None or not rivals:
            continue
        # Best rival: highest accuracy or lowest error; ties keep the earlier contender.
        best = max(rivals, key=lambda n: sign*board[n][field])
        score = (lambda r: float(r["correct"])) if horizon == 5 else (lambda r: r["error"])
        mine, theirs = by_session(keyed[model], keys[horizon], score), by_session(keyed[best], keys[horizon], score)
        daily = [a - b for (_, a), (_, b) in zip(mine, theirs)]
        item = {"against": best, "sessions": len(daily), "minimum": minimum, "value": mean(daily),
                "low": None, "high": None, "verdict": "not enough history yet"}
        if len(daily) >= minimum:
            blocks = [mean(daily[i:i+block]) for i in range(0, len(daily) - block + 1, block)]
            centre = mean(blocks)
            spread = (sum((b-centre)**2 for b in blocks)/(len(blocks)-1))**0.5
            half = 1.96*spread/len(blocks)**0.5
            item.update(low=item["value"]-half, high=item["value"]+half)
            better = item["low"] > 0 if sign > 0 else item["high"] < 0
            worse = item["high"] < 0 if sign > 0 else item["low"] > 0
            item["verdict"] = "better" if better else "worse" if worse else "no measurable difference"
        result[horizon] = item
    return result


def rolling(calls, window=20):
    """Each direction contender's accuracy over the latest `window` shared reference sessions."""
    keyed, keys = shared(calls)
    lines = {}
    for name, records in keyed.items():
        if not any(k in records for k in keys[5]):
            continue
        sessions = by_session(records, keys[5], lambda r: float(r["correct"]))
        lines[name] = [{"date": sessions[i][0], "accuracy": mean([v for _, v in sessions[i-window+1:i+1]])}
                       for i in range(window-1, len(sessions))]
    return lines
