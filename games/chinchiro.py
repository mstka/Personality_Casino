"""Chinchiro (Cho-Han) dice game module."""
import random
import time

class Chinchiro:
    """A dice game where players guess even or odd."""

    def play_round(self, bet: int, guess: str) -> dict:
        """Play a single round of Chinchiro.

        Parameters
        ----------
        bet : int
            Amount bet by the player.
        guess : str
            Player guess "even" or "odd".

        Returns
        -------
        dict
            Dictionary containing bet, choice, result and processing time.
        """
        start = time.time()
        dice = random.randint(1, 6) + random.randint(1, 6)
        outcome = "even" if dice % 2 == 0 else "odd"
        result = "WIN" if guess == outcome else "LOSE"
        elapsed = time.time() - start
        return {
            "bet": bet,
            "choice": guess,
            "result": result,
            "time": elapsed,
        }
