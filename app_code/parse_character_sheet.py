import os
import re
import logging
import pandas as pd
import ezodf
from app_code import config_data as cd

logging.basicConfig(level=logging.INFO, format="%(levelname)-6s - %(message)s")
LOGGER = logging.getLogger("char_sheet")


class GensCharacterSheet:
    def __init__(self):
        self.spread_sheet_name = os.path.join(cd.DATA_DIR, 'character Sheet 2.0.ods')
        self.sheet_name = 'Sheet1'
        self.skill_dict = {}
        self.parse_spread_sheet()

    def parse_spread_sheet(self):
        if os.path.exists(self.spread_sheet_name) is False:
            raise FileNotFoundError("File '%s' not found" % self.spread_sheet_name)

        LOGGER.info("Character Sheet Spreadsheet opened")
        spreadsheet = ezodf.opendoc(self.spread_sheet_name)
        if self.sheet_name not in spreadsheet.sheets.names():
            raise ValueError("Sheet '%s' not found in '%s'" % (self.sheet_name, self.spread_sheet_name))

        sheet = spreadsheet.sheets[self.sheet_name]
        for col_idx in [0, 3, 6]:
            if col_idx == 0:
                start_row = 23
            else:
                start_row = 20
            end_row = 50

            for row_idx in range(start_row, end_row + 1):
                skill_name = sheet[row_idx, col_idx].value
                if skill_name is None:
                    continue
                skill_name = skill_name.strip()
                potential = skill_name[-1].upper()
                skill_name = skill_name[:-1].strip()

                if '(' in skill_name:
                    skill_name = skill_name.split('(')[1].split(')')[0]

                self.skill_dict[skill_name] = {
                    'potential': potential,
                    'row': row_idx,
                    'col': col_idx,
                }


def run():
    data_obj = GensCharacterSheet()
    list_skills(data_obj)


def list_skills(data_obj):
    for skill in sorted(data_obj.skill_dict):
        print("%s - pot:%s " % (skill, data_obj.skill_dict[skill]['potential']))


if __name__ == "__main__":
    run()
