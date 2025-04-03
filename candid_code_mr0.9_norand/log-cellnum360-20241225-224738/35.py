# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
BASELINE_PRIORITY = 1.0
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains metadata for each cache entry, including access frequency, recency of access, and a dynamic priority score. It also tracks overall cache usage patterns and resource availability to adjust priorities proactively.
metadata = {
    'frequency': defaultdict(lambda: BASELINE_FREQUENCY),
    'recency': {},
    'priority': defaultdict(lambda: BASELINE_PRIORITY)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim based on a combination of the lowest dynamic priority score and the longest time since last access, while ensuring consistency by considering the overall cache usage patterns and resource availability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    oldest_recency = -1

    for key, cached_obj in cache_snapshot.cache.items():
        priority = metadata['priority'][key]
        recency = metadata['recency'][key]

        if (priority < min_priority) or (priority == min_priority and recency < oldest_recency):
            min_priority = priority
            oldest_recency = recency
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the accessed entry are updated, and its dynamic priority score is recalculated based on current cache usage patterns and resource availability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['frequency'][key] += 1
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['priority'][key] = (FREQUENCY_WEIGHT * metadata['frequency'][key] +
                                 RECENCY_WEIGHT * (cache_snapshot.access_count - metadata['recency'][key]))

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a baseline access frequency, recency, and priority score, then adjusts these values based on current cache usage patterns and resource availability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    metadata['frequency'][key] = BASELINE_FREQUENCY
    metadata['recency'][key] = cache_snapshot.access_count
    metadata['priority'][key] = BASELINE_PRIORITY

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the dynamic priority scores of remaining entries to ensure consistency and adapts to any changes in resource availability, maintaining an optimal balance in the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    for key in cache_snapshot.cache:
        metadata['priority'][key] = (FREQUENCY_WEIGHT * metadata['frequency'][key] +
                                     RECENCY_WEIGHT * (cache_snapshot.access_count - metadata['recency'][key]))