# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
WEIGHT_ACCESS_FREQUENCY = 0.5
WEIGHT_PREDICTIVE_ACCESS = 0.3
WEIGHT_SEQUENTIAL_ORDER = 0.2

# Put the metadata specifically maintained by the policy below. The policy maintains a fusion of algorithmic scores, real-time access patterns, predictive access likelihood, and sequential access order. Each cache entry is associated with a score derived from these factors, updated continuously to reflect current and future access patterns.
access_frequency = defaultdict(int)
predictive_access_likelihood = defaultdict(float)
sequential_order = []
scores = defaultdict(float)

def calculate_score(key):
    return (WEIGHT_ACCESS_FREQUENCY * access_frequency[key] +
            WEIGHT_PREDICTIVE_ACCESS * predictive_access_likelihood[key] +
            WEIGHT_SEQUENTIAL_ORDER * (len(sequential_order) - sequential_order.index(key)))

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the cache entry with the lowest combined score, which is calculated using a weighted sum of real-time access frequency, predicted future access probability, and its position in the sequential access order.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_score = float('inf')
    for key in cache_snapshot.cache:
        score = calculate_score(key)
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the real-time access frequency is incremented, the predictive access likelihood is recalibrated using recent access patterns, and the sequential order is adjusted to reflect the latest access position.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] += 1
    predictive_access_likelihood[key] = min(1.0, predictive_access_likelihood[key] + 0.1)
    
    if key in sequential_order:
        sequential_order.remove(key)
    sequential_order.append(key)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the policy initializes its metadata with a baseline score, sets its real-time access frequency to one, estimates its predictive access likelihood based on initial access context, and places it at the end of the sequential order.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    access_frequency[key] = 1
    predictive_access_likelihood[key] = 0.5  # Initial estimate
    sequential_order.append(key)
    scores[key] = calculate_score(key)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the policy recalibrates the predictive access likelihood of remaining entries to account for the removal, adjusts the sequential order to close the gap left by the evicted entry, and normalizes the algorithmic scores to maintain balance.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in sequential_order:
        sequential_order.remove(evicted_key)
    
    for key in cache_snapshot.cache:
        predictive_access_likelihood[key] = max(0.0, predictive_access_likelihood[key] - 0.05)
        scores[key] = calculate_score(key)