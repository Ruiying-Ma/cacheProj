# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for frequency in priority score
BETA = 0.3   # Weight for recency in priority score
GAMMA = 0.2  # Weight for load balance factor in priority score

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic priority score for each cache entry, a load balance factor for different cache regions, and a frequency count of accesses. The priority score is a composite of recent access frequency, time since last access, and load balance factor.
frequency_count = defaultdict(int)
last_access_time = {}
priority_score = {}
load_balance_factor = 1.0

def calculate_priority_score(key, cache_snapshot):
    freq = frequency_count[key]
    recency = cache_snapshot.access_count - last_access_time[key]
    return ALPHA * freq - BETA * recency + GAMMA * load_balance_factor

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by choosing the entry with the lowest dynamic priority score, ensuring that frequently accessed and recently used items are retained while balancing the load across cache regions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_priority = float('inf')
    for key in cache_snapshot.cache:
        score = calculate_priority_score(key, cache_snapshot)
        if score < min_priority:
            min_priority = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency count for the accessed entry is incremented, and its dynamic priority score is recalculated to reflect the increased frequency and recent access. The load balance factor is adjusted if necessary to maintain even distribution.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    frequency_count[key] += 1
    last_access_time[key] = cache_snapshot.access_count
    priority_score[key] = calculate_priority_score(key, cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its frequency count to one and calculates its initial dynamic priority score. The load balance factor is updated to account for the new distribution of entries across cache regions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    frequency_count[key] = 1
    last_access_time[key] = cache_snapshot.access_count
    priority_score[key] = calculate_priority_score(key, cache_snapshot)
    # Update load balance factor if necessary
    load_balance_factor = len(cache_snapshot.cache) / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalculates the load balance factor to reflect the removal of the entry and adjusts the dynamic priority scores of remaining entries if necessary to maintain balance and optimize frequency considerations.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    # Remove metadata for evicted object
    if evicted_key in frequency_count:
        del frequency_count[evicted_key]
    if evicted_key in last_access_time:
        del last_access_time[evicted_key]
    if evicted_key in priority_score:
        del priority_score[evicted_key]
    
    # Recalculate load balance factor
    load_balance_factor = len(cache_snapshot.cache) / cache_snapshot.capacity
    
    # Adjust priority scores if necessary
    for key in cache_snapshot.cache:
        priority_score[key] = calculate_priority_score(key, cache_snapshot)