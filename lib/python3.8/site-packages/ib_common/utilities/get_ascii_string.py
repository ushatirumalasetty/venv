def get_ascii_string(char_sequence):
    if type(char_sequence) != int:
        from ib_common.utilities.is_null_or_empty import is_null_or_empty
        if is_null_or_empty(char_sequence) or len(char_sequence) == 0:
            return ''
        return ''.join([i if ord(i) < 128 else '' for i in char_sequence])
    else:
        return char_sequence
