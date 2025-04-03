# Import anything you need below
import time
from collections import defaultdict, deque

# Put tunable constant parameters below
TIMED_EVICTION_THRESHOLD = 300  # seconds

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive buffer that records access patterns, an adaptive window that adjusts based on recent access frequency, an event threshold counter for significant access changes, and a timed eviction timestamp for each cache entry.
predictive_buffer = defaultdict(int)  # Maps object keys to their predictive scores
adaptive_window = deque()  # Keeps track of access order for LRU
event_threshold_counter = 0
timed_eviction_timestamps = {}  # Maps object keys to their last access time

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first checking entries that exceed the timed eviction threshold, then considering entries with the least predictive buffer score, and finally using the adaptive window to break ties by evicting the least recently accessed entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    current_time = time.time()
    
    # Check for timed eviction threshold
    for key, last_access_time in timed_eviction_timestamps.items():
        if current_time - last_access_time > TIMED_EVICTION_THRESHOLD:
            candid_obj_key = key
            break
    
    if candid_obj_key is None:
        # Consider entries with the least predictive buffer score
        min_score = float('inf')
        for key in cache_snapshot.cache:
            if predictive_buffer[key] < min_score:
                min_score = predictive_buffer[key]
                candid_obj_key = key
    
    if candid_obj_key is None:
        # Use the adaptive window to break ties by evicting the least recently accessed entry
        if adaptive_window:
            candid_obj_key = adaptive_window.popleft()
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive buffer is updated to increase the score for the accessed entry, the adaptive window is adjusted to reflect the increased frequency, and the event threshold counter is incremented to track the change in access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Update predictive buffer
    predictive_buffer[obj.key] += 1
    
    # Update adaptive window
    if obj.key in adaptive_window:
        adaptive_window.remove(obj.key)
    adaptive_window.append(obj.key)
    
    # Update event threshold counter
    global event_threshold_counter
    event_threshold_counter += 1
    
    # Update timed eviction timestamp
    timed_eviction_timestamps[obj.key] = time.time()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the predictive buffer initializes a score for the new entry, the adaptive window is recalibrated to include the new entry, and the event threshold counter is reset to account for the new state of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Initialize predictive buffer score
    predictive_buffer[obj.key] = 1
    
    # Recalibrate adaptive window
    adaptive_window.append(obj.key)
    
    # Reset event threshold counter
    global event_threshold_counter
    event_threshold_counter = 0
    
    # Set timed eviction timestamp
    timed_eviction_timestamps[obj.key] = time.time()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the predictive buffer removes the score of the evicted entry, the adaptive window is adjusted to exclude the evicted entry, and the event threshold counter is decremented to reflect the reduced cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Remove predictive buffer score
    if evicted_obj.key in predictive_buffer:
        del predictive_buffer[evicted_obj.key]
    
    # Adjust adaptive window
    if evicted_obj.key in adaptive_window:
        adaptive_window.remove(evicted_obj.key)
    
    # Decrement event threshold counter
    global event_threshold_counter
    event_threshold_counter -= 1
    
    # Remove timed eviction timestamp
    if evicted_obj.key in timed_eviction_timestamps:
        del timed_eviction_timestamps[evicted_obj.key]