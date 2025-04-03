# Import anything you need below
from collections import defaultdict, deque
import heapq

# Put tunable constant parameters below
FREQUENCY_LEVELS = 3  # Number of frequency levels
TIME_INTERVAL = 100  # Time interval for temporal quantization

# Put the metadata specifically maintained by the policy below. The policy maintains a hierarchical state modulation structure that categorizes cache entries into multiple levels based on access frequency and recency. It also uses a predictive feedback loop to estimate future access patterns, a temporal quantization grid to track access times in discrete intervals, and a heuristic adjustment layer to dynamically adjust priorities based on workload characteristics.
frequency_levels = defaultdict(lambda: deque())  # Frequency levels with recency tracking
access_times = {}  # Last access time for each object
future_access_likelihood = defaultdict(float)  # Predictive feedback loop
temporal_grid = defaultdict(int)  # Temporal quantization grid

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by analyzing the hierarchical state modulation to identify the least recently used entries within the lowest access frequency category. It then applies the predictive feedback loop to refine the choice by considering future access likelihood, and uses the temporal quantization grid to ensure that entries with outdated access intervals are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Find the least recently used entry in the lowest frequency level
    for level in range(FREQUENCY_LEVELS):
        if frequency_levels[level]:
            # Sort by future access likelihood and temporal grid
            candidates = sorted(frequency_levels[level], key=lambda k: (future_access_likelihood[k], temporal_grid[k]))
            candid_obj_key = candidates[0]
            break
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the hierarchical state modulation by promoting the accessed entry to a higher frequency category and adjusting its recency position. The predictive feedback loop is refined with the new access data, and the temporal quantization grid is updated to reflect the current access interval. The heuristic adjustment layer recalibrates priorities based on the updated access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count

    # Promote to a higher frequency level
    for level in range(FREQUENCY_LEVELS):
        if key in frequency_levels[level]:
            frequency_levels[level].remove(key)
            if level + 1 < FREQUENCY_LEVELS:
                frequency_levels[level + 1].append(key)
            else:
                frequency_levels[level].append(key)
            break

    # Update access time and temporal grid
    access_times[key] = current_time
    temporal_grid[key] = current_time // TIME_INTERVAL

    # Update predictive feedback loop
    future_access_likelihood[key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its hierarchical state modulation level to the lowest frequency category and sets its recency position. The predictive feedback loop incorporates the new entry into its future access estimations, while the temporal quantization grid records the initial access interval. The heuristic adjustment layer evaluates the impact of the new entry on overall cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count

    # Initialize in the lowest frequency level
    frequency_levels[0].append(key)

    # Set initial access time and temporal grid
    access_times[key] = current_time
    temporal_grid[key] = current_time // TIME_INTERVAL

    # Initialize predictive feedback loop
    future_access_likelihood[key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy removes the evicted entry from the hierarchical state modulation and updates the predictive feedback loop to exclude its data from future predictions. The temporal quantization grid is adjusted to remove the evicted entry's intervals, and the heuristic adjustment layer reassesses the cache's state to optimize future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key

    # Remove from frequency levels
    for level in range(FREQUENCY_LEVELS):
        if key in frequency_levels[level]:
            frequency_levels[level].remove(key)
            break

    # Remove from access times and temporal grid
    if key in access_times:
        del access_times[key]
    if key in temporal_grid:
        del temporal_grid[key]

    # Remove from predictive feedback loop
    if key in future_access_likelihood:
        del future_access_likelihood[key]