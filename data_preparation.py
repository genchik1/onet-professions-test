import os
import re
import pdb
import numpy as np
import pandas as pd
from pattern.text.en import singularize
import settings as s

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet

stop_words = set(stopwords.words("english"))
stop_words.remove('it')
lemmatizer = WordNetLemmatizer()


def open_my_file(settings):
    data = pd.read_csv(settings['path'], **settings['read_parameters'])
    return pd.DataFrame(data)


def open_match_file(fs):
    data = pd.read_excel(fs['path'])
    data = data[fs['columns']]
    return data


def open_match_files(match_files=s.MATCH_FILES):
    datas = []
    for fs in match_files:
        df = open_match_file(fs)
        df = df.rename(columns=fs['rename'])
        datas.append((df, fs))
    return datas


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
    x = x.str.replace(' & ', '&')
    return x


def replace_w(x, replace_words):
    for rw, rw_new in replace_words.items():
        if rw in x:
            x.remove(rw)
            if rw_new != '':
                x.append(rw_new)
    return x


def _singularize(x_list):
    return set(singularize(str(x)) for x in x_list)


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


def enrichment(x, words=s.REPLACE_WORDS):
    x = x.astype(str)
    x = x.apply(lambda x: str(x).split())
    x = x.apply(rm_number)
    x = x.apply(lambda x: replace_w(x, words))
    x = x.apply(_singularize)
    return x


def lemmatize_and_drop_stopwords(x_list):
    x_list = [word for word in x_list if not word in stop_words]
    x_list = set(lemmatizer.lemmatize(x, pos=wordnet.VERB) for x in x_list)
    return x_list


def _lemmatize_and_drop_stopwords(x_lists):
    result = []
    for x_list in x_lists:
        x_list = lemmatize_and_drop_stopwords(x_list)
        result.append(x_list)
    return result


def enrichments(data, fs, nlt=True, replace_words=s.REPLACE_WORDS):
    data['title'] = data['Title']
    dataset = pd.DataFrame(data[['title', 'code']].drop_duplicates().dropna())

    for col in fs['to_find_matches']:
        df = data[['title', 'code', col]].drop_duplicates().dropna()
        df[col] = enrichment(prepare(df[col]), replace_words)
        df = df.groupby(['title', 'code'])[col].apply(list).reset_index()
        df[col] = df[col].apply(_lemmatize_and_drop_stopwords)
        dataset = dataset.merge(df, on=['title', 'code'], how='outer')
        del df
    del data
    return dataset



