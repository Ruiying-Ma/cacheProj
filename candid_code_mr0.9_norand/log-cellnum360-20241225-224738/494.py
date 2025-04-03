# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
LATENCY_WEIGHT = 0.5
SUSTAINABILITY_WEIGHT = 0.3
PREDICTIVE_INDEX_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a Sustainability Matrix that tracks the environmental impact of caching decisions, an Adaptive Forecast that predicts future access patterns, a Latency Optimization score for each cache entry, and a Predictive Index that combines historical access frequency and recency.
sustainability_matrix = defaultdict(float)
adaptive_forecast = defaultdict(float)
latency_optimization = defaultdict(float)
predictive_index = defaultdict(lambda: {'frequency': 0, 'recency': 0})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest Predictive Index, adjusted by the Sustainability Matrix to minimize environmental impact, and the Latency Optimization score to ensure minimal performance degradation.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        pi = predictive_index[key]['frequency'] + predictive_index[key]['recency']
        sustainability = sustainability_matrix[key]
        latency = latency_optimization[key]
        
        score = (PREDICTIVE_INDEX_WEIGHT * pi) - (SUSTAINABILITY_WEIGHT * sustainability) + (LATENCY_WEIGHT * latency)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the Predictive Index by increasing the recency and frequency components, adjusts the Latency Optimization score based on current system performance, and recalibrates the Adaptive Forecast to refine future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    predictive_index[key]['frequency'] += 1
    predictive_index[key]['recency'] = cache_snapshot.access_count
    
    # Adjust Latency Optimization score (example logic)
    latency_optimization[key] = 1 / (1 + cache_snapshot.hit_count)
    
    # Recalibrate Adaptive Forecast (example logic)
    adaptive_forecast[key] = predictive_index[key]['frequency'] / cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its Predictive Index based on initial access patterns, updates the Sustainability Matrix to reflect the environmental cost of the new entry, and sets a baseline Latency Optimization score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    predictive_index[key] = {'frequency': 1, 'recency': cache_snapshot.access_count}
    
    # Update Sustainability Matrix (example logic)
    sustainability_matrix[key] = obj.size / cache_snapshot.capacity
    
    # Set baseline Latency Optimization score (example logic)
    latency_optimization[key] = 1.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the Sustainability Matrix to account for the reduced environmental impact, updates the Adaptive Forecast to improve future eviction decisions, and adjusts the Latency Optimization scores of remaining entries to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    
    # Recalibrate Sustainability Matrix (example logic)
    sustainability_matrix.pop(evicted_key, None)
    
    # Update Adaptive Forecast (example logic)
    for key in cache_snapshot.cache:
        adaptive_forecast[key] = predictive_index[key]['frequency'] / cache_snapshot.access_count
    
    # Adjust Latency Optimization scores (example logic)
    for key in cache_snapshot.cache:
        latency_optimization[key] = 1 / (1 + cache_snapshot.hit_count)