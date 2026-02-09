def format_number(i, max_val) -> str:
    return format_str(i, len(str(max(max_val,10))))


def format_str(no, digits) -> str:
    res = str(no)
    while len(res) < digits:
        res = "0" + res
    return res
