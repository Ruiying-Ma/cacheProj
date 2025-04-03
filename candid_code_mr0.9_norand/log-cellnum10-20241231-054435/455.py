# Import anything you need below
from collections import defaultdict

# Put tunable constant parameters below
QFL_BASELINE = 1
EM_WEIGHT = 1.0
TDC_WEIGHT = 1.0
NAI_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains metadata including Quantum Flux Levels (QFL) for each cache entry, an Entropy Map (EM) representing access patterns, Temporal Dynamics Coefficients (TDC) for time-based access prediction, and a Neural Adaptation Index (NAI) for learning from past evictions.
QFL = defaultdict(lambda: QFL_BASELINE)
EM = defaultdict(int)
TDC = defaultdict(int)
NAI = defaultdict(int)

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by calculating a composite score for each entry using a weighted sum of QFL, EM, TDC, and NAI. The entry with the lowest score is selected for eviction, balancing between least accessed, least temporally relevant, and least adaptable entries.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        score = (QFL[key] * EM_WEIGHT + 
                 EM[key] * EM_WEIGHT + 
                 TDC[key] * TDC_WEIGHT + 
                 NAI[key] * NAI_WEIGHT)
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QFL of the accessed entry is incremented to reflect increased quantum stability, the EM is updated to decrease entropy by reinforcing the access pattern, the TDC is adjusted to reflect the current time dynamics, and the NAI is fine-tuned to learn from the successful retention of the entry.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    QFL[obj.key] += 1
    EM[obj.key] += 1
    TDC[obj.key] = cache_snapshot.access_count
    NAI[obj.key] += 1

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QFL is initialized to a baseline level, the EM is updated to include the new access pattern, the TDC is calibrated to predict future access based on current temporal trends, and the NAI is initialized to start learning from the new entry's behavior.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    QFL[obj.key] = QFL_BASELINE
    EM[obj.key] = 1
    TDC[obj.key] = cache_snapshot.access_count
    NAI[obj.key] = 0

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QFL of the evicted entry is reset, the EM is adjusted to remove the outdated access pattern, the TDC is recalibrated to account for the change in cache dynamics, and the NAI is updated to learn from the eviction decision, improving future adaptability.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    QFL.pop(evicted_obj.key, None)
    EM.pop(evicted_obj.key, None)
    TDC.pop(evicted_obj.key, None)
    NAI[evicted_obj.key] = -1