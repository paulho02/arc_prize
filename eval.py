
# function that evaluates the deviation between two environments
# can be used to calculate a score how good a environment is
def evaluate(env1: list, env2: list):
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
