# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import collections

# Put tunable constant parameters below
INITIAL_FIELD = 1
INITIAL_UNSELFLIKE = 1
INITIAL_PSEUDOANGINA = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including 'Field' (frequency of access), 'Unselflike' (selflessness score based on sharing data), 'Pseudoangina' (urgency score based on access patterns), and 'Icemen' (cool-down period since last access).
metadata = collections.defaultdict(lambda: {'Field': INITIAL_FIELD, 'Unselflike': INITIAL_UNSELFLIKE, 'Pseudoangina': INITIAL_PSEUDOANGINA, 'Icemen': 0})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score from the metadata fields. Entries with the lowest combined score of 'Field', 'Unselflike', 'Pseudoangina', and 'Icemen' are evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (metadata[key]['Field'] + 
                 metadata[key]['Unselflike'] + 
                 metadata[key]['Pseudoangina'] + 
                 metadata[key]['Icemen'])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the 'Field' value is incremented, 'Unselflike' is adjusted based on the sharing behavior, 'Pseudoangina' is recalculated to reflect the urgency of access, and 'Icemen' is reset to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['Field'] += 1
    metadata[key]['Unselflike'] = max(1, metadata[key]['Unselflike'] - 1)  # Adjust based on sharing behavior
    metadata[key]['Pseudoangina'] = max(1, metadata[key]['Pseudoangina'] - 1)  # Recalculate urgency
    metadata[key]['Icemen'] = 0

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, 'Field' is initialized to 1, 'Unselflike' is set based on initial sharing potential, 'Pseudoangina' is set based on initial urgency, and 'Icemen' is set to zero.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['Field'] = INITIAL_FIELD
    metadata[key]['Unselflike'] = INITIAL_UNSELFLIKE
    metadata[key]['Pseudoangina'] = INITIAL_PSEUDOANGINA
    metadata[key]['Icemen'] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates 'Field', 'Unselflike', 'Pseudoangina', and 'Icemen' for remaining entries to ensure balanced cache performance and fairness.
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
        metadata[key]['Icemen'] += 1  # Increment cool-down period for remaining entries