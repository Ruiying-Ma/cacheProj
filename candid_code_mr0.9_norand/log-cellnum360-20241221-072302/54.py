# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASE_TEMPORAL_LOCALITY_SCORE = 1
TEMPORAL_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache line including a temporal locality score, a coherency flag, a prefetch buffer index, and an instruction pipeline stage indicator.
metadata = defaultdict(lambda: {
    'temporal_locality_score': BASE_TEMPORAL_LOCALITY_SCORE,
    'coherency_flag': False,
    'prefetch_buffer_index': 0,
    'pipeline_stage': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache line with the lowest temporal locality score, prioritizing lines with a coherency flag indicating they are not shared, and considering lines that are not in the prefetch buffer or are at the earliest pipeline stage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        meta = metadata[key]
        score = meta['temporal_locality_score']
        if score < min_score or (
            score == min_score and not meta['coherency_flag'] and
            (meta['prefetch_buffer_index'] == 0 or meta['pipeline_stage'] == 0)
        ):
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal locality score of the accessed line is incremented, the coherency flag is checked and updated if necessary, the prefetch buffer index is adjusted to reflect recent access, and the pipeline stage indicator is updated to reflect the current stage of execution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    meta = metadata[obj.key]
    meta['temporal_locality_score'] += 1
    # Assume coherency flag update logic is based on some condition
    meta['coherency_flag'] = True  # Example update
    meta['prefetch_buffer_index'] = cache_snapshot.access_count % 10  # Example logic
    meta['pipeline_stage'] = 1  # Example update to reflect current stage

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal locality score is initialized to a base value, the coherency flag is set based on initial sharing status, the prefetch buffer index is set to the current buffer position, and the pipeline stage indicator is initialized to the first stage.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    metadata[obj.key] = {
        'temporal_locality_score': BASE_TEMPORAL_LOCALITY_SCORE,
        'coherency_flag': False,  # Assume initial sharing status is not shared
        'prefetch_buffer_index': cache_snapshot.access_count % 10,  # Example logic
        'pipeline_stage': 0  # Initial stage
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the metadata of the evicted line is cleared, and the temporal locality scores of remaining lines are slightly decayed to reflect the passage of time, while the coherency flags and prefetch buffer indices are re-evaluated to ensure consistency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in metadata:
        del metadata[evicted_obj.key]

    for key in cache_snapshot.cache:
        meta = metadata[key]
        meta['temporal_locality_score'] *= TEMPORAL_DECAY_FACTOR
        # Re-evaluate coherency flag and prefetch buffer index if needed
        meta['coherency_flag'] = False  # Example re-evaluation
        meta['prefetch_buffer_index'] = cache_snapshot.access_count % 10  # Example logic