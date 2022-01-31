from numpy.core import numeric
from numpy.core.defchararray import isdigit
import pandas as pd
import numpy as np
import re
import os

def process_df(df):
    # calculate total lifetime 
    df = df[
        ['Aki (s-1)', 'Lower Level Conf','Lower Level Term', 'Lower Level J',
'Upper Level Conf', 'Upper Level Term', 'Upper Level J', 'Ek', 'Ei']
    ]

    df_up_lv_sum = df.groupby(['Upper Level Conf', 'Upper Level Term', 'Upper Level J'], as_index=False).sum()
    df_up_lv_mean = df.groupby(['Upper Level Conf', 'Upper Level Term', 'Upper Level J'], as_index=False).mean()
    
    
    df_up_lv_sum = df_up_lv_sum.rename(columns={'Aki (s-1)':'value_k'})
    df_up_lv_sum['value_k'] = 1/df_up_lv_sum['value_k']

    df_up_lv = df_up_lv_sum[['Upper Level Conf', 'Upper Level Term', 'Upper Level J', 'value_k']]
    df_up_lv['Ek'] = df_up_lv_mean['Ek']
    # df_up_lv['Ei'] = df_up_lv_mean['Ei']

    # print(df_up_lv)
    def calc(x):
        # print(x)
        x['average_value_k'] = x['value_k'].mean()
        x['average_Ek'] = x['Ek'].mean()
        x['var_Ek'] = x['Ek'].var()
        x['var_value_k'] = x['value_k'].var()
        x['count'] = len(x)
        
        return x


    pattern = re.compile('\(.*\)')
    df_up_lv['Upper Level Conf'] = df_up_lv['Upper Level Conf'].apply(lambda x: pattern.sub('', x))
    # df_up_lv['Lower Level Conf'] = df_up_lv['Lower Level Conf'].apply(lambda x: pattern.sub('', x))
    df_up_lv = df_up_lv.drop('Upper Level J', axis=1)
    # print(df_up_lv)
    df_conf_term = df_up_lv.groupby(['Upper Level Conf', 'Upper Level Term'], as_index=False).apply(calc).reset_index(drop=True)
    df_conf_term = df_conf_term.drop(['value_k', 'Ek'], axis=1)
    df_conf_term = df_conf_term.drop_duplicates(['Upper Level Conf', 'Upper Level Term'])
    
    # print(df_conf_term)
    df_conf_term = df_conf_term.rename(columns={'average_value_k':'average_total_lifetime'})
    df_conf_term = df_conf_term.rename(columns={'var_value_k':'var_total_lifetime'})
    return df_conf_term

def write_df(df, atom, dir):
    # write data into csv files 
    if not os.path.exists(dir):
        os.mkdir(dir)
    file_name = os.path.join(dir, atom+'_total_lifetime'+'.csv')
    df.to_csv(file_name, index=False, float_format='%.4e')
    print('write data done!')


def solve(atoms_file, in_dir, out_dir):
    # function call
    atoms_df = pd.read_excel(atoms_file)
    atoms_list = atoms_df.iloc[:, 0].to_list()
    # atoms_list = ['Ag I']
    for i in range(len(atoms_list)):
        file_name = os.path.join(in_dir, atoms_list[i]+'_processed'+'.csv')
        print('---------------------')
        print(atoms_list[i])
        if not os.path.exists(file_name):
            continue
        df = pd.read_csv(file_name)
        df = process_df(df)
        write_df(df, atoms_list[i], out_dir)

solve('neutral_atoms.xlsx', 'processed_neutral_data', 'total_lifetime_neutral_data')
solve('singly_charged_ions.xlsx', 'processed_singly_charged_data', 'total_lifetime_singly_charged_data')

