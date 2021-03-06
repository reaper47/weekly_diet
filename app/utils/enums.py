from enum import Enum
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parent
ROOT = FILE_PATH.parent.parent
UI_FOLDER = f'{FILE_PATH.parent}/ui'


class UiThemes(Enum):
    DAY = f'{UI_FOLDER}/day.ui'
    GUI = f'{UI_FOLDER}/gui.ui'


class Files(Enum):
    DIET_JSON = f'{ROOT}/diet.json'


class MealType(Enum):
    BREAKFAST = 'breakfast'
    MID_MORNING = 'mid morning'
    LUNCH = 'lunch'
    MID_AFTERNOON = 'mid afternoon'
    LATE_AFTERNOON = 'late afternoon'
    DINNER = 'dinner'

    @staticmethod
    def from_string(meal_type: str):
        meal_type = meal_type.lower()
        if 'breakfast' in meal_type:
            return MealType.BREAKFAST
        elif all([x in meal_type for x in ['mid', 'morning']]):
            return MealType.MID_MORNING
        elif 'lunch' in meal_type:
            return MealType.LUNCH
        elif all([x in meal_type for x in ['mid', 'afternoon']]):
            return MealType.MID_AFTERNOON
        elif all([x in meal_type for x in ['late', 'afternoon']]):
            return MealType.LATE_AFTERNOON
        elif 'dinner' in meal_type:
            return MealType.DINNER
        else:
            raise NotImplementedError
