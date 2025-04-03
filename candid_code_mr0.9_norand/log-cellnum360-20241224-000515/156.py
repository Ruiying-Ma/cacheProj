# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
BASELINE_EFFICIENCY_SCORE = 1
PRUNING_THRESHOLD = 10

# Put the metadata specifically maintained by the policy below. The policy maintains a cyclic list of cache entries, an efficiency score for each entry, and a global preemptive cycle counter. Each entry's efficiency score is updated based on access frequency and recency, while the preemptive cycle counter tracks the number of cycles completed.
cyclic_list = deque()  # To maintain the order of cache entries
efficiency_scores = defaultdict(lambda: BASELINE_EFFICIENCY_SCORE)  # Efficiency scores for each entry
preemptive_cycle_counter = 0  # Global preemptive cycle counter

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects a victim for eviction by identifying the entry with the lowest efficiency score within the current cycle. If multiple entries have the same score, the oldest entry is chosen. The preemptive cycle counter is used to periodically trigger an adaptive pruning process, which adjusts efficiency scores based on recent access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key in cyclic_list:
        if efficiency_scores[key] < min_score:
            min_score = efficiency_scores[key]
            candid_obj_key = key
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the efficiency score of the accessed entry is increased, reflecting its recent use. The entry is moved to the end of the cyclic list to indicate its recency, and the preemptive cycle counter is incremented to track the ongoing cycle.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    efficiency_scores[obj.key] += 1
    cyclic_list.remove(obj.key)
    cyclic_list.append(obj.key)
    global preemptive_cycle_counter
    preemptive_cycle_counter += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its efficiency score is initialized to a baseline value. The object is added to the end of the cyclic list, and the preemptive cycle counter is incremented. If the insertion triggers a new cycle, adaptive pruning is applied to adjust scores based on the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    efficiency_scores[obj.key] = BASELINE_EFFICIENCY_SCORE
    cyclic_list.append(obj.key)
    global preemptive_cycle_counter
    preemptive_cycle_counter += 1
    if preemptive_cycle_counter >= PRUNING_THRESHOLD:
        adaptive_pruning()

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the cyclic list is updated to remove the evicted entry. The preemptive cycle counter is checked, and if a cycle is completed, adaptive pruning is applied to recalibrate efficiency scores, ensuring the cache adapts to changing access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    cyclic_list.remove(evicted_obj.key)
    global preemptive_cycle_counter
    if preemptive_cycle_counter >= PRUNING_THRESHOLD:
        adaptive_pruning()

def adaptive_pruning():
    '''
    This function applies adaptive pruning to adjust efficiency scores based on recent access patterns.
    - Return: `None`
    '''
    global preemptive_cycle_counter
    for key in cyclic_list:
        efficiency_scores[key] = max(BASELINE_EFFICIENCY_SCORE, efficiency_scores[key] - 1)
    preemptive_cycle_counter = 0