'''
This module should hold all debug flags, so that we can conveniently choose which debugging message should be displayed.
'''


game_controller_fires_no_events = False
game_status_fires_no_events = False


# Per file debug flags:
player_py_debug = True # This debugging message is in charge of all debug messages inside player.py.
gamestatus_py_debug = True # This debugging message is in charge of all debug messages inside gamestatus.py.


# Colors are hard to see.
print_chest_button_led_color_changes = True # TODO: Not read anywhere, for the time being.
