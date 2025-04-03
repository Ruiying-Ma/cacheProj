# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PRIORITY_INCREMENT = 1.0
INITIAL_LATENCY_ESTIMATE = 1.0
LOAD_BALANCE_FACTOR = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic priority score for each cache entry, a historical access latency record, and a load balance factor for different cache regions.
priority_scores = defaultdict(float)
access_latency = defaultdict(float)
load_balance = LOAD_BALANCE_FACTOR

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest priority score, recalibrated by recent access latency and load balance factor, ensuring minimal impact on performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        recalibrated_score = (priority_scores[key] / (access_latency[key] + 1)) * load_balance
        if recalibrated_score < min_score:
            min_score = recalibrated_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the priority score of the accessed entry is increased, the access latency record is updated with the latest latency, and the load balance factor is adjusted to reflect the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    priority_scores[obj.key] += PRIORITY_INCREMENT
    access_latency[obj.key] = cache_snapshot.access_count - access_latency[obj.key]
    # Adjust load balance factor if needed (not specified how, so keeping it constant)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority score based on the average priority of existing entries, updates the access latency record with an initial estimate, and recalibrates the load balance factor to accommodate the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    if cache_snapshot.cache:
        average_priority = sum(priority_scores.values()) / len(cache_snapshot.cache)
    else:
        average_priority = 0
    priority_scores[obj.key] = average_priority
    access_latency[obj.key] = INITIAL_LATENCY_ESTIMATE
    # Recalibrate load balance factor if needed (not specified how, so keeping it constant)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the priority scores of remaining entries to ensure dynamic reordering, updates the access latency record to remove the evicted entry's data, and adjusts the load balance factor to reflect the reduced cache load.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    if evicted_obj.key in priority_scores:
        del priority_scores[evicted_obj.key]
    if evicted_obj.key in access_latency:
        del access_latency[evicted_obj.key]
    # Recalibrate load balance factor if needed (not specified how, so keeping it constant)