# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.2   # Weight for last access time
GAMMA = 0.2  # Weight for data priority level
DELTA = 0.1  # Weight for predicted future access time

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, data priority level, and predicted future access time for each cached object.
metadata = {}

def calculate_composite_score(obj_key, current_time):
    meta = metadata[obj_key]
    access_frequency = meta['access_frequency']
    last_access_time = meta['last_access_time']
    data_priority_level = meta['data_priority_level']
    predicted_future_access_time = meta['predicted_future_access_time']
    
    score = (ALPHA * access_frequency +
             BETA * (current_time - last_access_time) +
             GAMMA * data_priority_level +
             DELTA * predicted_future_access_time)
    return score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each object based on its access frequency, last access time, data priority level, and predicted future access time. The object with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_score = float('inf')
    current_time = cache_snapshot.access_count
    
    for key in cache_snapshot.cache:
        score = calculate_composite_score(key, current_time)
        if score < lowest_score:
            lowest_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency by incrementing it, refreshes the last access time to the current time, and recalculates the predicted future access time based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    
    if key in metadata:
        metadata[key]['access_frequency'] += 1
        metadata[key]['last_access_time'] = current_time
        # Recalculate predicted future access time (simple heuristic)
        metadata[key]['predicted_future_access_time'] = current_time + 10  # Example heuristic

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency to 1, sets the last access time to the current time, assigns a data priority level based on the type of data, and estimates the predicted future access time using historical data patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    current_time = cache_snapshot.access_count
    key = obj.key
    
    metadata[key] = {
        'access_frequency': 1,
        'last_access_time': current_time,
        'data_priority_level': 1,  # Example priority level
        'predicted_future_access_time': current_time + 10  # Example heuristic
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the metadata associated with the evicted object and recalibrates the predicted future access times for the remaining objects to ensure accuracy in future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    # Recalibrate predicted future access times (simple heuristic)
    current_time = cache_snapshot.access_count
    for key in metadata:
        metadata[key]['predicted_future_access_time'] = current_time + 10  # Example heuristic