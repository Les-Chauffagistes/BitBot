from collections.abc import Callable
from typing import Awaitable

from discord import Interaction


class InteractionHandler:
    def __init__(self):
        self.interactions: dict[str, Callable[[Interaction, list[str]], Awaitable[None]]] = {}

    def register_interaction(self, interaction_id: str):
        """
        A wrapper that takes an interaction custom ID (string) and an async function (handler) as arguments, and registers the handler for that interaction.
        """
        def wrapper(func: Callable[[Interaction, list[str]], Awaitable[None]]):
            self.interactions[interaction_id] = func
            return func
        return wrapper

    def handle_interaction(self, interaction_id, interaction: Interaction, values: list[str]):
        if interaction_id in self.interactions:
            return self.interactions[interaction_id](interaction, values)
        else:
            raise ValueError(f"No handler registered for interaction: {interaction_id}")
