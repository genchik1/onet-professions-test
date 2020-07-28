import re
import pandas as pd
import settings as s
import calculate as c
import data_preparation as dp


def re_list(x):
    if len(x)>0:
        return x[0]
    else:
        return ''


# Open datasets:
onet_prof = dp.open_match_files()           # onet_prof = [(data, parameters), ...]
my_prof = dp.open_my_file(s.MY_PROFESSIONS_FILE)


# Data preparations:
my_prof['my_professions'] = dp.prepare(my_prof['my_professions'])
my_prof['my_professions_set'] = dp.enrichment(my_prof['my_professions'])

my_prof['my_professions_set'] = my_prof['my_professions_set'].apply(dp.lemmatize_and_drop_stopwords)


for (data, parameters) in onet_prof:
    for col in parameters['to_find_matches']:
        data[col] = data[col].apply(lambda x: re.sub(r'\((.*?)\)', '', str(x)))
        data[col] = dp.prepare(data[col])


# Enrichment:
onet_prof_all = pd.DataFrame({}, columns=['title', 'code'])
for (data, parameters) in onet_prof:
    data = dp.enrichments(data, parameters)
    onet_prof_all = onet_prof_all.merge(data, on=['title', 'code'], how='outer')
    del data
del onet_prof


# Calculate:
data = c.match(my_prof, onet_prof_all)

data['accuracy'] = c.accuracy(data['codes'])


# find a family of professions
if s.ADD_SOC_FAMILY:
    fd = dp.open_my_file(s.FAMILY)
    data['fcode'] = c.fcode(data['codes'])
    data = data.merge(fd, on='fcode', how='left')
    data['family'] = data['family'].fillna('undefined')


# Save settings:
ld = len(data)

with pd.ExcelWriter(s.OUTPUT_FILE['path'], engine='xlsxwriter') as writer:
    data.to_excel(writer, **s.OUTPUT_FILE['parameters'], sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column('A:A', 24)
    worksheet.set_column('B:B', 24)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:D', 10)
    worksheet.set_column('E:E', 30)
    worksheet.set_column('F:F', 40)
    worksheet.conditional_format(f'D{0}:D{ld+1}', {'type': 'data_bar'})


print (data.groupby(['lvl']).size())