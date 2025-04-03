# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_SUSTAINABILITY_SCORE = 1
DEFAULT_HEURISTIC_REFINEMENT_INDEX = 0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a sustainability score for each cache entry, a heuristic refinement index, a quantum allocation timestamp, and a real-time synchronization counter.
sustainability_scores = defaultdict(lambda: BASELINE_SUSTAINABILITY_SCORE)
heuristic_refinement_indices = defaultdict(lambda: DEFAULT_HEURISTIC_REFINEMENT_INDEX)
quantum_allocation_timestamps = {}
real_time_synchronization_counter = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest sustainability score, breaking ties using the heuristic refinement index and the oldest quantum allocation timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    min_heuristic_index = float('inf')
    oldest_timestamp = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = sustainability_scores[key]
        heuristic_index = heuristic_refinement_indices[key]
        timestamp = quantum_allocation_timestamps[key]
        
        if (score < min_score or
            (score == min_score and heuristic_index < min_heuristic_index) or
            (score == min_score and heuristic_index == min_heuristic_index and timestamp < oldest_timestamp)):
            min_score = score
            min_heuristic_index = heuristic_index
            oldest_timestamp = timestamp
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the sustainability score of the accessed entry is increased, the heuristic refinement index is adjusted based on recent access patterns, and the real-time synchronization counter is incremented.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    sustainability_scores[obj.key] += 1
    heuristic_refinement_indices[obj.key] += 1  # Example adjustment, can be more complex
    global real_time_synchronization_counter
    real_time_synchronization_counter += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its sustainability score to a baseline value, sets the heuristic refinement index to a default state, and records the current time as the quantum allocation timestamp.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    sustainability_scores[obj.key] = BASELINE_SUSTAINABILITY_SCORE
    heuristic_refinement_indices[obj.key] = DEFAULT_HEURISTIC_REFINEMENT_INDEX
    quantum_allocation_timestamps[obj.key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the heuristic refinement index for remaining entries to reflect the updated cache state and resets the real-time synchronization counter to ensure alignment with current access trends.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del sustainability_scores[evicted_obj.key]
    del heuristic_refinement_indices[evicted_obj.key]
    del quantum_allocation_timestamps[evicted_obj.key]
    
    # Recalibrate heuristic refinement indices
    for key in cache_snapshot.cache:
        heuristic_refinement_indices[key] = max(0, heuristic_refinement_indices[key] - 1)  # Example recalibration
    
    global real_time_synchronization_counter
    real_time_synchronization_counter = 0