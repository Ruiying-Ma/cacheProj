# Import anything you need below
import collections

# Put tunable constant parameters below
INITIAL_SYNTHESIZED_SCORE = 1
NEUTRAL_HEURISTIC_INDEX = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a pattern recognition matrix to identify access patterns, a synthesized data score for each cache entry, a cyclical access counter, and a heuristic migration index to track potential future access shifts.
pattern_recognition_matrix = collections.defaultdict(int)
synthesized_data_score = collections.defaultdict(lambda: INITIAL_SYNTHESIZED_SCORE)
cyclical_access_counter = collections.defaultdict(int)
heuristic_migration_index = collections.defaultdict(lambda: NEUTRAL_HEURISTIC_INDEX)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the entry with the lowest synthesized data score, adjusted by the cyclical access counter and heuristic migration index to account for potential future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (synthesized_data_score[key] - 
                 cyclical_access_counter[key] + 
                 heuristic_migration_index[key])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the pattern recognition matrix is updated to reinforce the identified access pattern, the synthesized data score is incremented, the cyclical access counter is reset, and the heuristic migration index is adjusted to reflect the likelihood of future hits.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    pattern_recognition_matrix[obj.key] += 1
    synthesized_data_score[obj.key] += 1
    cyclical_access_counter[obj.key] = 0
    heuristic_migration_index[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the pattern recognition matrix is updated to include the new access pattern, the synthesized data score is initialized based on initial access frequency, the cyclical access counter is set to zero, and the heuristic migration index is initialized to a neutral value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    pattern_recognition_matrix[obj.key] = 1
    synthesized_data_score[obj.key] = INITIAL_SYNTHESIZED_SCORE
    cyclical_access_counter[obj.key] = 0
    heuristic_migration_index[obj.key] = NEUTRAL_HEURISTIC_INDEX

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the pattern recognition matrix is adjusted to deprioritize the evicted pattern, the synthesized data score of the evicted entry is removed, the cyclical access counter is decremented for all entries, and the heuristic migration index is recalibrated to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in pattern_recognition_matrix:
        del pattern_recognition_matrix[evicted_obj.key]
    if evicted_obj.key in synthesized_data_score:
        del synthesized_data_score[evicted_obj.key]
    if evicted_obj.key in cyclical_access_counter:
        del cyclical_access_counter[evicted_obj.key]
    if evicted_obj.key in heuristic_migration_index:
        del heuristic_migration_index[evicted_obj.key]
    
    for key in cache_snapshot.cache:
        cyclical_access_counter[key] -= 1
        heuristic_migration_index[key] = max(0, heuristic_migration_index[key] - 1)