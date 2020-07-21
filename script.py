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
    x = x.str.replace(r'[\\,|,/,",",(,),$,&,@,#,*,]', '')
    x = x.str.replace(',', '')
    x = x.str.replace('.', '')
    x = x.str.replace(r'\s+', ' ')
    x = x.str.replace(r'\d+', '')
    x = x.dropna()
    return x


def enrichment(data, name, args):
    replace_words, remove_list = args
    data[f'{name}_enrichment'] = _prepare(data[name]).astype(str)
    try:
        data = data.drop_duplicates()
    except:
        print ('error')
    for k, v in replace_words.items():
        data[f'{name}_enrichment'] = data[f'{name}_enrichment'].str.replace(k, v)
    data[f'{name}_list'] = data[f'{name}_enrichment'].apply(lambda x: str(x).split())
    data[f'{name}_list'] = data[f'{name}_list'].apply(lambda l: [x for x in l if x not in remove_list])
    data[f'{name}_list_singularize'] = data[f'{name}_list'].apply(lambda x_list: [singularize(str(x)) for x in x_list])
    return data


def main(skills, job_zones, my_data, skills_col='skills', job_zones_col='Title', my_data_col='my_name', *args):
    job_zones = enrichment(job_zones, job_zones_col, args)
    skills = enrichment(skills, skills_col, args)
    skills = enrichment(skills, 'Title', args)
    my_data = enrichment(my_data, my_data_col, args)
    result = []

    for my_data_dict in my_data.to_dict('record'):
        my_name_list_singularize = my_data_dict['my_name_list_singularize']
        my_name = my_data_dict[my_data_col]
        my_name_enrichment = my_data_dict[my_data_col+'_enrichment']

        title_list = {}


        x_y = 100
        y_x = 100

        N = 0

        skills['index'] = range(len(skills))

        i = 0

        for n, skills_dict in enumerate(skills.to_dict('record')):
            title_list_singularize = skills_dict[f'Title_list_singularize']
            skills_list_singularize = skills_dict[f'skills_list_singularize']
            title = skills_dict['Title']
            code = skills_dict['O*NET-SOC Code']

            if len(set(my_name_list_singularize).symmetric_difference(set(title_list_singularize))) == 0:
                result.append({'my_name':my_name, 'title':title, 'lvl':0, 'code':code})
                i+=1
                break
            
            if i == 0:
                x_y_list = set(my_name_list_singularize) - set(skills_list_singularize)
                y_x_list = set(skills_list_singularize) - set(my_name_list_singularize)

                x_y_ = len(x_y_list)
                y_x_ = len(y_x_list)

                if x_y_ > 0:
                    if x_y > x_y_:
                        x_y = x_y_
                        if y_x > y_x_:
                            y_x = y_x_
                            N = n

        if x_y != 100:
            df = skills[skills['index']==N].to_dict('record')[0]
            result.append({'my_name':my_name, 'title':df['Title'], 'lvl':1, 'code':df['O*NET-SOC Code']})

        # min_ = min(list(title_list.keys()))



        #         # i+=1
        #         # break

        # if i == 0:
        #     for skills_dict in skills.to_dict('record'):
        #         title_list_singularize = skills_dict[f'{skills_col}_list_singularize']
        #         title = skills_dict['Title']
        #         code = skills_dict['O*NET-SOC Code']

        #         new_list = set(my_name_list_singularize) - set(title_list_singularize)
        #         if len(new_list) == 1:
        #             result.append({'my_name':my_name, 'title':title, 'lvl':2, 'code':code})
        #             i+=1
        #             break

        # if i == 0:
        #     for skills_dict in skills.to_dict('record'):
        #         title_list_singularize = skills_dict[f'{skills_col}_list_singularize']
        #         title = skills_dict['Title']
        #         code = skills_dict['O*NET-SOC Code']

        #         new_list = set(my_name_list_singularize) - set(title_list_singularize)
        #         if len(new_list) == 1:
        #             result.append({'my_name':my_name, 'title':title, 'lvl':2, 'code':code})
        #             i+=1
        #             break

        # for job_zones_dict in job_zones.to_dict('record'):
        #     title_list_singularize = job_zones_dict[f'{job_zones_col}_list_singularize']
        #     title = job_zones_dict[job_zones_col]
        #     code = job_zones_dict['O*NET-SOC Code']

        #     new_list = list(set(my_name_list_singularize) & set(title_list_singularize))
        #     title_list.append((len(new_list), title, (title_list_singularize, code)))

        # title_list_sort = sorted(title_list, reverse=True)
        # max_elem = title_list_sort[0][0]

        # if max_elem > 0:
        #     title_list = {}
        #     for (n, value, (title_list_singularize, code)) in title_list_sort:
        #         if n == max_elem:
        #             title_list[value] = (title_list_singularize, code)
        # else:
        #     title_list = {}


        # if len(title_list) == 1:
        #     result.append({'my_name':my_name, 'title':list(title_list.keys())[0], 'lvl':0, 'code':code})

        # elif len(title_list) > 1 and len(title_list) <= 2:
        #     for key, (value, code) in title_list.items():
        #         new_ = set(my_name_list_singularize).symmetric_difference(set(value))
        #         if len(new_) == 1:
        #             result.append({'my_name':my_name, 'title':key, 'lvl':1, 'code':code})
        #             break

        # else:
            # title_list = []
            # for skills_dict in skills.to_dict('record'):
            #     title_list_singularize = skills_dict[f'{skills_col}_list_singularize']
            #     title = skills_dict['Title']
            #     code = skills_dict['O*NET-SOC Code']

            #     new_list = set(my_name_list_singularize) - set(title_list_singularize)
            #     if len(new_list) == 0:
            #         result.append({'my_name':my_name, 'title':title, 'lvl':2, 'code':code})
            #         break

            # title_list_sort = sorted(title_list, reverse=True)
            # max_elem = title_list_sort[0][0]

            # if max_elem > 0:
            #     title_list = {}
            #     for (n, value, (title_list_singularize, code)) in title_list_sort:
            #         if n == max_elem:
            #             title_list[value] = (title_list_singularize, code)
            # else:
            #     title_list = {}



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
    skills = pd.read_excel(path+'Skills.xlsx')[['O*NET-SOC Code', 'Element Name', 'Title']]
    skills['skills'] = skills['Title'] + ' ' + skills['Element Name']
    my_data = pd.read_csv(path+'my.txt', sep=';', header=None, index_col=None, names=["my_name"], engine='python', squeeze=True)
    my_data = pd.DataFrame(my_data)
    
    result = main(skills, job_zones, my_data, 'skills', 'Title', 'my_name', replace_words, remove_list)

    # print (result.head(20))
    print ('len', len(result))

    result.to_excel('two_version.xlsx', index=None)






