# Import anything you need below
from collections import defaultdict
import math

# Put tunable constant parameters below
DEFAULT_TEMPORAL_DEVIATION = 1.0
DEFAULT_COHESION_SCORE = 0.5
PREDICTIVE_SCORE_INCREMENT = 1.0
TEMPORAL_DEVIATION_DECAY = 0.9
COHESION_SCORE_DECAY = 0.9
ELASTIC_THROUGHPUT_ADJUSTMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a predictive score for each cache entry based on historical access patterns, a temporal deviation metric to track the variance in access intervals, and a cohesion score to measure the relatedness of cache entries. It also tracks the elastic throughput, which adjusts the cache's responsiveness to varying workloads.
predictive_scores = defaultdict(float)
temporal_deviations = defaultdict(lambda: DEFAULT_TEMPORAL_DEVIATION)
cohesion_scores = defaultdict(lambda: DEFAULT_COHESION_SCORE)
last_access_times = {}
elastic_throughput = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest predictive score, adjusted by its temporal deviation and cohesion score. Entries with high temporal deviation and low cohesion are prioritized for eviction, ensuring that the cache adapts to changing access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (predictive_scores[key] - 
                 temporal_deviations[key] + 
                 (1 - cohesion_scores[key]))
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the predictive score of the accessed entry is increased, while its temporal deviation is recalculated to reflect the new access interval. The cohesion score is updated based on the relationship of the accessed entry with other entries accessed in close temporal proximity.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Update predictive score
    predictive_scores[key] += PREDICTIVE_SCORE_INCREMENT
    
    # Update temporal deviation
    if key in last_access_times:
        interval = current_time - last_access_times[key]
        temporal_deviations[key] = (temporal_deviations[key] * TEMPORAL_DEVIATION_DECAY + interval) / 2
    
    # Update cohesion score
    for other_key in cache_snapshot.cache:
        if other_key != key:
            cohesion_scores[other_key] = (cohesion_scores[other_key] * COHESION_SCORE_DECAY + 1) / 2
    
    # Update last access time
    last_access_times[key] = current_time

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its predictive score based on initial access patterns, sets its temporal deviation to a default value, and calculates its initial cohesion score by analyzing its relationship with existing cache entries. The elastic throughput is adjusted to accommodate the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    current_time = cache_snapshot.access_count
    
    # Initialize predictive score
    predictive_scores[key] = 0.0
    
    # Set default temporal deviation
    temporal_deviations[key] = DEFAULT_TEMPORAL_DEVIATION
    
    # Calculate initial cohesion score
    for other_key in cache_snapshot.cache:
        if other_key != key:
            cohesion_scores[other_key] = (cohesion_scores[other_key] * COHESION_SCORE_DECAY + 1) / 2
    
    # Update last access time
    last_access_times[key] = current_time
    
    # Adjust elastic throughput
    global elastic_throughput
    elastic_throughput += ELASTIC_THROUGHPUT_ADJUSTMENT

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive scores of remaining entries to reflect the removal of the evicted entry. The temporal deviation and cohesion scores are adjusted to account for the change in cache composition, and the elastic throughput is fine-tuned to maintain optimal performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Remove metadata for evicted object
    if evicted_key in predictive_scores:
        del predictive_scores[evicted_key]
    if evicted_key in temporal_deviations:
        del temporal_deviations[evicted_key]
    if evicted_key in cohesion_scores:
        del cohesion_scores[evicted_key]
    if evicted_key in last_access_times:
        del last_access_times[evicted_key]
    
    # Recalibrate predictive scores
    for key in cache_snapshot.cache:
        predictive_scores[key] *= 0.9
    
    # Adjust elastic throughput
    global elastic_throughput
    elastic_throughput -= ELASTIC_THROUGHPUT_ADJUSTMENT