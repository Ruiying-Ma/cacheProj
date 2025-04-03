# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for time since last access in relevance score
BETA = 0.5   # Weight for frequency count in relevance score

# Put the metadata specifically maintained by the policy below. The policy maintains a timestamp of the last access time, a frequency count for each item indicating the number of accesses, and a dynamic relevance score which is adjusted based on custom heuristics including time since last access and frequency count.
last_access_time = {}
frequency_count = {}
relevance_score = {}

def calculate_relevance_score(current_time, last_access, frequency):
    time_since_last_access = current_time - last_access
    return ALPHA * time_since_last_access + BETA * frequency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest dynamic relevance score. If multiple items have the same score, the oldest accessed item is chosen.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_relevance_score = float('inf')
    oldest_access_time = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        score = relevance_score[key]
        last_access = last_access_time[key]
        if score < min_relevance_score or (score == min_relevance_score and last_access < oldest_access_time):
            min_relevance_score = score
            oldest_access_time = last_access
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Immediately after a cache hit, the policy updates the last access time to the current time, increments the frequency count by 1, and recalculates the dynamic relevance score based on the updated metadata.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key

    last_access_time[key] = current_time
    frequency_count[key] += 1
    relevance_score[key] = calculate_relevance_score(current_time, last_access_time[key], frequency_count[key])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Immediately after inserting a new object, the policy sets the last access time to the current time, initializes the frequency count to 1, and calculates the initial dynamic relevance score based on the current state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key

    last_access_time[key] = current_time
    frequency_count[key] = 1
    relevance_score[key] = calculate_relevance_score(current_time, last_access_time[key], frequency_count[key])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Immediately after evicting the victim, the policy removes all associated metadata for the evicted item and optionally recalculates relevance scores for remaining items if the policy dictates.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key

    del last_access_time[evicted_key]
    del frequency_count[evicted_key]
    del relevance_score[evicted_key]