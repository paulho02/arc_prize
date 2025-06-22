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

        max_x = max(x for x, _ in self.env.keys())
        max_y = max(y for _, y in self.env.keys())

        env_list = [[0] * (max_y + 1) for _ in range(max_x + 1)]

        for (x, y), value in self.env.items():
            env_list[x][y] = value

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

    def plot(self, title=None):
        title = title if title else str(self)
        env_list = self.to_list()

        print("------------------")
        print(f"Env '{title}':")
        for row in env_list:
            for col in row:
                print(f" {col} ", end="")
            print()
        print("------------------")


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
    def set(env_key: str, env: Environment):
        """
        Set method for the global environment manager.
        """
        if env_key not in GEMService._envs.keys():
            raise ValueError(f"Environment '{env_key}' does not exist.")

        if not isinstance(env, Environment):
            raise TypeError(
                "Provided environment must be an instance of Environment class.")

        GEMService._envs[env_key] = env

    @staticmethod
    def get(env_key: str) -> Environment:

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
    def reset_env(env_key: str):
        """
        Resets the environment with the given key to an empty state.
        """
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
    def delete(env_key: str):
        """
        Deletes the environment with the given key from the global environment manager.
        """
        if env_key in GEMService._envs.keys():
            del GEMService._envs[env_key]

    @staticmethod
    def add_env(env_key: str):
        if env_key in GEMService.envs:
            raise ValueError(f"Environment '{env_key}' already exists.")

        GEMService._envs[env_key] = Environment()

    @staticmethod
    def print_initial_env():
        """
        Print method for specific hardcoded environment.
        """
        GEMService.get_initial_env().plot("INITIAL_ENV")

    @staticmethod
    def print_output_env():
        """
        Print method for specific hardcoded environment.
        """
        GEMService.get_output_env().plot(title="OUTPUT_ENV")
