# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import numpy as np

# Put tunable constant parameters below
ALPHA = 0.1  # Learning rate for Q-learning
GAMMA = 0.9  # Discount factor for Q-learning
REWARD_HIT = 1  # Reward for a cache hit
REWARD_MISS = -1  # Reward for a cache miss
REWARD_EVICT = -0.5  # Reward for an eviction

# Put the metadata specifically maintained by the policy below. The policy maintains a Q-table for action-value pairs, a policy network for selecting actions, a temporal difference error tracker, a probabilistic model of access patterns, a Markov chain to track the state of the cache, and a population of candidate policies evolved using a genetic algorithm.
Q_table = {}  # Q-table for action-value pairs
policy_network = {}  # Policy network for selecting actions
temporal_difference_error = {}  # Temporal difference error tracker
access_pattern_model = {}  # Probabilistic model of access patterns
markov_chain_state = {}  # Markov chain to track the state of the cache
candidate_policies = []  # Population of candidate policies

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy uses the policy network to select an eviction candidate based on the current state of the cache, informed by the Q-table values and the probabilistic model. If multiple candidates are equally viable, the genetic algorithm evolves the best eviction strategy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    state = tuple(sorted(cache_snapshot.cache.keys()))
    if state not in Q_table:
        Q_table[state] = {key: 0 for key in cache_snapshot.cache.keys()}
    
    # Select the object with the lowest Q-value for eviction
    candid_obj_key = min(Q_table[state], key=Q_table[state].get)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    The policy updates the Q-value for the accessed object using temporal difference learning, adjusts the action-value function based on the reward received, updates the Markov chain state, and refines the probabilistic model to improve future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    state = tuple(sorted(cache_snapshot.cache.keys()))
    next_state = state
    reward = REWARD_HIT
    
    if state not in Q_table:
        Q_table[state] = {key: 0 for key in cache_snapshot.cache.keys()}
    
    Q_value = Q_table[state][obj.key]
    max_next_Q_value = max(Q_table[next_state].values())
    
    # Temporal difference update
    Q_table[state][obj.key] = Q_value + ALPHA * (reward + GAMMA * max_next_Q_value - Q_value)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    The policy updates the Q-table to reflect the new state-action pair, adjusts the policy network, updates the Markov chain state, and may introduce new candidate policies using the genetic algorithm based on the updated state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    state = tuple(sorted(cache_snapshot.cache.keys()))
    next_state = tuple(sorted(list(cache_snapshot.cache.keys()) + [obj.key]))
    reward = REWARD_MISS
    
    if state not in Q_table:
        Q_table[state] = {key: 0 for key in cache_snapshot.cache.keys()}
    
    if next_state not in Q_table:
        Q_table[next_state] = {key: 0 for key in cache_snapshot.cache.keys()}
        Q_table[next_state][obj.key] = 0
    
    Q_value = Q_table[state].get(obj.key, 0)
    max_next_Q_value = max(Q_table[next_state].values())
    
    # Temporal difference update
    Q_table[state][obj.key] = Q_value + ALPHA * (reward + GAMMA * max_next_Q_value - Q_value)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    The policy updates the Q-value for the evicted object to reflect the cost of eviction, refines the policy network through policy gradient methods, updates the Markov chain state, and adjusts the probabilistic model to account for the change in cache contents.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    state = tuple(sorted(cache_snapshot.cache.keys()))
    next_state = tuple(sorted(list(cache_snapshot.cache.keys()) + [obj.key]))
    reward = REWARD_EVICT
    
    if state not in Q_table:
        Q_table[state] = {key: 0 for key in cache_snapshot.cache.keys()}
    
    if next_state not in Q_table:
        Q_table[next_state] = {key: 0 for key in cache_snapshot.cache.keys()}
        Q_table[next_state][obj.key] = 0
    
    Q_value = Q_table[state].get(evicted_obj.key, 0)
    max_next_Q_value = max(Q_table[next_state].values())
    
    # Temporal difference update
    Q_table[state][evicted_obj.key] = Q_value + ALPHA * (reward + GAMMA * max_next_Q_value - Q_value)