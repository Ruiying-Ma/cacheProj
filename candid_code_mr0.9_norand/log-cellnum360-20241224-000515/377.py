# Import anything you need below
import collections

# Put tunable constant parameters below
BASELINE_PRIORITY = 1
TEMPORAL_DISPLACEMENT_DECAY = 0.9
REDLINE_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal displacement score for each cache entry, a priority level based on access frequency and recency, a vector representing access patterns, and a dynamic redline threshold that adjusts based on cache performance.
temporal_displacement_scores = collections.defaultdict(float)
priority_levels = collections.defaultdict(lambda: BASELINE_PRIORITY)
access_pattern_vectors = collections.defaultdict(lambda: collections.deque(maxlen=10))
dynamic_redline_threshold = 0.5

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying entries with the lowest priority level and highest temporal displacement score, while ensuring the vector fusion indicates minimal future access likelihood. Entries below the dynamic redline threshold are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority = float('inf')
    max_displacement = float('-inf')

    for key, cached_obj in cache_snapshot.cache.items():
        priority = priority_levels[key]
        displacement = temporal_displacement_scores[key]
        vector_fusion = sum(access_pattern_vectors[key])

        if priority < min_priority or (priority == min_priority and displacement > max_displacement):
            if vector_fusion < dynamic_redline_threshold:
                min_priority = priority
                max_displacement = displacement
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal displacement score is reset, the priority level is increased, the access pattern vector is updated to reflect the recent access, and the dynamic redline threshold is adjusted to reflect improved cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    temporal_displacement_scores[key] = 0
    priority_levels[key] += 1
    access_pattern_vectors[key].append(1)
    global dynamic_redline_threshold
    dynamic_redline_threshold *= (1 - REDLINE_ADJUSTMENT_FACTOR)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal displacement score is initialized, the priority level is set to a baseline value, the access pattern vector is initialized to reflect the initial access, and the dynamic redline threshold is recalibrated to accommodate the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    temporal_displacement_scores[key] = 0
    priority_levels[key] = BASELINE_PRIORITY
    access_pattern_vectors[key].append(1)
    global dynamic_redline_threshold
    dynamic_redline_threshold *= (1 + REDLINE_ADJUSTMENT_FACTOR)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the temporal displacement scores of remaining entries are recalculated, priority levels are adjusted to reflect the new cache state, access pattern vectors are updated to remove the evicted entry's influence, and the dynamic redline threshold is fine-tuned to optimize future cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in temporal_displacement_scores:
        del temporal_displacement_scores[evicted_key]
    if evicted_key in priority_levels:
        del priority_levels[evicted_key]
    if evicted_key in access_pattern_vectors:
        del access_pattern_vectors[evicted_key]

    for key in cache_snapshot.cache:
        temporal_displacement_scores[key] *= TEMPORAL_DISPLACEMENT_DECAY
        access_pattern_vectors[key].append(0)

    global dynamic_redline_threshold
    dynamic_redline_threshold *= (1 - REDLINE_ADJUSTMENT_FACTOR)