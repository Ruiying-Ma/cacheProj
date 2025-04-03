# Import anything you need below
import math

# Put tunable constant parameters below
INITIAL_PREDICTIVE_SCORE = 1.0
NEUTRAL_DYNAMIC_REFERENCE_SCORE = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a logarithmically scaled access frequency count, a predictive score based on historical access patterns, an informed centroid representing the average access pattern, and a dynamic reference score that adjusts based on recent access trends.
access_frequency = {}
predictive_score = {}
dynamic_reference_score = {}
informed_centroid = {'x': 0, 'y': 0}
total_objects = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each cache entry, which combines the inverse of the logarithmic access frequency, the predictive score, the distance from the informed centroid, and the dynamic reference score. The entry with the lowest composite score is evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        log_access_freq = math.log(access_frequency.get(key, 1) + 1)
        pred_score = predictive_score.get(key, INITIAL_PREDICTIVE_SCORE)
        dyn_ref_score = dynamic_reference_score.get(key, NEUTRAL_DYNAMIC_REFERENCE_SCORE)
        
        centroid_dist = math.sqrt((cached_obj.size - informed_centroid['x'])**2 + (cache_snapshot.access_count - informed_centroid['y'])**2)
        
        composite_score = (1 / log_access_freq) + pred_score + centroid_dist + dyn_ref_score
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the logarithmic access frequency count is incremented, the predictive score is updated based on the latest access pattern, the informed centroid is recalculated to include the new access, and the dynamic reference score is adjusted to reflect the recent hit.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = access_frequency.get(key, 0) + 1
    predictive_score[key] = predictive_score.get(key, INITIAL_PREDICTIVE_SCORE) * 1.1  # Example update
    dynamic_reference_score[key] = dynamic_reference_score.get(key, NEUTRAL_DYNAMIC_REFERENCE_SCORE) * 0.9  # Example update
    
    global informed_centroid, total_objects
    total_objects += 1
    informed_centroid['x'] = (informed_centroid['x'] * (total_objects - 1) + obj.size) / total_objects
    informed_centroid['y'] = (informed_centroid['y'] * (total_objects - 1) + cache_snapshot.access_count) / total_objects

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the logarithmic access frequency is initialized, the predictive score is set based on initial access predictions, the informed centroid is updated to include the new object, and the dynamic reference score is initialized to a neutral value.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    access_frequency[key] = 1
    predictive_score[key] = INITIAL_PREDICTIVE_SCORE
    dynamic_reference_score[key] = NEUTRAL_DYNAMIC_REFERENCE_SCORE
    
    global informed_centroid, total_objects
    total_objects += 1
    informed_centroid['x'] = (informed_centroid['x'] * (total_objects - 1) + obj.size) / total_objects
    informed_centroid['y'] = (informed_centroid['y'] * (total_objects - 1) + cache_snapshot.access_count) / total_objects

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting a victim, the informed centroid is recalculated to exclude the evicted object, and the dynamic reference scores of remaining objects are adjusted to reflect the change in the cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    key = evicted_obj.key
    if key in access_frequency:
        del access_frequency[key]
    if key in predictive_score:
        del predictive_score[key]
    if key in dynamic_reference_score:
        del dynamic_reference_score[key]
    
    global informed_centroid, total_objects
    if total_objects > 1:
        total_objects -= 1
        informed_centroid['x'] = (informed_centroid['x'] * (total_objects + 1) - evicted_obj.size) / total_objects
        informed_centroid['y'] = (informed_centroid['y'] * (total_objects + 1) - cache_snapshot.access_count) / total_objects
    else:
        informed_centroid = {'x': 0, 'y': 0}
        total_objects = 0
    
    for key in dynamic_reference_score:
        dynamic_reference_score[key] *= 1.1  # Example adjustment