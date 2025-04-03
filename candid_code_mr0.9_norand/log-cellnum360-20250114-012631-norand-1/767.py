# Import anything you need below. You must not use any randomness. For example, you cannot `import random`. Also, you cannot use any function in `numpy` that uses randomness, such as the functions in `numpy.random`.
from collections import deque, defaultdict

# Put tunable constant parameters below
PCI_WEIGHT = 1.0
TAR_WEIGHT = 1.0
QCM_WEIGHT = 1.0
HAR_WEIGHT = 1.0

# Put the metadata specifically maintained by the policy below. The policy maintains a FIFO queue, a Predictive Clustering Index (PCI) for access patterns, a Temporal Anomaly Resolution (TAR) score for access times, a Quantum-Causal Mapping (QCM) for causal relationships, and a Heuristic Adaptation Ratio (HAR) for dynamic factor adjustment.
fifo_queue = deque()
pci = defaultdict(float)
tar = defaultdict(float)
qcm = defaultdict(float)
har = 1.0

def evict(cache_snapshot, obj):
    '''
    This function defines how the policy chooses the eviction victim.
    The policy first identifies clusters with the lowest PCI scores, then selects the object with the highest TAR score within those clusters. If there is a tie, the QCM is used to determine the least causally impactful object, adjusted by the HAR. The selected object is then evicted from the front of the FIFO queue.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The new object that needs to be inserted into the cache.
    - Return:
        - `candid_obj_key`: The key of the cached object that will be evicted to make room for `obj`.
    '''
    candid_obj_key = None
    # Your code below
    min_pci = float('inf')
    candidates = []

    # Identify clusters with the lowest PCI scores
    for key in cache_snapshot.cache:
        if pci[key] < min_pci:
            min_pci = pci[key]
            candidates = [key]
        elif pci[key] == min_pci:
            candidates.append(key)

    # Select the object with the highest TAR score within those clusters
    max_tar = float('-inf')
    tar_candidates = []
    for key in candidates:
        if tar[key] > max_tar:
            max_tar = tar[key]
            tar_candidates = [key]
        elif tar[key] == max_tar:
            tar_candidates.append(key)

    # Use QCM to determine the least causally impactful object, adjusted by the HAR
    min_qcm = float('inf')
    for key in tar_candidates:
        adjusted_qcm = qcm[key] * har
        if adjusted_qcm < min_qcm:
            min_qcm = adjusted_qcm
            candid_obj_key = key

    return candid_obj_key

def update_after_hit(cache_snapshot, obj):
    '''
    This function defines how the policy update the metadata it maintains immediately after a cache hit.
    The PCI is updated to reflect the current access pattern, the TAR score is adjusted for the recent access time, the QCM is recalculated for updated causal relationships, and the HAR is fine-tuned based on recent evictions. The FIFO queue remains unchanged.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object accessed during the cache hit.
    - Return: `None`
    '''
    # Your code below
    pci[obj.key] += PCI_WEIGHT
    tar[obj.key] = cache_snapshot.access_count
    qcm[obj.key] += QCM_WEIGHT
    har = (cache_snapshot.hit_count + 1) / (cache_snapshot.miss_count + 1)

def update_after_insert(cache_snapshot, obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after inserting a new object into the cache.
    The new object is added to the rear of the FIFO queue. The PCI is updated to include the new access pattern, the TAR score is initialized, the QCM is updated for new causal relationships, and the HAR is adjusted for the new cache composition.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object that was just inserted into the cache.
    - Return: `None`
    '''
    # Your code below
    fifo_queue.append(obj.key)
    pci[obj.key] = PCI_WEIGHT
    tar[obj.key] = cache_snapshot.access_count
    qcm[obj.key] = QCM_WEIGHT
    har = (cache_snapshot.hit_count + 1) / (cache_snapshot.miss_count + 1)

def update_after_evict(cache_snapshot, obj, evicted_obj):
    '''
    This function defines how the policy updates the metadata it maintains immediately after evicting the victim.
    The evicted object is removed from the front of the FIFO queue. The PCI is recalculated to remove the evicted pattern, TAR scores are normalized, the QCM is updated to remove causal links, and the HAR is adjusted based on the eviction's success.
    - Args:
        - `cache_snapshot`: A snapshot of the current cache state.
        - `obj`: The object to be inserted into the cache.
        - `evicted_obj`: The object that was just evicted from the cache.
    - Return: `None`
    '''
    # Your code below
    fifo_queue.popleft()
    del pci[evicted_obj.key]
    del tar[evicted_obj.key]
    del qcm[evicted_obj.key]
    har = (cache_snapshot.hit_count + 1) / (cache_snapshot.miss_count + 1)