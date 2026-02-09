def format_number(i, max_val) -> str:
    return format_str(i, len(str(max(max_val,10))))


def format_str(no, digits) -> str:
    res = str(no)
    while len(res) < digits:
        res = "0" + res
    return res

def get_necessary_numbers(jig_sizes, rack_sizes) -> set[int]:
        
        numbers = set()
        numbers.add(0)
        numbers.update(rack_sizes)
        changed = True

        while changed:
            new_numbers = set()
            for rack in numbers:              
                for jig in jig_sizes:
                    new_number = rack - jig
                    if (new_number >= 0):
                        new_numbers.add(new_number)

            changed = not new_numbers.issubset(numbers)
            numbers.update(new_numbers)            

        numbers.update(jig_sizes)
        return numbers


def get_necessary_rack_numbers(jig_sizes, rack_size) -> set[int]:
        
        numbers = set()
        numbers.add(0)
        numbers.add(rack_size)
        changed = True

        while changed:
            new_numbers = set()
            for rack in numbers:              
                for jig in jig_sizes:
                    new_number = rack - jig
                    if (new_number >= 0):
                        new_numbers.add(new_number)

            changed = not new_numbers.issubset(numbers)
            numbers.update(new_numbers)         

        return numbers