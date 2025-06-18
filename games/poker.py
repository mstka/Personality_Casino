"""Simplified Poker game module."""
import random
import time

class Poker:
    """A simple high-card Poker game."""

    def play_round(self, bet: int, guess: str) -> dict:
        """Play a single round of Poker.

        Parameters
        ----------
        bet : int
            Amount bet by the player.
        guess : str
            Player guess or choice (not used in simplified game).

        Returns
        -------
        dict
            Dictionary containing bet, choice, result and processing time.
        """
        start = time.time()
        player_card = random.randint(1, 13)
        dealer_card = random.randint(1, 13)
        result = "WIN" if player_card > dealer_card else "LOSE"
        elapsed = time.time() - start
        return {
            "bet": bet,
            "choice": guess,
            "result": result,
            "time": elapsed,
        }
