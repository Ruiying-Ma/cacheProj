# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import collections

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
TIME_WEIGHT = 0.4
LOCALITY_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a hybrid tree-based structure with frequencies of accesses, last accessed time, and object's spatial locality information. The tree nodes keep track of neighborhood access patterns and adapt dynamically.
metadata = {
    'frequency': collections.defaultdict(int),
    'last_accessed': {},
    'locality_score': collections.defaultdict(int),
    'neighborhood': collections.defaultdict(set)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses a victim by balancing between the least frequently accessed objects, oldest access times, and objects with the least spatial locality score. It evaluates combined metrics to select an optimal eviction candidate.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = metadata['frequency'][key]
        last_accessed = metadata['last_accessed'][key]
        locality_score = metadata['locality_score'][key]
        
        score = (FREQUENCY_WEIGHT * frequency +
                 TIME_WEIGHT * (cache_snapshot.access_count - last_accessed) +
                 LOCALITY_WEIGHT * locality_score)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the accessed object's frequency count, refreshes its last accessed timestamp, and recalculates its spatial locality score based on recent neighborhood accesses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['frequency'][key] += 1
    metadata['last_accessed'][key] = cache_snapshot.access_count
    
    # Update locality score based on neighborhood accesses
    neighborhood = metadata['neighborhood'][key]
    locality_score = sum(metadata['frequency'][neighbor] for neighbor in neighborhood)
    metadata['locality_score'][key] = locality_score

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency count, sets its last accessed timestamp to the current time, and computes its initial spatial locality score based on neighboring objects.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['frequency'][key] = 1
    metadata['last_accessed'][key] = cache_snapshot.access_count
    
    # Initialize locality score based on neighboring objects
    neighborhood = set(cache_snapshot.cache.keys())
    neighborhood.discard(key)
    metadata['neighborhood'][key] = neighborhood
    locality_score = sum(metadata['frequency'][neighbor] for neighbor in neighborhood)
    metadata['locality_score'][key] = locality_score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy rebalances the tree-based structure, recalculates local neighborhood patterns to adjust spatial locality scores, and removes the evicted object's metadata from the tracking system.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove evicted object's metadata
    del metadata['frequency'][evicted_key]
    del metadata['last_accessed'][evicted_key]
    del metadata['locality_score'][evicted_key]
    del metadata['neighborhood'][evicted_key]
    
    # Rebalance the tree-based structure and update locality scores
    for key in metadata['neighborhood']:
        if evicted_key in metadata['neighborhood'][key]:
            metadata['neighborhood'][key].remove(evicted_key)
            locality_score = sum(metadata['frequency'][neighbor] for neighbor in metadata['neighborhood'][key])
            metadata['locality_score'][key] = locality_score