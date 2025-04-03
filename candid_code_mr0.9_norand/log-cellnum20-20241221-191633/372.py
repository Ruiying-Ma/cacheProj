# Import anything you need below
from collections import defaultdict, deque

# Put tunable constant parameters below
TEMPORAL_BUFFER_SIZE = 100  # Size of the temporal buffer
PREDICTIVE_ADJUSTMENT_FACTOR = 0.1  # Factor for predictive adjustment

# Put the metadata specifically maintained by the policy below. The policy maintains a cyclic deviation counter for each cache line, a temporal buffer to track recent access patterns, an ordered allocation list to manage cache line priorities, and a predictive adjustment model to anticipate future access needs.
cyclic_deviation_counters = defaultdict(int)
temporal_buffer = deque(maxlen=TEMPORAL_BUFFER_SIZE)
ordered_allocation_list = []
predictive_adjustment_model = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache line with the highest cyclic deviation counter, indicating it has deviated most from recent access patterns, and cross-referencing with the ordered allocation list to ensure minimal disruption.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    max_deviation = -1
    for key in ordered_allocation_list:
        if cyclic_deviation_counters[key] > max_deviation:
            max_deviation = cyclic_deviation_counters[key]
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the cyclic deviation counter for the accessed line is reset, the temporal buffer is updated to reflect the recent access, the line is moved to a higher priority in the ordered allocation list, and the predictive adjustment model is refined using the new access data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    cyclic_deviation_counters[obj.key] = 0
    temporal_buffer.append(obj.key)
    if obj.key in ordered_allocation_list:
        ordered_allocation_list.remove(obj.key)
    ordered_allocation_list.insert(0, obj.key)
    predictive_adjustment_model[obj.key] += PREDICTIVE_ADJUSTMENT_FACTOR

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the cyclic deviation counter is initialized, the temporal buffer is updated to include the new object, the object is added to the ordered allocation list based on predicted access frequency, and the predictive adjustment model is updated to incorporate the new object's characteristics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    cyclic_deviation_counters[obj.key] = 0
    temporal_buffer.append(obj.key)
    ordered_allocation_list.append(obj.key)
    predictive_adjustment_model[obj.key] = 0.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the cyclic deviation counter of the evicted line is cleared, the temporal buffer is adjusted to remove the evicted line's influence, the ordered allocation list is reordered to reflect the change, and the predictive adjustment model is recalibrated to account for the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in cyclic_deviation_counters:
        del cyclic_deviation_counters[evicted_obj.key]
    if evicted_obj.key in temporal_buffer:
        temporal_buffer.remove(evicted_obj.key)
    if evicted_obj.key in ordered_allocation_list:
        ordered_allocation_list.remove(evicted_obj.key)
    if evicted_obj.key in predictive_adjustment_model:
        del predictive_adjustment_model[evicted_obj.key]