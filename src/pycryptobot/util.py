def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n


def get_comparison_string(val1, val2, label="", precision=2):
    truncated_val1 = truncate(val1, precision)
    truncated_val2 = truncate(val2, precision)
    label = f"{label}: " if label != "" else ""

    if val1 > val2:
        sign = ">"
    elif val1 < val2:
        sign = "<"
    else:
        sign = "="

    return f"{label}{truncated_val1} {sign} {truncated_val2}"
