# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
MAX_CANDIDATES = 5  # Maximum number of candidates to consider for eviction

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, a hierarchical level indicator for each cache entry, and a dynamic threshold value for each level that scales based on usage analytics.
metadata = {
    'access_frequency': defaultdict(int),
    'recency': defaultdict(int),
    'hierarchy_level': defaultdict(int),
    'thresholds': defaultdict(lambda: 1),  # Default threshold for each level
    'level_objects': defaultdict(deque)  # Objects in each hierarchy level
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy uses hierarchical eviction by first checking the lowest hierarchy level for eviction candidates. Within a level, it selects the entry with the lowest access frequency and recency score, ensuring bounded latency by limiting the search to a fixed number of candidates.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    for level in sorted(metadata['level_objects'].keys()):
        candidates = list(metadata['level_objects'][level])[:MAX_CANDIDATES]
        if not candidates:
            continue
        # Find the candidate with the lowest access frequency and recency score
        candid_obj_key = min(
            candidates,
            key=lambda k: (metadata['access_frequency'][k], metadata['recency'][k])
        )
        if candid_obj_key:
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the accessed entry are incremented. If the entry's frequency surpasses the current level's threshold, it is promoted to a higher hierarchy level, and the threshold is adjusted based on overall cache usage patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    metadata['access_frequency'][obj_key] += 1
    metadata['recency'][obj_key] = cache_snapshot.access_count

    current_level = metadata['hierarchy_level'][obj_key]
    if metadata['access_frequency'][obj_key] > metadata['thresholds'][current_level]:
        # Promote to a higher level
        metadata['level_objects'][current_level].remove(obj_key)
        metadata['hierarchy_level'][obj_key] += 1
        new_level = metadata['hierarchy_level'][obj_key]
        metadata['level_objects'][new_level].append(obj_key)
        # Adjust threshold
        metadata['thresholds'][current_level] = max(
            metadata['thresholds'][current_level], metadata['access_frequency'][obj_key]
        )

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it to the lowest hierarchy level with initial access frequency and recency scores. The threshold for this level is recalibrated based on the current cache usage analytics to maintain optimal scaling.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    obj_key = obj.key
    metadata['access_frequency'][obj_key] = 1
    metadata['recency'][obj_key] = cache_snapshot.access_count
    metadata['hierarchy_level'][obj_key] = 0
    metadata['level_objects'][0].append(obj_key)
    # Recalibrate threshold for level 0
    metadata['thresholds'][0] = max(
        metadata['thresholds'][0], metadata['access_frequency'][obj_key]
    )

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the threshold for the affected hierarchy level, taking into account the recent usage analytics to ensure the threshold remains adaptive and reflective of current access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    level = metadata['hierarchy_level'][evicted_key]
    metadata['level_objects'][level].remove(evicted_key)
    del metadata['access_frequency'][evicted_key]
    del metadata['recency'][evicted_key]
    del metadata['hierarchy_level'][evicted_key]
    
    # Recalculate threshold for the affected level
    if metadata['level_objects'][level]:
        metadata['thresholds'][level] = max(
            metadata['access_frequency'][k] for k in metadata['level_objects'][level]
        )
    else:
        metadata['thresholds'][level] = 1  # Reset to default if no objects