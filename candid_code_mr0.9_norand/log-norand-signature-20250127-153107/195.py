# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import collections

# Put tunable constant parameters below
ALPHA = 0.1  # Learning rate for Q-value updates
GAMMA = 0.9  # Discount factor for future rewards
REWARD_HIT = 1  # Reward for a cache hit
REWARD_MISS = -1  # Reward for a cache miss
REWARD_EVICTION = -0.5  # Penalty for eviction

# Put the metadata specifically maintained by the policy below. The policy maintains a Q-table for action-value pairs, a policy network for selecting actions, a temporal difference error tracker, a probabilistic model of access patterns, a Markov chain to track the state of the cache, and a population of candidate policies evolved using a genetic algorithm.
Q_table = collections.defaultdict(lambda: collections.defaultdict(float))
access_pattern = collections.defaultdict(int)
markov_chain = collections.defaultdict(lambda: collections.defaultdict(int))
policy_network = collections.defaultdict(float)
candidate_policies = []

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
    min_q_value = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        q_value = Q_table[key]['evict']
        if q_value < min_q_value:
            min_q_value = q_value
            candid_obj_key = key
    
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
    state = tuple(cache_snapshot.cache.keys())
    next_state = state
    reward = REWARD_HIT
    current_q = Q_table[obj.key]['hit']
    max_next_q = max(Q_table[obj.key].values())
    Q_table[obj.key]['hit'] = current_q + ALPHA * (reward + GAMMA * max_next_q - current_q)
    access_pattern[obj.key] += 1
    markov_chain[state][next_state] += 1

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
    state = tuple(cache_snapshot.cache.keys())
    next_state = state + (obj.key,)
    reward = REWARD_MISS
    current_q = Q_table[obj.key]['insert']
    max_next_q = max(Q_table[obj.key].values())
    Q_table[obj.key]['insert'] = current_q + ALPHA * (reward + GAMMA * max_next_q - current_q)
    access_pattern[obj.key] += 1
    markov_chain[state][next_state] += 1

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
    state = tuple(cache_snapshot.cache.keys())
    next_state = state
    reward = REWARD_EVICTION
    current_q = Q_table[evicted_obj.key]['evict']
    max_next_q = max(Q_table[evicted_obj.key].values())
    Q_table[evicted_obj.key]['evict'] = current_q + ALPHA * (reward + GAMMA * max_next_q - current_q)
    access_pattern[evicted_obj.key] -= 1
    markov_chain[state][next_state] += 1