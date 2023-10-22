from collections import deque
from copy import copy, deepcopy
from math import cos, pi, sin, sqrt
from threading import Lock, Thread
from tkinter import BOTH, CENTER, LAST, Canvas, Tk, font

''' A graphical user iterface for a SimSims network '''

class Coords():
    ''' 
    Represent coordinate pairs.

    Args:
        x1,y1,x2,y2,...: a sequence of coordinate pairs
    '''

    def __init__(self, *args, **kwargs):
        self._coords = []
        self.append(*args)

    def __copy__(self):
        newone = type(self)()
        newone._coords = deepcopy(self._coords)
        return newone

    def __iter__(self):
        return self._coords.__iter__()

    def __getitem__(self, i):
        return self._coords[i]

    def __len__(self):
        return len(self._coords)

    def __str__(self):
        return "["+", ".join([str(f) for f in self._coords])+"]"

    def __eq__(self, other):
        return self._coords == other._coords

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def x(self):
        return self._coords[0]

    @property
    def y(self):
        return self._coords[1]

    def append(self, *args):
        ''' Append one or several coordinate pairs.
            Args:
               x1, y1, x2, y2, ...:    list of coordinate pairs
        '''
        nargs = len(args)
        assert nargs % 2 == 0
        for i in range(0, nargs, 2):
            self._coords.extend((float(args[i]), float(args[i+1])))

    def translate(self, *args):
        ''' Returns a copy of stored coordinates, translated with dx, dy.
            Args:
                dx, dy: value by witch to translate coordinates.
        '''
        if len(args) == 1:
            assert isinstance(args[0], Coords)
            dx, dy = args[0].x, args[0].y
        elif len(args) == 2:
            dx, dy = args[0], args[1]
        else:
            raise ValueError("To many or wrong arguments")

        nw = type(self)()
        for i in range(0, len(self._coords), 2):
            nw.append(self._coords[i]+dx, self._coords[i+1]+dy)
        return nw


class MTCanvas(Canvas):
    ''' A Canvas modified to have limited capability of multi 
        threaded functionality.

        Args:
            master: Master TK-object.
            w: with of the drawing area.
            h: height of the drawing area.
    '''

    def __init__(self, master, w, h):
        Canvas.__init__(self, master, width=w, height=h)
        #self._queue = deque()
        self._queue = set()
        self._lock = Lock()

    def draw_component(self, component):
        self._lock.acquire()
        self._queue.add(component)
        self._lock.release()

    def exec_draw(self):
        ''' Draws objects in the queue. '''
        self._lock.acquire()
        if len(self._queue) > 0:
            for component in self._queue:
                component.update()
            self._queue.clear()
            self.update()
        self._lock.release()


class SimSimsGUI(Tk):
    ''' A GUI class for a SimSims User Interface. 
        A GUI object create other ui objects for tokens, 
        places and transitions.
    '''

    def __init__(self, w=400, h=400):
        Tk.__init__(self)

        self._is_alive = True
        self._uis = []
        self._on_close = None
        self._canvas = MTCanvas(self, w, h)
        self._canvas.pack()

        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind('<Escape>', lambda e: self._close())

        self.update()

    @property
    def canvas(self):
        ''' The canvas used for drawing objects.'''
        return self._canvas

    @property
    def is_alive(self):
        return self._is_alive

    def create_token_gui(self, properties={}):
        ''' Creates an UI for a token.
            Args:
                owner:  The token that uses the ui
                properties: Properties to the ui (see subclass documentation)
        '''
        return GUITokenComponent(self.canvas, properties)

    def create_place_gui(self, properties={}):
        ''' Creates an UI for a place.
            Args:
                owner:  The place that uses the ui
                properties: Properties to the ui (see subclass documentation)
        '''
        ui = GUIPlaceComponent(self.canvas, properties)
        if ui:
            self._uis.append(ui)

        return ui

    def create_transition_gui(self, properties={}):
        ''' Creates an UI for a transition.
            Args:
                owner:  The transition that uses the ui
                properties: Properties to the ui (see subclass documentation)
        '''
        ui = GUITransitionComponent(self.canvas, properties)
        if ui:
            self._uis.append(ui)

        return ui

    def connect(self, src_ui, dst_ui, properties={}):
        ''' Connects the src_ui node_ui ui to dst_ui's UI. 
            No other other purpose than visual.
            Args:
                src_ui: src of an arc.
                dst_ui: dst of an arc.
        '''
        if [x for x in src_ui._arcs if x._out == dst_ui]:
            return

        barcs = [x for x in dst_ui._arcs if x._out == src_ui]
        if barcs:
            barcs[0].bidirectional = True
        else:
            a_ui = self._create_arc_gui(src_ui, dst_ui, properties)
            if a_ui:
                a_ui._out = dst_ui
                a_ui._in = src_ui
                src_ui._arcs.append(a_ui)
                dst_ui._arcs.append(a_ui)
                a_ui.update_position()

    def disconnect(self, src_ui, dst_ui):
        ''' Disconnects the src_uiwith dst_ui's GUI. 
            No other other purpose than visual.
            Args:
                src_ui: src of an arc.
                dst_ui: dst of an arc.
        '''
        # If the arc exists
        arcs = [x for x in dst_ui._arcs if x._out == src_ui if x.bidirectional]
        if arcs:
            a_ui = arcs.pop()
            a_ui.bidirectional = False
            a_ui._set_status(GUIComponent.STATUS_REDRAW)

        arcs = [x for x in src_ui._arcs if x._out == dst_ui]
        if arcs:
            a_ui = arcs.pop()
            if a_ui.bidirectional:
                a_ui.reverse()
                a_ui.bidirectional = False
                a_ui._set_status(GUIComponent.STATUS_REDRAW)
            else:
                src_ui._arcs.remove(a_ui)
                dst_ui._arcs.remove(a_ui)
                a_ui._set_status(GUIComponent.STATUS_DELETE)

    def remove(self, gui):
        ''' Removes a node from the ui.
            Args:
                node_ui: node to remove.
        '''
        gui._set_status(GUIComponent.STATUS_DELETE)
        if gui in self._uis:
            self._uis.remove(gui)

    def on_close(self, fkn):
        ''' Set function to call when UI signals a shoot '''
        self._on_close = fkn

    def start(self):
        ''' Start GUI animation. '''
        self._redraw_frame()

    def close(self):
        ''' Close the GUI animation. '''
        self._close()

    def _redraw_frame(self):
        ''' Help function to keep the animation running. '''
        if self.is_alive:
            self.canvas.exec_draw()
            self.after(50, self._redraw_frame)

    def _close(self):
        ''' Help function to clean up and close.'''
        self._is_alive = False
        Tk.iconify(self)
        if self._on_close:
            self._on_close()
        self.quit()

    def _create_arc_gui(self, src_d, dst_d, properties):
        return GUIArcComponent(self.canvas, src_d, dst_d, properties)


class GUIComponent:
    ''' A base class for objects to draw.
        Args:
            canvas: Tk canvas object.
            properties: properties for the object.
        Properties:
            canvas: Tk canvas object.
            position: current position.
            shapes: shapes of the object.
    '''
    STATUS_OK = 0x00
    STATUS_RESHAPE = 0x01
    STATUS_DELETE = 0x02
    STATUS_DEFINE = 0x04
    STATUS_REDRAW = 0x08

    def __init__(self, canvas, properties):
        self._shapes = []
        self._xy = Coords(0.0, 0.0)
        self._canvas = canvas
        self._status = GUIComponent.STATUS_OK
        self._set_status(GUIComponent.STATUS_DEFINE)
        self._properties = {}
        self.properties = properties

    def __str__(self):
        if "lable" in self.properties.keys():
            lable = " lable: "+self.properties["lable"]
        else:
            lable = ""
        return str(self.__class__.__name__)+" "+str(self.position)+lable

    @property
    def canvas(self):
        ''' The canvas used for drawing objects. '''
        return self._canvas

    @property
    def position(self):
        ''' The position of the object '''
        return self._xy

    @position.setter
    def position(self, *args):
        ''' Sets the position of the object as coordinate pair.'''
        self._reposition(*args)

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, properties):
        self._verify_properties(copy(properties))

    @property
    def shapes(self):
        ''' The canvas used for drawing objects. '''
        return self._shapes

    def update_properties(self, properties):
        ''' Update the properties '''
        self.properties = properties
        self._set_status(GUIComponent.STATUS_RESHAPE)

    def update(self):
        if self._status != GUIComponent.STATUS_OK:
            if self._status & GUIComponent.STATUS_DEFINE:
                self._delete()
                self._define()
            if self._status & GUIComponent.STATUS_DELETE:
                self._delete()
            if self._status & GUIComponent.STATUS_RESHAPE:
                self._reshape()
            if self._status & GUIComponent.STATUS_REDRAW:
                self._reshape()
            self._update()
            self._status = GUIComponent.STATUS_OK

    def rmove(self, dx, dy):
        ''' Moves a graphical component relative its current possition.
            Args:
                dx: relative move in x-direction
                dy: relative move in y-direction
        '''
        self.position = self.position.translate(dx, dy)

    def move(self, x, y):
        ''' Moves a graphical component relative its current possition.
            Args:
                dx: relative move in x-direction
                dy: relative move in y-direction
        '''
        self.position = Coords(x, y)

    def _define(self):
        pass

    def _delete(self):
        for shape in self._shapes:
            self.canvas.delete(shape[0])
        self._shapes.clear()
        

    def _verify_properties(self, properties):
        ''' Assures default property values. '''
        self.properties.update(properties)
        if not "color" in self.properties.keys():
            self.properties["color"] = "#000"
        self._set_status(GUIComponent.STATUS_REDRAW)

    def _reposition(self, *args):
        if len(args) == 1:
            assert isinstance(args[0], Coords)
            coords = args[0]
        elif len(args) == 2:
            coords = Coords(args[0], args[1])
        if self._xy != coords:
            self._xy = coords
            self._set_status(GUIComponent.STATUS_RESHAPE)

    def _reshape(self):
        ''' Draws the component '''
        for s in self._shapes:
            if s[1]:
                coords = s[1].translate(self.position)
                self.canvas.coords(s[0], coords[:])

    def _set_status(self, status):
        self._status |= status
        if status != GUIComponent.STATUS_OK:
            self.canvas.draw_component(self)

    def _update(self):
        pass
   
    @classmethod
    def _sf_radius(cls, k, n, b):
        if k > n-b:
            r = 1
        else:
            r = sqrt(k-1/2)/sqrt(n-(b+1)/2)
        return r

    @classmethod
    def sunflower(cls, n, alpha, radius):
        if n == 1:
            return [Coords(0.0, 0.0)]
        pairs = []
        b = round(alpha*sqrt(n))
        phi = (sqrt(5)+1)/2
        for k in range(1, n+1):
            r = radius*GUIComponent._sf_radius(k, n, b)
            theta = 2*pi*k/phi**2
            x = r*cos(theta)
            y = r*sin(theta)
            pairs.append(Coords(x, y))

        return pairs


class GUINodeComponent(GUIComponent):
    ''' A node component in the gui.
        Args:
            canvas: Tk Canvas
            size: size of the node
            properties: properties for the object.
        Properties:
            tokens: number of tokens
    '''

    def __init__(self, canvas, size, properties={}):
        self._arcs = []
        self._tokens = []
        self._font = None
        self._radius = size
        GUIComponent.__init__(self, canvas, properties)

    def __del__(self):
        for arc in copy(self._arcs):
            arc._in._arcs.remove(arc)
            arc._out._arcs.remove(arc)

            del arc
        self._tokens.clear()

    @property
    def tokens(self):
        ''' Number of tokens '''
        return len(self._tokens)

    def add_token(self, token_ui):
        ''' Add a token UI to this node_ui.
            Args:
                token_ui: UI of the token to add.
        '''
        token_ui.position = Coords(0.0, 0.0)
        self._tokens.append(token_ui)
        self._reposition(self.position)

    def remove_token(self, token_ui):
        ''' Remove a token UI to this node_ui.
            Args:
                token_ui: UI of the token to remove.
        '''
        token_ui.position = Coords(0.0, 0.0)
        self._tokens.remove(token_ui)
        self._reposition(self.position)

    def autoplace(self, index, n_places):
        ''' Place a graphical ui component.
            Args:
                index: the index of the component to place.
                places: the number of spots. Should be the same for all components.
        '''
        w, h = (self.canvas.winfo_width(), self.canvas.winfo_height())
        allpos = GUIComponent.sunflower(
            n_places, 1.0, min(w, h)/2-1.5*self._radius)
        x = w // 2
        y = h // 2

        self.position = Coords(x, y).translate(allpos[index-1])
        for a in self._arcs:
            a.update_position()

    def _define(self):
        GUIComponent._define(self)
        self._font = font.Font(family='Arial', size=7)

    def _reposition(self, args):
        GUIComponent._reposition(self, *args)
        cps = GUIComponent.sunflower(self.tokens, 1.0, 0.8*self._radius)

        try:
            for i in range(self.tokens):
                self._tokens[i].position = cps[i].translate(self.position)
            for a in self._arcs:
                a.update_position()
        except:
            pass

    def anchor_point(self, coord):
        ''' Virtual method to calculate an anchor point for an arc. 
            Arg:
                coord: point that make out the direction for the anchor point.
        '''
        raise NotImplementedError()

    def _verify_properties(self, properties):
        ''' Override from GUIComponent. '''
        GUIComponent._verify_properties(self, properties)
        if not "fill" in self.properties.keys():
            self.properties["fill"] = "#fff"


class GUIPlaceComponent(GUINodeComponent):
    ''' A graphical place component. '''

    def __init__(self, canvas, properties={}):
        GUINodeComponent.__init__(self, canvas, 15.0, properties)

    def anchor_point(self, coord):
        ''' Overrides from GUINodeComponent. '''
        x1, y1 = self.position
        x2, y2 = coord[0]-x1, coord[1]-y1
        r = self._radius
        sr = sqrt(x2*x2 + y2*y2)
        if sr > 0:
            x = r*x2/sr
            y = r*y2/sr
        else:
            x = x1
            y = y1-r
        return Coords(x+x1, y+y1)

    def _define(self):
        ''' Overrides from GUIComponent. '''
        GUINodeComponent._define(self)
        shape = self.canvas.create_oval(
            0.0, 0.0, 0.0, 0.0, fill=self.properties["fill"], width=2, outline=self.properties["color"])
        self.canvas.tag_lower(shape)
        coords = Coords(-self._radius, -self._radius,
                        self._radius, self._radius)
        self.shapes.append((shape, coords))
        if "lable" in self.properties.keys():
            shape = self.canvas.create_text(
                0.0, 0.0, text=self.properties["lable"], font=self._font, justify=CENTER, fill=self.properties["color"])
            coords = Coords(0.0, self._radius+7)
            self.shapes.append((shape, coords))
    def _verify_properties(self, properties):
        ''' Override from UIDrawer '''
        GUINodeComponent._verify_properties(self, properties)
        if self.shapes and "color" in properties.keys():
            self.canvas.itemconfig(self._shapes[0][0], outline=self.properties["color"])
            if len(self.shapes) > 1:
                self.canvas.itemconfig(self._shapes[1][0], fill=self.properties["color"])
        if self.shapes and "fill" in properties.keys():
            self.canvas.itemconfig(self._shapes[0][0], fill=self.properties["fill"])

class GUITransitionComponent(GUINodeComponent):
    ''' A graphical transition drawer '''

    def __init__(self, canvas, properties={}):
        GUINodeComponent.__init__(self, canvas, 12.0, properties)

    def _define(self):
        ''' Overrides from GUINodeComponent '''
        GUINodeComponent._define(self)
        shape = self.canvas.create_rectangle(
            0.0, 0.0, 0.0, 0.0, fill=self.properties["fill"], width=2, outline=self.properties["color"])
        self.canvas.tag_lower(shape)
        coords = Coords(-self._radius, -self._radius,
                        self._radius, self._radius)
        self.shapes.append((shape, coords))
        if "lable" in self.properties.keys():
            shape = self.canvas.create_text(
                0.0, 0.0, text=self.properties["lable"], font=self._font, justify=CENTER, fill=self.properties["color"])
            coords = Coords(0.0, self._radius+7)
            self.shapes.append((shape, coords))
    def _verify_properties(self, properties):
        ''' Override from UIDrawer '''
        GUINodeComponent._verify_properties(self, properties)
        if self.shapes and "color" in properties.keys():
            self.canvas.itemconfig(self._shapes[0][0], outline=self.properties["color"])
            if len(self.shapes) > 1:
                self.canvas.itemconfig(self._shapes[1][0], fill=self.properties["color"])
        if self.shapes and "fill" in properties.keys():
            self.canvas.itemconfig(self._shapes[0][0], fill=self.properties["fill"])

    def anchor_point(self, coord):
        ''' Overrides from GUINodeComponent '''
        x1, y1 = self.position.x, self.position.y
        dx, dy = coord.x-x1, coord.y-y1
        dxa, dya = abs(dx), abs(dy)

        if dxa < 0.0001 and dya < 0.0001:
            (x, y) = (0.0, 0.0)
        elif dxa > dya:
            x = self._radius
            y = self._radius*dya/dxa
        else:
            x = self._radius*dxa/dya
            y = self._radius

        if dx < 0.0:
            x = -x
        if dy < 0.0:
            y = -y

        return Coords(x+x1, y+y1)


class GUITokenComponent(GUIComponent):
    ''' A graphical token drawer '''
    BASE_LENGTH = 2.0

    def __init__(self, canvas, properties={}):
        GUIComponent.__init__(self, canvas, properties)

    def _define(self):
        shape = self.canvas.create_oval(
            0.0, 0.0, 0.0, 0.0, fill=self.properties["color"], width=0, outline=self.properties["color"])
        self.canvas.tag_raise(shape)
        coords = Coords(-GUITokenComponent.BASE_LENGTH, -GUITokenComponent.BASE_LENGTH,
                        GUITokenComponent.BASE_LENGTH, GUITokenComponent.BASE_LENGTH)
        self.shapes.append((shape, coords))


class GUIArcComponent(GUIComponent):
    '''An arc component in the ui.'''

    STATUS_ARROWS = 0x100

    def __init__(self, canvas, outc, inc, properties={}):
        GUIComponent.__init__(self, canvas, properties)
        self._in = inc
        self._out = outc
        self._arrows = LAST

    @property
    def bidirectional(self):
        return self._arrows == BOTH

    @bidirectional.setter
    def bidirectional(self, b):
        if b:
            self._arrows = BOTH
        else:
            self._arrows = LAST
        self._set_status(GUIArcComponent.STATUS_ARROWS)

    def reverse(self):
        tmp = self._in
        self._in = self._out
        self._out = self._in
        self.position = Coords(self.position[2],self.position[3],self.position[0],self.position[1])

    def update_position(self):
        ''' Update the position of the arc's drawer '''
        coord1 = self._in.anchor_point(self._out.position)
        coord2 = self._out.anchor_point(self._in.position)
        coords = Coords(coord1[0], coord1[1], coord2[0], coord2[1])
        self.position = coords

    def _reshape(self):
        if self.shapes:
            self.canvas.coords(self.shapes[0][0], self.position[:])

    def _define(self):
        ''' Overrides from GUIComponent '''
        GUIComponent._define(self)
        coord1 = Coords(0.0, 0.0)
        coord2 = Coords(0.0, 0.0)
        arrow = None
        if self.properties["arrows"]:
            arrow = self._arrows
        else:
            arrow = None
        s = self.canvas.create_line(
            coord1[0], coord1[1], coord2[0], coord2[1], fill=self.properties["color"], width=3, arrow=arrow)
        self.shapes.append((s, None))

    def _update(self):
        if not self.shapes:
            return
        if self._status & GUIArcComponent.STATUS_ARROWS and self.properties["arrows"]:
            self.canvas.itemconfig(self._shapes[0][0], arrow=self._arrows)

    def _verify_properties(self, properties):
        ''' Override from UIDrawer '''
        GUIComponent._verify_properties(self, properties)
        if self.shapes and "color" in properties.keys():
            self.canvas.itemconfig(self._shapes[0][0], fill=self.properties["color"])
        if not "arrows" in self.properties.keys():
            self.properties["arrows"] = False


__author__ = 'Pedher Johansson'
__copyright__ = 'Copyright 2021, Fortsättningskurs i Python'
__version__ = '1.8'
__email__ = 'pedher.johansson@bth.se'

# TEST PROGRAM AND EXAMPLE
if __name__ == "__main__":
    import time

    def callback():
        print("GUI window is closing")

    # Creating GUI
    gui = SimSimsGUI()

    # Creating GUI components for places and transitions
    p1 = gui.create_place_gui({"lable": "p1"})
    # p2 = gui.create_place_gui({"lable": "p2"})
    # t1 = gui.create_transition_gui({"lable": "t1"})
    # t2 = gui.create_transition_gui({"lable": "t2"})

    # Autplace places and transitions
    places = 1
    p1.autoplace(1, places)
    # p2.autoplace(2, places)
    # t1.autoplace(3, places)
    # t2.autoplace(4, places)

    #gui.remove(p3)

    # Connect places and transitions, i.e., creating arcs between them
    # gui.connect(p1, t1, {"arrows": True})
    # gui.connect(p1, t2, {"arrows": True})
    # gui.connect(p2, t2, {"arrows": True})
    # gui.connect(t2, p2, {"arrows": True})

    # # Create GUI components for two tokens
    # r1 = gui.create_token_gui({"color": "#ff0000"})
    # r2 = gui.create_token_gui({"color": "#00ff00"})
    # r3 = gui.create_token_gui({"color": "#0000ff"})

    # # Place the tokens
    # p1.add_token(r1)
    # p1.add_token(r2)
    # t1.add_token(r3)

    # # Sets a callback funktion that is called when the window closes.
    # gui.on_close(callback)

    # Start animation
    gui.start()

    # Main loop in a a non-threaded simulation
    # i = 0
    # while gui.is_alive:
    #     gui.update_idletasks()
    #     # Code to be run on each step

    #     p2.move(200+cos(i*0.1), 100+sin(i*0.1)*40)
    #     p1.move(200+cos(i*0.1)*80, 200+sin(i*0.2)*80)
    #     if i % 2 == 0:
    #         p1.remove_token(r1)
    #         t1.add_token(r1)
    #         p1.properties = {"color":"#000"}
    #     else:
    #         t1.remove_token(r1)
    #         p1.add_token(r1)
    #         p1.properties = {"color":"#f00"}
    #     i += 1

    #     # Updates the GUI
    #     gui.update()
    #     # Change the number below to speed things up or slow it down.
    #     time.sleep(0.1)

    # A simple threaded example below.

    # def moving_token():
    #     while gui.is_alive:
    #         p1.remove_token(r1)
    #         t1.add_token(r1)
    #         #p1.properties = {"color":"#000"}
    #         time.sleep(0.6)
    #         t1.remove_token(r1)
    #         p1.add_token(r1)
    #         #p1.properties = {"color":"#f00"}
    #         time.sleep(0.7)

    # def moving_place():
    #     i = 0
    #     while gui.is_alive:
    #         p1.move(200+cos(i*pi*0.01)*60, 200+sin(i*pi*0.01)*60)
    #         i += 1
    #         time.sleep(0.06)

    # thr1 = Thread(target=moving_token)
    # thr1.start()
    # thr2 = Thread(target=moving_place)
    # thr2.start()

    # gui.mainloop()
