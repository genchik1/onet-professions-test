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


OUTPUT_FILE = {

}


REPLACE_WORDS = {
    'sr':'senior',
    'i': '',
    'ii': '',
    'iii': '',
    'iiii': '',
    'ownwer':'owner',
}



if not os.path.isdir(OUTPUT_DATA_PATHS):
    os.makedirs(OUTPUT_DATA_PATHS)








