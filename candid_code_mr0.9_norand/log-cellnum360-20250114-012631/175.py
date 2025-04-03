# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
SUBSET_SIZE = 5  # Number of entries to consider from the front of the FIFO queue for eviction

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, a simplified interaction strength matrix, an access frequency counter, and a recency timestamp for each object.
fifo_queue = deque()
interaction_strength = defaultdict(lambda: defaultdict(int))
access_frequency = defaultdict(int)
recency_timestamp = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the front of the FIFO queue and selects a subset of cache entries from the front. It evicts the one with the lowest interaction strength from the simplified matrix, adjusted by the lowest access frequency and oldest recency timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    subset = list(fifo_queue)[:SUBSET_SIZE]
    min_score = float('inf')
    
    for key in subset:
        strength = sum(interaction_strength[key].values())
        frequency = access_frequency[key]
        recency = recency_timestamp[key]
        score = strength - frequency - recency
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    The policy increases the interaction strength of the accessed entry in the simplified matrix, increments the access frequency, and refreshes the recency timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] += 1
    recency_timestamp[key] = cache_snapshot.access_count
    
    for other_key in cache_snapshot.cache:
        if other_key != key:
            interaction_strength[key][other_key] += 1
            interaction_strength[other_key][key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    The policy adds the new object to the rear of the FIFO queue, initializes the interaction strength in the simplified matrix, sets the access frequency to 1, and sets the recency timestamp to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    fifo_queue.append(key)
    access_frequency[key] = 1
    recency_timestamp[key] = cache_snapshot.access_count
    
    for other_key in cache_snapshot.cache:
        interaction_strength[key][other_key] = 0
        interaction_strength[other_key][key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    The policy removes the evicted object from the front of the FIFO queue, updates the simplified interaction strength matrix by removing the evicted entry's interactions, and adjusts the access frequency and recency timestamps for the remaining objects if necessary.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    fifo_queue.popleft()
    
    del interaction_strength[evicted_key]
    for other_key in interaction_strength:
        if evicted_key in interaction_strength[other_key]:
            del interaction_strength[other_key][evicted_key]
    
    del access_frequency[evicted_key]
    del recency_timestamp[evicted_key]