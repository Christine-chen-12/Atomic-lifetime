# A database of Atomic Lifetime for Neutral Atoms and Singly Charged Ions

## Aims and objectives of this project
The aim of this research project is to fill a research gap by creating a new database dedicated to storing the lifetimes of neutral atoms and singly charged ions available on the NIST website.   

The main objectives of the project are: 
1. to follow the order of the periodic table of elements by crawling spectral data from NIST, 
2. to calculate lifetimes according to the lifetime equation and, to introduce some of the lifetimes and adjust them to conform to the cascade effect and to give the corresponding data results.
The results of the project are output as csv files, the code and all the output files obtained are kept, with five files for each element: original data, processed data, total lifetime, partial lifetime, renormalization of partial lifetime, and the results of each processing step are presented for easy checking and retrieval.


## Some important notes
Before running the code, there is necessary to make sure the required table existed, which contain the required atoms or ions, and the (n+2), where n is the principal quantum number of the highest level occupied in the ground states, and you shoule guarantee the path of table is the same as python code.  

The algorithms and also the running steps are as below, and also gives the format of command in case you want to use other tables to do data scraping or calculation:  
1. **Scrape Data from NIST database**   
Scrape the original data from NIST database.
when you want to change required table content and name, use the function 'solve' to recall and run in **scrape_data.py**
The format of function call is:  
solve (‘name of original excel’, ‘corresponding name of folder’)

2. **Process Original data**  
After scrapying data, it is necessary to clean data.
if changing the initial table, use the below code to recall the function in **processed_data.py**
The format of function call is:  
solve (‘name of original excel’, ‘name of output folder after scraping’, ‘name of targeted output folder’).  

3. **Calculate total lifetime**  
This step calculates the total lifetime
use the code below and rerun **cal_total_lifetime.py**
solve (‘name of original excel’, ‘name of output folder in processing step’, ‘name of targeted output folder’).  

4. **Calculate partial lifetime**     
This step calculates the partial lifetime 
use the code below and rerun **cal_total_lifetime.py**
solve (‘name of original excel’, ‘name of output folder in processing step’, ‘name of targeted output folder’).  
 
5. **Renormalize the partial lifetime**  
This step renrmalize the partial lifetime.
use the code below and rerun the **re_partial_lifetime.py** to get information.
solve (‘name of original excel’, ‘name of output folder in total lifetime’, ‘name of output folder in partial lifetime’, ‘name of targeted output folder’).

## Use pytest to check the data
use the command to do data checking, 

```bash
pytest test_tau.py
```
mak sure the path of the code is the same as **test_tau.py**


