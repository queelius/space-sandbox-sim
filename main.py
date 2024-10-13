from model.bh import BarnesHut
import pygame
from pygame.math import Vector2 as vec2
from utils.utils import *
from model.body import Body
import utils.const as const
import model.forces as forces
from model.body_list import BodyList
from model.apply_merges_slow import apply_merges_slow
from view.renderer import Renderer
from controller.controller import Controller
from model.springs import Springs
from view.draw_springs import draw_springs
from utils.body_factories import make_body_circle, make_body_square
from model.composite_body import CompositeBody
from utils.spring_mesh import create_spring_mesh

def main():
    pygame.init()
    screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
    pygame.display.set_caption("Space Sandbox Sim")
    clock = pygame.time.Clock()
    bodies = BodyList(max_bodies=const.MAX_BODIES)
    renderer = Renderer(screen, const.WIDTH, const.HEIGHT, bodies)
    controller = Controller(bodies, renderer)
    springs = Springs(bodies, [])
    barnes_hut : BarnesHut = BarnesHut(theta=0.5)

    sun = make_body_circle(
        num_bodies=70,
        center=vec2(const.WIDTH / 2, const.HEIGHT / 2),
        radius=210.0,
        mass=5e6)
    
    earth = make_body_circle(
        num_bodies=30,
        center=vec2(const.WIDTH / 2 + 175, const.HEIGHT / 2 + 200),
        radius=40.0,
        mass=1e5)    
    
    create_spring_mesh(springs=springs,
                       composite=sun,
                       stiffness=30000.0,
                       damping=1000.0,
                       break_force=10000000.0,
                       k=9)

    create_spring_mesh(springs=springs,
                       composite=earth,
                       stiffness=30000.0,
                       damping=100.0,
                       break_force=100000.0,
                       k=11)

    #from utils.utils import convex_hull

    
    for body in sun:
        bodies.add(body)

    for body in earth:
        bodies.add(body)
    
    while controller.is_running():

        time_delta = clock.tick(const.FPS) / 1000.0

        for event in pygame.event.get():
            controller.handle_event(event)

        # Reset forces for all bodies
        for body in bodies:
            body.reset_force()

        barnes_hut.build_tree(bodies)
        #large_bodies = [body for body in bodies if body.mass > 10000]
        
        barnes_hut.compute_forces(bodies, forces.gravitational_force)
        barnes_hut.compute_overlapping_pairs()
        barnes_hut.compute_local_forces(forces.repulsion_force)
        barnes_hut.compute_local_forces(forces.collision_damping_force)

        springs.update()
        comps = springs.find_composite_bodies()
        
        # Apply zoom and pan transformations
            

        for body in bodies:
            body.update()

        

        #controller.selected_body = apply_merges_slow(
        #    barnes_hut, bodies, controller.selected_body, max_iter=1)
        #if follow_sel and sel_body:
        #    renderer.pan_offset = -sel_body.pos + vec2(const.WIDTH / (2 * renderer.zoom), const.HEIGHT / (2 * renderer.zoom))

        #barnes_hut.draw_quads(screen, barnes_hut.root, evnt.zoom, evnt.pan_x, evnt.pan_y)

        renderer.render()

        def render_hull(hull):
            for i in range(len(hull)):
                start_pos = (hull[i] + renderer.pan_offset) * renderer.zoom
                end_pos = (hull[(i + 1) % len(hull)] + renderer.pan_offset) * renderer.zoom
                pygame.draw.line(surface=renderer.screen,
                                color=(255, 255, 255),
                                start_pos=(int(start_pos.x), int(start_pos.y)),
                                end_pos=(int(end_pos.x), int(end_pos.y)),
                                width=10)
        # Compute the convex hull based on the positions of bodies within comps[1]
        for comp in comps:
            hull = convex_hull([body.pos for body in comp.bodies])
            render_hull(hull)

        #screen_pos = (comps[1].pos + renderer.pan_offset) * renderer.zoom
        #radius = max(1, int(comps[1].radius * renderer.zoom))
        #pygame.draw.circle(renderer.screen,
        #                   (255, 110, 10),
        #                   (int(screen_pos.x), int(screen_pos.y)),
        #                   radius)


        #draw_springs(screen, springs, renderer.zoom, renderer.pan_offset.x, renderer.pan_offset.y)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()