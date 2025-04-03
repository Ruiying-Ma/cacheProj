# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
DEFAULT_PRIORITY = 1
DEFAULT_SEQUENTIAL_ACCESS = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic priority list for each cache item, a load factor indicating current cache pressure, and a sequential access counter for each item to track access patterns.
priority = defaultdict(lambda: DEFAULT_PRIORITY)
sequential_access = defaultdict(lambda: DEFAULT_SEQUENTIAL_ACCESS)
load_factor = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by dynamically sorting items based on a combination of their priority, load factor, and sequential access counter, prioritizing items with lower priority and sequential access.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        score = (priority[key] + sequential_access[key]) * load_factor
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the item's priority is increased, its sequential access counter is incremented, and the load factor is adjusted to reflect the current cache pressure.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    priority[obj.key] += 1
    sequential_access[obj.key] += 1
    global load_factor
    load_factor = cache_snapshot.size / cache_snapshot.capacity

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its priority and sequential access counter to default values and recalculates the load factor to account for the new item.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    priority[obj.key] = DEFAULT_PRIORITY
    sequential_access[obj.key] = DEFAULT_SEQUENTIAL_ACCESS
    global load_factor
    load_factor = cache_snapshot.size / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy decreases the load factor to reflect reduced cache pressure and adjusts the priorities of remaining items to ensure dynamic sorting remains effective.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    global load_factor
    load_factor = cache_snapshot.size / cache_snapshot.capacity
    del priority[evicted_obj.key]
    del sequential_access[evicted_obj.key]
    for key in cache_snapshot.cache:
        priority[key] = max(DEFAULT_PRIORITY, priority[key] - 1)