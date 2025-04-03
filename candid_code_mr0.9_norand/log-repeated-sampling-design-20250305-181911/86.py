# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for recency
BETA = 0.3   # Weight for frequency
GAMMA = 0.2  # Weight for retrieval cost

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic weighted access score (DWAS) for each cache entry, which is calculated based on a combination of access recency, access frequency, and the computational cost of retrieving the object if evicted.
metadata = {
    'recency': {},  # Stores the last access time for each object
    'frequency': {},  # Stores the access frequency for each object
    'retrieval_cost': {},  # Stores the retrieval cost for each object
    'dwas': {}  # Stores the DWAS for each object
}

def calculate_dwas(key):
    recency = metadata['recency'].get(key, 0)
    frequency = metadata['frequency'].get(key, 0)
    retrieval_cost = metadata['retrieval_cost'].get(key, 1)  # Default retrieval cost is 1
    return ALPHA * recency + BETA * frequency + GAMMA * retrieval_cost

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache entry with the lowest DWAS, thereby prioritizing entries that are less frequently and recently accessed and have a lower cost of retrieval.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_dwas = float('inf')
    
    for key in cache_snapshot.cache:
        dwas = metadata['dwas'].get(key, float('inf'))
        if dwas < min_dwas:
            min_dwas = dwas
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy increases the DWAS of the accessed entry, updating the components of the score to reflect higher recency and frequency values while also considering the object's retrieval cost.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['frequency'][key] = metadata['frequency'].get(key, 0) + 1
    metadata['dwas'][key] = calculate_dwas(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its DWAS based on the initial access recency and frequency, as well as an estimated retrieval cost, ensuring it's balanced with existing entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['frequency'][key] = 1
    metadata['retrieval_cost'][key] = obj.size  # Assuming retrieval cost is proportional to size
    metadata['dwas'][key] = calculate_dwas(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the policy recalculates the DWAS for all remaining entries to ensure the scores are adjusted proportionally, accounting for the reduced total cache size and the removed entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['recency']:
        del metadata['recency'][evicted_key]
    if evicted_key in metadata['frequency']:
        del metadata['frequency'][evicted_key]
    if evicted_key in metadata['retrieval_cost']:
        del metadata['retrieval_cost'][evicted_key]
    if evicted_key in metadata['dwas']:
        del metadata['dwas'][evicted_key]
    
    for key in cache_snapshot.cache:
        metadata['dwas'][key] = calculate_dwas(key)