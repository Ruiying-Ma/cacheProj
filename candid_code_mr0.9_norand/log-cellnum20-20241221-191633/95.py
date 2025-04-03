# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.4
PREDICTIVE_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a multi-layered metadata structure including access frequency, recency, and a predictive score based on historical access patterns. It also keeps a heuristic model that adapts based on workload characteristics and an algorithmic tuning parameter that adjusts the weight of each metadata component dynamically.
access_frequency = defaultdict(int)
recency = {}
predictive_score = defaultdict(float)
heuristic_model = {
    'frequency_weight': FREQUENCY_WEIGHT,
    'recency_weight': RECENCY_WEIGHT,
    'predictive_weight': PREDICTIVE_WEIGHT
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects an eviction victim by calculating a composite score for each cache entry, which is a weighted sum of its access frequency, recency, and predictive score. The entry with the lowest composite score is chosen for eviction, with weights adjusted by the heuristic model to adapt to changing access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        freq = access_frequency[key]
        rec = recency[key]
        pred = predictive_score[key]
        
        composite_score = (heuristic_model['frequency_weight'] * freq +
                           heuristic_model['recency_weight'] * rec +
                           heuristic_model['predictive_weight'] * pred)
        
        if composite_score < min_score:
            min_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the access frequency and recency metadata for the accessed entry are updated to reflect the new access. The predictive score is recalibrated using the heuristic model, which considers the current workload characteristics to adjust the prediction accuracy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    access_frequency[obj.key] += 1
    recency[obj.key] = cache_snapshot.access_count
    # Recalibrate predictive score (simple example, can be more complex)
    predictive_score[obj.key] = (predictive_score[obj.key] + 1) / 2

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a baseline predictive score derived from similar past entries, sets its access frequency to one, and updates the heuristic model to incorporate the new entry's characteristics into its workload analysis.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    access_frequency[obj.key] = 1
    recency[obj.key] = cache_snapshot.access_count
    # Initialize predictive score (simple example, can be more complex)
    predictive_score[obj.key] = 0.5

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy updates the heuristic model to learn from the eviction decision, adjusting its parameters to better predict future access patterns. The algorithmic tuning parameter is also refined to improve the balance between frequency, recency, and prediction in future eviction decisions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Example of heuristic model adjustment (simple example, can be more complex)
    heuristic_model['frequency_weight'] *= 0.99
    heuristic_model['recency_weight'] *= 1.01
    heuristic_model['predictive_weight'] *= 1.00