# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_RETENTION_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a sequential access counter, a logical index map for each data block, and a retention score for data blocks based on access patterns and frequency.
sequential_access_counter = 0
logical_index_map = {}
retention_score_map = defaultdict(lambda: INITIAL_RETENTION_SCORE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the data block with the lowest retention score, prioritizing blocks that have not been accessed sequentially and have lower logical index values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_retention_score = float('inf')
    min_logical_index = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        retention_score = retention_score_map[key]
        logical_index = logical_index_map[key]

        if (retention_score < min_retention_score) or (retention_score == min_retention_score and logical_index < min_logical_index):
            min_retention_score = retention_score
            min_logical_index = logical_index
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the sequential access counter is incremented, the logical index of the accessed block is updated to reflect its new position in the access sequence, and the retention score is increased based on the frequency of access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global sequential_access_counter
    sequential_access_counter += 1
    logical_index_map[obj.key] = sequential_access_counter
    retention_score_map[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the sequential access counter is reset, the logical index map is updated to include the new object with the highest index, and the retention score is initialized based on initial access frequency assumptions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global sequential_access_counter
    sequential_access_counter = 0
    logical_index_map[obj.key] = len(cache_snapshot.cache)
    retention_score_map[obj.key] = INITIAL_RETENTION_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the logical index map is adjusted to remove the evicted block, the sequential access counter is decremented if necessary, and retention scores are recalculated to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global sequential_access_counter
    if evicted_obj.key in logical_index_map:
        del logical_index_map[evicted_obj.key]
    if evicted_obj.key in retention_score_map:
        del retention_score_map[evicted_obj.key]
    sequential_access_counter = max(0, sequential_access_counter - 1)