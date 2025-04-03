# Import anything you need below
from collections import defaultdict
import heapq

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
BASELINE_RECENCY = 1
IMPORTANCE_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a temporal overlay map that tracks access patterns over time, an adaptive isolation index that categorizes cache entries based on their access frequency and recency, a hierarchical gradient score that prioritizes entries based on multi-level importance, and a predictive allocation model that forecasts future access likelihood.
temporal_overlay_map = {}
adaptive_isolation_index = defaultdict(lambda: {'frequency': BASELINE_FREQUENCY, 'recency': BASELINE_RECENCY})
hierarchical_gradient_score = {}
predictive_allocation_model = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by evaluating the hierarchical gradient score to identify the least important entries, then cross-references with the adaptive isolation index to ensure low-frequency and low-recency entries are prioritized for eviction.
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
        score = hierarchical_gradient_score[key] + adaptive_isolation_index[key]['frequency'] + adaptive_isolation_index[key]['recency']
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the temporal overlay map is updated to reflect the current access time, the adaptive isolation index is adjusted to increase the frequency and recency score of the accessed entry, and the hierarchical gradient score is recalibrated to reflect the increased importance of the entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    temporal_overlay_map[obj.key] = cache_snapshot.access_count
    adaptive_isolation_index[obj.key]['frequency'] += 1
    adaptive_isolation_index[obj.key]['recency'] = cache_snapshot.access_count
    hierarchical_gradient_score[obj.key] = IMPORTANCE_WEIGHT * (adaptive_isolation_index[obj.key]['frequency'] + adaptive_isolation_index[obj.key]['recency'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the temporal overlay map logs the initial access time, the adaptive isolation index assigns a baseline frequency and recency score, the hierarchical gradient score is initialized based on predicted importance, and the predictive allocation model is updated to incorporate the new entry's potential future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    temporal_overlay_map[obj.key] = cache_snapshot.access_count
    adaptive_isolation_index[obj.key] = {'frequency': BASELINE_FREQUENCY, 'recency': BASELINE_RECENCY}
    hierarchical_gradient_score[obj.key] = IMPORTANCE_WEIGHT * (BASELINE_FREQUENCY + BASELINE_RECENCY)
    predictive_allocation_model[obj.key] = 0  # Initialize with a default prediction score

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the temporal overlay map removes the entry's access history, the adaptive isolation index is recalibrated to redistribute scores among remaining entries, the hierarchical gradient score is adjusted to reflect the new cache composition, and the predictive allocation model is refined to improve future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    if evicted_obj.key in temporal_overlay_map:
        del temporal_overlay_map[evicted_obj.key]
    if evicted_obj.key in adaptive_isolation_index:
        del adaptive_isolation_index[evicted_obj.key]
    if evicted_obj.key in hierarchical_gradient_score:
        del hierarchical_gradient_score[evicted_obj.key]
    if evicted_obj.key in predictive_allocation_model:
        del predictive_allocation_model[evicted_obj.key]
    
    # Recalibrate scores for remaining entries
    for key in cache_snapshot.cache:
        hierarchical_gradient_score[key] = IMPORTANCE_WEIGHT * (adaptive_isolation_index[key]['frequency'] + adaptive_isolation_index[key]['recency'])