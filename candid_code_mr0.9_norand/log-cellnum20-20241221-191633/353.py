# Import anything you need below
from collections import deque, defaultdict
import bisect

# Put tunable constant parameters below

# Put the metadata specifically maintained by the policy below. The policy maintains a linear queue to track the order of access, a sequential access counter for each item, and a sorted list of items based on their access frequency.
access_queue = deque()  # Linear queue to track order of access
access_counters = defaultdict(int)  # Sequential access counter for each item
sorted_access_list = []  # Sorted list of items based on their access frequency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the item with the lowest access frequency from the sorted list. If there is a tie, it evicts the item that was accessed least recently according to the linear queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Find the item with the lowest access frequency
    min_freq = sorted_access_list[0][0]
    candidates = [key for freq, key in sorted_access_list if freq == min_freq]
    
    # Find the least recently used among the candidates
    for key in access_queue:
        if key in candidates:
            candid_obj_key = key
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the sequential access counter for the accessed item is incremented, and the item is moved to the end of the linear queue. The sorted list is updated to reflect the new access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Increment access counter
    access_counters[key] += 1
    
    # Update sorted list
    # Remove old entry
    old_entry = (access_counters[key] - 1, key)
    sorted_access_list.remove(old_entry)
    
    # Insert new entry
    new_entry = (access_counters[key], key)
    bisect.insort(sorted_access_list, new_entry)
    
    # Move to end of queue
    access_queue.remove(key)
    access_queue.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, it is added to the end of the linear queue with an initial access counter of one. The sorted list is updated to include the new item based on its access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    # Initialize access counter
    access_counters[key] = 1
    
    # Add to sorted list
    new_entry = (1, key)
    bisect.insort(sorted_access_list, new_entry)
    
    # Add to end of queue
    access_queue.append(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the item is removed from the linear queue and the sorted list. The sequential access counters of remaining items are unaffected.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    key = evicted_obj.key
    # Remove from queue
    access_queue.remove(key)
    
    # Remove from sorted list
    entry = (access_counters[key], key)
    sorted_access_list.remove(entry)
    
    # Remove access counter
    del access_counters[key]