import os
import re
import numpy as np
import pandas as pd
from pattern.text.en import singularize


def _prepare(x):
    x = x.astype(str)
    x = x.str.lower()
    x = x.str.rstrip()
    x = x.astype(str)
    x = x.str.replace(r'[\,|,/,",",(,),I,$,&,@,#,*,]', '')
    x = x.str.replace(',', '')
    x = x.str.replace('.', '')
    x = x.str.replace(r'\s+', ' ')
    x = x.str.replace(r'\d+', '')
    x = x.drop_duplicates()
    x = x.dropna()
    return x


def enrichment(data, name, args):
    replace_words, remove_list = args
    data[f'{name}_enrichment'] = _prepare(data[name]).astype(str)
    for k, v in replace_words.items():
        data[f'{name}_enrichment'] = data[f'{name}_enrichment'].str.replace(k, v)
    data[f'{name}_list'] = data[f'{name}_enrichment'].apply(lambda x: str(x).split())
    data[f'{name}_list'] = data[f'{name}_list'].apply(lambda l: [x for x in l if x not in remove_list])
    data[f'{name}_list_singularize'] = data[f'{name}_list'].apply(lambda x_list: [singularize(str(x)) for x in x_list])
    return data


def main(job_zones, my_data, *args):
    job_zones = enrichment(job_zones, 'Title', args)
    my_data = enrichment(my_data, 'my_name', args)

    result = []

    for my_data_dict in my_data.to_dict('record'):
        my_name_list_singularize = my_data_dict['my_name_list_singularize']
        my_name = my_data_dict['my_name']

        title_list = []

        for job_zones_dict in job_zones.to_dict('record'):
            title_list_singularize = job_zones_dict['Title_list_singularize']
            title = job_zones_dict['Title']
            code = job_zones_dict['O*NET-SOC Code']

            new_list = list(set(my_name_list_singularize) & set(title_list_singularize))
            title_list.append((len(new_list), title, (title_list_singularize, code)))

        title_list_sort = sorted(title_list, reverse=True)
        max_elem = title_list_sort[0][0]

        if max_elem > 0:
            title_list = {}
            for (n, value, (title_list_singularize, code)) in title_list_sort:
                if n == max_elem:
                    title_list[value] = (title_list_singularize, code)
        else:
            title_list = {}


        if len(title_list) == 1:
            result.append({'my_name':my_name, 'title':list(title_list.keys())[0], 'lvl':0, 'code':code})

        if len(title_list) > 1:
            for key, (value, code) in title_list.items():
                new_ = set(my_name_list_singularize).symmetric_difference(set(value))
                if len(new_) == 1:
                    result.append({'my_name':my_name, 'title':key, 'lvl':1, 'code':code})
                    break

    return pd.DataFrame(result)


if __name__ == '__main__':
    path = ""

    replace_words = {
        'cfo': 'chief financial officer',
        'sme': 'busines analyst',
        'chef': 'chief',
        'sr': 'senior',
        'rd': 'research and development',
    }

    remove_list = ['in','and','the','of','or','ii']

    # Open datas:
    job_zones = pd.read_excel(path+'Job Zones.xlsx')[['O*NET-SOC Code', 'Title']]
    my_data = pd.read_csv(path+'my.txt', sep=';', header=None, index_col=None, names=["my_name"], engine='python', squeeze=True)
    my_data = pd.DataFrame(my_data)
    
    result = main(job_zones, my_data, replace_words, remove_list)

    print (result.head(20))
    print ('len', len(result))

    result.to_excel('first_version_130_validate.xlsx', index=None)






