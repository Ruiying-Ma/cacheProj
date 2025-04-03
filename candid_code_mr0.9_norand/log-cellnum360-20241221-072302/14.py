# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
CLEANUP_THRESHOLD = 5  # Example threshold for cleanup counter
INITIAL_ALIGNMENT_SCORE = 1  # Initial score for new objects
STATE_RETENTION_IMPORTANCE = 10  # Example threshold for state retention

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a cache alignment score for each cache line, an index mapping table for quick lookup, a cleanup counter for each cache line, and a state retention flag indicating the importance of retaining the data.
alignment_scores = defaultdict(lambda: INITIAL_ALIGNMENT_SCORE)
cleanup_counters = defaultdict(int)
state_retention_flags = defaultdict(bool)
index_mapping_table = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache line with the lowest cache alignment score, prioritizing lines with a cleanup counter above a certain threshold, and considering the state retention flag to avoid evicting critical data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        if state_retention_flags[key]:
            continue
        if cleanup_counters[key] > CLEANUP_THRESHOLD:
            if alignment_scores[key] < min_score:
                min_score = alignment_scores[key]
                candid_obj_key = key
    if candid_obj_key is None:
        for key, cached_obj in cache_snapshot.cache.items():
            if alignment_scores[key] < min_score:
                min_score = alignment_scores[key]
                candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the cache alignment score of the accessed line is incremented, the cleanup counter is reset to zero, and the state retention flag is evaluated to determine if it should be adjusted based on access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    alignment_scores[obj.key] += 1
    cleanup_counters[obj.key] = 0
    if alignment_scores[obj.key] > STATE_RETENTION_IMPORTANCE:
        state_retention_flags[obj.key] = True

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the cache alignment score is initialized based on the object's expected access pattern, the cleanup counter is set to zero, and the state retention flag is set based on the initial importance of the data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    alignment_scores[obj.key] = INITIAL_ALIGNMENT_SCORE
    cleanup_counters[obj.key] = 0
    state_retention_flags[obj.key] = False
    index_mapping_table[obj.key] = obj

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the index mapping table is updated to remove the evicted entry, the cleanup counter for the evicted line is reset, and the state retention flag is cleared to prepare the line for future use.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in index_mapping_table:
        del index_mapping_table[evicted_obj.key]
    cleanup_counters[evicted_obj.key] = 0
    state_retention_flags[evicted_obj.key] = False