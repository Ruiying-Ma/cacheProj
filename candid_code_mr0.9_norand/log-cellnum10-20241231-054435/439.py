# Import anything you need below
import zlib

# Put tunable constant parameters below
NEUTRAL_DEVIATION_SCORE = 0
INITIAL_SAMPLING_INDEX = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a CRC value for each cache entry to detect redundancy, a loop counter to track access patterns, a deviation score to measure access frequency changes, and a sampling index to adjust based on sequential access patterns.
metadata = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the highest deviation score, indicating the least consistent access pattern, and cross-referencing with the CRC to ensure minimal redundancy impact.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    max_deviation_score = -1
    for key, cached_obj in cache_snapshot.cache.items():
        obj_metadata = metadata[key]
        if obj_metadata['deviation_score'] > max_deviation_score:
            max_deviation_score = obj_metadata['deviation_score']
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the CRC is recalculated to ensure data integrity, the loop counter is incremented to reflect the access, the deviation score is adjusted to reflect the change in access frequency, and the sampling index is updated to fine-tune sequential access adjustments.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_metadata = metadata[obj.key]
    obj_metadata['crc'] = zlib.crc32(obj.key.encode())
    obj_metadata['loop_counter'] += 1
    obj_metadata['deviation_score'] = abs(obj_metadata['loop_counter'] - obj_metadata['sampling_index'])
    obj_metadata['sampling_index'] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the CRC is initialized to establish a baseline, the loop counter is set to zero, the deviation score is initialized to a neutral value, and the sampling index is set to start tracking sequential access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    metadata[obj.key] = {
        'crc': zlib.crc32(obj.key.encode()),
        'loop_counter': 0,
        'deviation_score': NEUTRAL_DEVIATION_SCORE,
        'sampling_index': INITIAL_SAMPLING_INDEX
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the CRC values are recalibrated to maintain redundancy checks, the loop counters are adjusted to reflect the removal, the deviation scores are recalculated to account for the change in cache dynamics, and the sampling indices are reset to adapt to the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del metadata[evicted_obj.key]
    for key, obj_metadata in metadata.items():
        obj_metadata['crc'] = zlib.crc32(key.encode())
        obj_metadata['loop_counter'] = max(0, obj_metadata['loop_counter'] - 1)
        obj_metadata['deviation_score'] = abs(obj_metadata['loop_counter'] - obj_metadata['sampling_index'])
        obj_metadata['sampling_index'] = INITIAL_SAMPLING_INDEX