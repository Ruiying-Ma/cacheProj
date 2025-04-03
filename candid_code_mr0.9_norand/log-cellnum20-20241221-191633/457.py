# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
WEIGHT_CYCLIC_INDEX = 1.0
WEIGHT_LOAD_VARIANCE = 1.0
WEIGHT_TIMESTAMP = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a cyclic permutation index for cache entries, a load variance counter to track access frequency variance, a timestamp marker for each entry to record the last access time, and a hybrid eviction score combining these factors.
cyclic_permutation_index = deque()  # To maintain the order of cache entries
load_variance_counter = defaultdict(int)  # To track access frequency variance
timestamp_marker = {}  # To record the last access time for each entry

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim by calculating a hybrid eviction score for each entry, which is a weighted combination of the cyclic permutation index, load variance, and timestamp marker. The entry with the highest score is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    max_score = float('-inf')
    
    for key in cache_snapshot.cache:
        cyclic_index = cyclic_permutation_index.index(key)
        load_variance = load_variance_counter[key]
        timestamp = timestamp_marker[key]
        
        # Calculate hybrid eviction score
        score = (WEIGHT_CYCLIC_INDEX * cyclic_index +
                 WEIGHT_LOAD_VARIANCE * load_variance +
                 WEIGHT_TIMESTAMP * (cache_snapshot.access_count - timestamp))
        
        if score > max_score:
            max_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the cyclic permutation index is rotated to bring the accessed entry to the front, the load variance counter is adjusted to reflect the increased access frequency, and the timestamp marker is updated to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    # Rotate cyclic permutation index to bring the accessed entry to the front
    cyclic_permutation_index.remove(key)
    cyclic_permutation_index.appendleft(key)
    
    # Adjust load variance counter
    load_variance_counter[key] += 1
    
    # Update timestamp marker
    timestamp_marker[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the cyclic permutation index is updated to include the new entry, the load variance counter is initialized for the new entry, and the timestamp marker is set to the current time.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    # Update cyclic permutation index to include the new entry
    cyclic_permutation_index.appendleft(key)
    
    # Initialize load variance counter for the new entry
    load_variance_counter[key] = 1
    
    # Set timestamp marker to the current time
    timestamp_marker[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the cyclic permutation index is adjusted to remove the evicted entry, the load variance counter is recalculated to exclude the evicted entry's data, and the timestamp markers are left unchanged for remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    # Adjust cyclic permutation index to remove the evicted entry
    cyclic_permutation_index.remove(evicted_key)
    
    # Recalculate load variance counter to exclude the evicted entry's data
    del load_variance_counter[evicted_key]
    
    # Timestamp markers are left unchanged for remaining entries