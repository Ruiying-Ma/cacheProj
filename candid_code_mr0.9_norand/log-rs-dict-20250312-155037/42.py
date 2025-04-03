# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
import math

# Put tunable constant parameters below
SEASHELL_WEIGHT = 0.5
SLOYD_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency, and a unique 'seashell' score derived from a combination of access patterns and object size. It also tracks a 'sloyd' score representing the complexity of the object's usage patterns.
metadata = {
    'access_frequency': {},
    'recency': {},
    'seashell_score': {},
    'sloyd_score': {}
}

def calculate_seashell_score(obj, access_frequency, recency):
    return SEASHELL_WEIGHT * (access_frequency + 1) / (recency + 1) * obj.size

def calculate_sloyd_score(obj, access_frequency, recency):
    return SLOYD_WEIGHT * math.log(access_frequency + 1) / (recency + 1)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim based on the lowest combined 'seashell' and 'sloyd' scores, prioritizing objects that are infrequently accessed, less recent, and have simpler usage patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_combined_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        seashell_score = metadata['seashell_score'][key]
        sloyd_score = metadata['sloyd_score'][key]
        combined_score = seashell_score + sloyd_score
        
        if combined_score < min_combined_score:
            min_combined_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    After a cache hit, the access frequency and recency are updated, and the 'seashell' score is recalculated to reflect the increased access. The 'sloyd' score is adjusted to account for the complexity of the access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    
    metadata['seashell_score'][key] = calculate_seashell_score(
        obj, metadata['access_frequency'][key], metadata['recency'][key]
    )
    metadata['sloyd_score'][key] = calculate_sloyd_score(
        obj, metadata['access_frequency'][key], metadata['recency'][key]
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency and recency, assigns an initial 'seashell' score based on the object's size and predicted access pattern, and sets a baseline 'sloyd' score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['access_frequency'][key] = 1
    metadata['recency'][key] = cache_snapshot.access_count
    
    metadata['seashell_score'][key] = calculate_seashell_score(
        obj, metadata['access_frequency'][key], metadata['recency'][key]
    )
    metadata['sloyd_score'][key] = calculate_sloyd_score(
        obj, metadata['access_frequency'][key], metadata['recency'][key]
    )

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the policy recalculates the 'seashell' and 'sloyd' scores for the remaining objects to ensure the scores reflect the current cache state and access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in metadata['access_frequency']:
        del metadata['access_frequency'][evicted_key]
        del metadata['recency'][evicted_key]
        del metadata['seashell_score'][evicted_key]
        del metadata['sloyd_score'][evicted_key]
    
    for key, cached_obj in cache_snapshot.cache.items():
        metadata['seashell_score'][key] = calculate_seashell_score(
            cached_obj, metadata['access_frequency'][key], metadata['recency'][key]
        )
        metadata['sloyd_score'][key] = calculate_sloyd_score(
            cached_obj, metadata['access_frequency'][key], metadata['recency'][key]
        )