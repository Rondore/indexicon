#!/usr/bin/env python3

import math
import os

install_path = os.path.dirname(os.path.realpath(__file__)) + '/'

def pretty_age(age: int) -> str:
    """
    Convert a numerical age in seconds to human readable format
    """
    age = int(age)
    if age <= 120: return str(age) + " seconds"
    age = math.floor( age / 60 )
    if age <= 90 : return str(age) + " minutes"
    age = math.floor( age / 60 )
    if age <= 36 : return str(age) + " hours"
    age = math.floor( age / 24 )
    if age > 10000 : return "never"
    return str(age) + " days"

def get_install_path() -> str:
    return install_path

def get_combined_url(start, end):
    while start[-1] == '/':
        start = start[:-1]
    while end[0] == '/':
        end = end[1:]
    return start + '/' + end

def format_number(number: int) -> str:
    string = str(number)
    hole: str = string
    parts: (str|None) = None
    if '.' in string:
        hole, parts = string.split('.')
    length = len(hole)
    chunks = math.ceil(length / 3)
    if chunks > 1:
        compiled = ''
        comma = ''
        for offset in range(chunks):
            end = offset * -3
            if offset == 0:
                part = hole[end - 3 :]
            else:
                part = hole[end - 3 : end]
            compiled = part + comma + compiled
            comma = ','
        hole = compiled
    if parts == None:
        return hole
    return hole + '.' + parts

def environment_variable(name: str, fallback: str) -> str:
    full_name = 'INDEXICON_' + name
    if hasattr(os.environ, full_name):
        return os.environ[full_name]
    else:
        return fallback

def environment_variable_list(name: str, fallback: list[str]) -> list[str]:
    full_name = 'INDEXICON_' + name
    if hasattr(os.environ, full_name):
        string_as_list = os.environ[full_name]
        return string_as_list.split('|')
    else:
        return fallback