from math import fabs
from numpy.core import numeric
from numpy.core.defchararray import isdigit
import pandas as pd
import numpy as np
import re
import os

def process_df(df_up, df_up_low):
    # adjust the partial lifetime

    # sort values and retain the top-5
    df_up_low = df_up_low.sort_values(['Upper Level Conf', 'Upper Level Term', 'average_partial_lifetime']).reset_index(drop=True)
    df_grp_up = df_up_low.groupby(['Upper Level Conf', 'Upper Level Term'], as_index=False).head(5)

    def calc(x):
        up_conf, up_term = x.iloc[0]['Upper Level Conf'], x.iloc[0]['Upper Level Term']
        tau_i = 1/((1/x['average_partial_lifetime']).sum())
        inv_tau_i = 1/tau_i
        T_i = df_up[(df_up['Upper Level Conf'] == up_conf) & (df_up['Upper Level Term'] == up_term)]['average_total_lifetime'].values[0]
        R_i = T_i / tau_i
        inv_T_i = 1/T_i

        Xif = x['average_partial_lifetime'] * R_i
        

        new_tau_i = 1/((1/Xif).sum())
        # assert T_i - new_tau_i<1e-5
        
        assert T_i - new_tau_i<1e-5
        # if not T_i - new_tau_i<1e-5:
        #     print(T_i)
        #     print(new_tau_i)
        #     print(T_i <= new_tau_i)
        #     print(x.iloc[:, :6])
        #     print('============')
        

        x['re_partial_lifetime'] = Xif
        x['difference'] = x['average_partial_lifetime'] - x['re_partial_lifetime']
        
        return x

    df_grp_up = df_grp_up.groupby(['Upper Level Conf', 'Upper Level Term'], as_index=False).apply(calc).reset_index(drop=True)
    ret_df = df_grp_up[['Upper Level Conf', 'Upper Level Term', 'Lower Level Conf','Lower Level Term', 'average_partial_lifetime',
            're_partial_lifetime', 'difference']]
    return ret_df


    
def write_df(df, atom, dir):
    # write data into csv file
    if not os.path.exists(dir):
        os.mkdir(dir)
    file_name = os.path.join(dir, atom+'_re_partial_lifetime'+'.csv')
    df.to_csv(file_name, index=False, float_format='%.4e')
    print('write data done!')



def solve(atoms_file, in_dir1, in_dir2, out_dir):
    # function call
    atoms_df = pd.read_excel(atoms_file)
    atoms_list = atoms_df.iloc[:, 0].to_list()
    # atoms_list = ['Ac I']
    
    for i in range(len(atoms_list)):
        file_name = os.path.join(in_dir1, atoms_list[i]+'_total_lifetime'+'.csv')
        file_name2 = os.path.join(in_dir2, atoms_list[i]+'_partial_lifetime'+'.csv')
        print(atoms_list[i])
        if not os.path.exists(file_name):
            continue
        df_up = pd.read_csv(file_name)
        df_up_low = pd.read_csv(file_name2)
        df = process_df(df_up, df_up_low)
        write_df(df, atoms_list[i], out_dir)


solve('neutral_atoms.xlsx', 'total_lifetime_neutral_data', 'partial_lifetime_neutral_data', 're_partial_lifetime_neutral_data')
solve('singly_charged_ions.xlsx', 'total_lifetime_singly_charged_data', 'partial_lifetime_singly_charged_data', 're_partial_lifetime_singly_charged_data')

