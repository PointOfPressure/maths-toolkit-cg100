# PC stub. Never copy to the device: it would shadow the real casioplot.
def set_pixel(x, y, c=None):
    return None

def get_pixel(x, y):
    return (255, 255, 255)

def draw_string(x, y, text, color=None, size=None):
    return None

def clear_screen():
    return None

def show_screen():
    return None

def getkey():
    return 0
