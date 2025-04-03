# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import time

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for recency in the consensus-based score
BETA = 0.5   # Weight for frequency in the consensus-based score

# Put the metadata specifically maintained by the policy below. The policy maintains a distributed ledger of access frequencies, timestamps, and object states across multiple nodes using Byzantine fault tolerance to ensure consistency and reliability. Each object in the cache is associated with a consensus-based score that reflects its importance and recency.
metadata = {
    'access_frequency': {},  # Dictionary to store access frequency of objects
    'timestamps': {},        # Dictionary to store the last access time of objects
    'scores': {}             # Dictionary to store the consensus-based scores of objects
}

def calculate_score(key):
    '''
    Helper function to calculate the consensus-based score for an object.
    - Args:
        - `key`: The key of the object.
    - Return:
        - `score`: The calculated score.
    '''
    frequency = metadata['access_frequency'].get(key, 0)
    timestamp = metadata['timestamps'].get(key, 0)
    current_time = time.time()
    recency = current_time - timestamp
    score = ALPHA * recency + BETA * frequency
    return score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the object with the lowest consensus-based score, ensuring that the decision is agreed upon by a majority of nodes to maintain linearizability and prevent inconsistencies.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_score(key)
        if score < lowest_score:
            lowest_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the access frequency and timestamp of the object in the distributed ledger. The consensus-based score is recalculated and agreed upon by the nodes to reflect the increased importance of the object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = metadata['access_frequency'].get(key, 0) + 1
    metadata['timestamps'][key] = time.time()
    metadata['scores'][key] = calculate_score(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency, timestamp, and state in the distributed ledger. The consensus-based score is calculated and agreed upon by the nodes to integrate the new object into the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['timestamps'][key] = time.time()
    metadata['scores'][key] = calculate_score(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the policy removes the object's metadata from the distributed ledger. The remaining objects' consensus-based scores are recalculated and agreed upon by the nodes to ensure the cache state remains consistent and up-to-date.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
    if evicted_key in metadata['timestamps']:
        del metadata['timestamps'][evicted_key]
    if evicted_key in metadata['scores']:
        del metadata['scores'][evicted_key]
    
    # Recalculate scores for remaining objects
    for key in cache_snapshot.cache:
        metadata['scores'][key] = calculate_score(key)