# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
INITIAL_QES = 1.0
INITIAL_NII = 0.0
INITIAL_TRM = 1.0
QES_INCREMENT = 0.5
ASF = 0.1

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Entropy Score (QES) for each cache entry, a Neural Interference Index (NII) to track dynamic interference patterns, a Temporal Resonance Map (TRM) to capture access frequency over time, and an Adaptive Stability Factor (ASF) to adjust sensitivity to changes in access patterns.
qes = defaultdict(lambda: INITIAL_QES)
nii = defaultdict(lambda: INITIAL_NII)
trm = defaultdict(lambda: INITIAL_TRM)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the entry with the lowest Quantum Entropy Score, adjusted by the Neural Interference Index and the Temporal Resonance Map, ensuring that entries with stable access patterns are less likely to be evicted.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = qes[key] - nii[key] + ASF * trm[key]
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the Quantum Entropy Score of the accessed entry is increased to reflect its continued relevance, the Neural Interference Index is recalibrated to account for recent access patterns, and the Temporal Resonance Map is updated to reinforce the temporal access frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    qes[key] += QES_INCREMENT
    nii[key] = (nii[key] + 1) / 2  # Recalibrate NII
    trm[key] += 1  # Reinforce TRM

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the Quantum Entropy Score is initialized based on initial access predictions, the Neural Interference Index is set to a neutral state, and the Temporal Resonance Map is updated to include the new entry with a baseline frequency.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    qes[key] = INITIAL_QES
    nii[key] = INITIAL_NII
    trm[key] = INITIAL_TRM

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the Quantum Entropy Scores of remaining entries are recalibrated to reflect the new cache state, the Neural Interference Index is adjusted to reduce interference from the evicted entry, and the Temporal Resonance Map is updated to remove the evicted entry's influence.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    del qes[evicted_key]
    del nii[evicted_key]
    del trm[evicted_key]
    
    for key in cache_snapshot.cache:
        qes[key] *= (1 - ASF)  # Recalibrate QES
        nii[key] *= (1 - ASF)  # Adjust NII
        trm[key] *= (1 - ASF)  # Update TRM