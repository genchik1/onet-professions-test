import os


INPUT_DATA_PATHS = 'data'
OUTPUT_DATA_PATHS = 'result_data'


MY_PROFESSIONS_FILE = {
    'path': os.path.join(INPUT_DATA_PATHS, 'my.txt'),
    'read_parameters': {
        "sep": ';',
        "header": None,
        "index_col": None,
        "names": ["my_professions"],
        "engine": 'python',
        "squeeze": True,
    }
}


MATCH_FILES = [
    {
        'path': os.path.join(INPUT_DATA_PATHS, 'Alternate Titles.xlsx'),
        'columns': ['Title', 'O*NET-SOC Code', 'Short Title', 'Alternate Title'],
        'to_find_matches': ['Title', 'Short Title', 'Alternate Title'],
        'rename': {'O*NET-SOC Code':'code',}
    },
]

STEPS = ['Title', 'Short Title', 'Alternate Title']

USE_NLTK = True

if USE_NLTK:
    STEPS = ['Title', 'Alternate Title', 'Short Title', 'Title nltk', 'Alternate Title nltk', 'Short Title nltk']

REPLACE_WORDS = {
    'sr':'senior',
    'i': '',
    'ii': '',
    'iii': '',
    'iiii': '',
    'ownwer':'owner',
}


ADD_SOC_FAMILY = True

FAMILY = {
    'path': os.path.join(INPUT_DATA_PATHS, 'family.csv'),
    'read_parameters': {
        "sep": ';',
        "header": 0,
        "index_col": None,
        'dtype':{'fcode':str}
    }
}



OUTPUT_FILE = {
    'path': os.path.join(OUTPUT_DATA_PATHS,'test_nlt.xlsx'),
    'parameters': {
        # 'sep': '\t',
        'index': None,
        'columns': ['my_professions', 'title', 'lvl', 'accuracy', 'family', 'codes', 'nltk', 'coefficient']
    }
}


if not os.path.isdir(OUTPUT_DATA_PATHS):
    os.makedirs(OUTPUT_DATA_PATHS)

