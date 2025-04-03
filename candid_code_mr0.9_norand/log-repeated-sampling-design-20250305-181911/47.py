# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for recency
BETA = 0.5   # Weight for frequency

# Put the metadata specifically maintained by the policy below. The policy maintains access frequency, recency of access, and a 'cost of eviction' score for each cached object. The 'cost of eviction' score is influenced by factors such as time since last access and frequency of access.
metadata = {
    'access_frequency': {},  # Dictionary to store access frequency of each object
    'recency_of_access': {},  # Dictionary to store recency of access (timestamp) of each object
    'cost_of_eviction': {}  # Dictionary to store cost of eviction score of each object
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on an adaptive algorithm that dynamically adjusts the weight of the 'cost of eviction' score considering current cache usage patterns and overall cache hit rate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_cost = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        cost = metadata['cost_of_eviction'][key]
        if cost < min_cost:
            min_cost = cost
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increments the access frequency, updates the recency of access timestamp, and recalculates the 'cost of eviction' score to reflect increased importance of the accessed object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency_of_access'][key] = cache_snapshot.access_count
    metadata['cost_of_eviction'][key] = calculate_cost_of_eviction(key, cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    Upon inserting a new object, the policy initializes the access frequency and recency of access, and assigns a preliminary 'cost of eviction' score based on predefined heuristics and immediate context of insertion.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['recency_of_access'][key] = cache_snapshot.access_count
    metadata['cost_of_eviction'][key] = calculate_cost_of_eviction(key, cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the policy recalibrates the 'cost of eviction' scores of remaining objects to ensure that future evictions align with current cache priorities and usage patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del metadata['access_frequency'][evicted_key]
    del metadata['recency_of_access'][evicted_key]
    del metadata['cost_of_eviction'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['cost_of_eviction'][key] = calculate_cost_of_eviction(key, cache_snapshot)

def calculate_cost_of_eviction(key, cache_snapshot):
    '''
    Helper function to calculate the cost of eviction for a given object key.
    - Args:
        - `key`: The key of the object.
        - `cache_snapshot`: A snapshot of the current cache state.
    - Return:
        - `cost`: The calculated cost of eviction.
    '''
    frequency = metadata['access_frequency'][key]
    recency = metadata['recency_of_access'][key]
    current_time = cache_snapshot.access_count
    
    cost = ALPHA * (current_time - recency) + BETA * (1 / frequency)
    return cost