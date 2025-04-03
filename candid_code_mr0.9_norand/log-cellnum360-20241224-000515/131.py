# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
INITIAL_FILTER_SCORE = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a sequential access list, a temporal access frequency map, an adaptive filter score for each item, and a load distribution counter for cache segments.
sequential_access_list = deque()
temporal_access_frequency = defaultdict(int)
adaptive_filter_scores = defaultdict(lambda: INITIAL_FILTER_SCORE)
load_distribution_counter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying items with the lowest adaptive filter score, then selecting among them the one with the least recent access based on the sequential access list.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Find the minimum adaptive filter score
    min_score = min(adaptive_filter_scores[key] for key in cache_snapshot.cache)
    
    # Filter keys with the minimum score
    candidates = [key for key in cache_snapshot.cache if adaptive_filter_scores[key] == min_score]
    
    # Find the least recently accessed among candidates
    for key in sequential_access_list:
        if key in candidates:
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the temporal access frequency map by incrementing the frequency count for the accessed item, adjusts the adaptive filter score based on recent access patterns, and updates the sequential access list to reflect the most recent access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temporal_access_frequency[key] += 1
    adaptive_filter_scores[key] = temporal_access_frequency[key] / (cache_snapshot.access_count + 1)
    
    # Update sequential access list
    if key in sequential_access_list:
        sequential_access_list.remove(key)
    sequential_access_list.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its temporal access frequency to a baseline value, assigns an initial adaptive filter score based on current cache load, and appends it to the end of the sequential access list.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    temporal_access_frequency[key] = BASELINE_FREQUENCY
    adaptive_filter_scores[key] = INITIAL_FILTER_SCORE
    sequential_access_list.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the adaptive filter scores for remaining items to reflect the new cache state, updates the load distribution counter to ensure balanced cache segment usage, and removes the evicted item from the sequential access list.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in sequential_access_list:
        sequential_access_list.remove(evicted_key)
    
    # Recalibrate adaptive filter scores
    for key in cache_snapshot.cache:
        adaptive_filter_scores[key] = temporal_access_frequency[key] / (cache_snapshot.access_count + 1)
    
    # Update load distribution counter
    load_distribution_counter[evicted_key] -= 1