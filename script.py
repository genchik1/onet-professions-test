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
    x = x.str.replace(r'[\\,|,/,",",(,),$,&,@,#,*,]', '')
    x = x.str.replace(',', '')
    x = x.str.replace('.', '')
    x = x.str.replace(r'\s+', ' ')
    return x


def _singularize(x_str):
    return set(singularize(str(x)) for x in str(x_str).split())


def _enrichment(x):
    x = x.astype(str)
    x = x.apply(_singularize)
    return x


def enrichment(data, columns):
    data['title'] = data['Title']

    data_ = pd.DataFrame({}, columns=['title'])

    for col in columns:
        df = data[['title', col]].drop_duplicates().dropna()
        df[col] = _enrichment(prepare(df[col]))
        df = df.groupby(['title'])[col].apply(list).reset_index()
        data_ = data_.merge(df, on='title', how='outer')

    return data_


def search(df, my_name_list, accuracy):
    for df_set in df:
        if accuracy == 0:
            if len(my_name_list.symmetric_difference(df_set)) == 0:
                return 1
        elif accuracy == 1:
            if len(my_name_list-df_set) == 0:
                return 1
        elif accuracy == 2:
            if len(my_name_list-df_set) == 1 and len(my_name_list)>1:
                return 1
    return 0


def _add_concat_col(data_dict):
    result = []
    for col in data_dict:
        if isinstance(col, list):
            for co in col:
                if isinstance(co, set):
                    for c in co:
                        result.append(c)
    return [set(np.unique(np.array(result)))]


def add_concat_col(data, steps):
    data['all'] = data[steps].apply(_add_concat_col, axis=1)
    return data


def step(data, my_name_df, steps, result, i, accuracy):
    my_name = my_name_df['My_name']
    my_name_list = my_name_df['l_My_name']
    for df in data.to_dict('record'):
        title = df['title']
        for step, lvl in steps.items():
            if isinstance(df[step], list):
                i = search(df[step], my_name_list, accuracy)
                if i > 0:
                    result.append({'my_name':my_name, 'title':title, 'lvl':lvl})
                    break
        if i > 0:
            break

    return result, i


def main(my_data, data, steps):
    my_data = pd.DataFrame(my_data)
    my_data['l_My_name'] = _enrichment(prepare(my_data['My_name']))

    data = enrichment(data, steps)
    data = add_concat_col(data, steps)

    result = []

    steps = {step:step for step in steps}

    for my_name_df in my_data.to_dict('record'):
        i = 0

        for accuracy, steps_ in enumerate([steps, {'all': 'all'}, {'all': 'pool accuracy'}]):
            if i == 0:
                result, i = step(data, my_name_df, steps_, result, i, accuracy)

        if i == 0:
            result.append({'my_name':my_name_df['My_name'], 'title':'None', 'lvl':'None'})
                        
    return pd.DataFrame(result)


if __name__ == '__main__':
    # Open datas:
    alternatet_titles = pd.read_excel('Alternate Titles.xlsx')[['Title', 'Alternate Title', 'Short Title']]
    my_data = pd.read_csv('my.txt', sep=';', header=None, index_col=None, names=["My_name"], engine='python', squeeze=True)

    result = main(my_data, alternatet_titles, ['Title', 'Short Title', 'Alternate Title'])

    l_my_data = len(my_data)
    l_result = len(result)

    assert l_my_data == l_result, f"count of inputs and outputs must be equal ({l_my_data}:{l_result})!"
    
    result.to_excel('result.xlsx', index=None)

    print(result.groupby(['lvl']).size())
