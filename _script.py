import os
import re
import pdb
import numpy as np
import pandas as pd
from pattern.text.en import singularize


def prepare(x):
    x = x.astype(str)
    x = x.str.lower()
    x = x.str.rstrip()
    x = x.astype(str)
    x = x.str.replace(r'[\\,|,",",(,),$,@,#,*,]', '')
    x = x.str.replace(',', '')
    x = x.str.replace('.', '')
    x = x.str.replace('/', ' ')
    x = x.str.replace(r'\s+', ' ')
    return x


def _singularize(x_list):
    return set(singularize(str(x)) for x in x_list)


def replace_w(x, replace_words):
    for rw, rw_new in replace_words.items():
        if rw in x:
            x.remove(rw)
            if rw_new != '':
                x.append(rw_new)
    return x

def rm_number(x_list):
    new = []
    if isinstance(x_list, list):
        for x in x_list:
            try:
                x = int(x)
                if not isinstance(x, int):
                    new.append(x)
            except ValueError:
                new.append(x)
    return new



def _enrichment(x, words):
    x = x.astype(str)
    x = x.apply(lambda x: str(x).split())
    x = x.apply(rm_number)
    x = x.apply(lambda x: replace_w(x, words))
    x = x.apply(_singularize)
    return x


def enrichment(data, columns, replace_words):
    data['title'] = data['Title']

    data_ = pd.DataFrame({}, columns=['title'])

    for col in columns:
        df = data[['title', col]].drop_duplicates().dropna()
        df[col] = _enrichment(prepare(df[col]),replace_words)
        df = df.groupby(['title'])[col].apply(list).reset_index()
        data_ = data_.merge(df, on='title', how='outer')

    return data_


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


def search(df, my_name_list, accuracy):
    for df_set in df:
        if accuracy == 0:
            if len(my_name_list.symmetric_difference(df_set)) == 0:
                return 1
        elif accuracy == 1 or accuracy==2:
            if len(my_name_list-df_set) == 0:
                return 1
        elif accuracy == 3:
            if len(my_name_list-df_set) < 3 and len(my_name_list)>1:
                return 1
    return 0


def funstep(data, my_name_df, steps, result, i, accuracy):
    my_name = my_name_df['My_name']
    my_name_list = my_name_df['l_My_name']
    for df in data.to_dict('record'):
        for step, lvl in steps.items():
            if isinstance(df[step], list):
                # pdb.set_trace()
                i = search(df[step], my_name_list, accuracy)
                if i > 0:
                    result.append({
                        'lvl':lvl,
                        'my_name':my_name,
                        'accuracy':accuracy,
                        **df,
                        'my_name_list':my_name_list,
                    })
                    break
        if i > 0:
            break        

    return result, i


def main(my_data, files, steps, replace_words, output_columns):
    data = pd.DataFrame({}, columns=['title'])

    for i, (name, columns) in enumerate(files.items()):
        _data = pd.read_excel(name)[['Title', *columns]]
        if i==0:
            _data = enrichment(_data, ['Title', *columns], replace_words)
        else:
            _data = enrichment(_data, columns, replace_words)
        data = data.merge(_data, on='title', how='outer')
        del _data

    data = add_concat_col(data, steps)

    my_data = pd.DataFrame(my_data)
    my_data['l_My_name'] = _enrichment(prepare(my_data['My_name']), replace_words)

    result = []

    steps = {step:step for step in steps}

    for my_name_df in my_data.to_dict('record'):
        i = 0
# , steps, {'all': 'all'}, {'all': 'pool accuracy'}
        for accuracy, mysteps in enumerate([steps, ]):
            if i == 0:
                result, i = funstep(data, my_name_df, mysteps, result, i, accuracy)
                if i > 0:
                    break

        if i == 0:
            result.append({'my_name':my_name_df['My_name'], 'title':'None', 'lvl':'None'})
                        
    return pd.DataFrame(result)[output_columns]


if __name__ == '__main__':
    # Open datas:

    files = {
        # 'Alternate Titles.xlsx': ['Short Title', 'Alternate Title'],
        # 'Emerging Tasks.xlsx': ['Task'],
        # 'Occupation Data.xlsx': ['Description'],
        # 'Sample of Reported Titles.xlsx': ['Reported Job Title'],
        # 'Skills.xlsx': ['Element Name'],
        # 'Career Starters Matrix.xlsx': ['Related Title'],
    }

    replace_words = {
        'sr':'senior',
        'i': '',
        'ii': '',
        'iii': '',
        'iiii': '',
        'ownwer':'owner',
    }

    my_data = pd.read_csv('my.txt', sep=';', header=None, index_col=None, names=["My_name"], engine='python', squeeze=True)


    output_columns = ['my_name', 'title', 'accuracy', 'lvl', 'Short Title', 'Alternate Title', 'my_name_list']

    result = main(my_data, files, ['Title', *[c for cols in files.values() for c in cols]], replace_words, output_columns)

    l_my_data = len(my_data)
    l_result = len(result)

    assert l_my_data == l_result, f"count of inputs and outputs must be equal ({l_my_data}:{l_result})!"
    
    print(result.groupby(['lvl']).size())
    print(result.groupby(['lvl', 'accuracy']).size())

    result.to_excel('result.xlsx', index=None)
    
    

