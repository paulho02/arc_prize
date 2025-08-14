import logging
from typing import Union

from instruction_language.logging_setup import setup_logger


class Environment():
    def __init__(self, env: dict[tuple[int, int], int] = None):
        if env is None:
            env = {}
        self.env: dict[tuple[int, int], int] = env

    def get(self, x: int, y: int) -> int:
        """
        Get the value at the specified coordinates (x, y).
        If the coordinates do not exist, return 0.
        """
        return self.env.get((x, y), 0)

    def set(self, x: int, y: int, value: int):
        """
        Set the value at the specified coordinates (x, y).
        If the coordinates do not exist, they will be created.
        """
        self.env[(x, y)] = value

    def to_list(self) -> list[list[int]]:
        """
        Convert the environment to a 2D list representation.
        """
        if not self.env:
            return []

        # Filter out keys where x or y is None
        non_null_keys = []
        for x, y in self.env.keys():
            if x is not None and y is not None:
                non_null_keys.append((x, y))
        if not non_null_keys:
            return []

        max_x = max(x for x, _ in non_null_keys)
        max_y = max(y for _, y in non_null_keys)

        env_list = [[0] * (max_y + 1) for _ in range(max_x + 1)]

        for (x, y), value in self.env.items():
            if x is not None and y is not None:
                env_list[x][y] = value if value is not None else 0

        return env_list

    @staticmethod
    def from_list(env_list: list[list[int]]) -> 'Environment':
        """
        Load the environment from a 2D list representation.
        """
        environment = Environment()

        for x, row in enumerate(env_list):
            for y, value in enumerate(row):
                # if value != 0:
                environment.set(x, y, value)

        return environment

    def plot(self, title=None, print_func=print):
        title = title if title else str(self)
        env_list = self.to_list()

        output_lines = []
        output_lines.append("------------------")
        output_lines.append(f"Env '{title}':")
        for row in env_list:
            row_str = " ".join(f"{col:3}" for col in row)
            output_lines.append(row_str)
        output_lines.append("------------------")

        # If print_func is like logger.info, print each line separately
        for line in output_lines:
            print_func(line)


def evaluate(env1: Environment, env2: Environment) -> int:
    # todo maybe need to be adjusted to work with environments that support more than 2 possible values
    """
    function that evaluates the deviation between two environments
    can be used to calculate a score how good a environment is
    """
    env1 = env1.to_list()
    env2 = env2.to_list()

    deviation_score = 0
    max_rows = max(len(env1), len(env2))
    max_cols = max(len(env1[0]) if env1 else 0, len(env2[0]) if env2 else 0)

    for i in range(max_rows):
        for j in range(max_cols):
            val1 = env1[i][j] if i < len(env1) and j < len(env1[i]) else None
            val2 = env2[i][j] if i < len(env2) and j < len(env2[i]) else None
            if val1 != val2:
                deviation_score += 1

    return deviation_score


class GEMService:
    """
    (Global Memory Manager Service)
    """

    _envs: dict[str, Environment] = {
        "INITIAL_ENV": Environment(),
        "OUTPUT_ENV": Environment(),
    }

    @staticmethod
    def set(env_key: Union[str, int], env: Environment):
        """
        Set method for the global environment manager.
        """
        env_key = str(env_key)
        if env_key not in GEMService._envs.keys():
            raise ValueError(f"Environment '{env_key}' does not exist.")

        if not isinstance(env, Environment):
            raise TypeError(
                "Provided environment must be an instance of Environment class.")

        GEMService._envs[env_key] = env

    @staticmethod
    def get(env_key: Union[str, int]) -> Environment:

        env_key = str(env_key)
        if env_key not in GEMService._envs.keys():
            raise ValueError(f"Environment '{env_key}' does not exist.")
        return GEMService._envs[env_key]

    @staticmethod
    def get_initial_env():
        """
        Get method for specific hardcoded environment.
        """
        return GEMService.get("INITIAL_ENV")

    @staticmethod
    def get_output_env():
        """
        Get method for specific hardcoded environment.
        """
        return GEMService.get("OUTPUT_ENV")

    @staticmethod
    def reset_env(env_key: Union[str, int]):
        """
        Resets the environment with the given key to an empty state.
        """
        env_key = str(env_key)
        if env_key not in GEMService._envs.keys():
            raise ValueError(f"Environment '{env_key}' does not exist.")

        GEMService._envs[env_key] = Environment()

    @staticmethod
    def reset_all_envs():
        """
        Resets all environments to an empty state.
        """
        for key in GEMService._envs.keys():
            GEMService._envs[key] = Environment()

    @staticmethod
    def delete(env_key: Union[str, int]):
        """
        Deletes the environment with the given key from the global environment manager.
        """
        env_key = str(env_key)
        if env_key in GEMService._envs.keys():
            del GEMService._envs[env_key]

    @staticmethod
    def add_env(env_key: Union[str, int]):
        env_key = str(env_key)
        if env_key in GEMService._envs:
            raise ValueError(f"Environment '{env_key}' already exists.")

        GEMService._envs[env_key] = Environment()

    @staticmethod
    def print_initial_env(print_func=print):
        """
        Print method for specific hardcoded environment.
        """
        GEMService.get_initial_env().plot("INITIAL_ENV", print_func=print_func)

    @staticmethod
    def print_output_env(print_func=print):
        """
        Print method for specific hardcoded environment.
        """
        GEMService.get_output_env().plot(title="OUTPUT_ENV", print_func=print_func)
