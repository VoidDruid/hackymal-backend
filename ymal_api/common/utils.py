def to_snake(string: str) -> str:
    letters = []
    for index, letter in enumerate(string):
        if letter.isupper() and index != 0:
            letters.append("_")
        letters.append(letter.lower())

    return "".join(letters)
