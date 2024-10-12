from model.bh import BarnesHut
from model.body import Body
from model.body_list import BodyList
from model.forces import merge_bodies

def apply_merges_slow(bh: BarnesHut,
                      bodies: BodyList,
                      sel_body: Body,
                      max_iter=1):
    
    while max_iter > 0:
        max_iter -= 1
        body_to_index = None
        merges = False
        for body1, body2 in bh.overlapping_pairs:
            new_body = merge_bodies(body1, body2)
            if new_body:
                if body_to_index is None:
                    body_to_index = {body: i for i, body in enumerate(bodies)}
                merges = True
                if body1 is sel_body or body2 is sel_body:
                    sel_body = new_body
                i = body_to_index[body1]
                j = body_to_index[body2]
                bodies[i] = new_body
                bodies[j] = bodies[bodies.num_bodies-1]
                body_to_index[new_body] = i
                body_to_index[bodies[j]] = j
                bodies.num_bodies -= 1

        if not merges:
            break
        bh.build_tree(bodies)

    return sel_body

    