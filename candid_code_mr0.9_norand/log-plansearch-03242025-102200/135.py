# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.

from collections import deque, defaultdict

# Put tunable constant parameters below
PROBATION_SEGMENT_SIZE_LIMIT = 0.5  # Fraction of the total cache capacity allocated to the probation segment
FREQUENCY_THRESHOLD = 2  # Threshold for promoting an object from probation to protected

# Put the metadata specifically maintained by the policy below. The policy maintains a segmented cache with two segments: a 'probation' segment for newly inserted objects and a 'protected' segment for frequently accessed objects. It uses a Count Bloom Filter to approximate the access frequency of each object, an LFU queue for the 'protected' segment, and an LRU queue for the 'probation' segment.

probation_segment = deque()  # LRU queue for the probation segment
protected_segment = defaultdict(int)  # LFU queue for the protected segment
count_bloom_filter = defaultdict(int)  # Count Bloom Filter to approximate access frequency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first attempts to evict objects from the 'probation' segment using the LRU queue. If the 'probation' segment is empty, it evicts the least frequently used object from the 'protected' segment using the LFU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if probation_segment:
        candid_obj_key = probation_segment.popleft()
    else:
        candid_obj_key = min(protected_segment, key=protected_segment.get)
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the object's count in the Count Bloom Filter. If the object is in the 'probation' segment and its frequency exceeds a threshold, it is promoted to the 'protected' segment and moved to the LFU queue. If the object is already in the 'protected' segment, its position in the LFU queue is updated.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter[obj.key] += 1
    if obj.key in probation_segment:
        if count_bloom_filter[obj.key] > FREQUENCY_THRESHOLD:
            probation_segment.remove(obj.key)
            protected_segment[obj.key] = count_bloom_filter[obj.key]
    elif obj.key in protected_segment:
        protected_segment[obj.key] = count_bloom_filter[obj.key]

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy adds it to the 'probation' segment and the LRU queue. The object's count in the Count Bloom Filter is initialized. If the 'probation' segment exceeds its size limit, the least recently used object is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    probation_segment.append(obj.key)
    count_bloom_filter[obj.key] = 1
    probation_size_limit = int(cache_snapshot.capacity * PROBATION_SEGMENT_SIZE_LIMIT)
    while sum(cache_snapshot.cache[key].size for key in probation_segment) > probation_size_limit:
        evicted_key = probation_segment.popleft()
        del count_bloom_filter[evicted_key]

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes it from the Count Bloom Filter, the LRU queue (if it was in the 'probation' segment), or the LFU queue (if it was in the 'protected' segment). The metadata is updated to reflect the current state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in probation_segment:
        probation_segment.remove(evicted_obj.key)
    elif evicted_obj.key in protected_segment:
        del protected_segment[evicted_obj.key]
    del count_bloom_filter[evicted_obj.key]