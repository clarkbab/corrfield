from scipy.sparse import csr_matrix, csgraph
import torch
import torch.nn.functional as F

from .filters import *
from .utils import *

def minimum_spanning_tree(dist):
    device = dist.device
    N = dist.shape[1]
    mst = csgraph.minimum_spanning_tree(csr_matrix(dist[0].cpu().numpy()))
    # BFO returns the list of reachable nodes in the MST from node 0.
    # For some cases, not all nodes are reachable - which is weird because
    # MST should span all nodes. Only use reachable nodes for these cases.
    bfo_nodes, bfo_pre = csgraph.breadth_first_order(mst, 0, directed=False)
    if bfo_nodes.shape != bfo_pre.shape:
        print('issue with MST having non-connected nodes')
    edges = torch.tensor([bfo_pre[bfo_nodes][1:], bfo_nodes[1:]], dtype=torch.long, device=device).t().view(1, -1, 2)
    level = torch.zeros((1, N, 1), dtype=torch.long, device=device)
    for i in range(N-1):
        level[0, edges[0, i, 1], 0] = level[0, edges[0, i, 0], 0] + 1
        
    idx = edges[0,:,1].sort()[1]
    edges = edges[:, idx, :]
        
    return edges, level

def sym_knn_graph(dist, k):
    device = dist.device
    N = dist.shape[1]
    
    include_self=False
    ind = (-dist).topk(k + (1 - int(include_self)), dim=-1)[1][:, :, 1 - int(include_self):]
    A = torch.zeros((N, N), dtype=torch.bool, device=device)
    A[torch.arange(N).repeat(k), ind[0].t().contiguous().view(-1)] = 1
    A[ind[0].t().contiguous().view(-1), torch.arange(N).repeat(k)] = 1
    
    edges = A.nonzero()
    edges_idx = torch.zeros_like(A, dtype=torch.long)
    edges_idx[A] = torch.arange(edges.shape[0], device=device)
    edges_reverse_idx = edges_idx.t()[A]
    
    return edges.unsqueeze(0), edges_reverse_idx.unsqueeze(0)

def kpts_dist(kpts, img, beta, k=64):
    device = kpts.device
    B, N, _ = kpts.shape
    _, _, D, H, W = img.shape
    
    dist = pdist(kpts_world(kpts, (D, H, W), align_corners=True)).sqrt()
    dist[:, torch.arange(dist.shape[1]), torch.arange(dist.shape[2])] = 1e15
    dist[dist<0.1] = 0.1
    img_mean = mean_filter(img, 2)
    kpts_mean = F.grid_sample(img_mean, kpts.view(1, 1, 1, -1, 3).to(img_mean.dtype), mode='nearest', align_corners=True).view(1, -1, 1)
    dist += pdist(kpts_mean, p=1)/beta
    
    include_self=False
    ind = (-dist).topk(k + (1 - int(include_self)), dim=-1)[1][:, :, 1 - int(include_self):]
    A = torch.zeros((B, N, N), device=device)
    A[:, torch.arange(N).repeat(k), ind[0].t().contiguous().view(-1)] = 1
    A[:, ind[0].t().contiguous().view(-1), torch.arange(N).repeat(k)] = 1
    dist = A*dist
    
    return dist

def random_kpts(mask, d, num_points=None):
    device = mask.device
    _, _, D, H, W = mask.shape
    
    kpts = torch.nonzero(mask[:, :, ::d, ::d, ::d]).unsqueeze(0).float()[:, :, 2:] * d
    
    if not num_points is None:
        kpts = kpts[:, torch.randperm(kpts.shape[1])[:num_points], :]
    
    return kpts_pt(kpts, (D, H, W), align_corners=True)