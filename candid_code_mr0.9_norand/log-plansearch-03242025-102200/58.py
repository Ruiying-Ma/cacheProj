# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import defaultdict, deque

# Put tunable constant parameters below
NEW_THRESHOLD = 2
PROBATION_THRESHOLD = 5

# Put the metadata specifically maintained by the policy below. The policy maintains three segments: a 'new' segment for newly inserted objects, a 'frequent' segment for frequently accessed objects, and a 'probation' segment for objects that have been accessed more than once but are not frequently accessed. Additionally, it uses a Count Bloom Filter to approximate the access frequency of each object and an LFU queue to track the least frequently used objects.
new_segment = deque()
probation_segment = deque()
frequent_segment = deque()
count_bloom_filter = defaultdict(int)
lfu_queue = defaultdict(deque)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first attempts to evict objects from the 'new' segment. If the 'new' segment is empty, it evicts from the 'probation' segment based on the LFU queue. If both segments are empty, it evicts from the 'frequent' segment, again based on the LFU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    if new_segment:
        candid_obj_key = new_segment.popleft().key
    elif probation_segment:
        min_freq = min(lfu_queue.keys())
        candid_obj_key = lfu_queue[min_freq].popleft().key
        if not lfu_queue[min_freq]:
            del lfu_queue[min_freq]
    elif frequent_segment:
        min_freq = min(lfu_queue.keys())
        candid_obj_key = lfu_queue[min_freq].popleft().key
        if not lfu_queue[min_freq]:
            del lfu_queue[min_freq]
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the object's count in the Count Bloom Filter. If the object is in the 'new' segment and its count exceeds a threshold, it is moved to the 'probation' segment. If the object is in the 'probation' segment and its count exceeds a higher threshold, it is moved to the 'frequent' segment. The LFU queue is updated to reflect the new access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter[obj.key] += 1
    if obj in new_segment:
        if count_bloom_filter[obj.key] > NEW_THRESHOLD:
            new_segment.remove(obj)
            probation_segment.append(obj)
            lfu_queue[1].append(obj)
    elif obj in probation_segment:
        if count_bloom_filter[obj.key] > PROBATION_THRESHOLD:
            probation_segment.remove(obj)
            frequent_segment.append(obj)
        else:
            lfu_queue[1].append(obj)
    elif obj in frequent_segment:
        lfu_queue[1].append(obj)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy places it in the 'new' segment and initializes its count in the Count Bloom Filter. If the 'new' segment is full, it evicts the least recently inserted object from this segment. The LFU queue is updated to include the new object with its initial frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    new_segment.append(obj)
    count_bloom_filter[obj.key] = 1
    lfu_queue[1].append(obj)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy removes it from the Count Bloom Filter and the LFU queue. If the object was in the 'new' segment, no further action is needed. If it was in the 'probation' or 'frequent' segment, the policy ensures that the segments are balanced by potentially promoting objects from 'new' to 'probation' or from 'probation' to 'frequent' based on their access counts.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del count_bloom_filter[evicted_obj.key]
    for freq in lfu_queue:
        if evicted_obj in lfu_queue[freq]:
            lfu_queue[freq].remove(evicted_obj)
            if not lfu_queue[freq]:
                del lfu_queue[freq]
            break
    if evicted_obj in probation_segment:
        probation_segment.remove(evicted_obj)
    elif evicted_obj in frequent_segment:
        frequent_segment.remove(evicted_obj)
    # Balance segments if necessary
    if len(new_segment) > 0 and len(probation_segment) < len(new_segment):
        obj_to_promote = new_segment.popleft()
        probation_segment.append(obj_to_promote)
        lfu_queue[1].append(obj_to_promote)
    if len(probation_segment) > 0 and len(frequent_segment) < len(probation_segment):
        obj_to_promote = probation_segment.popleft()
        frequent_segment.append(obj_to_promote)
        lfu_queue[1].append(obj_to_promote)