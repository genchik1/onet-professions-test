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


def _match(code_title, end_data, i, my_prof_dict, my_profession_set, onet_prof, steps, nltk, nltk2):
    if nltk:
        stop_words = set(stopwords.words("english"))
        lemmatizer = WordNetLemmatizer()
        my_profession_set = [word for word in my_profession_set if not word in stop_words]
        my_profession_set = set(lemmatizer.lemmatize(x, pos=wordnet.VERB) for x in my_profession_set)
 
    for step in steps:
        result_codes = []
        result_titles = []

        for onet_prof_dict in onet_prof.to_dict('record'):
            code = onet_prof_dict['code']
            names_list = onet_prof_dict[step]

            for names in names_list:
                if nltk:
                    names = [word for word in names if not word in stop_words]
                    names = set(lemmatizer.lemmatize(x, pos=wordnet.VERB) for x in names)

                if len(my_profession_set.symmetric_difference(names)) == 0:
                    if step == 'Title':
                        end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code], 'nltk':nltk})
                        i += 1
                        break
                    result_codes.append(code)
                    result_titles.append(onet_prof_dict['title'])

            if i > 0:
                break

        if len(result_codes)>0 and i == 0:
            result_codes = list(np.unique(np.array(result_codes)))
            if len(result_codes)==1:
                end_data.append({**my_prof_dict, 'title':code_title[result_codes[0]], 'lvl':step, 'codes':result_codes, 'nltk':nltk})
                i+=1
            elif len(result_codes)>1:
                if nltk2:
                    if nltk:
                        end_data.append({**my_prof_dict, 'title':'undefined', 'lvl':step, 'codes':result_codes, 'nltk':nltk})
                        break
                else:
                    end_data.append({**my_prof_dict, 'title':'undefined', 'lvl':step, 'codes':result_codes, 'nltk':nltk})
                    break

        if i > 0:
            break
    
    # pdb.set_trace()
    return i, end_data


def match(my_prof, onet_prof, steps=s.STEPS, nltk=True):
    end_data = []

    from collections import defaultdict

    code_title = onet_prof[['code', 'title']].drop_duplicates().dropna()
    # code_title = code_title.set_index('code')
    code_title = pd.Series(code_title['title'].tolist(), index=code_title['code'])
    print (code_title)
    code_title = code_title.to_dict()

    print (code_title['11-1011.00'])

    for my_prof_dict in my_prof.to_dict('record'):
        my_profession_set = my_prof_dict['my_professions_set']

        i, end_data = _match(code_title, end_data, 0, my_prof_dict, my_profession_set, onet_prof, steps, False, nltk)

        if i == 0 and nltk:
            i, end_data = _match(code_title, end_data, i, my_prof_dict, my_profession_set, onet_prof, steps, True, nltk)
            
    return pd.DataFrame(end_data)


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







