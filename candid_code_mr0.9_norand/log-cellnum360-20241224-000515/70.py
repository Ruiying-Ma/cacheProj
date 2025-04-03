# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
BASELINE_PREDICTIVE_SCORE = 1.0
FREQUENCY_WEIGHT = 0.5
RECENCY_WEIGHT = 0.5

# Put the metadata specifically maintained by the policy below. The policy maintains a synthesized data profile for each cache entry, which includes access frequency, recency, and a predictive score derived from a feedback loop that analyzes past eviction decisions. It also tracks network traversal patterns to understand data flow and access trends.
cache_metadata = defaultdict(lambda: {
    'frequency': 0,
    'recency': 0,
    'predictive_score': BASELINE_PREDICTIVE_SCORE,
    'network_traversal': 0
})

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by evaluating the predictive score, which forecasts future access likelihood based on historical patterns and network traversal data. Entries with the lowest predictive score are prioritized for eviction, ensuring adaptive progression in cache management.
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
        score = cache_metadata[key]['predictive_score']
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy updates the access frequency and recency for the hit entry. It also refines the predictive score using the feedback loop, incorporating the latest access data and network traversal insights to enhance future predictions.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    metadata = cache_metadata[obj.key]
    metadata['frequency'] += 1
    metadata['recency'] = cache_snapshot.access_count
    metadata['predictive_score'] = (FREQUENCY_WEIGHT * metadata['frequency'] +
                                    RECENCY_WEIGHT * metadata['recency'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a baseline predictive score and network traversal pattern. It also updates the overall cache profile to reflect the new data synthesis, ensuring adaptive progression in managing cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    cache_metadata[obj.key] = {
        'frequency': 1,
        'recency': cache_snapshot.access_count,
        'predictive_score': BASELINE_PREDICTIVE_SCORE,
        'network_traversal': 0
    }

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the predictive feedback loop by analyzing the evicted entry's historical data and its impact on cache performance. This information is used to refine the predictive scoring model and update network traversal patterns for remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del cache_metadata[evicted_obj.key]
    # Optionally, adjust other entries based on the eviction
    for key in cache_snapshot.cache:
        cache_metadata[key]['network_traversal'] += 1