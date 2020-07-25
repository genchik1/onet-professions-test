import os
import re
import pdb
import numpy as np
import pandas as pd
import settings as s
import pdb


def match(my_prof, onet_prof, steps=s.STEPS):
    end_data = []
    for my_prof_dict in my_prof.to_dict('record'):
        my_profession_set = my_prof_dict['my_professions_set']

        i = 0

        # pdb.set_trace()
        
        for step in steps:
            result_codes = []
            result_titles = []
    
            for onet_prof_dict in onet_prof.to_dict('record'):
                code = onet_prof_dict['code']
                names_list = onet_prof_dict[step]

                for names in names_list:
                    if len(my_profession_set.symmetric_difference(names)) == 0:
                        if step == 'Title':
                            end_data.append({**my_prof_dict, 'title':onet_prof_dict['title'], 'lvl':step, 'codes':[code]})
                            i += 1
                            break
                        result_codes.append(code)
                        result_titles.append(onet_prof_dict['title'])

                if i > 0:
                    break
    
            if len(result_codes)>0 and i == 0:
                result_codes = list(np.unique(np.array(result_codes)))
                if len(result_codes)>1:
                    end_data.append({**my_prof_dict, 'title':'undefined', 'lvl':step, 'codes':result_codes})
                else:
                    end_data.append({**my_prof_dict, 'title':result_titles[0], 'lvl':step, 'codes':result_codes})

                break

            elif i > 0:
                break


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







