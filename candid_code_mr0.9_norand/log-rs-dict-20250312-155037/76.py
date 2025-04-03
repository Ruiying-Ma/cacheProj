# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict

# Put tunable constant parameters below
AGE_THRESHOLD = 100
OWNERSHIP_THRESHOLD = 10
FUNGAL_GROUP_THRESHOLD = 5
MOBILITY_STATIC_THRESHOLD = 20

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including the 'age' of cache entries, 'ownership' status indicating if an entry is frequently accessed by a specific user, 'fungal' status representing if an entry is part of a larger group of related entries, and 'mobility' status indicating if an entry is static or dynamic in nature.
metadata = {
    'age': defaultdict(int),
    'ownership': defaultdict(int),
    'fungal': defaultdict(bool),
    'mobility': defaultdict(str)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on a combination of factors: entries with the oldest age, entries not owned by any specific user, entries not part of a fungal group, and entries with static mobility status are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        age = metadata['age'][key]
        ownership = metadata['ownership'][key]
        fungal = metadata['fungal'][key]
        mobility = metadata['mobility'][key]
        
        priority = age + (OWNERSHIP_THRESHOLD - ownership) + (FUNGAL_GROUP_THRESHOLD if not fungal else 0) + (MOBILITY_STATIC_THRESHOLD if mobility == 'static' else 0)
        
        if priority < min_priority:
            min_priority = priority
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the policy updates the 'age' by resetting it to zero, reinforces the 'ownership' status if the entry is accessed by the same user, checks and updates the 'fungal' status if the entry is part of a related group, and updates the 'mobility' status based on the nature of the access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    metadata['age'][obj.key] = 0
    metadata['ownership'][obj.key] += 1
    metadata['fungal'][obj.key] = check_fungal_status(obj)
    metadata['mobility'][obj.key] = update_mobility_status(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the 'age' to zero, sets the 'ownership' status based on the user accessing the entry, determines the 'fungal' status by checking related entries, and sets the 'mobility' status based on the initial access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata['age'][obj.key] = 0
    metadata['ownership'][obj.key] = 1
    metadata['fungal'][obj.key] = check_fungal_status(obj)
    metadata['mobility'][obj.key] = update_mobility_status(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting the victim, the policy recalculates the 'age' for remaining entries, adjusts the 'ownership' status for entries accessed by the evicted user's group, re-evaluates the 'fungal' status for related entries, and updates the 'mobility' status to reflect the new cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache.keys():
        metadata['age'][key] += 1
        if metadata['ownership'][key] == metadata['ownership'][evicted_obj.key]:
            metadata['ownership'][key] -= 1
        metadata['fungal'][key] = check_fungal_status(cache_snapshot.cache[key])
        metadata['mobility'][key] = update_mobility_status(cache_snapshot.cache[key])

def check_fungal_status(obj):
    # Dummy function to check fungal status
    return False

def update_mobility_status(obj):
    # Dummy function to update mobility status
    return 'static'