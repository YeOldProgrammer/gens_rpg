import os
import re
import json
import copy
import logging
import pandas as pd
import ezodf
from app_code import config_data as cd

logging.basicConfig(level=logging.INFO, format="%(levelname)-6s - %(message)s")
LOGGER = logging.getLogger("char_sheet")

POTENTIAL_STARTING = 25
POTENTIAL_MAX = 16
POTENTIAL_MIN = 6

BLANK_CHARACTER = {
    'year_born': 145,
    'year_current': 145,
    'sex': 'male',
    'name': '',
    'tribe': '',
    'potential_used': 0,
    'potential': {
        'physical': 0,
        'mental': 0,
        'social': 0,
        'mystical': 0,
        'family': 0,
        'health': 0,
    },
    'virtues': {
        # Traditional
        'Frugal': 0,
        'Industrious': 0,
        'Spiritual': 0,
        'Prudence': 0,
        'Severity': 0,
        'Honest': 0,
        'Cruel': 0,
        'Arbitrary': 0,
        'Unpretentious': 0,
        'Vengeful': 0,
        'Chaste': 0,
        'Dignity': 0,

        # Modern
        'Generous': 0,
        'Content': 0,
        'Secular': 0,
        'Impulsive': 0,
        'Openness': 0,
        'Deceptive': 0,
        'Merciful': 0,
        'Justice': 0,
        'Cultured': 0,
        'Compassion': 0,
        'Lustful': 0,
        'Humility': 0,
    },
    'lifepaths': [],
    'skills': {},
    'traits': {},
}


class CharacterGen:
    def __init__(self):
        self.character_data = {}

    def import_data(self, character_data):
        self.character_data = copy.deepcopy(character_data)

    def export_data(self):
        return json.dumps(self.character_data, indent=4)

    def set_potential(self, **kwargs):
        total = 0
        for arg in kwargs:
            if arg not in self.character_data['potential']:
                raise KeyError("Potential '%s' is not valid", arg)

            if isinstance(kwargs[arg], int) is False:
                raise TypeError("Potential '%s' is not an int", arg)

            if kwargs[arg] < POTENTIAL_MIN or kwargs[arg] > POTENTIAL_MAX:
                raise ValueError("Potential '%s' value %d is out of range (%d-%d)",
                                 arg, kwargs[arg], POTENTIAL_MIN, POTENTIAL_MAX)

            total += kwargs[arg] - POTENTIAL_MIN

        self.character_data['potential_used'] = total
        for arg in kwargs:
            self.character_data['potential'][arg] = kwargs[arg]
