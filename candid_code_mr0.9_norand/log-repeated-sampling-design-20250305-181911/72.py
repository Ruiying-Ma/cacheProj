# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for recency in priority score
BETA = 0.5   # Weight for frequency in priority score

# Put the metadata specifically maintained by the policy below. The policy maintains a timestamp for each cached object, a frequency count of accesses, and a dynamic priority score combining recentness and frequency.
timestamps = {}
frequencies = {}
priority_scores = {}

def calculate_priority_score(timestamp, frequency, current_time):
    recency = current_time - timestamp
    return ALPHA * recency + BETA * frequency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy calculates the priority score for each cached object and evicts the one with the lowest score. If multiple objects have the same score, it evicts the least recently accessed one among them.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority_score = float('inf')
    min_timestamp = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        score = priority_scores[key]
        if score < min_priority_score or (score == min_priority_score and timestamps[key] < min_timestamp):
            min_priority_score = score
            min_timestamp = timestamps[key]
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the timestamp to the current time, increments the frequency count by one, and recalculates the priority score based on the updated values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key

    timestamps[key] = current_time
    frequencies[key] += 1
    priority_scores[key] = calculate_priority_score(timestamps[key], frequencies[key], current_time)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Upon inserting a new object, the policy initializes its timestamp to the current time and sets the frequency count to one. It then calculates the initial priority score using these values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key

    timestamps[key] = current_time
    frequencies[key] = 1
    priority_scores[key] = calculate_priority_score(timestamps[key], frequencies[key], current_time)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy re-evaluates the priority scores of all remaining objects to ensure that the most valuable items are prioritized for retention.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del timestamps[evicted_key]
    del frequencies[evicted_key]
    del priority_scores[evicted_key]

    current_time = cache_snapshot.access_count
    for key in cache_snapshot.cache:
        priority_scores[key] = calculate_priority_score(timestamps[key], frequencies[key], current_time)