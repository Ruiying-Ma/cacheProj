# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_HIT_WEIGHT = 0.7
INITIAL_AGE_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including a dynamic priority score, a hit frequency counter, and an age timestamp. The dynamic priority score is calculated based on a weighted combination of hit frequency and age, with weights adjusted dynamically based on overall cache performance.
cache_metadata = {
    'hit_frequency': defaultdict(int),
    'age_timestamp': {},
    'priority_score': {},
    'hit_weight': INITIAL_HIT_WEIGHT,
    'age_weight': INITIAL_AGE_WEIGHT
}

def calculate_priority_score(hit_frequency, age, hit_weight, age_weight):
    return hit_weight * hit_frequency - age_weight * age

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by choosing the entry with the lowest dynamic priority score. This approach balances between retaining frequently accessed items and ensuring that older items are not kept indefinitely.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        priority_score = cache_metadata['priority_score'][key]
        if priority_score < min_priority_score:
            min_priority_score = priority_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the hit frequency counter for the accessed entry is incremented, and the age timestamp is updated to the current time. The dynamic priority score is recalculated using the updated hit frequency and age.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['hit_frequency'][key] += 1
    cache_metadata['age_timestamp'][key] = cache_snapshot.access_count
    cache_metadata['priority_score'][key] = calculate_priority_score(
        cache_metadata['hit_frequency'][key],
        cache_snapshot.access_count - cache_metadata['age_timestamp'][key],
        cache_metadata['hit_weight'],
        cache_metadata['age_weight']
    )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the hit frequency counter to 1 and sets the age timestamp to the current time. The dynamic priority score is calculated using these initial values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    cache_metadata['hit_frequency'][key] = 1
    cache_metadata['age_timestamp'][key] = cache_snapshot.access_count
    cache_metadata['priority_score'][key] = calculate_priority_score(
        1,
        0,
        cache_metadata['hit_weight'],
        cache_metadata['age_weight']
    )

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy reviews the overall cache performance and adjusts the weights used in calculating the dynamic priority score to optimize for the current workload characteristics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Adjust weights based on cache performance
    hit_ratio = cache_snapshot.hit_count / (cache_snapshot.hit_count + cache_snapshot.miss_count)
    
    # Simple heuristic: if hit ratio is low, increase the weight of hit frequency
    if hit_ratio < 0.5:
        cache_metadata['hit_weight'] = min(1.0, cache_metadata['hit_weight'] + 0.1)
        cache_metadata['age_weight'] = max(0.0, 1.0 - cache_metadata['hit_weight'])
    else:
        cache_metadata['age_weight'] = min(1.0, cache_metadata['age_weight'] + 0.1)
        cache_metadata['hit_weight'] = max(0.0, 1.0 - cache_metadata['age_weight'])