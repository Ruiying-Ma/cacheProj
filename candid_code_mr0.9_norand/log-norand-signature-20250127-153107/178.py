# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import numpy as np

# Put tunable constant parameters below
ALPHA = 0.1  # Learning rate for Q-learning
GAMMA = 0.9  # Discount factor for Q-learning
REWARD_HIT = 1
REWARD_MISS = -1
REWARD_EVICT = -0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a Q-table for action-value pairs, a policy network for selecting actions, a temporal difference error tracker, a probabilistic model of access patterns, a Markov chain to track the state of the cache, and a population of candidate policies evolved using a genetic algorithm.
Q_table = {}  # Q-table for action-value pairs
policy_network = {}  # Policy network for selecting actions
temporal_difference_error = {}  # Temporal difference error tracker
access_pattern_model = {}  # Probabilistic model of access patterns
markov_chain = {}  # Markov chain to track the state of the cache
candidate_policies = []  # Population of candidate policies evolved using a genetic algorithm

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
    if state not in policy_network:
        policy_network[state] = list(cache_snapshot.cache.keys())
    
    # Select the eviction candidate based on the policy network
    candidates = policy_network[state]
    if len(candidates) == 0:
        return None
    
    # Use Q-table to find the best candidate
    best_value = float('-inf')
    for candidate in candidates:
        if (state, candidate) in Q_table:
            value = Q_table[(state, candidate)]
        else:
            value = 0
        if value > best_value:
            best_value = value
            candid_obj_key = candidate
    
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
    action = obj.key
    reward = REWARD_HIT
    
    if (state, action) not in Q_table:
        Q_table[(state, action)] = 0
    
    best_next_value = max(Q_table.get((next_state, a), 0) for a in cache_snapshot.cache.keys())
    td_error = reward + GAMMA * best_next_value - Q_table[(state, action)]
    Q_table[(state, action)] += ALPHA * td_error
    
    # Update Markov chain state
    markov_chain[state] = next_state
    
    # Update access pattern model
    if action not in access_pattern_model:
        access_pattern_model[action] = 0
    access_pattern_model[action] += 1

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
    action = obj.key
    reward = REWARD_MISS
    
    if (state, action) not in Q_table:
        Q_table[(state, action)] = 0
    
    best_next_value = max(Q_table.get((next_state, a), 0) for a in cache_snapshot.cache.keys())
    td_error = reward + GAMMA * best_next_value - Q_table[(state, action)]
    Q_table[(state, action)] += ALPHA * td_error
    
    # Update Markov chain state
    markov_chain[state] = next_state
    
    # Update policy network
    if state not in policy_network:
        policy_network[state] = []
    policy_network[state].append(action)
    
    # Introduce new candidate policies using genetic algorithm
    candidate_policies.append(policy_network.copy())

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
    action = evicted_obj.key
    reward = REWARD_EVICT
    
    if (state, action) not in Q_table:
        Q_table[(state, action)] = 0
    
    best_next_value = max(Q_table.get((next_state, a), 0) for a in cache_snapshot.cache.keys())
    td_error = reward + GAMMA * best_next_value - Q_table[(state, action)]
    Q_table[(state, action)] += ALPHA * td_error
    
    # Update Markov chain state
    markov_chain[state] = next_state
    
    # Refine policy network through policy gradient methods
    if state in policy_network and action in policy_network[state]:
        policy_network[state].remove(action)
    
    # Adjust probabilistic model
    if action in access_pattern_model:
        access_pattern_model[action] -= 1
        if access_pattern_model[action] <= 0:
            del access_pattern_model[action]