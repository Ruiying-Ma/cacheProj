# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_LFI = 1
NEUTRAL_POINTER_POSITION = 0

# Put the metadata specifically maintained by the policy below. The policy maintains a dynamic pointer for each cache line, a Load Frequency Index (LFI) for each object, and a global Immediate Cache Refresh (ICR) flag. The dynamic pointer adjusts based on access patterns, LFI tracks how often an object is accessed, and ICR ensures zero latency compliance by preemptively refreshing cache lines.
lfi = defaultdict(lambda: BASELINE_LFI)  # Load Frequency Index for each object
dynamic_pointer = defaultdict(lambda: NEUTRAL_POINTER_POSITION)  # Dynamic pointer for each cache line
icr_flag = False  # Global Immediate Cache Refresh flag

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the cache line with the lowest Load Frequency Index. If multiple lines have the same LFI, the dynamic pointer is used to break ties by pointing to the least recently adjusted line.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_lfi = float('inf')
    min_pointer_time = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        if lfi[key] < min_lfi:
            min_lfi = lfi[key]
            min_pointer_time = dynamic_pointer[key]
            candid_obj_key = key
        elif lfi[key] == min_lfi:
            if dynamic_pointer[key] < min_pointer_time:
                min_pointer_time = dynamic_pointer[key]
                candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Load Frequency Index of the accessed object is incremented, and the dynamic pointer for that cache line is adjusted to reflect the recent access. The Immediate Cache Refresh flag is checked and, if set, triggers a refresh of the cache line to ensure zero latency compliance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    lfi[obj.key] += 1
    dynamic_pointer[obj.key] = cache_snapshot.access_count
    
    if icr_flag:
        # Trigger a refresh of the cache line (implementation depends on system specifics)
        pass

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its Load Frequency Index to a baseline value and sets the dynamic pointer to a neutral position. The Immediate Cache Refresh flag is set to ensure the new object is immediately available with zero latency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    lfi[obj.key] = BASELINE_LFI
    dynamic_pointer[obj.key] = NEUTRAL_POINTER_POSITION
    global icr_flag
    icr_flag = True

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy resets the dynamic pointer of the evicted line to a default state and decrements the global Immediate Cache Refresh flag if it was set, ensuring the cache remains optimized for zero latency compliance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    dynamic_pointer[evicted_obj.key] = NEUTRAL_POINTER_POSITION
    global icr_flag
    if icr_flag:
        icr_flag = False