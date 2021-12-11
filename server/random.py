import random, string


def random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def add_list(current, target):
    add = []
    intersection = set(current) & set(target)
    for i in target:
        if i not in intersection:
            add.append(i)
    return add


def remove_list(current, target):
    remove = []
    intersection = set(current) & set(target)
    for i in current:
        if i not in intersection:
            remove.append(i)
    return remove
