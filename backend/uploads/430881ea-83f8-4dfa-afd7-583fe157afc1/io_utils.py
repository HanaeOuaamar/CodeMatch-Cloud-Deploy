def load_numbers(path):
    with open(path, "r", encoding="utf-8") as f:
        return [int(line.strip()) for line in f]
def sum_numbers(nums):
    return sum(nums)