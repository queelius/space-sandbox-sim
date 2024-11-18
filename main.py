from model.bh import BarnesHut
import math
import pygame
from pprint import pprint
from pygame.math import Vector2 as vec2
from model.body import Body
import utils.const as const
import model.forces as forces
from model.body_list import BodyList
from view.renderer import Renderer
from controller.controller import Controller
from model.springs import Springs
from model.springs import Spring
import utils.factories as fact
from model.composite_body import CompositeBody
from utils.spring_mesh import create_spring_mesh
import model.spontaneous_body_merging as spont
from audio.audio_manager import AudioManager
from audio.audio_queue import AudioQueue
from events.event_bus import EventBus
import view.draw as draw
from utils.circle_tools import CircleTools
from model.spontaneous_body_merging import generate_spontaneous_body_merging
from model.merge_condition import MergeCondtion
from model.condition import Condition
from model.virtual_spring_field import generate_virtual_spring_field
from model.convex_hull import ConvexHull
from model.sim_state import SimState

def main():
    pygame.init()
    screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
    pygame.display.set_caption("Space Sandbox Sim")
    event_bus = EventBus()

    # clock = pygame.time.Clock()
    bodies = BodyList(max_bodies=const.MAX_BODIES)
    renderer = Renderer(event_bus, screen, const.WIDTH, const.HEIGHT, bodies)
    controller = Controller(event_bus, bodies, renderer)
    springs = Springs(bodies, [], event_bus)
    barnes_hut : BarnesHut = BarnesHut(theta=0.5)
    #audio_manager = AudioManager(event_bus, lambda: renderer.get_viewport())

    # sun = fact.make_body_circle(
    #     layers=6,
    #     slack=1e-3,
    #     center=vec2(const.WIDTH / 2 + 1400, const.HEIGHT / 2 + 100),
    #     mass=1e7,
    #     random_color=utils.random_colorizer_based_on_body_density)
    
    # for body in sun:
    #     bodies.add(body)
  
    # earth = fact.make_body_circle(
    #     layers=6,
    #     center=vec2(const.WIDTH / 2, const.HEIGHT / 2 + 100),
    #     mass=1e5,
    #     slack=1e-3,
    #     vel=vec2(500, -250),
    #     random_color=utils.random_colorizer_based_on_body_density,
    #     )
    
    # for body in earth:
    #     bodies.add(body)
    
    sun = CompositeBody(fact.make_shape(
        low_mass=1e3,
        high_mass=1e4,
        max_width=300,
        max_height=300,
        shape_pred=lambda p: p.length() < 150,
        slack=1,
        max_tries=1000))
    for body in sun.bodies:
        body.pos = body.pos + vec2(const.WIDTH / 2, const.HEIGHT / 2)
        bodies.add(body)

    #sun.add_rotational_energy(1e7)
    #sun.add_anglular_velocity2(2 * math.pi / 20)
    #sun.add_internal_energy(1e8)

    sun_springs = create_spring_mesh(springs=springs,
                       composite=sun.bodies,
                       stiffness=1e4,
                       damping=1e1,
                       break_force=Spring.MAX_SPRING_FORCE,
                       break_distance_factor=2,
                       k=7)
    sun.springs = sun_springs
    composites = [sun]
    


    # earth = CompositeBody(fact.make_shape(
    #     low_mass=1e2,
    #     high_mass=1e3,
    #     max_width=150,
    #     max_height=150,
    #     shape_pred=lambda pos: pos.length() < 75,
    #     slack=5,
    #     max_tries=100))
    
    # for body in earth:
    #     body.pos = body.pos + vec2(const.WIDTH / 2, const.HEIGHT / 2 + 100)
    #     bodies.add(body)

    # earth.add_rotational_energy(1e6)
    # earth.add_velocity(vec2(500, -250))

    # create_spring_mesh(springs=springs,
    #                    composite=earth.bodies,
    #                    stiffness=1e4,
    #                    damping=1e2,
    #                    break_force=Spring.MAX_SPRING_FORCE * 1.0,
    #                    break_distance_factor=2,
    #                    k=7)

    from events.handlers import register_handlers
    register_handlers(event_bus, bodies, renderer, controller, sun)


    gravity = forces.generate_gravitational_force(
        event_bus=event_bus,
        G=const.SIM_GRAVITY)
    repulsion = forces.generate_repulsion_force(
       event_bus=event_bus,
       strength=1e3,
       factor=CircleTools.intersection_area,
       beta=1.5)
    collision_damping = forces.generate_collision_damping_force(
       event_bus=event_bus,
       damping=1e2)
    virtual_spring_field = generate_virtual_spring_field(
        event_bus=event_bus,
        distance_threshold=const.NEIGHBORHOOD_RADIUS,
        relative_speed_threshold=100,
        stiffness=1e4,
        damping=1e1,
        break_force=Spring.MAX_SPRING_FORCE * 0.75,
        break_distance_factor=1.5)
   
    spont_merge = spont.generate_spontaneous_body_merging(
        event_bus,
        merge_condition=(MergeCondtion.intersection_area(area_ratio=0.75) &
                         MergeCondtion.relative_speed(speed_threshold=100)))
    

        
    renderer.draw_bodies = True

    while controller.is_running():
        for event in pygame.event.get():
            controller.handle_event(event)
        controller.update()

        bodies.reset_forces()

        if SimState().paused:
            pygame.time.wait(100) # sleep for .1 seconds
            renderer.render()
            draw.draw_springs(springs, renderer)
            pygame.display.update()            
            continue

        barnes_hut.build_tree(bodies)
        barnes_hut.compute_forces(bodies, gravity)
        barnes_hut.compute_neighborhood_pairs(const.NEIGHBORHOOD_RADIUS)
        barnes_hut.compute_local_forces(repulsion)
        barnes_hut.compute_local_forces(collision_damping)

        virtual_spring_field(
            neighbors=barnes_hut.overlapping_pairs,
            springs=springs)
        
        spont_merge(neighbors=barnes_hut.overlapping_pairs,
                    bodies=bodies)

        
        SimState().update(pygame.time.get_ticks())
        springs.update()
        bodies.update()

        comps = springs.find_composite_bodies()
        composites.extend(comps)
        for comp in composites:
            comp.update()

        renderer.render() # should be updated to print composites too
        # for comp in comps:
        #     draw.draw_hull(
        #         hull=comp.convex_hull(),
        #         renderer=renderer,
        #         color=comp.average_color(),
        #         fill=True)

        draw.draw_springs(springs, renderer)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()