# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PRIORITY_INCREMENT = 1
INITIAL_PRIORITY = 1
LOAD_FACTOR_INCREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including a priority score, memory allocation size, load distribution factor, and a buffer synchronization timestamp. The priority score is dynamically adjusted based on access frequency and recency. Memory allocation size tracks the space occupied by each entry. Load distribution factor indicates the load balance across cache entries. Buffer synchronization timestamp records the last synchronization time with the main memory.
metadata = defaultdict(lambda: {
    'priority_score': INITIAL_PRIORITY,
    'memory_allocation_size': 0,
    'load_distribution_factor': 0,
    'buffer_sync_timestamp': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest priority score, considering both access frequency and recency. If there is a tie, it selects the entry with the largest memory allocation size to free up more space. In case of further ties, it considers the load distribution factor to maintain balanced load across cache entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    max_memory_size = -1
    min_load_factor = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        entry_metadata = metadata[key]
        if (entry_metadata['priority_score'] < min_priority or
            (entry_metadata['priority_score'] == min_priority and entry_metadata['memory_allocation_size'] > max_memory_size) or
            (entry_metadata['priority_score'] == min_priority and entry_metadata['memory_allocation_size'] == max_memory_size and entry_metadata['load_distribution_factor'] < min_load_factor)):
            min_priority = entry_metadata['priority_score']
            max_memory_size = entry_metadata['memory_allocation_size']
            min_load_factor = entry_metadata['load_distribution_factor']
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the priority score of the accessed entry to reflect its recent use. It also updates the buffer synchronization timestamp to ensure the entry is in sync with the main memory. The load distribution factor is recalculated to reflect the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['priority_score'] += PRIORITY_INCREMENT
    metadata[key]['buffer_sync_timestamp'] = cache_snapshot.access_count
    metadata[key]['load_distribution_factor'] += LOAD_FACTOR_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority score based on the expected access pattern. It updates the memory allocation size to reflect the space occupied by the new entry. The load distribution factor is adjusted to incorporate the new entry, and the buffer synchronization timestamp is set to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['priority_score'] = INITIAL_PRIORITY
    metadata[key]['memory_allocation_size'] = obj.size
    metadata[key]['load_distribution_factor'] = LOAD_FACTOR_INCREMENT
    metadata[key]['buffer_sync_timestamp'] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the load distribution factor to account for the removed entry. It also updates the buffer synchronization timestamps of remaining entries to ensure consistency. The memory allocation size metadata is adjusted to reflect the freed space, and priority scores of remaining entries may be slightly increased to maintain relative importance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata:
        del metadata[evicted_key]

    for key in cache_snapshot.cache:
        metadata[key]['load_distribution_factor'] -= LOAD_FACTOR_INCREMENT / len(cache_snapshot.cache)
        metadata[key]['buffer_sync_timestamp'] = cache_snapshot.access_count
        metadata[key]['priority_score'] += PRIORITY_INCREMENT / len(cache_snapshot.cache)