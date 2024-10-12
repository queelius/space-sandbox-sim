from body import Body
import pygame
import pygame_gui
import math

max_mass = 1e20
min_mass = 1e-5
max_radius = 1e20
min_radius = 1e-5

class SpaceSandboxGUI:
    def __init__(self, manager, width, height):
        """Initialize the GUI for Space Sandbox."""
        self.manager = manager
        self.width = width
        self.height = height
        self.distance_input = None
        self.mass_slider = None
        self.radius_slider = None
        self.color_picker_button = None
        self.color_picker_dialog = None
        self.submit_button = None
        self.labels = []
        self.selected_object = None
        self.mass_value_label = None
        self.radius_value_label = None

    def create_edit_inputs(self, selected_object: Body):
        """Create input fields for editing the properties of a selected object."""
        self.selected_object = selected_object
        self._create_mass_slider(selected_object)
        self._create_radius_slider(selected_object)
        self._create_color_picker_button()
        self.submit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((320, self.height - 80), (100, 30)),
            text='Submit',
            manager=self.manager
        )

    def _create_mass_slider(self, selected_object: Body):
        log_min_mass = math.log10(min_mass)
        log_max_mass = math.log10(max_mass)
        initial_value = math.log10(selected_object.mass) if min_mass <= selected_object.mass <= max_mass else log_min_mass
        self.mass_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, self.height - 210), (300, 30)),
            start_value=initial_value,
            value_range=(log_min_mass, log_max_mass),
            manager=self.manager
        )
        self.labels.append(pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, self.height - 240), (300, 30)),
            text='Mass (logarithmic scale):',
            manager=self.manager
        ))
        self.mass_value_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((320, self.height - 210), (100, 30)),
            text=f'{selected_object.mass:.2e}',
            manager=self.manager
        )

    def _create_radius_slider(self, selected_object: Body):
        log_min_radius = math.log10(min_radius)
        log_max_radius = math.log10(max_radius)
        initial_value = math.log10(selected_object.radius) if min_radius <= selected_object.radius <= max_radius else log_min_radius
        self.radius_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, self.height - 170), (300, 30)),
            start_value=initial_value,
            value_range=(log_min_radius, log_max_radius),
            manager=self.manager
        )
        self.labels.append(pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, self.height - 200), (300, 30)),
            text='Radius (logarithmic scale):',
            manager=self.manager
        ))
        self.radius_value_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((320, self.height - 170), (100, 30)),
            text=f'{selected_object.radius:.2e}',
            manager=self.manager
        )

    def _create_color_picker_button(self):
        self.color_picker_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, self.height - 130), (300, 30)),
            text='Select Color',
            manager=self.manager
        )
        self.labels.append(pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, self.height - 160), (300, 30)),
            text='Color:',
            manager=self.manager
        ))

    def open_color_picker(self):
        self.color_picker_dialog = pygame_gui.windows.UIColourPickerDialog(
            rect=pygame.Rect((self.width // 2 - 200, self.height // 2 - 200), (400, 400)),
            manager=self.manager,
            window_title='Pick a Color'
        )

    def handle_submit(self, selected_object: Body, bodies: list[Body]):
        """Handle the submit action to update or create celestial objects."""
        if self.mass_slider and self.radius_slider and selected_object:
            self._update_selected_object(selected_object)
            self._cleanup_edit_inputs()
        if self.submit_button:
            self.submit_button.kill()
            self.submit_button = None
        self._cleanup_labels()

    def _update_selected_object(self, selected_object: Body):
        selected_object.mass = 10 ** self.mass_slider.get_current_value()
        selected_object.radius = 10 ** self.radius_slider.get_current_value()
        if self.color_picker_dialog and self.color_picker_dialog.current_colour:
            selected_object.color = tuple(self.color_picker_dialog.current_colour)

    def handle_events(self, event):
        """Handle GUI events such as opening the color picker or interacting with sliders."""
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.color_picker_button:
                    self.open_color_picker()
            elif event.user_type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                if self.color_picker_dialog:
                    self.color_picker_dialog.kill()
                    self.color_picker_dialog = None
                    if event.colour and self.selected_object:
                        # Update the color of the selected body
                        self.selected_object.color = tuple(event.colour)
            elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == self.mass_slider:
                    mass_value = 10 ** self.mass_slider.get_current_value()
                    self.mass_value_label.set_text(f'{mass_value:.2e}')
                elif event.ui_element == self.radius_slider:
                    radius_value = 10 ** self.radius_slider.get_current_value()
                    self.radius_value_label.set_text(f'{radius_value:.2e}')

    def _cleanup_edit_inputs(self):
        if self.mass_slider:
            self.mass_slider.kill()
            self.mass_slider = None
        if self.radius_slider:
            self.radius_slider.kill()
            self.radius_slider = None
        if self.color_picker_button:
            self.color_picker_button.kill()
            self.color_picker_button = None
        if self.color_picker_dialog:
            self.color_picker_dialog.kill()
            self.color_picker_dialog = None
        if self.mass_value_label:
            self.mass_value_label.kill()
            self.mass_value_label = None
        if self.radius_value_label:
            self.radius_value_label.kill()
            self.radius_value_label = None

    def _cleanup_labels(self):
        for label in self.labels:
            label.kill()
        self.labels.clear()