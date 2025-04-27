import json


def load_riddle(riddle_name):
    with open(f"../riddle_storage/{riddle_name}.json", "r") as file:
        riddle = json.load(file)    
    return riddle

def print_riddle(riddle):
    for row in riddle:
        print(row)
    print()

def map_values(riddle):
    mapped_riddle = []
    for row in riddle:
        mapped_row = []
        for px in row:
            if px is None:
                mapped_row.append(0)
            else:
                mapped_row.append(1)
        mapped_riddle.append(mapped_row)
    
    return mapped_riddle


riddle = load_riddle("line_1px")
riddle = map_values(riddle)
print_riddle(riddle)


