from numpy.core import numeric
from numpy.core.defchararray import isdigit
import pandas as pd
import numpy as np
import re
import os
def process_df(df, stat):
    # pre-processed data to prepare for later calculation

    if 'Upper Level  Conf., Term, J' not in df.columns or df['Upper Level  Conf., Term, J'].isna().all():
        return None
    if 'Aki (s-1)' not in df.columns or df['Aki (s-1)'].isna().all():
        return None
    df = df.loc[:, ~df.columns.str.contains('Unnamed')]
    
    # delete the data if 'Upper Level  Conf., Term, J' is empty
    if 'Upper Level  Conf., Term, J' in df.columns:
        df = df[~(df['Upper Level  Conf., Term, J'].isna())]
        df['Upper Level  Conf., Term, J'] = df['Upper Level  Conf., Term, J'].astype(str)

    mask = (df['Ritz  Wavelength  Vac (nm)']=='')


    # rename and distinguish the two 'Unc.  (nm)'
    if 'Unc.  (nm)' in df.columns and  'Unc.  (nm).1' in df.columns:
        df['Unc.(nm)O']=df['Unc.  (nm)']
        df['Unc.(nm)R']=df['Unc.  (nm).1']
        df[mask]['Unc.(nm)R'] = df[mask]['Unc.(nm)O']
        df_uncr = df['Unc.(nm)R']
        df = df.drop('Unc.(nm)R', axis=1)
        df = df.drop('Unc.(nm)O', axis=1)
        df.insert(0, 'Unc.(nm)', df_uncr)
        df = df.drop('Unc.  (nm)', axis=1)
        df = df.drop('Unc.  (nm).1', axis=1)
    

    df[mask]['Ritz  Wavelength  Vac (nm)'] = df[mask]['Observed  Wavelength  Vac (nm)']
    df = df.drop('Observed  Wavelength  Vac (nm)', axis=1)
    df_wav = df['Ritz  Wavelength  Vac (nm)']
    df = df.drop('Ritz  Wavelength  Vac (nm)', axis=1)
    df.insert(0, 'Wavelength', df_wav)
    # df = df.rename(columns={'Ritz  Wavelength  Vac (nm)':'Wavelength'})


    df = df.drop(['Rel.  Int. (?)', 'Acc.'], axis=1)
    df.loc[df['Type']=='', 'Type'] = 'E1'
    df = df[~(df['Aki (s-1)'].isna())]
    

    df = remove_question_mark(df, stat)
    return df

def remove_question_mark(df, stat):
    # delete the data with '?'
    print('before remove ?: ', len(df))
    stat['before remove ?'] = len(df)
    mask = [True] *len(df)
    for i in range(len(df)):
        for j in range(len(df.iloc[i])):
            if 'Ref' in df.columns[j]:
                continue
                
            if '?' in str(df.iloc[i, j]):
                # print(df.columns[j])
                # print(df.iloc[i, j])
                mask[i] = False
                break
    # print(mask)
    df = df[mask]
    print('after remove ?: ', len(df))
    stat['after remove ?'] = len(df)
    df = df.reset_index(drop=True)
    return df


def remove_n_plus_2(df, val, stat):
    # delete the data when the principal quantum number larger than n+2
    if len(df) == 0:
        return None
    df = df.rename(columns={'Upper Level  Conf., Term, J':'Upper Level Conf'})
    df = df.rename(columns={'Upper Level  Conf., Term, J.1':'Upper Level Term'})
    df = df.rename(columns={'Upper Level  Conf., Term, J.2':'Upper Level J'})

    df = df.rename(columns={'Lower Level  Conf., Term, J':'Lower Level Conf'})
    df = df.rename(columns={'Lower Level  Conf., Term, J.1':'Lower Level Term'})
    df = df.rename(columns={'Lower Level  Conf., Term, J.2':'Lower Level J'})

    
    
    
    if df['Upper Level J'].dtype != str:
        df['Upper Level J'] = df['Upper Level J'].astype(str)
    if df['Lower Level J'].dtype != str:
        df['Lower Level J'] = df['Lower Level J'].astype(str)

    

    

    def change(x):
        x = x.replace(' ','')
        x = x.replace('[','')
        x = x.replace(']','')
        x = x.replace('(', '')
        x = x.replace(')', '')
        return x
    
    # df['Ek  (cm-1)']= df['Ek  (cm-1)'].apply(lambda x: x.replace('+x', ''))
    # df['Ei  (cm-1)']= df['Ei  (cm-1)'].apply(lambda x: x.replace('+x', ''))
    pattern = re.compile('[^\d\.]')
    df['Ek  (cm-1)'] = df['Ek  (cm-1)'].astype(str)
    df['Ei  (cm-1)'] = df['Ei  (cm-1)'].astype(str)
    # print(df['Ek  (cm-1)'])
    # print(df['Ei  (cm-1)'])
    df['Ek  (cm-1)'] = df['Ek  (cm-1)'].apply(lambda x: pattern.sub('', x))
    df['Ei  (cm-1)'] = df['Ei  (cm-1)'].apply(lambda x: pattern.sub('', x))
    
    df['Ek  (cm-1)']= df['Ek  (cm-1)'].apply(change).astype(float)
    df['Ei  (cm-1)']= df['Ei  (cm-1)'].apply(change).astype(float)
    df = df.rename(columns={'Ek  (cm-1)':'Ek'})
    df = df.rename(columns={'Ei  (cm-1)':'Ei'})

   


    # pattern = re.compile(r'\(.*\)')
    pattern = re.compile(r'\(.*\)|<sup>.*?<\/sup>')
    # print(df['Upper Level Conf'])
    df['Upper Level Conf_temp'] = df['Upper Level Conf'].apply(lambda x: pattern.sub('', x))
    # df['Lower Level Conf'] = df['Lower Level Conf'].apply(lambda x: pattern.sub('', x))
    mask = [True] *len(df)
    print('before remove n+2:', len(df))
    stat['before remove n+2'] = len(df)
    for i in range(len(df)):
        conf = df.iloc[i]['Upper Level Conf_temp']
        numbers = re.findall(r"\d+", conf)
        numbers = [int(x) for x in numbers]
        x = max(numbers)
        if x > int(val):
            mask[i] = False
    df = df[mask]
    df = df.drop('Upper Level Conf_temp', axis=1)
    print('after remove n+2:', len(df))
    stat['after remove n+2'] = len(df)
    
    pattern = re.compile(r'<.*?>')
    df['Upper Level Conf'] = df['Upper Level Conf'].apply(lambda x: pattern.sub('', x))
    return df


def write_df(df, atom, dir):
    # write data into csv file
    if not os.path.exists(dir):
        os.mkdir(dir)
    file_name = os.path.join(dir, atom+'_processed'+'.csv')
    df.to_csv(file_name, index=False)
    print('write data done!')


def solve(atoms_file, in_dir, out_dir):
    # function call
    atoms_df = pd.read_excel(atoms_file)
    atoms_list = atoms_df.iloc[:, 0].to_list()
    stat = pd.DataFrame(columns={'atom', 'before remove ?', 'after remove ?', 'before remove n+2', 'after remove n+2'})
    stat['atom'] = atoms_list
    stat[['before remove ?', 'after remove ?', 'before remove n+2', 'after remove n+2']] = 0
    stat = stat.set_index('atom')
    # print(stat)
    # atoms_list = ['Tm II']
    for i in range(len(atoms_list)):
        file_name = os.path.join(in_dir, atoms_list[i]+'_original'+'.csv')
        # file_name = './original_data/'+atoms_list[i]+'_original'+'.csv'
        print(atoms_list[i])
        if not os.path.exists(file_name):
            continue
        n_plus_2 = atoms_df.iloc[i]['n+2']
        df = pd.read_csv(file_name)
        df = process_df(df, stat.loc[atoms_list[i]])
        if df is None:
            continue
        df = remove_n_plus_2(df, n_plus_2, stat.loc[atoms_list[i]])
        if df is None or len(df) ==0:
            continue
        write_df(df, atoms_list[i], out_dir)
        # print(df)
    print(stat)
    stat.to_csv(atoms_file[:-5]+'_stat.csv')

    
solve('neutral_atoms.xlsx', 'original_neutral_data', 'processed_neutral_data')
solve('singly_charged_ions.xlsx', 'original_singly_charged_data', 'processed_singly_charged_data')

