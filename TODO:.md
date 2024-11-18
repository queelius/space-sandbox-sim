TODO:

- Use Dealunay for creating the links between the points in a composite body.
- Maybe look up more efficient convex hull algorithms. I'm using a custom
  made one, but there are probably better ones out there.
    - Although, we may be better off rolling our own `cupy` implementation
      of the convex hull algorithm.
- Use a `cupy` QuadTree implementation. We'll use it for `local forces` and
  other local interactions, like spontaneous spring generation, occupancy
  detection for local repulsive forces, etc.
- Investigage `scipy.spatial.Delaunay` for creating the links between the
    ```
    points = np.array([body.pos for body in sun])
    tri = Delaunay(points)
    print(tri)
    ```
