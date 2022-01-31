from numpy.core import numeric
from numpy.core.defchararray import isdigit
import pandas as pd
import numpy as np
import re
import os

def process_df(df):
    # calculate partial lifetime 
    df = df[
        ['Aki (s-1)', 'Lower Level Conf','Lower Level Term', 'Lower Level J',
'Upper Level Conf', 'Upper Level Term', 'Upper Level J', 'Ek', 'Ei']
    ]
    # print(df['Upper Level Term'])
    df_up_lv_sum = df.groupby(['Upper Level Conf', 'Upper Level Term', 'Upper Level J',
    'Lower Level Conf', 'Lower Level Term', 'Lower Level J'], as_index=False).sum()
    df_up_lv_mean = df.groupby(['Upper Level Conf', 'Upper Level Term', 'Upper Level J',
    'Lower Level Conf', 'Lower Level Term', 'Lower Level J'], as_index=False).mean()
    
    df_up_lv_sum = df_up_lv_sum.rename(columns={'Aki (s-1)':'partial_lifetime'})
    # print(df_up_lv_sum.iloc[:, :7])
    df_up_lv_sum['partial_lifetime'] = 1/df_up_lv_sum['partial_lifetime']
    

    df_up_lv = df_up_lv_sum[['Upper Level Conf', 'Upper Level Term', 'Upper Level J', 
    'Lower Level Conf', 'Lower Level Term', 'Lower Level J', 'partial_lifetime']]
    df_up_lv['Ek'] = df_up_lv_mean['Ek']
    df_up_lv['Ei'] = df_up_lv_mean['Ei']
    

    # print(df_up_lv)
    def calc(x):
        x['average_partial_lifetime'] = x['partial_lifetime'].mean()
        x['var_partial_lifetime'] = x['partial_lifetime'].var()

        x['average_Ek'] = x['Ek'].mean()
        x['var_Ek'] = x['Ek'].var()
        x['average_Ei'] = x['Ei'].mean()
        x['var_Ei'] = x['Ei'].var()
        
        x['count'] = len(x)

        
        return x
    
    pattern = re.compile('\(.*\)')
    df_up_lv['Upper Level Conf'] = df_up_lv['Upper Level Conf'].apply(lambda x: pattern.sub('', x))
    df_up_lv['Lower Level Conf'] = df_up_lv['Lower Level Conf'].apply(lambda x: pattern.sub('', x))
    df_up_lv = df_up_lv.drop(['Upper Level J', 'Lower Level J'], axis=1)

    # print(df_up_lv.iloc[:, :7])
    df_conf_term = df_up_lv.groupby(['Upper Level Conf', 'Upper Level Term', 'Lower Level Conf', 'Lower Level Term'], as_index=False).apply(calc).reset_index(drop=True)
    # print(df_conf_term)

    df_conf_term = df_conf_term.drop(['partial_lifetime', 'Ek', 'Ei'], axis=1)
    df_conf_term = df_conf_term.drop_duplicates(['Upper Level Conf', 'Upper Level Term', 'Lower Level Conf', 'Lower Level Term'])

    return df_conf_term

def write_df(df, atom, dir):
    # write data into csv files
    if not os.path.exists(dir):
        os.mkdir(dir)
    file_name = os.path.join(dir, atom+'_partial_lifetime'+'.csv')
    df.to_csv(file_name, index=False, float_format='%.4e')
    print('write data done!')



def solve(atoms_file, in_dir, out_dir):
    # function call
    atoms_df = pd.read_excel(atoms_file)
    atoms_list = atoms_df.iloc[:, 0].to_list()

    # atoms_list = ['Ac I']
    for i in range(len(atoms_list)):
        file_name = os.path.join(in_dir, atoms_list[i]+'_processed'+'.csv')
        print(atoms_list[i])
        if not os.path.exists(file_name):
            continue
        df = pd.read_csv(file_name)
        df = process_df(df)
        write_df(df, atoms_list[i], out_dir)

solve('neutral_atoms.xlsx', 'processed_neutral_data', 'partial_lifetime_neutral_data')
solve('singly_charged_ions.xlsx', 'processed_singly_charged_data', 'partial_lifetime_singly_charged_data')

