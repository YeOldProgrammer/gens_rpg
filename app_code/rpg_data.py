import sys
import logging
from app_code import parse_life_paths as lp, parse_character_sheet as cs

LOGGER = logging.getLogger('data')

try:
    CHAR_DATA = cs.GensCharacterSheet()
    LIFEPATH_DATA = lp.GensCareers(CHAR_DATA.skill_dict)

except Exception as error_text:
    LOGGER.error("Uncaught data exception - exiting: %s", error_text, exec_info=True)
    sys.exit(1)
