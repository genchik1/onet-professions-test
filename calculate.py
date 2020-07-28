import os
import re
import pdb
import numpy as np
import pandas as pd
import settings as s


def _match(code_title, end_data, my_prof_dict, onet_prof, type_, i):

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
                        if step == 'Title':
                            end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code], 'coefficient':coefficient, 'dl':False})
                            i += 1
                            break
                        result_codes.append(code)
                        result_titles.append(onet_prof_dict['title'])

                elif type_ == 'difference':
                    if len(my_profession_set-names) == 0:
                        if step == 'Title':
                            end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code], 'coefficient':coefficient, 'dl':False})
                            i += 1
                            break
                        result_codes.append(code)
                        result_titles.append(onet_prof_dict['title'])

            if i > 0:
                break

        if len(result_codes)>0 and i == 0:
            result_codes = list(np.unique(np.array(result_codes)))
            if len(result_codes)==1:
                end_data.append({**my_prof_dict, 'title':code_title[result_codes[0]], 'lvl':step, 'codes':result_codes, 'coefficient':coefficient, 'dl':False})
                i+=1
                break

            elif len(result_codes)>1:
                end_data.append({**my_prof_dict, 'title':'undefined', 'lvl':step, 'codes':result_codes, 'coefficient':coefficient, 'dl':False})
                i+=1
                break

        if i > 0:
            break
    
    return i, end_data


def match(my_prof, onet_prof):
    end_data = []

    code_title = onet_prof[['code', 'title']].drop_duplicates().dropna()
    code_title = pd.Series(code_title['title'].tolist(), index=code_title['code'])
    code_title = code_title.to_dict()

    for my_prof_dict in my_prof.to_dict('record'):
        i = 0
        for type_ in s.COMPARISON_OF_WORDS:
            if i==0:
                i, end_data = _match(code_title, end_data, my_prof_dict, onet_prof, type_, i)
        if i == 0:
            end_data.append({**my_prof_dict, 'title':'NONE', 'lvl':'NONE', 'codes':'NONE', 'coefficient':0})

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