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
from view.draw import draw_springs
from view.draw import draw_hull
import utils.factories as fact
from model.composite_body import CompositeBody
from utils.spring_mesh import create_spring_mesh
from utils.utils import convex_hull
from utils import factories
from audio.audio_manager import AudioManager
from audio.audio_queue import AudioQueue
from events.event_bus import EventBus


def main():
    pygame.init()
    screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
    pygame.display.set_caption("Space Sandbox Sim")
    event_bus = EventBus()
    clock = pygame.time.Clock()
    bodies = BodyList(max_bodies=const.MAX_BODIES)
    renderer = Renderer(screen, const.WIDTH, const.HEIGHT, bodies)
    controller = Controller(bodies, renderer)
    springs = Springs(bodies, [], event_bus)
    barnes_hut : BarnesHut = BarnesHut(theta=0.5)
    audio_manager = AudioManager(event_bus, lambda: renderer.get_viewport())

    #sun = fact.make_body_circle(
    #    num_bodies=72,
    #    center=vec2(const.WIDTH / 2, const.HEIGHT / 2),
    #    radius=220.0,
    #    mass=5e6)
    
    earth = fact.make_body_circle(
        num_bodies=28,
        center=vec2(const.WIDTH / 2 + 200, const.HEIGHT / 2 + 200),
        radius=32.0,
        mass=1e5,
        vel=vec2(10, -10))
    
    #sun = fact.make_circle(
    #    num_bodies=72,
    #    expected_total_mass=5e6,
    #    com=vec2(const.WIDTH / 2, const.HEIGHT / 2),
    #    com_vel=vec2(0, 0),
    #    radius=220.0,
    #    core_mass_prop=None)

    # is a circle at center pos=(0,0) with radius 250
    def is_circle(pos: vec2) -> bool:
        return pos.length() < 250
    
    sun = fact.make_shape(
        num_bodies=100,
        low_mass=1e3,
        high_mass=1e5,
        max_width=500,
        max_height=500,
        shape_pred=is_circle,
        max_tries=1000000)
    
    for body in sun:
        body.pos += vec2(const.WIDTH / 2 + 1000, const.HEIGHT / 2 + 1000)
        #body.pos = body.pos + vec2(const.WIDTH / 2 + 1000, const.HEIGHT / 2 + 1000)
        

    
    #create_spring_mesh(springs=springs,
    #                   composite=sun,
    #                   stiffness=100000.0,
    #                   damping=1000.0,
    #                   break_force=10000000.0,
    #                   k=7)

    create_spring_mesh(springs=springs,
                       composite=earth,
                       stiffness=5000.0,
                       damping=1000.0,
                       break_force=30000.0,
                       k=5)
    
    mass = 0
    for body in sun:
        mass += body.mass
        bodies.add(body)

    print(f"Sun mass: {mass}")

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
        
        for body in bodies:
            body.update()
        

        #controller.selected_body = apply_merges_slow(
        #    barnes_hut, bodies, controller.selected_body, max_iter=1)
        #if follow_sel and sel_body:
        #    renderer.pan_offset = -sel_body.pos + vec2(const.WIDTH / (2 * renderer.zoom), const.HEIGHT / (2 * renderer.zoom))

        #barnes_hut.draw_quads(barnes_hut.root, renderer.screen, renderer.zoom, renderer.pan_offset)

        renderer.render()
        # Compute the convex hull based on the positions of bodies within comps[1]
        for comp in comps:
            draw_hull(hull=convex_hull([body.pos for body in comp.bodies]),
                      screen=renderer.screen,
                      zoom=renderer.zoom,
                      pan_offset=renderer.pan_offset)

        draw_springs(springs, screen, renderer.zoom, renderer.pan_offset)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()