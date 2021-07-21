import numpy as np

class Graph:
        
    def __init__(self, 
                 k_hop, mode):
        
        """
        inputs:
            mode: "hand", "pose", "pose_hand"
        """
        
        self.k_hop = k_hop
        self.mode = mode
        
        self.create_vertex()
        self.create_edge()
        self.create_adjacent_matrix()
        self.create_D()
        self.create_k_hop_matrix()
        
    def create_vertex(self):
        self.pose_num_vertices = 33
        self.hand_num_vertices = 21
        if self.mode == "hand":
            self.num_vertices = self.hand_num_vertices * 2
        elif self.mode == "pose":
            self.num_vertices = self.pose_num_vertices
        elif self.mode == "pose_hand":
            self.num_vertices = self.pose_num_vertices + \
                                self.hand_num_vertices * 2
            
            
        
    def create_edge(self):
        self_edges = [(v, v) for v in range(self.num_vertices)]
        neighbor_edges = [(0, 1), (0, 4), (1, 2), (2, 3),
                         (3, 7), (4, 5), (5, 6), (6, 8), 
                         (9, 10), (11, 12), (11, 13), (11, 23), (12, 14),
                         (12, 24), (13, 15), (14, 16), (15, 17), (15, 19),
                         (15, 21), (16, 18), (16, 20), (16, 22), (17, 19),
                         (18, 20), (23, 24), (23, 25), (24, 26), (25, 27),
                         (26, 28), (27, 29), (27, 31), (28, 30), (28, 32), 
                         (29, 31), (30, 32), 
                        ]
        
        hand_edges = [
            (0, 1), (0, 5), (0, 9), (0, 13), (0, 17),
            (1, 2), (2, 3), (3, 4), (5, 6), (5, 9), 
            (6, 7), (7, 8), (9, 10), (9, 13), (10, 11),
            (11, 12), (13, 14), (13, 17), (14, 15), (15, 16),
            (17, 18), (18, 19), (19, 20)
        ]
        
        if self.mode == "hand":
            left_hand_edges = hand_edges.copy()
            right_hand_edges = [(i+self.hand_num_vertices, j+self.hand_num_vertices) \
                                 for i, j in hand_edges]
            self.edges = self_edges + left_hand_edges + right_hand_edges
        elif self.mode == "pose":
            self.edges = self_edges + neighbor_edges
        elif self.mode == "pose_hand":
            left_hand_edges = [(i+self.pose_num_vertices, j+self.pose_num_vertices) \
                                 for i, j in hand_edges]
            right_hand_edges = [(i+self.hand_num_vertices, j+self.hand_num_vertices) \
                                 for i, j in left_hand_edges]
            self.edges = self_edges + neighbor_edges + left_hand_edges + right_hand_edges
        
    def create_adjacent_matrix(self):
        self.A = np.zeros((self.num_vertices, self.num_vertices))
        for i, j in self.edges:
            self.A[i, j] = 1
            self.A[j, i] = 1
        
    def create_D(self):
        sum_row = self.A.sum(axis=1)
        self.D = np.diag(sum_row)
        
    def normalize_A(self, A):
        return np.linalg.inv(self.D) @ A
    
    def create_k_hop_matrix(self):
        
        As = []
        
        for hop in range(1, self.k_hop + 1):
            As.append(self.normalize_A(np.power(self.A, hop)))
        
        self.A_k = np.stack(As, axis=0)
        