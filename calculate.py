import os
import re
import pdb
import numpy as np
import pandas as pd
import settings as s
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet
from collections import defaultdict


def lemmatize_and_drop_stop_words(dataset, stop_words, lemmatizer):
    dataset = [word for word in dataset if not word in stop_words]
    dataset = set(lemmatizer.lemmatize(x, pos=wordnet.VERB) for x in dataset)
    return dataset


def _match(code_title, end_data, my_prof_dict, onet_prof, steps, nltk, nltk2, type_='symmetric_difference'):
    i = 0

    my_profession_set = my_prof_dict['my_professions_set']

    if nltk is not None:
        my_profession_set = lemmatize_and_drop_stop_words(my_profession_set, **nltk)
 
    for step in steps:
        result_codes = []
        result_titles = []
    
        for onet_prof_dict in onet_prof.to_dict('record'):
            code = onet_prof_dict['code']
            names_list = onet_prof_dict[step]

            for names in names_list:
                if nltk is not None:
                    names = lemmatize_and_drop_stop_words(names, **nltk)

                if type_=='symmetric_difference':
                    if len(my_profession_set.symmetric_difference(names)) == 0:
                        if step == 'Title':
                            end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code], 'nltk':nltk, 'type':type_})
                            i += 1
                            break
                        result_codes.append(code)
                        result_titles.append(onet_prof_dict['title'])
                elif type_ == 'diff':
                    if len(my_profession_set - names) == 0:
                        if step == 'Title':
                            end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code], 'nltk':nltk, 'type':type_})
                            i += 1
                            break
                        result_codes.append(code)
                        result_titles.append(onet_prof_dict['title'])

            if i > 0:
                break

        if len(result_codes)>0 and i == 0:
            result_codes = list(np.unique(np.array(result_codes)))
            if len(result_codes)==1:
                end_data.append({**my_prof_dict, 'title':code_title[result_codes[0]], 'lvl':step, 'codes':result_codes, 'nltk':nltk, 'type':type_})
                i+=1
            elif len(result_codes)>1:
                if nltk2:
                    if nltk is not None and type_ == 'diff':
                        end_data.append({**my_prof_dict, 'title':'undefined', 'lvl':step, 'codes':result_codes, 'nltk':nltk, 'type':type_})
                        break
                else:
                    end_data.append({**my_prof_dict, 'title':'undefined', 'lvl':step, 'codes':result_codes, 'nltk':nltk, 'type':type_})
                    break

        if i > 0:
            break
    
    # pdb.set_trace()
    return i, end_data


def match(my_prof, onet_prof, steps=s.STEPS, nltk=True):

    code_title = onet_prof[['code', 'title']].drop_duplicates().dropna()
    code_title = pd.Series(code_title['title'].tolist(), index=code_title['code'])
    code_title = code_title.to_dict()


    nltk_settings = {
        'stop_words': set(stopwords.words("english")),
        'lemmatizer': WordNetLemmatizer(),
    }

    end_data = []

    for my_prof_dict in my_prof.to_dict('record'):
        i = 0
        for type_ in ['symmetric_difference']:
            if i == 0:
                i, end_data = _match(code_title, end_data, my_prof_dict, onet_prof, steps, None, nltk, type_)
                if nltk and i == 0:
                    i, end_data = _match(code_title, end_data, my_prof_dict, onet_prof, steps, nltk_settings, nltk, type_)
            
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

