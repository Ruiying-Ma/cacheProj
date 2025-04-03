# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict, deque

# Put tunable constant parameters below
RECENTLY_ACCESSED_THRESHOLD = 5

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a 'recently accessed' segment and a 'frequently accessed' segment. It also maintains a clock hand for each segment and a Count Bloom Filter to approximate the access frequency of each object.
recently_accessed_segment = deque()
frequently_accessed_segment = deque()
recently_accessed_clock_hand = 0
frequently_accessed_clock_hand = 0
count_bloom_filter = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first checks the 'recently accessed' segment using the clock hand to find an object with the lowest access frequency as indicated by the Count Bloom Filter. If no suitable candidate is found, it then checks the 'frequently accessed' segment in a similar manner.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    global recently_accessed_clock_hand, frequently_accessed_clock_hand
    candid_obj_key = None

    # Check recently accessed segment
    for _ in range(len(recently_accessed_segment)):
        key = recently_accessed_segment[recently_accessed_clock_hand]
        if key in cache_snapshot.cache:
            if candid_obj_key is None or count_bloom_filter[key] < count_bloom_filter[candid_obj_key]:
                candid_obj_key = key
        recently_accessed_clock_hand = (recently_accessed_clock_hand + 1) % len(recently_accessed_segment)
        if candid_obj_key:
            break

    # If no suitable candidate found, check frequently accessed segment
    if candid_obj_key is None:
        for _ in range(len(frequently_accessed_segment)):
            key = frequently_accessed_segment[frequently_accessed_clock_hand]
            if key in cache_snapshot.cache:
                if candid_obj_key is None or count_bloom_filter[key] < count_bloom_filter[candid_obj_key]:
                    candid_obj_key = key
            frequently_accessed_clock_hand = (frequently_accessed_clock_hand + 1) % len(frequently_accessed_segment)
            if candid_obj_key:
                break

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access count in the Count Bloom Filter for the accessed object. If the object is in the 'recently accessed' segment and its access frequency exceeds a threshold, it is moved to the 'frequently accessed' segment. The clock hand for the respective segment is advanced.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    global recently_accessed_clock_hand, frequently_accessed_clock_hand
    count_bloom_filter[obj.key] += 1

    if obj.key in recently_accessed_segment:
        if count_bloom_filter[obj.key] > RECENTLY_ACCESSED_THRESHOLD:
            recently_accessed_segment.remove(obj.key)
            frequently_accessed_segment.append(obj.key)
        recently_accessed_clock_hand = (recently_accessed_clock_hand + 1) % len(recently_accessed_segment)
    elif obj.key in frequently_accessed_segment:
        frequently_accessed_clock_hand = (frequently_accessed_clock_hand + 1) % len(frequently_accessed_segment)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy places it in the 'recently accessed' segment and initializes its access count in the Count Bloom Filter. The clock hand for the 'recently accessed' segment is advanced.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    global recently_accessed_clock_hand
    recently_accessed_segment.append(obj.key)
    count_bloom_filter[obj.key] = 1
    recently_accessed_clock_hand = (recently_accessed_clock_hand + 1) % len(recently_accessed_segment)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy decrements the access count in the Count Bloom Filter for the evicted object. The clock hand for the respective segment is advanced to the next object.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    global recently_accessed_clock_hand, frequently_accessed_clock_hand
    if evicted_obj.key in recently_accessed_segment:
        recently_accessed_segment.remove(evicted_obj.key)
        recently_accessed_clock_hand = (recently_accessed_clock_hand + 1) % len(recently_accessed_segment)
    elif evicted_obj.key in frequently_accessed_segment:
        frequently_accessed_segment.remove(evicted_obj.key)
        frequently_accessed_clock_hand = (frequently_accessed_clock_hand + 1) % len(frequently_accessed_segment)
    count_bloom_filter[evicted_obj.key] -= 1