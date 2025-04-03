# Import anything you need below
import math

# Put tunable constant parameters below
BASELINE_QFM = 0.1
NEUTRAL_ETS = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Frequency Map (QFM) that tracks the access frequency of each cache item using quantum-inspired probabilistic states. It also keeps an Entropic Transition Score (ETS) for each item, representing the entropy of access patterns, and a Temporal Reflex Index (TRI) that records the recency of access harmonized with predictive models.
QFM = {}
ETS = {}
TRI = {}

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy selects the eviction victim by identifying the item with the lowest combined score of QFM and ETS, adjusted by the TRI. This approach ensures that items with low access frequency, high entropy, and low recency are prioritized for eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (QFM[key] + ETS[key]) / (1 + TRI[key])
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QFM is updated to increase the probability state of the accessed item, the ETS is recalculated to reflect reduced entropy, and the TRI is adjusted to reflect the recent access, enhancing its predictive harmony.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    QFM[key] = min(1.0, QFM[key] + 0.1)  # Increase QFM, capped at 1.0
    ETS[key] = max(0.0, ETS[key] - 0.1)  # Decrease ETS, floored at 0.0
    TRI[key] = cache_snapshot.access_count  # Update TRI to current time

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QFM initializes the item's frequency state to a baseline level, the ETS is set to a neutral entropy value, and the TRI is initialized to reflect the current time, ensuring the new item is harmonized with existing cache dynamics.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    QFM[key] = BASELINE_QFM
    ETS[key] = NEUTRAL_ETS
    TRI[key] = cache_snapshot.access_count

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QFM is adjusted to redistribute probability states among remaining items, the ETS is recalibrated to reflect the new cache entropy landscape, and the TRI is updated to account for the temporal shift caused by the eviction.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    if evicted_key in QFM:
        del QFM[evicted_key]
    if evicted_key in ETS:
        del ETS[evicted_key]
    if evicted_key in TRI:
        del TRI[evicted_key]
    
    # Adjust remaining items
    for key in cache_snapshot.cache:
        QFM[key] *= 0.9  # Slightly decrease QFM for remaining items
        ETS[key] += 0.1  # Slightly increase ETS for remaining items
        TRI[key] = cache_snapshot.access_count  # Update TRI to current time