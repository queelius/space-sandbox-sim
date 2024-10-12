from pygame_gui import UIManager
import pygame_gui
import pygame
import random
import math
import const
from body import Body
from space_gui import SpaceSandboxGUI
from pygame.math import Vector2 as vec2
from body_list import BodyList
import utils
from bh import BarnesHut

class EventProc:
    def __init__(self, gui: SpaceSandboxGUI, manager: UIManager, bodies: BodyList, barnes_hut: BarnesHut):
        self.zoom: float = 1
        self.pan_x: float = 0 
        self.pan_y: float = 0
        self.is_panning: bool = False
        self.pan_start_x: float = 0
        self.pan_start_y: float = 0    
        self.sel_body = None
        self.follow_sel = True
        self.manager = manager
        self.gui = gui
        self.bodies = bodies
        self.running = True
        self.barnes_hut = barnes_hut
        self.auto_new_rel_body_mass_mu = 0.01
        self.auto_new_rel_body_mass_var = 0.0001

    def step(self):
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Process GUI events
            self.manager.process_events(event)
            self.gui.handle_events(event)

            # Mouse and keyboard events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click to select or create
                    if self.manager.get_focus_set() is None:
                        x, y = event.pos
                        x = (x / self.zoom) - self.pan_x
                        y = (y / self.zoom) - self.pan_y
                        xy = vec2(x, y)

                        if self.sel_body:
                            
                            if (self.sel_body.pos - xy).length() < self.sel_body.radius:
                                self.sel_body = None
                                self.follow_sel = False
                                continue
                            else:
                                found_body = False
                                for obj in self.bodies:
                                    if (obj.pos - xy).length() < obj.radius:
                                        self.sel_body = obj
                                        self.follow_sel = True
                                        found_body = True
                                        break
                                if not found_body:
                                    rel_mass = min(1e-6, random.gauss(self.auto_new_rel_body_mass_mu,
                                                                      self.auto_new_rel_body_mass_var))
                                    new_mass = rel_mass * self.sel_body.mass                                    
                                    new_body = utils.add_orbital_body(self.bodies, self.sel_body, xy, new_mass)
                                    print(f"[new orbital body {new_body}] around {self.sel_body} at a distance {(new_body.pos - self.sel_body.pos).length()}]")
                        
                        else:
                            found_body = False
                            for obj in self.bodies:
                                if (obj.pos - xy).length() < obj.radius:
                                    self.sel_body = obj
                                    self.follow_sel = True
                                    found_body = True
                                    break

                            if not found_body:

                                rel_mass = max(1e-6, random.gauss(self.auto_new_rel_body_mass_mu,
                                                                  self.auto_new_rel_body_mass_var))
                                # let ref mass be largest body mass in the system
                                ref_mass = max([body.mass for body in self.bodies], default=1)
                                new_mass = rel_mass * ref_mass
                                new_obj = Body(xy, new_mass, random.choice(const.COLORS))
                                new_obj.velocity = utils.weighted_velocity(self.bodies)
                                self.bodies.add(new_obj)
                                print(f"[new body: {new_obj}]")

                elif event.button == 3: # Right click to create new body
                    if self.manager.get_focus_set() is None:
                        x, y = event.pos
                        x = (x / self.zoom) - self.pan_x
                        y = (y / self.zoom) - self.pan_y
                        xy = vec2(x, y)
                        
                        found_body = False
                        for body in self.bodies:
                            if (body.pos - xy).length() < body.radius:
                                found_body = True
                                break

                        if found_body:
                            continue

                        if self.sel_body:
                            rel_mass = input("Enter relative mass (percent) of new body (default to 0.1 to 1 percent of selected body): ")
                            eccen = input("Enter eccentricity of orbit (default: 0): ")
                            if eccen == "":
                                eccen = 0
                            else:
                                eccen = float(eccen)
                            # input is a string representing a decimal number, so let's convert it to a float
                            if rel_mass is None:
                                rel_mass = random.uniform(0.001, 0.01)
                            else:   
                                rel_mass = float(rel_mass) / 100.0
                            print(f"Relative mass: {rel_mass}")
                            mass = float(rel_mass) * self.sel_body.mass
                            print(f"Parent Mass: {self.sel_body.mass}")
                            print(f"Mass: {mass}")
                            new_body = utils.add_orbital_body(bodies=self.bodies,
                                                              other_body=self.sel_body,
                                                              pos=xy,
                                                              mass=mass,
                                                              eccentricity=eccen)
                            print(f"[new orbital body {new_body} around {self.sel_body} at a distance {(new_body.pos - self.sel_body.pos).length()}]")
                        else:
                            new_mass = input(f"Enter mass of new body (default: Normal({self.auto_new_body_mass_mu}, {self.auto_new_body_mass_var})): ")
                            new_vel = input("Enter velocity of new body (default: 0, 0): ")
                            if new_mass is None:
                                new_mass = max(self.auto_new_body_mass_min,
                                               random.gauss(self.auto_new_body_mass_mu, self.auto_new_body_mass_var))
                            new_obj = Body(xy, new_mass, random.choice(const.COLORS))
                            if new_vel is not None:
                                new_vel = vec2(*map(float, new_vel.split()))
                            else:
                                new_vel = utils.weighted_velocity(self.bodies)
                            new_obj.velocity = new_vel
                            self.bodies.add(new_obj)                   
                            print(f"[new body: {new_obj}]")
                elif event.button == 2:  # Middle mouse button to start panning
                    self.is_panning = True
                    self.pan_start_x, self.pan_start_y = event.pos
                elif event.button == 4:  # Scroll up to zoom in
                    self.zoom *= 1.1
                elif event.button == 5:  # Scroll down to zoom out
                    self.zoom /= 1.1
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:  # Release middle mouse button to stop panning
                    self.is_panning = False
            elif event.type == pygame.MOUSEMOTION:
                if self.is_panning:  # Pan the view while dragging with middle mouse button
                    dx, dy = event.pos
                    self.pan_x += (dx - self.pan_start_x) / self.zoom
                    self.pan_y += (dy - self.pan_start_y) / self.zoom
                    self.pan_start_x, self.pan_start_y = dx, dy
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL:
                    self.ctrl_pressed = False
                elif event.key == pygame.K_LSHIFT:
                    self.shift_pressed = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and self.sel_body:  # 'e' to edit selected body
                    self.gui.create_edit_inputs(self.sel_body)
                # let's let detect modifier keys
                elif event.key == pygame.K_LCTRL:
                    self.ctrl_pressed = True
                elif event.key == pygame.K_LSHIFT:
                    self.shift_pressed = True
                    
                elif event.key == pygame.K_b:
                    self.barnes_hut.theta += 0.5
                    print(f"[theta={self.barnes_hut.theta}]")
                elif event.key == pygame.K_v:
                    self.barnes_hut.theta -= 0.5
                    if self.barnes_hut.theta <= 0:
                        self.barnes_hut.theta = 1e-6
                    print(f"[theta={self.barnes_hut.theta}]")
                elif event.key == pygame.K_TAB:  # Tab key to cycle through bodies
                    if len(self.bodies) > 0:
                        if self.sel_body:
                            selected_index = self.bodies.index(self.sel_body)
                            selected_index = (selected_index + 1) % len(self.bodies)
                            self.sel_body = self.bodies[selected_index]
                        else:
                            self.sel_body = self.bodies[0]
                        self.follow_sel = True
                        print(f"[selected body: {self.sel_body}]")
                elif event.key == pygame.K_f:  # 'f' to toggle follow selected body
                    self.follow_sel = not self.follow_sel
                elif event.key == pygame.K_u:  # 'u' to unselect and stop following
                    self.sel_body = None
                    self.follow_sel = False
                elif event.key == pygame.K_DELETE and self.sel_body:
                    self.bodies.remove_item(self.sel_body)
                    self.sel_body = None
                    self.follow_sel = False
                elif event.key == pygame.K_c:  # Clear all bodies
                    self.bodies.clear()
                    self.sel_body = None
                    self.follow_sel = False
                elif event.key == pygame.K_a and self.sel_body:
                    num_bodies = input("Enter number of bodies to add (default: 1000): ")
                    num_bodies = int(num_bodies) if num_bodies else 1000
                    dist_mu = input("Enter mean distance from selected body (default: 12.5 x radius): ")
                    dist_mu = float(dist_mu) if dist_mu else 12.5 * self.sel_body.radius
                    dist_var = input("Enter distance variance (default: 0.05 * mean distance): ")
                    dist_var = float(dist_var) if dist_var else 0.05 * dist_mu
                    rel_mass_mu = input("Enter mean relative mass (default: 0.001): ")
                    rel_mass_mu = float(rel_mass_mu) if rel_mass_mu else 0.001
                    rel_mass_var = input("Enter relative mass variance (default: 0.001): ")
                    rel_mass_var = float(rel_mass_var) if rel_mass_var else 0.001

                    # print("Adding orbital bodies:")
                    # print("----------------")
                    # print(f"Number of bodies: {num_bodies}")
                    # print(f"Mean distance from body: {dist_mu}")
                    # print(f"Distance variance: {dist_var}")
                    # print(f"Mean relative mass: {rel_mass_mu}")
                    # print(f"Relative mass variance: {rel_mass_var}")
                    # print("----------------")

                    utils.add_orbital_bodies(
                        bodies=self.bodies,
                        num_bodies=num_bodies,
                        center_body=self.sel_body,
                        dist_mu=dist_mu,
                        dist_var=dist_var,
                        rel_mass_mu=rel_mass_mu,
                        rel_mass_var=rel_mass_var)

            # Handle GUI submissions
            if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.gui.submit_button:
                self.gui.handle_submit(self.sel_body, self.bodies)

