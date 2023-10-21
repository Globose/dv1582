import simsimsgui
import time

gui = simsimsgui.SimSimsGUI(w=500, h=500)
trans_gui = gui.create_transition_gui()
place_gui = gui.create_place_gui()
token_gui = gui.create_token_gui()

trans_gui.add_token(token_gui)
# trans_gui.remove_token(token_gui) # Objektet returneras inte
place_gui.add_token(token_gui)

trans_gui.autoplace(0,3)
place_gui.autoplace(1,3)

gui.connect(trans_gui, place_gui)

gui.start()
time.sleep(10)
