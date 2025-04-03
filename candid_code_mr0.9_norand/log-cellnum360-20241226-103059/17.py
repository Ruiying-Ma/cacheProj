# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.4
PREDICTIVE_WEIGHT = 0.2
HEURISTIC_ADJUSTMENT = 0.1
TEMPORAL_ALIGNMENT_ADJUSTMENT = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including a fusion score for each cache entry, which is a combination of access frequency, recency, and a predictive score derived from temporal patterns. It also keeps a heuristic weight that adjusts based on past eviction success and a temporal alignment factor that tracks the alignment of access patterns over time.
metadata = {
    'fusion_scores': defaultdict(lambda: {'frequency': 0, 'recency': 0, 'predictive': 0}),
    'heuristic_weights': defaultdict(lambda: 1.0),
    'temporal_alignment': defaultdict(lambda: 0.0)
}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest fusion score, adjusted by the heuristic weight. It also considers the temporal alignment factor to predict future access patterns, preferring to evict entries that are less likely to be accessed soon.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        fusion_score = (
            FREQUENCY_WEIGHT * metadata['fusion_scores'][key]['frequency'] +
            RECENCY_WEIGHT * metadata['fusion_scores'][key]['recency'] +
            PREDICTIVE_WEIGHT * metadata['fusion_scores'][key]['predictive']
        )
        adjusted_score = fusion_score * metadata['heuristic_weights'][key] - metadata['temporal_alignment'][key]
        
        if adjusted_score < min_score:
            min_score = adjusted_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increases the access frequency and recency components of the fusion score for the accessed entry. It also updates the heuristic weight based on the success of past predictions and adjusts the temporal alignment factor to reflect the current access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata['fusion_scores'][key]['frequency'] += 1
    metadata['fusion_scores'][key]['recency'] = cache_snapshot.access_count
    metadata['heuristic_weights'][key] += HEURISTIC_ADJUSTMENT
    metadata['temporal_alignment'][key] += TEMPORAL_ALIGNMENT_ADJUSTMENT

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its fusion score based on initial access predictions and sets a baseline heuristic weight. The temporal alignment factor is updated to incorporate the new entry's expected access pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata['fusion_scores'][key] = {'frequency': 1, 'recency': cache_snapshot.access_count, 'predictive': 0}
    metadata['heuristic_weights'][key] = 1.0
    metadata['temporal_alignment'][key] = 0.0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the heuristic weights of remaining entries based on the success of the eviction decision. It also updates the temporal alignment factor to better predict future access patterns, refining the fusion scores of the remaining entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    for key in cache_snapshot.cache:
        if key != evicted_key:
            metadata['heuristic_weights'][key] -= HEURISTIC_ADJUSTMENT
            metadata['temporal_alignment'][key] -= TEMPORAL_ALIGNMENT_ADJUSTMENT