# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_PRIORITY_LEVEL = 1
WORKLOAD_INDEX_ADJUSTMENT_FACTOR = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a sequential access counter, buffer priority levels, and a dynamic workload index. The sequential access counter tracks the number of consecutive accesses to a particular data stream. Buffer priority levels categorize data based on their importance and frequency of access. The dynamic workload index adjusts based on the current system load and access patterns.
sequential_access_counter = defaultdict(int)
buffer_priority_levels = defaultdict(lambda: INITIAL_PRIORITY_LEVEL)
dynamic_workload_index = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by first considering the buffer priority levels, evicting the lowest priority data first. If multiple candidates exist, it then considers the sequential access counter, evicting data with the lowest count. Finally, the dynamic workload index is used to make a decision if there is still a tie, favoring eviction of data that is least likely to be accessed under current workload conditions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    # Step 1: Find the lowest priority level
    min_priority = min(buffer_priority_levels[key] for key in cache_snapshot.cache)
    candidates = [key for key in cache_snapshot.cache if buffer_priority_levels[key] == min_priority]
    
    # Step 2: If multiple candidates, use sequential access counter
    if len(candidates) > 1:
        min_access_count = min(sequential_access_counter[key] for key in candidates)
        candidates = [key for key in candidates if sequential_access_counter[key] == min_access_count]
    
    # Step 3: If still a tie, use dynamic workload index
    if len(candidates) > 1:
        # For simplicity, choose the first candidate in this case
        candid_obj_key = candidates[0]
    else:
        candid_obj_key = candidates[0]
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the sequential access counter for the accessed data is incremented, and its buffer priority level is re-evaluated to potentially increase its priority. The dynamic workload index is also updated to reflect the current access pattern, ensuring it remains responsive to changes in workload.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    # Increment the sequential access counter
    sequential_access_counter[obj.key] += 1
    
    # Re-evaluate buffer priority level
    buffer_priority_levels[obj.key] += 1  # Simplified logic for increasing priority
    
    # Update dynamic workload index
    global dynamic_workload_index
    dynamic_workload_index += WORKLOAD_INDEX_ADJUSTMENT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the sequential access counter is initialized to zero, and the buffer priority level is set based on initial access frequency predictions. The dynamic workload index is adjusted to account for the new data, ensuring the cache remains balanced under the current workload.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    # Initialize the sequential access counter
    sequential_access_counter[obj.key] = 0
    
    # Set initial buffer priority level
    buffer_priority_levels[obj.key] = INITIAL_PRIORITY_LEVEL
    
    # Adjust dynamic workload index
    global dynamic_workload_index
    dynamic_workload_index -= WORKLOAD_INDEX_ADJUSTMENT_FACTOR

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the sequential access counter and buffer priority level of the evicted data are reset. The dynamic workload index is recalibrated to reflect the reduced cache load, ensuring that future eviction decisions remain optimal under the adjusted workload conditions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    # Reset the sequential access counter and buffer priority level for the evicted object
    del sequential_access_counter[evicted_obj.key]
    del buffer_priority_levels[evicted_obj.key]
    
    # Recalibrate dynamic workload index
    global dynamic_workload_index
    dynamic_workload_index += WORKLOAD_INDEX_ADJUSTMENT_FACTOR