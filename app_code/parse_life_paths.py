import os
import re
import sys
import json
import copy
import logging
import pandas as pd
import ezodf
from app_code import config_data as cd

logging.basicConfig(level=logging.INFO, format="%(levelname)-6s - %(message)s")
LOGGER = logging.getLogger("life_path")

SHEET_NAME = 'sheet_name'
SHEET_ROW = 'sheet_row'
PROFESSION_FULL = 'profession_full'
PROFESSION_NAME = 'profession_name'
PROFESSION_LATIN = 'profession_latin'
PROFESSION_DURATION = 'profession_duration'
REQUIREMENT_GENDER = 'gender'
GENERAL_SKILLS = 'general_skills'

SKILL = 'skill'
SKILLS_AGE_7_10 = 'skills age 7-10'
SKILLS_AGE_11_14 = 'skills age 11-14'
SKILLS = 'skills'
REQUIREMENTS = 'requirements'
TRAITS = 'traits'
NOTES = 'notes'
NOTE = 'note'

SKILL_GROUPS = [
    SKILLS_AGE_7_10,
    SKILLS_AGE_11_14,
    SKILLS,
]

DATA_FIELDS = SKILL_GROUPS + [
    TRAITS,
    REQUIREMENTS,
    NOTES,
    NOTE,
]


class GensCareers:
    def __init__(self, cs_skill_dict=None):
        self.spread_sheet_name = os.path.join(cd.DATA_DIR, 'lifepathfinal.ods')
        self.skill_dict = {}
        self.cs_skill_dict = cs_skill_dict
        self.skill_list = []
        self.lifepath_dict = {}
        self.parse_spread_sheet()
        self.skill_df = pd.DataFrame.from_dict(self.skill_list)

    def parse_spread_sheet(self):
        if os.path.exists(self.spread_sheet_name) is False:
            raise FileNotFoundError("File '%s' not found" % self.spread_sheet_name)

        LOGGER.info("Lifepath Spreadsheet opened")
        spreadsheet = ezodf.opendoc(self.spread_sheet_name)
        for sheet in spreadsheet.sheets:
            self.process_sheet(sheet)

    def process_sheet(self, sheet):
        sheet_name = sheet.name
        rowcount = sheet.nrows()
        LOGGER.debug("SHEET=%s (%d)", sheet_name, rowcount)

        first = True
        idx = 0
        buffer = {}
        self.clear_buffer(buffer)
        while idx < rowcount:
            row_name = sheet[idx, 0].value.lower()
            if row_name not in DATA_FIELDS:
                if first is True:
                    first = False
                else:
                    self.save_profession(buffer)

                buffer[SHEET_NAME] = sheet_name
                buffer[SHEET_ROW] = idx + 1
                profession_tokens = sheet[idx, 0].value.split('(')
                buffer[PROFESSION_NAME] = profession_tokens[0].strip().capitalize()
                buffer[PROFESSION_LATIN] = profession_tokens[1].split(')')[0].strip()
                buffer[PROFESSION_FULL] = buffer[SHEET_NAME] + ': ' + buffer[PROFESSION_NAME]
                buffer[REQUIREMENT_GENDER] = sheet[idx, 2].value.strip()

                year_list = re.findall(r'(\d+) years', sheet[idx, 3].value.strip().lower())
                general_skill_list = re.findall(r'(\d+) general skills', sheet[idx, 4].value.strip().lower())

                if len(year_list) > 0:
                    buffer[PROFESSION_DURATION] = int(year_list[0])
                else:
                    buffer[PROFESSION_DURATION] = 0

                if len(general_skill_list) > 0:
                    buffer[GENERAL_SKILLS] = int(general_skill_list[0])
                else:
                    buffer[GENERAL_SKILLS] = 0
            else:
                buffer[row_name] = []
                for cell in sheet.row(idx)[1:]:
                    if cell.value is None or cell.value.lower() == 'none':
                        continue

                    for value in cell.value.split(','):
                        buffer[row_name].append(value.strip())

                #LOGGER.info("idx:%d - %s", idx, profession_name)
            idx += 1

    @staticmethod
    def clear_buffer(buffer):
        for data_field in DATA_FIELDS:
            if data_field == 'note':
                data_field = 'notes'
        buffer[data_field] = []

    def save_profession(self, buffer):
        # LOGGER.info("Profession: %s\n%s\n", buffer.get('profession_name', 'INVALID'), json.dumps(buffer, indent=4))

        if buffer[PROFESSION_FULL] in self.lifepath_dict:
            LOGGER.error("Duplicate Lifepath Name:%s %s | %s",
                         buffer[PROFESSION_FULL], buffer[SHEET_NAME],
                         self.lifepath_dict[buffer[PROFESSION_FULL]][SHEET_NAME])

        self.lifepath_dict[buffer[PROFESSION_FULL]] = copy.deepcopy(buffer)

        for skill_group in SKILL_GROUPS:
            if skill_group not in buffer:
                continue

            for skill in buffer[skill_group]:
                skill = skill.capitalize()
                if skill not in self.skill_dict:
                    self.skill_dict[skill] = []

                # if self.cs_skill_dict is not None and skill not in self.cs_skill_dict:
                    # LOGGER.error("ERROR: undefined skill: '%s'", skill)
                    # kill, json.dumps(self.cs_skill_dict, indent=4, sort_keys=True))

                self.skill_dict[skill].append(buffer[PROFESSION_FULL])
                self.skill_list.append({
                    PROFESSION_FULL: buffer[PROFESSION_FULL],
                    SKILL: skill,
                    REQUIREMENTS: buffer[REQUIREMENTS]
                })

        self.clear_buffer(buffer)


def run():
    data_obj = GensCareers()
    list_skills(data_obj)
    # search_lifepath(data_obj, ['Religion', 'Ritual', 'Deception', 'Etiquette'])
    # search_lifepath(data_obj, ['Melee', 'Labor'])


def list_skills(data_obj):
    for skill in sorted(data_obj.skill_dict):
        #LOGGER.info("Skill: %s: %d", skill, len(data_obj.skill_dict[skill]))
        print("%s: %d" % (skill, len(data_obj.skill_dict[skill])))
    # LOGGER.info(a.skill_df.to_string())


def search_lifepath(data_obj, skill_list):
    skill_count = len(skill_list)
    match_df = data_obj.skill_df[data_obj.skill_df[SKILL].isin(skill_list)].set_index(
        [PROFESSION_FULL, SKILL]).count(level=PROFESSION_FULL)
    match_dict = match_df[match_df[REQUIREMENTS] >= skill_count].to_dict(orient="index")
    match_count = len(match_dict)
    print("Lifepath Match:%d" % match_count)
    for lifepath in match_dict:
        print("Life Path:%s req:%s" % (lifepath, data_obj.lifepath_dict[lifepath][REQUIREMENTS]))


if __name__ == "__main__":
    run()
