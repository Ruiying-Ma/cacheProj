# Import anything you need below. You must not use any randomness. For example, you cannot `import random`.
import numpy as np

# Put tunable constant parameters below
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
REWARD_HIT = 1
REWARD_MISS = -1
REWARD_EVICT = -1

# Put the metadata specifically maintained by the policy below. The policy maintains a Q-table for action-value pairs, a policy network for selecting actions, and a temporal difference error tracker for learning updates.
Q_table = {}
policy_network = {}
temporal_difference_error = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy uses the policy network to select an action (eviction candidate) based on the current state of the cache, which is represented by the Q-table values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_q_value = float('inf')
    for key in cache_snapshot.cache:
        if key in Q_table and Q_table[key] < min_q_value:
            min_q_value = Q_table[key]
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the Q-value for the accessed object using temporal difference learning, adjusting the action-value function based on the reward received.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key not in Q_table:
        Q_table[key] = 0
    reward = REWARD_HIT
    temporal_difference_error[key] = reward + DISCOUNT_FACTOR * max(Q_table.values()) - Q_table[key]
    Q_table[key] += LEARNING_RATE * temporal_difference_error[key]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy updates the Q-table to reflect the new state of the cache and adjusts the policy network to improve future action selections.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key not in Q_table:
        Q_table[key] = 0
    reward = REWARD_MISS
    temporal_difference_error[key] = reward + DISCOUNT_FACTOR * max(Q_table.values()) - Q_table[key]
    Q_table[key] += LEARNING_RATE * temporal_difference_error[key]

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy updates the Q-value for the evicted object to reflect the cost of eviction and uses this information to refine the policy network through policy gradient methods.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    if key not in Q_table:
        Q_table[key] = 0
    reward = REWARD_EVICT
    temporal_difference_error[key] = reward + DISCOUNT_FACTOR * max(Q_table.values()) - Q_table[key]
    Q_table[key] += LEARNING_RATE * temporal_difference_error[key]