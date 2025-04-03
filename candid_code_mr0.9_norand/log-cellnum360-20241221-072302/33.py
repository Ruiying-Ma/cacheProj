# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_PRIORITY = 1
DEFAULT_ADAPTIVE_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical priority list for cache entries, a priority inversion counter, a buffer for pending operations, and an adaptive scheduling score for each entry.
priority_list = defaultdict(lambda: DEFAULT_PRIORITY)
priority_inversion_counter = defaultdict(int)
adaptive_scheduling_score = defaultdict(lambda: DEFAULT_ADAPTIVE_SCORE)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by first considering entries with the lowest priority in the hierarchy, then checking for entries with high priority inversion counters, and finally using the adaptive scheduling score to break ties.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    max_inversion = -1
    min_score = float('inf')

    for key, cached_obj in cache_snapshot.cache.items():
        priority = priority_list[key]
        inversion = priority_inversion_counter[key]
        score = adaptive_scheduling_score[key]

        if (priority < min_priority or
            (priority == min_priority and inversion > max_inversion) or
            (priority == min_priority and inversion == max_inversion and score < min_score)):
            min_priority = priority
            max_inversion = inversion
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the entry's priority is increased in the hierarchy, the priority inversion counter is reset, and the adaptive scheduling score is adjusted based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    priority_list[key] += 1
    priority_inversion_counter[key] = 0
    adaptive_scheduling_score[key] *= 1.1  # Example adjustment, can be tuned

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the entry is assigned a default priority in the hierarchy, its priority inversion counter is initialized to zero, and its adaptive scheduling score is set based on initial access predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    priority_list[key] = DEFAULT_PRIORITY
    priority_inversion_counter[key] = 0
    adaptive_scheduling_score[key] = DEFAULT_ADAPTIVE_SCORE

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy updates the hierarchical priority list to reflect the removal, adjusts the priority inversion counters of remaining entries, and recalibrates the adaptive scheduling scores to account for the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    del priority_list[evicted_key]
    del priority_inversion_counter[evicted_key]
    del adaptive_scheduling_score[evicted_key]

    for key in cache_snapshot.cache:
        priority_inversion_counter[key] += 1
        adaptive_scheduling_score[key] *= 0.9  # Example adjustment, can be tuned