# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
SATURATE_LIMIT = 5
ACCESS_THRESHOLD = 3

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a 'recently accessed' segment and a 'frequently accessed' segment. Each segment uses a Clock algorithm for traversal. A Count Bloom Filter is used to approximate the access frequency of objects, and each object has an associated saturate counter to track its access count up to a predefined limit.
recently_accessed = deque()
frequently_accessed = deque()
saturate_counters = defaultdict(int)
count_bloom_filter = defaultdict(int)
clock_hand_recent = 0
clock_hand_frequent = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first attempts to evict an object from the 'recently accessed' segment using the Clock algorithm. If no suitable victim is found, it then attempts to evict from the 'frequently accessed' segment. The Count Bloom Filter helps identify objects with low access frequency, and the saturate counter ensures that objects with high but outdated access counts are not unfairly retained.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global clock_hand_recent, clock_hand_frequent
    candid_obj_key = None
    
    # Try to evict from recently accessed segment
    for _ in range(len(recently_accessed)):
        key = recently_accessed[clock_hand_recent]
        if count_bloom_filter[key] < ACCESS_THRESHOLD:
            candid_obj_key = key
            break
        clock_hand_recent = (clock_hand_recent + 1) % len(recently_accessed)
    
    # If no suitable victim found, try to evict from frequently accessed segment
    if candid_obj_key is None:
        for _ in range(len(frequently_accessed)):
            key = frequently_accessed[clock_hand_frequent]
            if count_bloom_filter[key] < ACCESS_THRESHOLD:
                candid_obj_key = key
                break
            clock_hand_frequent = (clock_hand_frequent + 1) % len(frequently_accessed)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the object's saturate counter is incremented if it is below the predefined limit. The Count Bloom Filter is updated to reflect the increased access frequency. If the object is in the 'recently accessed' segment and its access frequency crosses a threshold, it is moved to the 'frequently accessed' segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    if saturate_counters[key] < SATURATE_LIMIT:
        saturate_counters[key] += 1
    count_bloom_filter[key] += 1
    
    if key in recently_accessed and count_bloom_filter[key] >= ACCESS_THRESHOLD:
        recently_accessed.remove(key)
        frequently_accessed.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is placed in the 'recently accessed' segment with its saturate counter initialized to 1. The Count Bloom Filter is updated to reflect the new object's access frequency. The Clock hand is advanced to the next position in the 'recently accessed' segment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    recently_accessed.append(key)
    saturate_counters[key] = 1
    count_bloom_filter[key] = 1
    global clock_hand_recent
    clock_hand_recent = (clock_hand_recent + 1) % len(recently_accessed)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the Count Bloom Filter is updated to remove the object's access frequency. The Clock hand is advanced to the next position in the segment from which the object was evicted. If the evicted object was in the 'frequently accessed' segment, the policy checks if any objects in the 'recently accessed' segment should be promoted based on their access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in recently_accessed:
        recently_accessed.remove(key)
        global clock_hand_recent
        clock_hand_recent = clock_hand_recent % len(recently_accessed) if recently_accessed else 0
    elif key in frequently_accessed:
        frequently_accessed.remove(key)
        global clock_hand_frequent
        clock_hand_frequent = clock_hand_frequent % len(frequently_accessed) if frequently_accessed else 0
    
    del count_bloom_filter[key]
    del saturate_counters[key]
    
    # Check if any objects in the 'recently accessed' segment should be promoted
    for key in list(recently_accessed):
        if count_bloom_filter[key] >= ACCESS_THRESHOLD:
            recently_accessed.remove(key)
            frequently_accessed.append(key)