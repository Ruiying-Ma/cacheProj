# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
BLOOM_FILTER_SIZE = 1000  # Size of the Count Bloom Filter

# Put the metadata specifically maintained by the policy below. The policy maintains a Count Bloom Filter to approximate the access frequency of each object and an LRU queue to track the recency of access for each object.
count_bloom_filter = defaultdict(int)  # Count Bloom Filter to track access frequency
lru_queue = deque()  # LRU queue to track recency of access

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first identifying the least frequently accessed objects using the Count Bloom Filter. Among these, it selects the least-recently-used object from the LRU queue for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_access_count = float('inf')
    for key in lru_queue:
        if count_bloom_filter[key] < min_access_count:
            min_access_count = count_bloom_filter[key]
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access count for the object in the Count Bloom Filter and moves the object to the front of the LRU queue to mark it as most recently used.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter[obj.key] += 1
    lru_queue.remove(obj.key)
    lru_queue.appendleft(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its access count in the Count Bloom Filter and adds the object to the front of the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter[obj.key] = 1
    lru_queue.appendleft(obj.key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an object, the policy decrements the access count for the object in the Count Bloom Filter and removes the object from the LRU queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    count_bloom_filter[evicted_obj.key] -= 1
    if count_bloom_filter[evicted_obj.key] <= 0:
        del count_bloom_filter[evicted_obj.key]
    lru_queue.remove(evicted_obj.key)