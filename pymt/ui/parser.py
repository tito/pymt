'''
Parser: default parser from string to special type

Used specially for CSS
'''

__all__ = ['parse_color', 'parse_int', 'parse_float',
           'parse_string', 'parse_bool', 'parse_int2',
           'parse_float4']

import re

def parse_color(text):
    value = (1, 1, 1, 1)
    if text.startswith('rgb'):
        res = re.match('rgba?\((.*)\)', text)
        value = map(lambda x: int(x) / 255., re.split(',\ ?', res.groups()[0]))
        if len(value) == 3:
            value.append(1)
    elif text.startswith('#'):
        res = text[1:]
        value = [int(x, 16)/255. for x in re.split('([0-9a-f]{2})', res) if x != '']
        if len(value) == 3:
            value.append(1)
    return value

def parse_bool(text):
    if text.lower() in ('true', '1'):
        return True
    elif text.lower() in ('false', '0'):
        return False
    raise Exception('Invalid boolean: %s' % text)

def parse_string(text):
    if len(text) >= 2 and text[0] in ('"', "'") and text[-1] in ('"', "'"):
        text = text[1:-1]
    return text.strip()

def parse_int2(text):
    texts = [x for x in text.split(' ') if x.strip() != '']
    value = map(lambda x: parse_int(x), texts)
    if len(value) < 1:
        raise Exception('Invalid format int2 for %s' % text)
    elif len(value) == 1:
        value[1] = value[0]
    elif len(value) > 2:
        raise Exception('Too much value in %s : %s' % (text, str(value)))
    return value

def parse_float4(text):
    texts = [x for x in text.split(' ') if x.strip() != '']
    value = map(lambda x: parse_float(x), texts)
    if len(value) < 1:
        raise Exception('Invalid format float4 for %s' % text)
    elif len(value) == 1:
        return map(lambda x: value[0], range(4))
    elif len(value) == 2:
        return [value[0], value[1], value[0], value[1]]
    elif len(value) == 3:
        # ambigous case!
        return [value[0], value[1], value[0], value[2]]
    elif len(value) > 4:
        raise Exception('Too much value in %s' % text)
    return value

parse_int = int
parse_float = float

