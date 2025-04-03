# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BUFFER_SCORE_WEIGHT = 1.0
RESOURCE_CAP_SCORE_WEIGHT = 1.0
PRIORITY_LEVEL_WEIGHT = 1.0
TEMPORAL_SEQUENCE_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including a buffer score, a resource cap score, a priority level, and a temporal sequence number. The buffer score indicates the data's buffering needs, the resource cap score reflects the resource usage, the priority level denotes the request's importance, and the temporal sequence number tracks the order of access.
metadata = defaultdict(lambda: {
    'buffer_score': 1.0,  # Default buffer score
    'resource_cap_score': 0.0,
    'priority_level': 1.0,  # Default priority level
    'temporal_sequence': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which is a weighted sum of the buffer score, resource cap score, priority level, and temporal sequence number. The entry with the lowest composite score is selected for eviction, balancing the need to buffer data, cap resources, prioritize requests, and respect temporal access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        composite_score = (
            BUFFER_SCORE_WEIGHT * meta['buffer_score'] +
            RESOURCE_CAP_SCORE_WEIGHT * meta['resource_cap_score'] +
            PRIORITY_LEVEL_WEIGHT * meta['priority_level'] +
            TEMPORAL_SEQUENCE_WEIGHT * meta['temporal_sequence']
        )
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the priority level and updates the temporal sequence number to the current time for the accessed entry. The buffer score and resource cap score remain unchanged, ensuring that the entry's importance and recency are reflected in future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['priority_level'] += 1
    meta['temporal_sequence'] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns initial values to the metadata: a default buffer score, a calculated resource cap score based on current cache usage, a priority level derived from the request's context, and the current time as the temporal sequence number. This ensures the new entry is integrated into the cache with appropriate initial metadata.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['buffer_score'] = 1.0  # Default buffer score
    meta['resource_cap_score'] = obj.size / cache_snapshot.capacity
    meta['priority_level'] = 1.0  # Default priority level
    meta['temporal_sequence'] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the resource cap scores for remaining entries to reflect the freed resources. It also adjusts the buffer scores if necessary to accommodate changes in data buffering needs, while leaving priority levels and temporal sequence numbers unchanged to maintain consistency in request prioritization and access order.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    total_size = cache_snapshot.size
    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        meta['resource_cap_score'] = cached_obj.size / cache_snapshot.capacity
        # Adjust buffer scores if necessary (not specified how, so keeping it unchanged)