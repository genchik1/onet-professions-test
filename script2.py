import os
import re
import numpy as np
import pandas as pd
from pattern.text.en import singularize


def prepare(x):
    x = x.astype(str)
    x = x.str.lower()
    x = x.str.rstrip()
    x = x.astype(str)
    x = x.str.replace(r'\s+', ' ')
    return x


def enrichment(x):
    x = x.astype(str)
    x = x.apply(lambda x: str(x).split())
    x = x.apply(lambda x_list: [singularize(str(x)) for x in x_list])
    return x


def main(my_data, *args):
    my_data = pd.DataFrame(my_data)
    my_data['_list_My_name'] = enrichment(prepare(my_data['My_name']))


    for (data, columns) in args:
        for col in columns:
            new_col_list = '_list_'+col
            data[new_col_list] = enrichment(prepare(data[col]))


    result = []


    for my_name_df in my_data.to_dict('record'):
        my_name = my_name_df['My_name']
        my_name_list = my_name_df['_list_My_name']

        i = 0

        for (dataset, columns) in args:
            for col in columns:
                data = dataset[['Title', '_list_'+col]]
                for df in data.to_dict('record'):
                    title = df['Title']
                    x_col_list = df['_list_'+col]
                    if len(set(my_name_list).symmetric_difference(set(x_col_list))) == 0:
                        result.append({'my_name':my_name, 'title':title, 'lvl':col})
                        i+=1
                        break
                if i > 0:
                    break
            if i > 0:
                break

    return pd.DataFrame(result)


if __name__ == '__main__':
    # Open datas:
    alternatet_titles = pd.read_excel('Alternate Titles.xlsx')[['Title', 'Alternate Title', 'Short Title']]
    skills = pd.read_excel('Skills.xlsx')[['Element Name', 'Title']]
    my_data = pd.read_csv('my.txt', sep=';', header=None, index_col=None, names=["My_name"], engine='python', squeeze=True)

    result = main(my_data, (alternatet_titles, ['Title', 'Short Title', 'Alternate Title']), (skills, ['Element Name']))

    print ('len', len(result))

    result.to_excel('tree_version.xlsx', index=None)






