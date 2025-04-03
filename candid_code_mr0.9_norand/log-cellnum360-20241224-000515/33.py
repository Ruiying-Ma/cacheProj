# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
BASE_FREQUENCY = 1
RECALIBRATION_THRESHOLD = 100

# Put the metadata specifically maintained by the policy below. The policy maintains a cyclic buffer to track recent access patterns, an adaptive frequency counter for each cache entry, a validation flag for each entry to ensure data integrity, and a recalibration threshold to adjust frequency weights dynamically.
cyclic_buffer = deque()
frequency_counter = defaultdict(lambda: BASE_FREQUENCY)
validation_flags = defaultdict(lambda: True)
recalibration_counter = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest adaptive frequency count that also passes the cache validation check. If multiple entries have the same frequency, the oldest entry in the cyclic buffer is chosen.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_frequency = float('inf')
    for key in cyclic_buffer:
        if validation_flags[key] and frequency_counter[key] < min_frequency:
            min_frequency = frequency_counter[key]
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the adaptive frequency counter for the accessed entry is incremented, the entry's position is updated in the cyclic buffer to reflect recent access, and the recalibration threshold is checked to determine if frequency weights need adjustment.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    frequency_counter[obj.key] += 1
    cyclic_buffer.remove(obj.key)
    cyclic_buffer.append(obj.key)
    global recalibration_counter
    recalibration_counter += 1
    if recalibration_counter >= RECALIBRATION_THRESHOLD:
        recalibrate_frequencies()

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its adaptive frequency counter to a base value, sets its validation flag to true, and adds it to the cyclic buffer. The recalibration threshold is evaluated to ensure frequency counters remain balanced.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    frequency_counter[obj.key] = BASE_FREQUENCY
    validation_flags[obj.key] = True
    cyclic_buffer.append(obj.key)
    global recalibration_counter
    recalibration_counter += 1
    if recalibration_counter >= RECALIBRATION_THRESHOLD:
        recalibrate_frequencies()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the entry from the cyclic buffer, resets its adaptive frequency counter, and clears its validation flag. The recalibration threshold is adjusted if necessary to maintain optimal cache performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    cyclic_buffer.remove(evicted_obj.key)
    frequency_counter[evicted_obj.key] = BASE_FREQUENCY
    validation_flags[evicted_obj.key] = False
    global recalibration_counter
    recalibration_counter += 1
    if recalibration_counter >= RECALIBRATION_THRESHOLD:
        recalibrate_frequencies()

def recalibrate_frequencies():
    '''
    Recalibrate the frequency counters to maintain balance.
    '''
    global recalibration_counter
    recalibration_counter = 0
    for key in frequency_counter:
        frequency_counter[key] = max(BASE_FREQUENCY, frequency_counter[key] // 2)