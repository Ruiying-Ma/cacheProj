# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
RECENCY_BOOST = 10
INITIAL_RECENCY = 5
SATURATION_THRESHOLD = 0.8

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry including a recency score, an access frequency counter, and a uniformity score. Additionally, it tracks the overall cache saturation level.
metadata = {
    'recency': defaultdict(lambda: INITIAL_RECENCY),
    'frequency': defaultdict(int),
    'uniformity': defaultdict(float),
    'saturation_level': 0.0
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses an eviction victim by first checking if the cache saturation level exceeds a predefined threshold. If so, it selects the entry with the lowest combined score of recency and access uniformity, giving a recency boost to recently accessed items.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    if metadata['saturation_level'] > SATURATION_THRESHOLD:
        min_score = float('inf')
        for key, cached_obj in cache_snapshot.cache.items():
            recency_score = metadata['recency'][key]
            uniformity_score = metadata['uniformity'][key]
            combined_score = recency_score + uniformity_score
            if combined_score < min_score:
                min_score = combined_score
                candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the recency score of the accessed entry is increased, and its access frequency counter is incremented. The access uniformity score is adjusted to reflect the new access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['recency'][key] += RECENCY_BOOST
    metadata['frequency'][key] += 1
    metadata['uniformity'][key] = metadata['frequency'][key] / cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its recency score to a moderate value, sets the access frequency counter to one, and calculates an initial access uniformity score. The cache saturation level is updated to reflect the new state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['recency'][key] = INITIAL_RECENCY
    metadata['frequency'][key] = 1
    metadata['uniformity'][key] = 1 / cache_snapshot.access_count
    metadata['saturation_level'] = cache_snapshot.size / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalculates the cache saturation level. It also adjusts the recency and access uniformity scores of remaining entries to ensure they reflect the current cache state.
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
    if evicted_key in metadata['uniformity']:
        del metadata['uniformity'][evicted_key]
    
    metadata['saturation_level'] = cache_snapshot.size / cache_snapshot.capacity
    
    for key in cache_snapshot.cache:
        metadata['recency'][key] = max(0, metadata['recency'][key] - 1)
        metadata['uniformity'][key] = metadata['frequency'][key] / cache_snapshot.access_count