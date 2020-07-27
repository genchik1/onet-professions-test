import os
import re
import pdb
import numpy as np
import pandas as pd
import settings as s
import pdb
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet


def _match(code_title, end_data, my_prof_dict, onet_prof, nltk, type_, i):

    if nltk:
        my_profession_set = my_prof_dict['my_professions_set nltk']
    else:
        my_profession_set = my_prof_dict['my_professions_set']

    if type_ == 'symmetric_difference':
        coefficient = 1
    elif type_ == 'difference':
        coefficient = 0.5

    for step in s.STEPS:
        result_codes = []
        result_titles = []

        for onet_prof_dict in onet_prof.to_dict('record'):
            code = onet_prof_dict['code']
            names_list = onet_prof_dict[step]

            for names in names_list:
                if type_ == 'symmetric_difference':
                    if len(my_profession_set.symmetric_difference(names)) == 0:
                        if step == 'Title' or  step == 'Title nltk':
                            end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code], 'nltk':nltk, 'coefficient':coefficient})
                            i += 1
                            break
                        result_codes.append(code)
                        result_titles.append(onet_prof_dict['title'])
                elif type_ == 'difference':
                    if len(my_profession_set-names) == 0:
                        if step == 'Title' or  step == 'Title nltk':
                            end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code], 'nltk':nltk, 'coefficient':coefficient})
                            i += 1
                            break
                        result_codes.append(code)
                        result_titles.append(onet_prof_dict['title'])

            if i > 0:
                break

        if len(result_codes)>0 and i == 0:
            result_codes = list(np.unique(np.array(result_codes)))
            if len(result_codes)==1:
                end_data.append({**my_prof_dict, 'title':code_title[result_codes[0]], 'lvl':step, 'codes':result_codes, 'nltk':nltk, 'coefficient':coefficient})
                i+=1
                break

            elif len(result_codes)>1:
                if nltk:
                    end_data.append({**my_prof_dict, 'title':'undefined', 'lvl':step, 'codes':result_codes, 'nltk':nltk, 'coefficient':coefficient})
                    i+=1
                    break

        if i > 0:
            break
    
    return i, end_data


def match(my_prof, onet_prof, steps=s.STEPS):
    end_data = []

    code_title = onet_prof[['code', 'title']].drop_duplicates().dropna()
    code_title = pd.Series(code_title['title'].tolist(), index=code_title['code'])
    code_title = code_title.to_dict()

    nltk = s.USE_NLTK

    for my_prof_dict in my_prof.to_dict('record'):
        # pdb.set_trace()
        i = 0
        for type_ in ['symmetric_difference', 'difference']:
            if i==0:
                i, end_data = _match(code_title, end_data, my_prof_dict, onet_prof, False, type_, i)
                if i==0 and nltk:
                    i, end_data = _match(code_title, end_data, my_prof_dict, onet_prof, nltk, type_, i)
                # pdb.set_trace()

    end_data = pd.DataFrame(end_data)

    return end_data


def accuracy(x):
    x = x.apply(len)
    x = 1 / x
    return x


def _fcode(x_list):
    result = []
    for x in x_list:
        x = x.split('-')[0]
        result.append(x)
    result = np.unique(np.array(result))
    if len(result)==1:
        return result[0]
    else:
        return None


def fcode(x):
    x = x.apply(_fcode)
    return x

