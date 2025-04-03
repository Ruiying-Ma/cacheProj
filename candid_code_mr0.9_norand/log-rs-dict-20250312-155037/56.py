# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
WEIGHT_FREQUENCY = 0.5
WEIGHT_RECENCY = 0.3
WEIGHT_TYPE = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, and a 'priority score' calculated using a combination of these factors. Additionally, it tracks the type of data (e.g., static vs dynamic) and the time since last access.
metadata = {}

def calculate_priority_score(frequency, recency, data_type):
    type_score = 1 if data_type == 'dynamic' else 0
    return WEIGHT_FREQUENCY * frequency + WEIGHT_RECENCY * recency + WEIGHT_TYPE * type_score

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest priority score, which is a weighted sum of access frequency, recency, and type of data. Static data is given lower priority compared to dynamic data, and older data is deprioritized.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_priority_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata[key]['frequency']
        recency = cache_snapshot.access_count - metadata[key]['last_access']
        data_type = metadata[key]['data_type']
        priority_score = calculate_priority_score(frequency, recency, data_type)
        
        if priority_score < lowest_priority_score:
            lowest_priority_score = priority_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency is incremented, the recency of access is updated to the current time, and the priority score is recalculated to reflect the increased frequency and updated recency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['frequency'] += 1
    metadata[key]['last_access'] = cache_snapshot.access_count
    frequency = metadata[key]['frequency']
    recency = cache_snapshot.access_count - metadata[key]['last_access']
    data_type = metadata[key]['data_type']
    metadata[key]['priority_score'] = calculate_priority_score(frequency, recency, data_type)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the access frequency is initialized to 1, the recency of access is set to the current time, and the priority score is calculated based on these initial values and the type of data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key] = {
        'frequency': 1,
        'last_access': cache_snapshot.access_count,
        'data_type': 'dynamic' if 'dynamic' in key else 'static',
        'priority_score': calculate_priority_score(1, cache_snapshot.access_count, 'dynamic' if 'dynamic' in key else 'static')
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the metadata of the evicted object is removed from the cache. The remaining objects' priority scores are recalculated to ensure the eviction decision remains optimal.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata[key]['frequency']
        recency = cache_snapshot.access_count - metadata[key]['last_access']
        data_type = metadata[key]['data_type']
        metadata[key]['priority_score'] = calculate_priority_score(frequency, recency, data_type)