# Import anything you need below
import heapq
from collections import defaultdict

# Put tunable constant parameters below
LATENCY_DECAY = 0.9
HEURISTIC_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive model for access patterns, a latency buffer to track recent access times, an adaptive index for dynamically adjusting cache priorities, and heuristic scores for each cache entry.
latency_buffer = defaultdict(lambda: 0)
adaptive_index = defaultdict(lambda: 0)
heuristic_scores = defaultdict(lambda: 0)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by combining predictive synchronization to forecast future access needs, latency buffer to prioritize entries with higher recent access latency, and heuristic optimization to select the entry with the lowest combined score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key, cached_obj in cache_snapshot.cache.items():
        score = (latency_buffer[key] * LATENCY_DECAY) + (heuristic_scores[key] * HEURISTIC_WEIGHT)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the latency buffer to reflect the current access time, adjusts the adaptive index to increase the priority of the accessed entry, and recalibrates the heuristic score based on the updated access pattern prediction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    latency_buffer[obj.key] = cache_snapshot.access_count
    adaptive_index[obj.key] += 1
    heuristic_scores[obj.key] = adaptive_index[obj.key] / (latency_buffer[obj.key] + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its latency buffer entry, assigns an adaptive index value based on initial access predictions, and computes an initial heuristic score to integrate it into the cache's optimization framework.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    latency_buffer[obj.key] = cache_snapshot.access_count
    adaptive_index[obj.key] = 1
    heuristic_scores[obj.key] = adaptive_index[obj.key] / (latency_buffer[obj.key] + 1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive model to account for the removed entry, updates the latency buffer to remove the evicted entry's data, and adjusts the adaptive index to redistribute priorities among remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in latency_buffer:
        del latency_buffer[evicted_obj.key]
    if evicted_obj.key in adaptive_index:
        del adaptive_index[evicted_obj.key]
    if evicted_obj.key in heuristic_scores:
        del heuristic_scores[evicted_obj.key]
    
    # Recalibrate the predictive model (if applicable)
    # This is a placeholder for any additional recalibration logic needed