import requests
from lxml import etree
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import os


def bs_preprocess(html):
    '''
    Remove extra Spaces and newlines
    '''
    pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
    html = re.sub(pat, '', html)       # remove leading and trailing whitespaces
    html = re.sub('\n', ' ', html)     # convert newlines to spaces
                                    # this preserves newline delimiters
    html = re.sub('[\s]+<', '<', html) # remove whitespaces before opening tags
    html = re.sub('>[\s]+', '>', html) # remove whitespaces after closing tags
    return html

def get_html(atom):
    # target url
    url = 'https://physics.nist.gov/cgi-bin/ASD/lines1.pl?limits_type=0&low_w=&upp_w=&unit=1&submit=Retrieve+Data&de=0&format=0&line_out=0&en_unit=0&output=0&bibrefs=1&page_size=15&show_obs_wl=1&show_calc_wl=1&unc_out=1&order_out=0&max_low_enrg=&show_av=2&max_upp_enrg=&tsb_value=0&min_str=&A_out=0&intens_out=on&max_str=&allowed_out=1&forbid_out=1&min_accur=&min_intens=&conf_out=on&term_out=on&enrg_out=on&J_out=on'
    # the atomic type to be queried
    params = {
        'spectra':atom
    }
    # initiate a request
    r = requests.get(url, params=params)
    html = bs_preprocess(r.content.decode("utf-8"))
    print('got page!')
    return html

def get_data(html):
    if 'No lines are available' in html:
        return None
    print('parse the html...')
    # get soup object
    soup = BeautifulSoup(html,'lxml')

    # Find all table labels
    tables = soup.find_all('table')
    # the content of website is fixed and the fifth table is the target table we required
    table = tables[4]
    tbodies = []

    #save tbody 
    for child in table.children:
        if child.name == 'tbody':
            tbodies.append(child)
    data = [[] for i in range(3)]
    aux_data = [[] for i in range(3)]
    # print(data)

    print('read data...')

    # The data inside the TBody is parsed and read. Each subtable consists of two TBodies, the first is the table header and the second is the content body  
    up_conf_start = 0
    for index, tbody in enumerate(tbodies):
        for tr in tbody.children:
            if tr.name != 'tr':
                continue
            row = []
            aux_row = []
            
            cnt = 0
            if index%2==0: # jusitify if it is table header
                for th in tr.children:
                    if th.name != 'th':
                        continue
                    cell_string = th.text 
                    col_span = th.get('colspan') # There are cases where cells are merged, and note how many columns are merged
                    if col_span is not None:
                        if cell_string.replace(u'\xa0', u' ').strip() == 'Upper Level  Conf., Term, J':
                            up_conf_start = cnt
                        for i in range(int(col_span)):
                            row.append(cell_string.replace(u'\xa0', u' ').strip())
                            aux_row.append(cell_string.replace(u'\xa0', u' ').strip())
                            cnt+=1

                    else:
                        row.append(cell_string.replace(u'\xa0', u' ').strip())
                        aux_row.append(cell_string.replace(u'\xa0', u' ').strip())
                        cnt+=1
                # print(up_conf_start)
            else: # If it is not the table header, it is the data body
                cnt = 0
                for td in tr.children:
                    if td.name != 'td':
                        continue
                    td_string = str(td).replace('<td class="lft1">','')
                    td_string = td_string.replace('</td>','')
                    td_string = td_string.replace('<i>','')
                    td_string = td_string.replace('</i>','').strip()
                    
                    
                    # if cnt==up_conf_start:
                    #     print(td_string)
                    if ('<sup>' in td_string or '<sub>' in td_string) and cnt==up_conf_start:
                        row.append(td_string)
                        # row.append(td.text.replace(u'\xa0', u' ').strip())
                        cnt+=1
                        continue
                    

                    cell_string = td.text
                    url = re.findall(r'popded\(\'(https?:\/\/[^\s]*)\'\);', str(td))
                    if len(url)!=0:
#                         print(url[0])
                        row.append(url[0])
                    else:
                        row.append(cell_string.replace(u'\xa0', u' ').strip())
                    cnt+=1
            
            # get rid of empty lines
            if len(''.join(row)) == 0:
                continue      
            data[index//2].append(row)
            # aux_data[index//2].append(aux_row)
    print('get data done!')
    return data
    
def get_df(data, atom):
    # save data into dataframe
    
    all_data = []
    header = data[0][0]
    for i in range(len(header)):
        header[i] = header[i].replace('Air', 'Vac')
    # print(header)

    for i in range(3):
        if len(data[i])==0:
            continue
        all_data += data[i][1:]
    df = pd.DataFrame(all_data, columns=header)
    
    return df

def write_df(df, atom, dir):
    # save data into csv files
    if not os.path.exists(dir):
        os.mkdir(dir)
    file_name = os.path.join(dir, atom+'_original'+'.csv')
    df.to_csv(file_name, index=False)
    print('write data done!')

    
def solve(atoms_file, out_dir):
    # function call
    atoms_df = pd.read_excel(atoms_file)
    atoms_list = atoms_df.iloc[:, 0].to_list()
    invalid_atoms = []
    # atoms_list = ['Ar I']
    for atom in atoms_list:
        print('-------------------')
        print(atom)
        html = get_html(atom)
        data = get_data(html)
        if data is None:
            print(atom, 'is invalid!')
            invalid_atoms.append(atom)
            continue
        df = get_df(data, atom)
        if df is None:
            print(atom, 'is invalid!')
            invalid_atoms.append(atom)
            continue
        # df = process_df(df)
        write_df(df, atom, out_dir)

    print(invalid_atoms)

solve('neutral_atoms.xlsx', 'original_neutral_data')
solve('singly_charged_ions.xlsx', 'original_singly_charged_data')

# print(atoms_list)

'''
['Fm I', 'Md I', 'No I', 'Lr I', 'Rf I', 'Db I', 'Sg I', 'Bh I', 'Hs I', 'Mt I', 'Ds I', 'Rg I', 'Cn I', 'Nh I', 'Fl I', 'Mc I', 'Lv I', 'Ts I', 'Og I']
'''
'''
['Po II', 'At II', 'Rn II', 'Fr II', 'Np II', 'Fm II', 'Md II', 'No II', 'Lr II', 'Rf II', 'Db II', 'Sg II', 'Bh II', 'Hs II', 'Mt II', 'Ds II', 'Rg II', 'Cn II', 'Nh II', 'Fl II', 'Mc II', 'Lv II', 'Ts II', 'Og II']
'''