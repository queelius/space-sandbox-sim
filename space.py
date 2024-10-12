from bh import BarnesHut
import pygame
import pygame_gui
from pygame.math import Vector2 as vec2
from itertools import combinations
from utils import *
from body import Body
import const
from space_gui import SpaceSandboxGUI
import forces
from body_list import BodyList
from event_proc import EventProc
from apply_merges_slow import apply_merges_slow

pygame.init()
screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
pygame.display.set_caption("Space Sandbox Sim")
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((const.WIDTH, const.HEIGHT))
bodies = BodyList(max_bodies=const.MAX_BODIES)

large_body = Body(pos=vec2(const.WIDTH / 2, const.HEIGHT / 2),
                  base_color=const.COLORS[1],
                  mass=10000000.0)
bodies.add(large_body)



#springs = Springs(bodies, [])





gui : SpaceSandboxGUI = SpaceSandboxGUI(manager, const.WIDTH, const.HEIGHT)
barnes_hut : BarnesHut = BarnesHut(theta=10)
evnt : EventProc = EventProc(gui, manager, bodies, barnes_hut)

evnt.sel_body = large_body
evnt.follow_sel = True

while evnt.running:
    time_delta = clock.tick(const.FPS) / 1000.0
    screen.fill(const.BACKGROUND_COLOR)

    evnt.step()

    # Reset forces for all bodies
    for body in bodies:
        body.reset_force()

    barnes_hut.build_tree(bodies)
    #large_bodies = [body for body in bodies if body.mass > 10000]
    
    barnes_hut.compute_forces(bodies, forces.gravitational_force)

    barnes_hut.compute_overlapping_pairs()
    barnes_hut.compute_local_forces(forces.repulsion_force)
    barnes_hut.compute_local_forces(forces.collision_damping_force)
    for body in bodies:
        body.update()

    evnt.sel_body = apply_merges_slow(barnes_hut, bodies, evnt.sel_body, 1000)
    # Follow selected body if enabled
    if evnt.follow_sel and evnt.sel_body:
        evnt.pan_x = -evnt.sel_body.pos.x + const.WIDTH / (2 * evnt.zoom)
        evnt.pan_y = -evnt.sel_body.pos.y + const.HEIGHT / (2 * evnt.zoom)

    # Draw bodies
    #screen.fill(const.BACKGROUND_COLOR)
    for body in bodies:
        # TODO: Refactor to the View class in our MVC pattern. Also,
        #      use `pygame.Surface` for drawing the circle instead.
        draw_pos = (body.pos + vec2(evnt.pan_x, evnt.pan_y)) * evnt.zoom
        draw_radius = body.radius * evnt.zoom
        
        pygame.draw.circle(screen,
                           body.color,
                           (int(draw_pos.x), int(draw_pos.y)),
                           draw_radius)
        if body is evnt.sel_body:
            pygame.draw.circle(screen, const.HIGHLIGHT_COLOR, (int(draw_pos.x), int(draw_pos.y)), draw_radius + 7, 3)

    #barnes_hut.draw_quads(screen, barnes_hut.root, evnt.zoom, evnt.pan_x, evnt.pan_y)

    # Update the manager and draw UI elements
    manager.update(time_delta)
    manager.draw_ui(screen)

    # Update the display
    pygame.display.flip()

pygame.quit()