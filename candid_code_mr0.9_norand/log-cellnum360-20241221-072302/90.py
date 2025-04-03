# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY_SCORE = 1.0
PRIORITY_INCREMENT = 1.0
AGE_DECAY_FACTOR = 0.9

# Put the metadata specifically maintained by the policy below. The policy maintains a priority score for each cache entry, a temporal window counter, and a resource usage metric. The priority score is dynamically recalculated based on access frequency and recency, while the temporal window counter tracks the age of entries. Resource usage metric monitors the cache's current load and efficiency.
priority_scores = defaultdict(lambda: INITIAL_PRIORITY_SCORE)
temporal_window_counters = defaultdict(int)
resource_usage_metric = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying entries with the lowest priority score, considering both their age and resource usage. If multiple candidates have similar scores, the entry with the highest resource usage is chosen to optimize cache efficiency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority_score = float('inf')
    max_resource_usage = -1

    for key, cached_obj in cache_snapshot.cache.items():
        priority_score = priority_scores[key]
        age = temporal_window_counters[key]
        resource_usage = cached_obj.size

        # Calculate effective score considering age and resource usage
        effective_score = priority_score * (AGE_DECAY_FACTOR ** age)

        if (effective_score < min_priority_score) or (effective_score == min_priority_score and resource_usage > max_resource_usage):
            min_priority_score = effective_score
            max_resource_usage = resource_usage
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is increased, factoring in its recency and frequency of access. The temporal window counter is reset to zero for the hit entry, and the resource usage metric is adjusted to reflect the current cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    priority_scores[key] += PRIORITY_INCREMENT
    temporal_window_counters[key] = 0
    # Resource usage metric is already reflected in cache_snapshot.size

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial priority score based on predicted access patterns and sets the temporal window counter to zero. The resource usage metric is updated to account for the new entry's impact on cache load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    priority_scores[key] = INITIAL_PRIORITY_SCORE
    temporal_window_counters[key] = 0
    # Resource usage metric is already reflected in cache_snapshot.size

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the priority scores of remaining entries to ensure balance, increments the temporal window counters for all entries, and updates the resource usage metric to reflect the reduced load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in priority_scores:
        del priority_scores[evicted_key]
        del temporal_window_counters[evicted_key]

    for key in cache_snapshot.cache:
        temporal_window_counters[key] += 1
    # Resource usage metric is already reflected in cache_snapshot.size