# Import anything you need below
from collections import deque, defaultdict

# Put tunable constant parameters below
INITIAL_RECENCY_SCORE = 1
INITIAL_PREDICTIVE_SCORE = 1

# Put the metadata specifically maintained by the policy below. The policy maintains a queue for cache entries, a recency score for each entry, a predictive score based on access patterns, and a load factor indicating the current cache load equilibrium.
recency_scores = defaultdict(lambda: INITIAL_RECENCY_SCORE)
predictive_scores = defaultdict(lambda: INITIAL_PREDICTIVE_SCORE)
cache_queue = deque()
load_factor = 0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by selecting the entry with the lowest combined recency and predictive score, while ensuring the load factor remains balanced across different types of data.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key in cache_queue:
        combined_score = recency_scores[key] + predictive_scores[key]
        if combined_score < min_score:
            min_score = combined_score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the recency score of the accessed entry is increased, and the predictive score is adjusted based on recent access patterns. The queue is reordered to reflect the updated recency score.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    recency_scores[obj.key] += 1
    predictive_scores[obj.key] += 1  # Simplified adjustment
    cache_queue.remove(obj.key)
    cache_queue.append(obj.key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy assigns an initial recency and predictive score based on historical data. The load factor is recalculated to ensure equilibrium, and the queue is updated to include the new entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    recency_scores[obj.key] = INITIAL_RECENCY_SCORE
    predictive_scores[obj.key] = INITIAL_PREDICTIVE_SCORE
    cache_queue.append(obj.key)
    load_factor = cache_snapshot.size / cache_snapshot.capacity

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the load factor to maintain equilibrium, adjusts the predictive scores of remaining entries based on the eviction, and reorders the queue to reflect the changes.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    del recency_scores[evicted_obj.key]
    del predictive_scores[evicted_obj.key]
    cache_queue.remove(evicted_obj.key)
    load_factor = cache_snapshot.size / cache_snapshot.capacity
    # Adjust predictive scores based on eviction
    for key in cache_queue:
        predictive_scores[key] -= 1  # Simplified adjustment