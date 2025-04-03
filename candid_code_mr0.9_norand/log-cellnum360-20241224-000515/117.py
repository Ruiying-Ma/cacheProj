# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
ALIGNMENT_FACTOR_INCREMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a circular queue to track cache entries, a frequency counter for each entry to record access frequency, and a dynamic alignment factor that adjusts based on access patterns to prioritize certain entries.
circular_queue = deque()
frequency_counter = defaultdict(int)
dynamic_alignment_factor = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by traversing the circular queue and selecting the entry with the lowest frequency count, adjusted by the dynamic alignment factor to ensure balanced eviction across different access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key in circular_queue:
        freq = frequency_counter[key]
        alignment = dynamic_alignment_factor[key]
        score = freq + alignment
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency counter for the accessed entry is incremented, and the dynamic alignment factor is adjusted to slightly favor entries with similar access patterns, promoting temporal locality.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    frequency_counter[key] += 1
    dynamic_alignment_factor[key] += ALIGNMENT_FACTOR_INCREMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the entry is added to the circular queue with an initial frequency count of one, and the dynamic alignment factor is recalibrated to account for the new entry's potential impact on access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    circular_queue.append(key)
    frequency_counter[key] = 1
    dynamic_alignment_factor[key] = 0.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the circular queue is updated to remove the evicted entry, and the dynamic alignment factor is adjusted to reflect the change in cache composition, ensuring continued balance in future evictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    circular_queue.remove(evicted_key)
    del frequency_counter[evicted_key]
    del dynamic_alignment_factor[evicted_key]