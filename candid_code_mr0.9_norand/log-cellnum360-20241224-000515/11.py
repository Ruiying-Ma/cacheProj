# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
LOCALITY_BOOST = 10
MISS_PENALTY_INCREMENT = 1.1

# Put the metadata specifically maintained by the policy below. The policy maintains a 'locality score' for each page, which is a combination of temporal locality (recent access time) and spatial locality (proximity of accessed pages). It also tracks a 'miss penalty' score, estimating the cost of a cache miss for each page based on historical data.
locality_scores = defaultdict(lambda: 0)
miss_penalty_scores = defaultdict(lambda: 1.0)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses to evict the page with the lowest combined score of locality and miss penalty. This ensures that pages with high data locality and high miss penalty are retained longer, optimizing for both immediate performance and future access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        combined_score = locality_scores[key] + miss_penalty_scores[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the locality score of the accessed page is increased, reflecting its recent use. The miss penalty score remains unchanged, as it is only updated on cache misses.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    locality_scores[obj.key] += LOCALITY_BOOST

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its locality score based on the access pattern of nearby pages and sets an initial miss penalty score based on the average miss penalty of the cache.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Initialize locality score based on nearby pages
    locality_scores[obj.key] = cache_snapshot.access_count
    
    # Calculate average miss penalty
    if cache_snapshot.cache:
        avg_miss_penalty = sum(miss_penalty_scores[key] for key in cache_snapshot.cache) / len(cache_snapshot.cache)
    else:
        avg_miss_penalty = 1.0
    
    miss_penalty_scores[obj.key] = avg_miss_penalty

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalibrates the miss penalty scores of remaining pages, slightly increasing them to reflect the increased cost of future misses due to reduced cache size.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Increase miss penalty scores for remaining pages
    for key in cache_snapshot.cache:
        miss_penalty_scores[key] *= MISS_PENALTY_INCREMENT