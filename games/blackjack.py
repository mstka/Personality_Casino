"""Simplified Blackjack game module."""
import random
import time

class Blackjack:
    """A simple Blackjack game with numbers 1-10."""

    def play_round(self, bet: int, action: str) -> dict:
        """Play a single round of Blackjack.

        Parameters
        ----------
        bet : int
            Amount bet by the player.
        action : str
            Player action ("hit" or "stand" at start).

        Returns
        -------
        dict
            Dictionary containing bet, choice, result and processing time.
        """
        start = time.time()
        player = random.randint(4, 21)  # simple random hand
        dealer = random.randint(4, 21)
        player_bust = player > 21
        dealer_bust = dealer > 21
        if player_bust:
            result = "LOSE"
        elif dealer_bust or player > dealer:
            result = "WIN"
        elif player == dealer:
            result = "DRAW"
        else:
            result = "LOSE"
        elapsed = time.time() - start
        return {
            "bet": bet,
            "choice": action,
            "result": result,
            "time": elapsed,
        }
