import random
import string

def generate_luhn_digit(card_number: str) -> str:
    """
    Generate a check digit using the Luhn algorithm.
    """
    digits = [int(d) if d.isdigit() else ord(d) % 10 for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return str((10 - (total % 10)) % 10)

def generate_card_code() -> str:
    """
    Generate a 16-character card code: XW + 13 random chars + Luhn check digit.
    """
    prefix = "XW"
    # 13 random uppercase letters and digits
    chars = string.ascii_uppercase + string.digits
    body = ''.join(random.choices(chars, k=13))
    
    partial_code = prefix + body
    check_digit = generate_luhn_digit(partial_code)
    
    return partial_code + check_digit

def format_card_code(code: str) -> str:
    """
    Format card code with dashes: XXXX-XXXX-XXXX-XXXX
    """
    return '-'.join([code[i:i+4] for i in range(0, 16, 4)])
