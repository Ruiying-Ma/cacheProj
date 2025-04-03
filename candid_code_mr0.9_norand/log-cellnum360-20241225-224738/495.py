# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
FREQUENCY_WEIGHT = 0.4
RECENCY_WEIGHT = 0.4
CONTEXTUAL_WEIGHT = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a 'frequency score' for each cache entry, a 'recency score' based on the time since last access, and a 'contextual score' that adjusts based on the type of workload (e.g., read-heavy or write-heavy).
frequency_scores = defaultdict(int)
recency_scores = defaultdict(int)
contextual_scores = defaultdict(float)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry, which is a weighted sum of the frequency, recency, and contextual scores. The entry with the lowest composite score is selected for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_composite_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency_score = frequency_scores[key]
        recency_score = cache_snapshot.access_count - recency_scores[key]
        contextual_score = contextual_scores[key]
        
        composite_score = (FREQUENCY_WEIGHT * frequency_score +
                           RECENCY_WEIGHT * recency_score +
                           CONTEXTUAL_WEIGHT * contextual_score)
        
        if composite_score < min_composite_score:
            min_composite_score = composite_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the frequency score of the accessed entry is incremented, the recency score is reset to zero, and the contextual score is adjusted slightly based on the current workload pattern.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    frequency_scores[obj.key] += 1
    recency_scores[obj.key] = cache_snapshot.access_count
    # Adjust contextual score based on workload pattern
    contextual_scores[obj.key] *= 1.05  # Example adjustment

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, its frequency score is initialized to one, its recency score is set to zero, and its contextual score is set based on the current workload type.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    frequency_scores[obj.key] = 1
    recency_scores[obj.key] = cache_snapshot.access_count
    # Initialize contextual score based on workload type
    contextual_scores[obj.key] = 1.0  # Example initialization

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After evicting an entry, the policy recalibrates the contextual scores of remaining entries to ensure they reflect the current workload dynamics, while frequency and recency scores remain unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Recalibrate contextual scores
    for key in cache_snapshot.cache:
        contextual_scores[key] *= 0.95  # Example recalibration