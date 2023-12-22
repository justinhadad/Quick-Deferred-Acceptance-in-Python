#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import time 

start_time = time.time()

def deferred_acceptance(proposing, accepting):
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


def flip(matches, num_men):
    # Initialize an array of length 'num_men' with -1s
    B = [-1 for _ in range(num_men)]
    
    # Populate the array based on the matches
    for woman, man in enumerate(matches):
        if man != -1:
            B[man] = woman
            
    return B

    
def average_rank(matches, men_values):
    # Input: men-indexed matches
    # Output: average rank of woman with whom a man is matched
    
    total_rank = 0  # Sum of ranks of matched women
    num_matched_men = 0  # Number of men who are matched
    
    for man, woman in enumerate(matches):
        if woman != -1:  # Check if the man is matched
            num_matched_men += 1
            total_rank += men_values[man][woman]  # Add the rank of the matched woman for this man
            
    if num_matched_men == 0:  # Check to avoid division by zero
        return 0
    
    average_rank = total_rank / num_matched_men  # Calculate the average rank
    return average_rank


# Initialize matrices to store average ranks
max_size = 10
avg_rank_men_proposing = np.zeros((max_size, max_size))
avg_rank_men_accepting = np.zeros((max_size, max_size))
num_loops = 10

for men in range(3, max_size):
    for women in range(3, max_size):
#         if men > women:
#             continue
        
        for loop in range(num_loops):
            
            print(f"{men} men, {women} women")
            print(f"Iteration {loop+1}")
            
            men_values = np.array([np.random.permutation(range(0, women)) for _ in range(men)])
            women_values = np.array([np.random.permutation(range(0, men)) for _ in range(women)])

            print("\n Men's Preferences:")
            print(men_values)
            print("Women's Preferences:")
            print(women_values)
            
            # MPDA
            matches_men_proposing = deferred_acceptance(men_values, women_values)
            men_indexed_matches = flip(matches_men_proposing, men)
            avg_rank_MPDA = average_rank(men_indexed_matches, men_values)
            avg_rank_men_proposing[men][women] += (women - avg_rank_MPDA)
            
            # WPDA
            matches_men_accepting = deferred_acceptance(women_values, men_values)
            avg_rank_WPDA = average_rank(matches_men_accepting, men_values)
            avg_rank_men_accepting[men][women] += (women - avg_rank_WPDA)
            
            print(f"\n MPDA:")
            print(f"Stable Matchings: {men_indexed_matches}")
            print(f"Men Average Rank: {women - avg_rank_MPDA} \n")

            print(f"\n WPDA:")
            print(f"Stable Matchings: {matches_men_accepting}")
            print(f"Men Average Rank: {women - avg_rank_WPDA} \n")
            print("---------- \n")

        
        avg_rank_men_proposing[men][women] /= num_loops
        avg_rank_men_accepting[men][women] /= num_loops

# Export to CSV

print(pd.DataFrame(avg_rank_men_proposing))
print(pd.DataFrame(avg_rank_men_accepting))
pd.DataFrame(avg_rank_men_proposing).to_csv("avg_rank_men_proposing.csv", index=False)
pd.DataFrame(avg_rank_men_accepting).to_csv("avg_rank_men_accepting.csv", index=False)


end_time = time.time()

elapsed_time = end_time - start_time
print(f"Time taken for deferred_acceptance with max size {max_size} and {num_loops} loops: {elapsed_time} seconds")


# In[ ]:




