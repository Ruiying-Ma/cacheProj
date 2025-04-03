# Import anything you need below
import math

# Put tunable constant parameters below
BASELINE_FREQUENCY = 1
NEUTRAL_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a Quantum Oscillation Core (QOC) that tracks the oscillation frequency of cache entries, a Temporal Vector Field (TVF) that records the temporal access patterns, a Heuristic Modulation Network (HMN) that adjusts weights based on access frequency and recency, and an Entropic Equilibrium Dynamics (EED) measure that assesses the entropy of cache states.
QOC = {}  # {obj.key: frequency}
TVF = {}  # {obj.key: last_access_time}
HMN = {}  # {obj.key: weight}
EED = 0.0  # Entropy measure of the cache

def calculate_entropy(cache_snapshot):
    # Calculate the entropy of the cache based on the frequency of access
    total_accesses = sum(QOC.values())
    if total_accesses == 0:
        return 0.0
    entropy = -sum((freq / total_accesses) * math.log(freq / total_accesses) for freq in QOC.values() if freq > 0)
    return entropy

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy chooses the eviction victim by identifying the cache entry with the lowest combined score from the QOC and TVF, modulated by the HMN. The EED is used to ensure that the overall entropy of the cache remains balanced, preventing over-concentration of similar access patterns.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    min_score = float('inf')
    
    for key, cached_obj in cache_snapshot.cache.items():
        frequency = QOC.get(key, BASELINE_FREQUENCY)
        last_access_time = TVF.get(key, 0)
        weight = HMN.get(key, NEUTRAL_WEIGHT)
        
        # Calculate score
        score = (frequency + (cache_snapshot.access_count - last_access_time)) * weight
        
        if score < min_score:
            min_score = score
            candid_obj_key = key
    
    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    Upon a cache hit, the QOC frequency for the accessed entry is increased, the TVF is updated to reflect the latest access time, the HMN adjusts the weight to favor recent hits, and the EED is recalculated to reflect the new state of cache entropy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    key = obj.key
    QOC[key] = QOC.get(key, BASELINE_FREQUENCY) + 1
    TVF[key] = cache_snapshot.access_count
    HMN[key] = HMN.get(key, NEUTRAL_WEIGHT) * 1.1  # Favor recent hits
    global EED
    EED = calculate_entropy(cache_snapshot)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    After inserting a new object, the QOC initializes the frequency to a baseline level, the TVF records the current time as the initial access point, the HMN assigns a neutral weight, and the EED is updated to incorporate the new entry's impact on cache entropy.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    key = obj.key
    QOC[key] = BASELINE_FREQUENCY
    TVF[key] = cache_snapshot.access_count
    HMN[key] = NEUTRAL_WEIGHT
    global EED
    EED = calculate_entropy(cache_snapshot)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    Following an eviction, the QOC removes the frequency data of the evicted entry, the TVF clears its temporal data, the HMN rebalances weights across remaining entries, and the EED is recalculated to ensure the cache's entropy remains within optimal bounds.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    evicted_key = evicted_obj.key
    QOC.pop(evicted_key, None)
    TVF.pop(evicted_key, None)
    HMN.pop(evicted_key, None)
    
    # Rebalance weights
    total_weight = sum(HMN.values())
    if total_weight > 0:
        for key in HMN:
            HMN[key] /= total_weight
    
    global EED
    EED = calculate_entropy(cache_snapshot)