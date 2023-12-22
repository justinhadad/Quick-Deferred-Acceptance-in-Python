#!/usr/bin/env python
# coding: utf-8

# In[1]:


import random
import copy
import pandas as pd
from matplotlib import pyplot as plt
from operator import itemgetter
import numpy as np
import operator
import time
from scipy.interpolate import make_interp_spline, BSpline
from scipy.signal import savgol_filter
from itertools import permutations
# import sys
# sys.stdout = open('market_perms.txt','wt')

def deferred_acceptance(proposing, accepting, truncation=0):
    acc = np.argsort(accepting, axis=1)
    prop = np.argsort(proposing, axis=1)
    
    offers = [[] for woman in range(len(acc))] # women-indexed offers
    matches = [-1 for woman in range(len(acc))] # women-indexed matches
    unmatched = [i for i in range(len(prop))] # list of men who are unmatched
    offered = [] # list of women who are offered men
    
    while unmatched:
        
        for man in unmatched:
            for idx, woman in reversed(list(enumerate(prop[man]))):
                if woman != -1:
                    offers[woman].append(man)
                    prop[man][idx] = -1
                    if woman not in offered:
                        offered.append(woman)
                    break
        
        unmatched = []
            
        for woman in offered:
            current_man = matches[woman]
            for man in reversed(acc[woman]):
                if man == current_man:
                    break
                if man in offers[woman]:
                    if current_man != -1:
                        unmatched.append(current_man)
                    matches[woman] = man
                    break
            for man in offers[woman]:
                best_man = matches[woman]
                if man != best_man and man != current_man:
                    unmatched.append(man)
                    
        offers = [[] for woman in range(len(acc))] # women-indexed offers
        offered = []
            
    return matches

def average_rank(matches, men_values):
    #     Input: men-indexed matches
    #     Output: average rank of woman with whom a man is matched
    
#     format idx, num
    rank = 0
    men = 0
    for man, woman in enumerate(matches):
        if woman != -1:
            men+=1
            rank += men_values[man][woman]

#    return the [number of women - (1 + rank / men)]th best choice
    return len(matches) - (rank / men)

def ref_rank(matches, men_values):
    #     Input: men-indexed matches
    #     Output: rank of the first matched man (works by symmetry; values uncorrelated)
    
#     format idx, num
    for man, woman in enumerate(matches):
        if woman != -1:
            return man, len(matches) - (men_values[man][woman])


def remove_man(temp_men_values, temp_women_values, removed_person):
    men_values = copy.deepcopy(temp_men_values)
    women_values = copy.deepcopy(temp_women_values)
    
    del men_values[removed_person]
    [j.pop(removed_person) for j in women_values]
        
    return men_values, women_values

def generate_values(n):
    import itertools
    values = []
    perms = permutations(list(range(n)))
    double_perms = itertools.product(perms, repeat=n)
    
    for array in double_perms:
        value = []
        for row in array:
            value.append(list(row))
        values.append(value)
    return values

def flip(matches):
            # used to put matching in man-indexed [woman, woman, ...] format. "index man has value woman"
        woman = len(matches)
        B = [-1 for s in range(woman)]  
        for index, element in enumerate(matches):
            if element != -1:
                B[element] = index
        return B

def main():
    
    for n in range(2,4):
        strictly_better_count = 0
        strictly_equal_count = 0
        strictly_worse_count = 0
        
        still_ranks_mpda = 0
        still_ranks_wpda = 0
        
        print(f"Size of the Market: {n}")
        combs = 0
        avg_flags = 0
        ref_flags = 0
        values = generate_values(n)
        possibilities = len(values)
        print(f'There are {possibilities} possible combinations of rank-order preference profiles for one side, and {possibilities**2} unique preference profiles for two-sided matching markets.') 
        for men_values in values:
            for women_values in values:
                avg_already_flagged = False
                ref_already_flagged = False
                combs+=1
                print('\n \n \n')
                print(f'Combination {combs} \n')
                print('BALANCED')
                print('\n Men Values for Women')
                print(pd.DataFrame(men_values).rename(columns=lambda y: 'Woman '+str(y)).rename(index=lambda x: 'Man ' + str(x)))
                print('\n Women Values for Men')
                print(pd.DataFrame(women_values).rename(columns=lambda y: 'Man '+str(y)).rename(index=lambda x: 'Woman ' + str(x)))
                mpda = flip(deferred_acceptance(men_values, women_values))
                print(f'\n MPDA, Balanced Market: \n {mpda}')
                avg_rank_mpda = average_rank(mpda, men_values)
                
                for man, woman in enumerate(mpda):
                    print(f'Man {man} is matched with Woman {woman}, his {n - men_values[man][woman]}-ranked choice.')
                    
                ref_rank_mpda = ref_rank(mpda, men_values)

                
                print(f'\n On average, men get their {avg_rank_mpda}-ranked choice')
                
                for man in range(n):
                    print('-------')
                    print(f'\n REMOVING MAN {man}:')
                    new_men_values, new_women_values = remove_man(men_values, women_values, man)
                    print('\n Men Values for Women')
                    print(pd.DataFrame(new_men_values).rename(columns=lambda y: 'Woman '+str(y)).rename(index=lambda x: 'Man ' + str(x)))
                    print('\n Women Values for Men')
                    print(pd.DataFrame(new_women_values).rename(columns=lambda y: 'Man '+str(y)).rename(index=lambda x: 'Woman ' + str(x)))
                    wpda = deferred_acceptance(new_women_values, new_men_values)
                    wpda.insert(man, -1)
                    print(f'\n WPDA, One Less Man, Man {man} Removed: \n {wpda}')
                    avg_rank_wpda = average_rank(wpda, men_values)
                    ref_man, ref_rank_wpda = ref_rank(wpda, men_values)
                    print(f'\n On average, men get their {avg_rank_wpda}-ranked choice:')
                    
                    for _man, _woman in enumerate(wpda):
                        if _woman != -1:
                            print(f'Man {_man} is matched with Woman {_woman}, his {n - men_values[_man][_woman]}-ranked choice.')
                    
                            
                    ref_rank_mpda = n - men_values[ref_man][mpda[ref_man]]
                    print(f'\n \n In balanced MPDA, reference man (man {ref_man}) gets his {ref_rank_mpda}-ranked choice')
                    print(f'In one-less-man WPDA, reference man (man {ref_man}) gets his {ref_rank_wpda}-ranked choice')
                    
                    still_avg_rank_mpda = 0
                    still_avg_rank_wpda = 0
                    
                    for still_man in range(n):
                        if still_man != man:
                            still_avg_rank_mpda += n - men_values[still_man][mpda[still_man]]
                            still_avg_rank_wpda += n - men_values[still_man][wpda[still_man]]
                    
                    still_avg_rank_mpda /= (n - 1)
                    still_avg_rank_wpda /= (n - 1)

                    still_ranks_mpda += still_avg_rank_mpda / (possibilities**2)
                    still_ranks_wpda += still_avg_rank_wpda / (possibilities**2)
                    
                    print("\n \n Let's consider the men who are present in both markets. Call them the \'still men.\'")
                    print(f'The average rank of still men in balanced MPDA is {still_avg_rank_mpda}.')
                    print(f'The average rank of still men in WPDA with man {man} removed is {still_avg_rank_wpda}.')
                    
                    if still_avg_rank_mpda > still_avg_rank_wpda:
                        strictly_better_count += 1
                    elif still_avg_rank_mpda < still_avg_rank_wpda:
                        strictly_worse_count += 1
                    else: strictly_equal_count += 1
                    
                    if still_avg_rank_wpda > still_avg_rank_mpda and not avg_already_flagged:
                        avg_already_flagged = True
                        avg_flags +=1
                        print('AVG FLAG!')
                    if ref_rank_wpda > ref_rank_mpda and not ref_already_flagged:
                        ref_already_flagged = True
                        ref_flags +=1
                        print('REF FLAG!')
            
            print('\n \n \n \n')
            print(f'The average rank of still men in balanced MPDA is {still_ranks_mpda}.')
            print(f'The average rank of still men in WPDA with a man removed is {still_ranks_wpda}.')            
            
            print('\n \n \n \n \n')
            print(f'\n The average rank-outcome is at least as good under [WPDA with one less man] as it is under [balanced MPDA] {100* (1 - avg_flags/combs)}% of the time.')
            print(f'The reference man is always at least as well off under [WPDA with one less man] as he is under [balanced MPDA] {100* (1 - ref_flags/combs)}% of the time.')
            print('\n \n')

            
            print(f'Removing a man is strictly better {100*strictly_better_count / (strictly_better_count + strictly_equal_count + strictly_worse_count)}% of the time)')
            print(f'Removing a man is strictly worse {100*strictly_worse_count / (strictly_better_count + strictly_equal_count + strictly_worse_count)}% of the time)')
            print(f'Removing a man is strictly the same {100*strictly_equal_count / (strictly_better_count + strictly_equal_count + strictly_worse_count)}% of the time)')
            print('\n \n \n \n ------ \n \n \n \n')

                              
main()


# In[ ]:





# In[ ]:




