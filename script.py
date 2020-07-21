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


def enrichment(x):
    x = x.astype(str)
    x = x.apply(lambda x: str(x).split())
    x = x.apply(lambda x_list: list(singularize(str(x)) for x in x_list))
    return x


def main(my_data, *args):
    my_data = pd.DataFrame(my_data)
    my_data['_list_My_name'] = enrichment(prepare(my_data['My_name']))

    my_columns = []

    for (data, columns) in args:
        for col in columns:
            new_col_list = '_list_'+col
            data[new_col_list] = enrichment(prepare(data[col]))
        my_columns.extend(columns)


    result = []


    dataset = pd.DataFrame({}, columns=['Title'])

    for (data, columns) in args:
        _all_data = pd.DataFrame({}, columns=['Title'])
        for col in columns:
            if col != 'Title':
                new_col_list = '_list_'+col
                df = data[['Title', new_col_list]]
                df[new_col_list] = df[new_col_list].apply(tuple)
                df = df.drop_duplicates().dropna()
                df[new_col_list] = df[new_col_list].apply(list)
                df = df.groupby(['Title'])[new_col_list].apply(list).reset_index()
                df[new_col_list] = df[new_col_list].apply(lambda x_list: ' '.join([y for x in x_list for y in x]))
                print (df.head())
                _all_data = _all_data.merge(df, on='Title', how='outer')
                del df

        del data

        _all_data['all'] = ''
        for col in _all_data.columns:
            if col != 'Title' and col != 'all':
                _all_data['all'] = _all_data['all'] + ' ' + _all_data[col]

        dataset = dataset.merge(_all_data, on='Title', how='outer')
        del _all_data

    dataset['all'] = ''
    for col in [col for col in dataset.columns if col.startswith('all')]:
        if col != 'all':
            dataset['all'] = dataset['all'] + ' ' + dataset[col]
            del dataset[col]

    dataset['_list_all'] = dataset['all'].str.split()
    del dataset['all']

    print (dataset.head())

    args = list(args)
    
    args.append((dataset[['Title', '_list_all']], ['all']))

    print (args)

    for my_name_df in my_data.to_dict('record'):
        my_name = my_name_df['My_name']
        my_name_list = my_name_df['_list_My_name']

        i = 0
        for (dataset, columns) in args:
            for col in columns:
                if col != 'all':
                    data = dataset[['Title', '_list_'+col]]
                    data['_list_'+col] = data['_list_'+col].apply(tuple)
                    data = data.drop_duplicates().dropna()
                    data['_list_'+col] = data['_list_'+col].apply(list)
                    for df in data.to_dict('record'):
                        title = df['Title']
                        x_col_list = df['_list_'+col]
                        if len(set(my_name_list).symmetric_difference(set(x_col_list))) == 0:
                            result.append({'my_name':my_name, 'title':title, 'lvl':col})
                            i+=1
                            break
                    if i > 0:
                        break
                else:
                    if i == 0:
                        data = dataset[['Title', '_list_'+col]]
                        for df in data.to_dict('record'):
                            title = df['Title']
                            x_col_list = df['_list_'+col]
                            if isinstance(x_col_list, list):
                                if len(set(my_name_list)-set(x_col_list)) == 0:
                                    result.append({'my_name':my_name, 'title':title, 'lvl':col})
                                    i+=1
                                    break

    return pd.DataFrame(result)


if __name__ == '__main__':
    # Open datas:
    alternatet_titles = pd.read_excel('Alternate Titles.xlsx')[['Title', 'Alternate Title', 'Short Title']]
    skills = pd.read_excel('Skills.xlsx')[['Element Name', 'Title']]
    my_data = pd.read_csv('my.txt', sep=';', header=None, index_col=None, names=["My_name"], engine='python', squeeze=True)

    result = main(my_data, (alternatet_titles, ['Title', 'Short Title', 'Alternate Title']), (skills, ['Element Name']))

    print ('len', len(result))

    result.to_excel('for_version.xlsx', index=None)






