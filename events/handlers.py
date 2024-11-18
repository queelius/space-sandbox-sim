from model.body import Body
from utils import const
import utils.utils as utils
from model.sim_state import SimState

def register_handlers(event_bus, bodies, renderer, controller, sun):

    def handle_toggle_pause(data):
        if not SimState().paused:
            SimState().pause()
            event_bus.publish("show_message", {"message": "Simulation paused"})
        else:
            SimState().resume()
            event_bus.publish("show_message", {"message": "Simulation unpaused"})
        
    event_bus.subscribe("toggle_pause", handle_toggle_pause)
    event_bus.subscribe("zoom_in", lambda data: renderer.zoom_in(data.get("factor", 1.05)))
    event_bus.subscribe("zoom_out", lambda data: renderer.zoom_out(data.get("factor", 1.05)))
    event_bus.subscribe("show_message", lambda data: print(f"Message: {data['message']}"))
    event_bus.subscribe("select_body", lambda data: setattr(renderer, 'selected_body', data['body']))
    event_bus.subscribe("select_body", lambda data: setattr(controller, 'selected_body', data['body']))
    event_bus.subscribe("key_up_event", lambda data: (print(f"key up event: {data['key']}",
                                                            f"controller state: {data['controller_state']}",
                                                            f"event: {data['event']}",
                                                            f"modifier: {data['modifier']}")))
    event_bus.subscribe("unselect_body", lambda _: setattr(renderer, 'selected_body', None))
    event_bus.subscribe("unselect_body", lambda _: setattr(controller, 'selected_body', None))
    event_bus.subscribe("delete_body", lambda data: bodies.remove_item(data["body"]))
    event_bus.subscribe("clear_bodies", lambda _: bodies.clear())
    event_bus.subscribe("add_rotational_energy", lambda data: sun.add_rotational_energy(data["energy"]))
    event_bus.subscribe("exit", lambda _: setattr(controller, 'running', False))

    def move_body_handler(data):
        if "new_pos" in data:
            data["body"].pos = data["new_pos"]
        if "new_vel" in data:
            data["body"].vel = data["new_vel"]
    event_bus.subscribe("body_moved", move_body_handler)
    
    def new_body_handler(data):
        # check for `position' key in data, and raise an error if it is not present
        if "position" not in data:
            raise ValueError("Position key not found in data for new_body_handler")
        
        pos = data["position"]        
        mass = data.get("mass", 1e3)
        radius = data.get("radius", None)
        new_body = Body(pos=pos, mass=mass, radius=radius, base_color=(0, 0, 0))
        new_body.base_color = data.get("color", utils.random_colorizer_based_on_body_density(new_body))
        bodies.add(new_body)

    event_bus.subscribe("new_body", new_body_handler)

    #event_bus.subscribe("spring_connected", lambda data: print(f"spring_connected"))
    #event_bus.subscribe("spring_break_distance", lambda data: print(f"spring_break_distance: {data['break_distance']}"))
    #event_bus.subscribe("spring_break_force", lambda data: print(f"spring_break_force: {data['break_distance']}"))

    def cycle_selected_body(data):
        if renderer.selected_body:
            if renderer.selected_body is None:
                selected_index = 0
            else:
                selected_index = bodies.index(renderer.selected_body) + 1
                selected_index = selected_index % len(bodies)
            renderer.selected_body = bodies[selected_index]
            controller.selected_body = bodies[selected_index]

    event_bus.subscribe("cycle_body", cycle_selected_body)

    def handle_damping_energy_loss(body1, body2, energy_loss):
        """
        we distribute the energy loss from the damping force to the two bodies
        equally. We just add this as new mass to the bodies, by the principle
        of conservation of energy: E = mc^2, so m = E/c^2. we let c = SIM_LIGHT_SPEED
        """

        mass = energy_loss / const.SIM_LIGHT_SPEED ** 2
        # E = mc^2
        # if mass > 1e-3:
        #     event_bus.publish("show_message", {"message": f"Collision damping resulted in significant mass gain: {mass}"})
        body1.mass += mass / 2
        body2.mass += mass / 2

    event_bus.subscribe("collision_damping", lambda data: handle_damping_energy_loss(data["body1"], data["body2"], data["energy_loss"]))

    def pan_view_handler(data):
        renderer.pan(data["delta"])

    event_bus.subscribe('pan_view', pan_view_handler)

    def merge_body_handler(data):
        body1 = data["body1"]
        body2 = data["body2"]
        merged_body = utils.merge_bodies(body1, body2)
        bodies.remove_item(body1)
        bodies.remove_item(body2)
        bodies.add(merged_body)

    event_bus.subscribe("merge_bodies", merge_body_handler) 


    def add_orbital_bodies_handler(data):
        num_bodies = data.get("num_bodies", 1)
        mass = data.get("mass", 1e3)
        radius = data.get("radius", None)
        color = data.get("color", None)
        theta = data.get("theta", None)
        r = data.get("r", None)
        body_orbiting = data.get("body_orbiting", None)
        if body_orbiting is None:
            # let's take the composite `sun` and represent it as a point mass
            total_mass = sun.total_mass()
            com = sun.center_of_mass()

        for _ in range(num_bodies):
            new_body = utils.generate_orbital_bodies(
                mass, radius, color, theta, r, body_orbiting)
            bodies.add(new_body)
    event_bus.subscribe("add_orbital_bodies", add_orbital_bodies_handler)

    
