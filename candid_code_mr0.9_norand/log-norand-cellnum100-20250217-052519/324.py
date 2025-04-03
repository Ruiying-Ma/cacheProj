# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

# Put tunable constant parameters below
NUM_SHARDS = 4  # Number of shards to divide the cache into

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, last access time, shard assignment, and load metrics for each cache entry. It also keeps a global temporal index and load distribution map.
access_frequency = {}
last_access_time = {}
shard_assignment = {}
shard_load = {i: 0 for i in range(NUM_SHARDS)}
global_temporal_index = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the least frequently accessed entry within the most loaded shard, considering both temporal recency and load-balancing needs.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    most_loaded_shard = max(shard_load, key=shard_load.get)
    least_frequent_access = float('inf')
    oldest_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if shard_assignment[key] == most_loaded_shard:
            if access_frequency[key] < least_frequent_access or (access_frequency[key] == least_frequent_access and last_access_time[key] < oldest_time):
                least_frequent_access = access_frequency[key]
                oldest_time = last_access_time[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and last access time of the hit entry, adjusts the shard's load metrics, and updates the global temporal index to reflect the recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] += 1
    last_access_time[key] = cache_snapshot.access_count
    global_temporal_index[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it to a shard based on predictive data sharding, updates the shard's load metrics, and adds the entry to the global temporal index with its initial access time and frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    shard = min(shard_load, key=shard_load.get)
    shard_assignment[key] = shard
    shard_load[shard] += obj.size
    access_frequency[key] = 1
    last_access_time[key] = cache_snapshot.access_count
    global_temporal_index[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy updates the shard's load metrics to reflect the removal, removes the entry from the global temporal index, and adjusts the access frequency and last access time records accordingly.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    shard = shard_assignment[key]
    shard_load[shard] -= evicted_obj.size
    del shard_assignment[key]
    del access_frequency[key]
    del last_access_time[key]
    del global_temporal_index[key]