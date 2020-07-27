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


def damerau_levenshtein_distance(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1,lenstr1+1):
        d[(i,-1)] = i+1
    for j in range(-1,lenstr2+1):
        d[(-1,j)] = j+1
 
    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i,j)] = min(
                           d[(i-1,j)] + 1, # deletion
                           d[(i,j-1)] + 1, # insertion
                           d[(i-1,j-1)] + cost, # substitution
                          )
            if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
                d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost) # transposition
 
    return d[lenstr1-1,lenstr2-1]


def _match(code_title, end_data, my_prof_dict, onet_prof, nltk, type_, i):

    if nltk:
        my_profession_set = my_prof_dict['my_professions_set nltk']
    else:
        my_profession_set = my_prof_dict['my_professions_set']

    if type_ == 'symmetric_difference':
        coefficient = 1
    elif type_ == 'symmetric_diff':
        coefficient = 0.75
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
                            end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code], 'nltk':nltk, 'coefficient':coefficient, 'dl':False})
                            i += 1
                            break
                        result_codes.append(code)
                        result_titles.append(onet_prof_dict['title'])
                elif type_ == 'symmetric_diff':
                    if len(my_profession_set-names) == 1 and len(names-my_profession_set) == 1:
                        sd = list(my_profession_set.symmetric_difference(names))
                        sd = damerau_levenshtein_distance(sd[0], sd[1])
                        if sd==1:
                            # pdb.set_trace()
                            if step == 'Title' or  step == 'Title nltk':
                                end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code], 'nltk':nltk, 'coefficient':coefficient, 'dl':True})
                                i += 1
                                break
                            result_codes.append(code)
                            result_titles.append(onet_prof_dict['title'])
                elif type_ == 'difference':
                    if len(my_profession_set-names) == 0:
                        if step == 'Title' or  step == 'Title nltk':
                            end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code], 'nltk':nltk, 'coefficient':coefficient, 'dl':False})
                            i += 1
                            break
                        result_codes.append(code)
                        result_titles.append(onet_prof_dict['title'])

            if i > 0:
                break

        if len(result_codes)>0 and i == 0:
            result_codes = list(np.unique(np.array(result_codes)))
            if len(result_codes)==1:
                end_data.append({**my_prof_dict, 'title':code_title[result_codes[0]], 'lvl':step, 'codes':result_codes, 'nltk':nltk, 'coefficient':coefficient, 'dl':False})
                i+=1
                break

            elif len(result_codes)>1:
                if nltk:
                    end_data.append({**my_prof_dict, 'title':'undefined', 'lvl':step, 'codes':result_codes, 'nltk':nltk, 'coefficient':coefficient, 'dl':False})
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
        for type_ in s.COMPARISON_OF_WORDS:
            if i==0:
                i, end_data = _match(code_title, end_data, my_prof_dict, onet_prof, False, type_, i)
                if i==0 and nltk:
                    i, end_data = _match(code_title, end_data, my_prof_dict, onet_prof, nltk, type_, i)
                # pdb.set_trace()
        if i == 0:
            end_data.append({**my_prof_dict, 'title':'NONE', 'lvl':'NONE', 'codes':'NONE', 'nltk':'NONE', 'coefficient':0})

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

