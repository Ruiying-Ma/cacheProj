# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
HISTORICAL_WEIGHT = 0.5
FREQUENCY_WEIGHT = 0.3
LOAD_DISTRIBUTION_WEIGHT = 0.2
PRIORITY_INCREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry based on historical access patterns, real-time access frequency, and load distribution metrics. It also tracks the last access time and a dynamic priority score that adapts based on system load and access trends.
historical_access_patterns = defaultdict(int)
real_time_access_frequency = defaultdict(int)
load_distribution_metrics = defaultdict(float)
last_access_time = defaultdict(int)
priority_score = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest predictive score, which is calculated using a weighted combination of historical access patterns, current access frequency, and load distribution. Entries with lower priority scores are more likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    lowest_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        predictive_score = (
            HISTORICAL_WEIGHT * historical_access_patterns[key] +
            FREQUENCY_WEIGHT * real_time_access_frequency[key] +
            LOAD_DISTRIBUTION_WEIGHT * load_distribution_metrics[key]
        )
        if predictive_score < lowest_score or (
            predictive_score == lowest_score and priority_score[key] < priority_score[candid_obj_key]
        ):
            lowest_score = predictive_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the predictive score of the accessed entry by incrementing its real-time access frequency and adjusting its priority score based on the current system load. The last access time is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    real_time_access_frequency[obj.key] += 1
    priority_score[obj.key] += PRIORITY_INCREMENT
    last_access_time[obj.key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score using initial access frequency and load distribution metrics. The priority score is set based on the current system load, and the last access time is recorded as the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    historical_access_patterns[obj.key] = 1
    real_time_access_frequency[obj.key] = 1
    load_distribution_metrics[obj.key] = obj.size / cache_snapshot.capacity
    priority_score[obj.key] = cache_snapshot.size / cache_snapshot.capacity
    last_access_time[obj.key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive scores of remaining entries by slightly increasing their priority scores to reflect reduced competition. It also updates load distribution metrics to account for the change in cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    for key in cache_snapshot.cache:
        priority_score[key] += PRIORITY_INCREMENT
        load_distribution_metrics[key] = cache_snapshot.cache[key].size / cache_snapshot.capacity

    # Clean up metadata for the evicted object
    if evicted_obj.key in historical_access_patterns:
        del historical_access_patterns[evicted_obj.key]
    if evicted_obj.key in real_time_access_frequency:
        del real_time_access_frequency[evicted_obj.key]
    if evicted_obj.key in load_distribution_metrics:
        del load_distribution_metrics[evicted_obj.key]
    if evicted_obj.key in last_access_time:
        del last_access_time[evicted_obj.key]
    if evicted_obj.key in priority_score:
        del priority_score[evicted_obj.key]