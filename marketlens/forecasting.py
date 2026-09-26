"""Chronological models, immutable forecast payloads and outcome metrics."""
from collections import Counter
import hashlib
import json
import math

import numpy as np
from sklearn.calibration import _SigmoidCalibration
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .core import ASSETS, direction
from .market_data import require_contiguous, target_session

CONFIG = {"version": "calibrated-linear-v2", "fit_min": 120, "calibration": 40,
          "lookback": 20, "purge": 5, "classifier_C": 1.0, "ridge_alpha": 1.0}


class CalibratedDirection:
    """Frozen classifier + sklearn's Platt sigmoids, with explicit class alignment.

    The pinned sklearn 1.9.1 CV wrapper infers classes from calibration labels,
    losing a fitted Flat class when that later window has none. Use its sigmoid
    primitive directly, preserving fitted class order and exposing sample counts.
    Its standard target smoothing also handles an all-negative Flat column;
    this is not evidence of reliability for unseen Flat outcomes.
    """
    def __init__(self, estimator, x, labels):
        self.estimator = estimator
        self.classes_ = estimator.classes_
        scores = self.scores(x)
        self.calibrators = [_SigmoidCalibration().fit(scores[:, i], labels == label)
                            for i, label in enumerate(self.classes_)]

    def scores(self, x):
        scores = self.estimator.decision_function(x)
        return np.column_stack((-scores, scores)) if scores.ndim == 1 else scores

    def predict_proba(self, x):
        scores = self.scores(x)
        probabilities = np.column_stack([c.predict(scores[:, i]) for i, c in enumerate(self.calibrators)])
        return probabilities / probabilities.sum(axis=1, keepdims=True)


def data_hash(rows):
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def features(rows, index, symbol):
    values = np.array([r[symbol] for r in rows[index-20:index+1]], dtype=float)
    if len(values) != 21:
        raise ValueError("At least 21 complete prices are required for features.")
    return [values[-1]/values[-1-lag]-1 for lag in (1, 5, 20)] + [float(np.std(np.diff(values)/values[:-1], ddof=1))] + [float(symbol == s) for s in ASSETS]


def fit_model(rows):
    require_contiguous(rows)
    last_labelled = len(rows)-6
    cal_start = last_labelled - CONFIG["calibration"] + 1
    fit_end = cal_start - CONFIG["purge"] - 1
    fit_indices = list(range(20, fit_end+1))
    cal_indices = list(range(cal_start, last_labelled+1))
    if len(fit_indices) < CONFIG["fit_min"]:
        raise ValueError("Not enough history: need 120 fitting and 40 calibration sessions plus lookback and purged horizons.")

    def examples(indices):
        x, labels, returns = [], [], []
        for i in indices:
            for s in ASSETS:
                x.append(features(rows, i, s))
                labels.append(direction(rows[i+5][s]-rows[i][s]))
                returns.append(rows[i+1][s]/rows[i][s]-1)
        return np.array(x), np.array(labels), np.array(returns)

    x, y, r = examples(fit_indices)
    cx, cy, _ = examples(cal_indices)
    if not {"Up", "Down"}.issubset(set(y)) or not {"Up", "Down"}.issubset(set(cy)):
        raise ValueError("Need both Up and Down outcomes in fitting and calibration history.")
    if not set(cy).issubset(set(y)):
        raise ValueError("Calibration contains a class not observed during fitting.")
    classifier = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=500, random_state=0))
    classifier.fit(x, y)
    calibrated = CalibratedDirection(classifier, cx, cy)
    regressor = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    regressor.fit(x, r)
    metadata = {"cutoff": rows[-1]["date"], "fit_start": rows[20]["date"], "fit_end": rows[fit_end]["date"],
                "fit_label_end": rows[fit_end+5]["date"], "cal_start": rows[cal_start]["date"],
                "cal_end": rows[last_labelled]["date"], "fit_sessions": len(fit_indices),
                "cal_sessions": len(cal_indices), "classes": dict(Counter(y.tolist())),
                "cal_classes": dict(Counter(cy.tolist())), "data_hash": data_hash(rows), "config": CONFIG}
    metadata["version"] = CONFIG["version"] + "-" + data_hash(metadata)[:12]
    model = {"classifier": calibrated, "regressor": regressor, "metadata": metadata}
    predict(model, rows)  # Do not publish a model that cannot issue usable forecasts.
    return model


def predict(model, rows):
    require_contiguous(rows[-21:])
    current = rows[-1]
    if current["date"] < model["metadata"]["cutoff"]:
        raise ValueError("Cannot use a future model for an earlier forecast.")
    x = np.array([features(rows, len(rows)-1, s) for s in ASSETS])
    probabilities = model["classifier"].predict_proba(x)
    price_returns = model["regressor"].predict(x)
    results = []
    for i, symbol in enumerate(ASSETS):
        probs = dict(zip(model["classifier"].classes_, probabilities[i]))
        predicted = "Up" if probs.get("Up", 0) >= probs.get("Down", 0) else "Down"
        confidence = float(probs[predicted])
        price = float(current[symbol] * (1+price_returns[i]))
        if not math.isfinite(price) or price <= 0 or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError("Invalid model output.")
        common = {"symbol": symbol, "date": current["date"], "price": current[symbol],
                  "model": model["metadata"]["version"], "cutoff": model["metadata"]["cutoff"],
                  "momentum": direction(current[symbol] - rows[-21][symbol])}
        results += [{**common, "horizon": 5, "due": target_session(current["date"], 5), "direction": predicted,
                     "confidence": confidence, "estimate": None},
                    {**common, "horizon": 1, "due": target_session(current["date"], 1), "direction": None,
                     "confidence": None, "estimate": price}]
    return results


def evaluate(record, actual):
    change = actual / record["price"] - 1
    result = {**record, "actual_close": actual, "actual": direction(change), "return": change,
              "correct": None, "error": None, "ape": None}
    if record["horizon"] == 5:
        result["correct"] = result["actual"] == record["direction"]
    else:
        result["error"] = abs(record["estimate"] - actual)
        result["ape"] = result["error"] / actual
    return result


def metrics(records):
    directional = [r for r in records if r["horizon"] == 5 and r.get("actual_close") is not None]
    prices = [r for r in records if r["horizon"] == 1 and r.get("actual_close") is not None]
    def mean(values):
        return sum(values)/len(values) if values else None
    bins = []
    for i in range(5):
        items = [r for r in directional if min(4, int(r["confidence"]*5)) == i]
        bins.append({"low": i/5, "high": (i+1)/5, "count": len(items),
                     "confidence": mean([r["confidence"] for r in items]),
                     "accuracy": mean([r["correct"] for r in items])})
    return {"evaluated": len(directional), "price_evaluated": len(prices),
            "pending": sum(r.get("actual_close") is None for r in records),
            "accuracy": mean([r["correct"] for r in directional]),
            "always_up": mean([r["actual"] == "Up" for r in directional]),
            "momentum": mean([r["actual"] == r["momentum"] for r in directional]),
            "brier": mean([(r["confidence"]-r["correct"])**2 for r in directional]),
            "mae": mean([r["error"] for r in prices]), "mape": mean([r["ape"] for r in prices]),
            "last_close_mae": mean([abs(r["price"]-r["actual_close"]) for r in prices]), "bins": bins}
