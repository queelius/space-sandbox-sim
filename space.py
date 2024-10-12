from model.bh import BarnesHut
import pygame
import pygame_gui
from pygame.math import Vector2 as vec2
from utils.utils import *
from model.body import Body
import const
from space_gui import SpaceSandboxGUI
import model.forces as forces
from model.body_list import BodyList
from event_proc import EventProc
from model.apply_merges_slow import apply_merges_slow
from view.renderer import Renderer
from controller.controller import Controller

def main():
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

    renderer = Renderer(screen, const.WIDTH, const.HEIGHT, bodies)
    gui : SpaceSandboxGUI = SpaceSandboxGUI(manager, const.WIDTH, const.HEIGHT)
    barnes_hut : BarnesHut = BarnesHut(theta=10)
    evnt : EventProc = EventProc(gui, manager, bodies, barnes_hut)

    evnt.sel_body = large_body
    evnt.follow_sel = True

    while evnt.running:
        time_delta = clock.tick(const.FPS) / 1000.0
        #screen.fill(const.BACKGROUND_COLOR)

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
        #barnes_hut.draw_quads(screen, barnes_hut.root, evnt.zoom, evnt.pan_x, evnt.pan_y)
        renderer.pan_offset = vec2(evnt.pan_x, evnt.pan_y)
        renderer.zoom = evnt.zoom
        renderer.sel_body = evnt.sel_body

        renderer.render()

        # Update the manager and draw UI elements
        manager.update(time_delta)
        manager.draw_ui(screen)

        # Update the display
        pygame.display.flip()

    pygame.quit()