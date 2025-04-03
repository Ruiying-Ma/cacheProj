# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
ALPHA = 0.5  # Weight for access frequency
BETA = 0.3   # Weight for recency
GAMMA = 0.2  # Weight for latency

# Put the metadata specifically maintained by the policy below. The policy maintains a multi-dimensional metadata structure for each cache entry, including access frequency, recency, and a latency score derived from latency heuristics. It also tracks a hyper-parametric score that combines these factors using weights optimized through sequential optimization.
metadata = defaultdict(lambda: {'frequency': 0, 'recency': 0, 'latency': 0, 'score': 0})

def calculate_score(frequency, recency, latency):
    return ALPHA * frequency + BETA * recency - GAMMA * latency

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by calculating a composite score for each entry using the hyper-parametric score. The entry with the lowest score, indicating low access frequency, recency, and high latency, is chosen for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = metadata[key]['score']
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the policy increments the access frequency, updates the recency timestamp, and recalculates the latency score based on the latest access patterns. The hyper-parametric score is then re-evaluated to reflect these changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['frequency'] += 1
    metadata[key]['recency'] = cache_snapshot.access_count
    # Assume latency is recalculated based on some heuristic
    metadata[key]['latency'] = 1 / (metadata[key]['frequency'] + 1)
    metadata[key]['score'] = calculate_score(metadata[key]['frequency'], metadata[key]['recency'], metadata[key]['latency'])

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes the access frequency and recency to default values, assigns an initial latency score based on expected access patterns, and computes the initial hyper-parametric score using these values.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    metadata[key]['frequency'] = 1
    metadata[key]['recency'] = cache_snapshot.access_count
    metadata[key]['latency'] = 1  # Initial latency heuristic
    metadata[key]['score'] = calculate_score(metadata[key]['frequency'], metadata[key]['recency'], metadata[key]['latency'])

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy adjusts the weights used in the hyper-parametric score calculation through algorithmic efficiency techniques, aiming to improve future eviction decisions based on past performance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Example of adjusting weights (this is a placeholder for actual optimization logic)
    global ALPHA, BETA, GAMMA
    ALPHA = max(0.1, ALPHA * 0.99)
    BETA = max(0.1, BETA * 1.01)
    GAMMA = max(0.1, GAMMA * 1.01)
    
    # Remove metadata for evicted object
    del metadata[evicted_obj.key]