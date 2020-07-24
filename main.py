import pandas as pd
import data_preparation as dp


# Open datasets:
onet_prof = dp.open_match_files()           # onet_prof = [(data, parameters), ...]
my_prof = dp.open_my_professions_file()


# Data preparations:
my_prof['my_professions'] = dp.prepare(my_prof['my_professions'])
my_prof['my_professions_set'] = dp.enrichment(my_prof['my_professions'])
print (my_prof.head())


for (data, parameters) in onet_prof:
    for col in parameters['to_find_matches']:
        data[col] = dp.prepare(data[col])


# Enrichment:
onet_prof_all = pd.DataFrame({}, columns=['title', 'code'])
for (data, parameters) in onet_prof:
    data = dp.enrichments(data, parameters)
    onet_prof_all = onet_prof_all.merge(data, on=['title', 'code'], how='outer')
    del data
del onet_prof

print (onet_prof_all.head())


# Calculate:












