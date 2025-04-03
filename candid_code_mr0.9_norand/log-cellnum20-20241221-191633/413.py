# Import anything you need below
import heapq
from collections import defaultdict, deque

# Put tunable constant parameters below
DEFAULT_PRIORITY = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a hash map for quick access to cache entries, a priority queue to manage access priorities, and a transaction log to ensure integrity. Each entry in the hash map includes a priority level and a timestamp of the last access.
cache_metadata = {
    'hash_map': {},  # key -> (priority, timestamp)
    'priority_queue': [],  # (priority, timestamp, key)
    'transaction_log': deque()  # log of actions
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the lowest priority entry in the priority queue. In case of a tie, it chooses the oldest entry based on the timestamp. This ensures that less critical and less recently used data is evicted first.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    while cache_metadata['priority_queue']:
        priority, timestamp, key = heapq.heappop(cache_metadata['priority_queue'])
        if key in cache_metadata['hash_map'] and cache_metadata['hash_map'][key] == (priority, timestamp):
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the timestamp of the accessed entry in the hash map and increases its priority in the priority queue. The transaction log records this access to maintain integrity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    if key in cache_metadata['hash_map']:
        priority, _ = cache_metadata['hash_map'][key]
        new_priority = priority + 1
        new_timestamp = cache_snapshot.access_count
        cache_metadata['hash_map'][key] = (new_priority, new_timestamp)
        heapq.heappush(cache_metadata['priority_queue'], (new_priority, new_timestamp, key))
        cache_metadata['transaction_log'].append(f"Hit: {key}")

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns it a default priority and records the current timestamp in the hash map. The new entry is added to the priority queue, and the insertion is logged in the transaction log.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    priority = DEFAULT_PRIORITY
    timestamp = cache_snapshot.access_count
    cache_metadata['hash_map'][key] = (priority, timestamp)
    heapq.heappush(cache_metadata['priority_queue'], (priority, timestamp, key))
    cache_metadata['transaction_log'].append(f"Insert: {key}")

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the entry from the hash map and priority queue. The transaction log is updated to reflect the eviction, ensuring that the cache state remains consistent and recoverable.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in cache_metadata['hash_map']:
        del cache_metadata['hash_map'][evicted_key]
    # No need to remove from priority_queue as it will be ignored in future evictions
    cache_metadata['transaction_log'].append(f"Evict: {evicted_key}")