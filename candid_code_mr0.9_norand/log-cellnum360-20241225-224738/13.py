# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.7
RECENCY_WEIGHT = 0.3

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including access frequency, recency of access, and a dynamic priority score for each cache entry. It also tracks the average latency of cache accesses and the current hit ratio to adaptively tune the cache behavior.
access_frequency = defaultdict(int)
recency_of_access = {}
dynamic_priority_score = {}
average_latency = 0
hit_ratio = 0

def calculate_priority_score(key):
    frequency = access_frequency[key]
    recency = recency_of_access[key]
    return FREQUENCY_WEIGHT * frequency + RECENCY_WEIGHT * recency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim based on the lowest dynamic priority score, which is calculated using a weighted combination of access frequency and recency. Entries with lower access frequency and older recency are more likely to be evicted, but the weights are adjusted based on current hit ratio and latency metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_priority_score = float('inf')
    
    for key in cache_snapshot.cache:
        score = calculate_priority_score(key)
        if score < min_priority_score:
            min_priority_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency of the accessed entry are updated. The dynamic priority score is recalculated to reflect the increased recency and frequency. The average latency and hit ratio metrics are also updated to reflect the improved performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] += 1
    recency_of_access[key] = cache_snapshot.access_count
    dynamic_priority_score[key] = calculate_priority_score(key)
    
    # Update hit ratio
    hit_ratio = cache_snapshot.hit_count / cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access frequency and recency to default values and calculates an initial dynamic priority score. The average latency and hit ratio are recalibrated to account for the new entry's potential impact on cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    recency_of_access[key] = cache_snapshot.access_count
    dynamic_priority_score[key] = calculate_priority_score(key)
    
    # Recalculate hit ratio
    hit_ratio = cache_snapshot.hit_count / cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the average latency and hit ratio to reflect the removal of the entry. It also adjusts the weights used in the dynamic priority score calculation to optimize for the current cache performance metrics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in access_frequency:
        del access_frequency[key]
    if key in recency_of_access:
        del recency_of_access[key]
    if key in dynamic_priority_score:
        del dynamic_priority_score[key]
    
    # Recalculate hit ratio
    hit_ratio = cache_snapshot.hit_count / cache_snapshot.access_count