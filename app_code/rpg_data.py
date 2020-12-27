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


def cross_check():
    master_skill_list = []
    char_data_lower_list = []
    life_path_lower_list = []
    max_skill_len = 0

    for skill in CHAR_DATA.skill_dict:
        skill_len = len(skill)
        if skill_len > max_skill_len:
            max_skill_len = skill_len

        if skill not in master_skill_list:
            master_skill_list.append(skill)
        if skill.lower() not in char_data_lower_list:
            char_data_lower_list.append(skill.lower())

    for skill in LIFEPATH_DATA.skill_dict:
        skill_len = len(skill)
        if skill_len > max_skill_len:
            max_skill_len = skill_len

        if skill not in master_skill_list:
            master_skill_list.append(skill)
        if skill.lower() not in life_path_lower_list:
            life_path_lower_list.append(skill.lower())

    skill_format = "%-" + str(max_skill_len) + 's - %s %s'
    buffer = skill_format % ("Skill", 'CS', 'LP') + "\n"
    missing = False
    for skill in sorted(master_skill_list):
        skill_lower = skill.lower()
        if skill in CHAR_DATA.skill_dict:
            cs_found = 'X '
        elif skill_lower in char_data_lower_list:
            cs_found = ' L'
        else:
            cs_found = '  '

        if skill in LIFEPATH_DATA.skill_dict:
            lp_found = 'X '
        elif skill_lower in life_path_lower_list:
            lp_found = ' L'
        else:
            lp_found = '  '

        if lp_found.strip() != 'X' or cs_found.strip() != 'X':
            buffer = buffer + skill_format % (skill, cs_found, lp_found) + '\n'
            missing = True
        # else:
        #     buffer = buffer + skill_format % (skill, cs_found, lp_found) + '\n'

    if missing is True:
        LOGGER.error("Skill Audit\n" + buffer)
    else:
        LOGGER.info("Skill Audit\n" + buffer)

cross_check()
