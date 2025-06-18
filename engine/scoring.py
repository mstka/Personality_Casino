"""Scoring functions for analyzing game logs."""
from typing import List, Tuple, Dict


Metrics = Dict[str, float]


def calculate_scores(logs: List[Tuple[str, int, str, str, float]]) -> Metrics:
    """Calculate player metrics from logs.

    Parameters
    ----------
    logs : list of tuples
        Each tuple contains game, bet, choice, result, duration.

    Returns
    -------
    dict
        Dictionary with keys RISK, STRATEGY, CHALLENGE, ADAPT.
    """
    if not logs:
        return {"RISK": 0.0, "STRATEGY": 0.0, "CHALLENGE": 0.0, "ADAPT": 0.0}

    total_bet = sum(bet for _, bet, *_ in logs)
    avg_bet = total_bet / len(logs)
    wins = sum(1 for *_, result, _ in logs if result == "WIN")
    win_rate = wins / len(logs)

    unique_games = len(set(game for game, *_ in logs))
    challenge = unique_games / 4.0  # four games total

    avg_time = sum(duration for *_, duration in logs) / len(logs)
    adapt = max(0.0, 1.0 - avg_time / 5.0)

    return {
        "RISK": min(1.0, avg_bet / 100.0),
        "STRATEGY": win_rate,
        "CHALLENGE": challenge,
        "ADAPT": adapt,
    }


def classify_business_type(scores: Metrics) -> str:
    """Classify player into a business type based on scores."""
    if scores["RISK"] > 0.7 and scores["STRATEGY"] > 0.5:
        return "Entrepreneur"
    if scores["CHALLENGE"] < 0.3:
        return "Conservative"
    if scores["ADAPT"] > 0.8:
        return "Innovator"
    return "Balanced"
