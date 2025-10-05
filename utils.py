def grade_guess(target, guess):
    target_chars = list(target)
    result = [None]*5

    for i in range(5):
        if guess[i] == target[i]:
            result[i] = "green"
            target_chars[i] = None
    freq = {}
    for ch in target_chars:
        if ch:
            freq[ch] = freq.get(ch, 0) + 1

    for i in range(5):
        if result[i] is None:
            if freq.get(guess[i], 0) > 0:
                result[i] = "orange"
                freq[guess[i]] -= 1
            else:
                result[i] = "grey"

    return result