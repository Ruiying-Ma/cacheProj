# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
PRIORITY_INCREMENT = 1
BASELINE_QUANTUM_METRIC = 1

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including Priority Assimilation scores, Predictive Threading patterns, Quantum Metrics for access frequency, and Contextual Dynamics for usage context.
priority_assimilation = defaultdict(int)
predictive_threading = defaultdict(list)
quantum_metrics = defaultdict(int)
contextual_dynamics = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score from the Priority Assimilation, Predictive Threading, Quantum Metrics, and Contextual Dynamics, evicting the item with the lowest score.
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
        score = (priority_assimilation[key] +
                 sum(predictive_threading[key]) +
                 quantum_metrics[key] +
                 contextual_dynamics[key])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Priority Assimilation score is increased, Predictive Threading patterns are updated based on recent access sequences, Quantum Metrics are incremented, and Contextual Dynamics are adjusted to reflect the current usage context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    priority_assimilation[key] += PRIORITY_INCREMENT
    predictive_threading[key].append(cache_snapshot.access_count)
    quantum_metrics[key] += 1
    contextual_dynamics[key] = cache_snapshot.access_count

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Priority Assimilation score is initialized, Predictive Threading patterns are set based on initial access predictions, Quantum Metrics start at a baseline frequency, and Contextual Dynamics are established from the insertion context.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    key = obj.key
    priority_assimilation[key] = 0
    predictive_threading[key] = [cache_snapshot.access_count]
    quantum_metrics[key] = BASELINE_QUANTUM_METRIC
    contextual_dynamics[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    After eviction, the policy recalibrates Priority Assimilation scores for remaining items, refines Predictive Threading patterns to account for the change, adjusts Quantum Metrics to redistribute frequency weight, and updates Contextual Dynamics to reflect the new cache state.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    evicted_key = evicted_obj.key
    if evicted_key in priority_assimilation:
        del priority_assimilation[evicted_key]
    if evicted_key in predictive_threading:
        del predictive_threading[evicted_key]
    if evicted_key in quantum_metrics:
        del quantum_metrics[evicted_key]
    if evicted_key in contextual_dynamics:
        del contextual_dynamics[evicted_key]

    # Recalibrate remaining items
    for key in cache_snapshot.cache:
        priority_assimilation[key] = max(0, priority_assimilation[key] - 1)
        quantum_metrics[key] = max(BASELINE_QUANTUM_METRIC, quantum_metrics[key] - 1)
        contextual_dynamics[key] = cache_snapshot.access_count