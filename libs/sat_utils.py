import pandas as pd 

def name_parser(name: str) -> str:
    """ parses file name to generate fund name """
    name = name.split('.')[0]
    name = name.split('/')
    name = name[len(name)-1]

    return name 


def print_hello():
    print("hello")