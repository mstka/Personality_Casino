"""Simplified Roulette game module."""
import random
import time

class Roulette:
    """A Roulette game with numbers 0-36."""

    def play_round(self, bet: int, number: int) -> dict:
        """Play a single round of Roulette.

        Parameters
        ----------
        bet : int
            Amount bet by the player.
        number : int
            Number chosen by the player (0-36).

        Returns
        -------
        dict
            Dictionary containing bet, choice, result and processing time.
        """
        start = time.time()
        outcome = random.randint(0, 36)
        result = "WIN" if number == outcome else "LOSE"
        elapsed = time.time() - start
        return {
            "bet": bet,
            "choice": str(number),
            "result": result,
            "time": elapsed,
        }
