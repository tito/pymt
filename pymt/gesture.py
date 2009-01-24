'''Base for gesture recognition. You can easily use these class to create
new gesture, and compare them ! ::

    from pymt import *

    # Create a gesture
    g = Gesture()
    g.add_stroke(point_list=[(1,1), (3,4), (2,1)])
    g.normalize()

    # Add him to database
    gdb = GestureDatabase()
    gdb.add_gesture(g)

    # And for the next gesture, try to find him !
    g2 = Gesture()
    # ...
    gdb.find(g2)
'''

import math
import pickle, base64, zlib
from cStringIO import StringIO

class GestureDatabase(object):
    '''Class to handle a gesture database.'''
    def __init__(self):
        self.db = []
        #Add the ability to return missed gestures, as an easy way to create new gestures.
        self.returnmismatches = False

    def add_gesture(self, gesture):
        '''Add a new gesture in database'''
        self.db.append(gesture)

    def find(self, gesture, minscore=0.9):
        '''Find current gesture in database'''
        if not gesture:
            return

        best = None
        bestscore = minscore
        for g in self.db:
            score = g.get_score(gesture)
            if score < bestscore:
                continue
            bestscore = score
            best = g
        if not best:
            if self.returnmismatches:
                #Return the missed gesture, so that we can add it to the database.
                return self.gesture_to_str(gesture)
            return
        return (bestscore, best)

    def gesture_to_str(self, gesture):
        '''Convert a gesture into a unique string'''
        io = StringIO()
        p = pickle.Pickler(io)
        p.dump(gesture)
        data = base64.b64encode(zlib.compress(io.getvalue(), 9))
        return data

    def str_to_gesture(self, data):
        '''Convert a unique string to a gesture'''
        io = StringIO(zlib.decompress(base64.b64decode(data)))
        p = pickle.Unpickler(io)
        gesture = p.load()
        return gesture


class GesturePoint:
    def __init__(self, x, y):
        '''Stores the x,y coordinates of a point in the gesture'''
        self.x = float(x)
        self.y = float(y)

    def scale(self, factor):
        ''' Scales the point by the given factor '''
        self.x *= factor
        self.y *= factor
        return self

    def __repr__(self):
        return "Mouse_point:%f,%f"%(self.x,self.y)

class GestureStroke:
    ''' Gestures can be made up of multiple strokes '''
    def __init__(self):
        ''' A stroke in the gesture '''
        self.points = list()

    # These return the min and max coordinates of the stroke
    @property
    def max_x(self):
        if len(self.points) == 0:
            return 0
        return max(self.points, key = lambda pt: pt.x).x
    @property
    def min_x(self):
        if len(self.points) == 0:
            return 0
        return min(self.points, key = lambda pt: pt.x).x
    @property
    def max_y(self):
        if len(self.points) == 0:
            return 0
        return max(self.points, key = lambda pt: pt.y).y
    @property
    def min_y(self):
        if len(self.points) == 0:
            return 0
        return min(self.points, key = lambda pt: pt.y).y

    def add_point(self, x, y):
        '''
        add_point(x=x_pos, y=y_pos)
        Adds a point to the stroke
        '''
        self.points.append(GesturePoint(x, y))

    def scale_stroke(self, scale_factor):
        '''
        scale_stroke(scale_factor=float)
        Scales the stroke down by scale_factor
        '''
        self.points = map(lambda pt: pt.scale(scale_factor), self.points)

    def points_distance(self, point1, point2):
        '''
        points_distance(point1=GesturePoint, point2=GesturePoint)
        Returns the distance between two GesturePoint
        '''
        x = point1.x - point2.x
        y = point1.y - point2.y
        return math.sqrt(x*x + y*y)

    def stroke_length(self, point_list=None):
        '''
        stroke_length([point_list])
        Finds the length of the stroke. If a point list is given, finds the length of that list
        '''
        if point_list is None:
            point_list = self.points
        gesture_length = 0.0
        if len(point_list) <= 1: # If there is only one point, there is no length
            return gesture_length
        for i in xrange(len(point_list)-1):
            gesture_length += self.points_distance(point_list[i], point_list[i+1])
        return gesture_length

    def normalize_stroke(self, sample_points = 32):
        '''
        normalize_stroke([sample_points=int])
        Normalizes strokes so that every stroke has a standard number of points. Returns True if
        stroke is normalized, False if it can't be normalized. sample_points control the resolution of the stroke
        '''
        # If there is only one point or the length is 0, don't normalize
        if len(self.points) <= 1 or self.stroke_length(self.points) == 0.0:
            return False

        # Calulcate how long each point should be in the stroke
        target_stroke_size = self.stroke_length(self.points)/sample_points
        new_points = list()
        new_points.append(self.points[0])
        target_index = 0

        while self.stroke_length(new_points) < self.stroke_length():
            fromPt = new_points[-1] # Start from the last point in the new_points list
            for i in xrange(target_index, len(self.points)):
                distance = self.points_distance(fromPt, self.points[i])
                # When the distance between the start point to a point in the old stroke
                # is >= target distance, calculate where to place the new point
                if distance >= target_stroke_size:
                    x_size = self.points[i].x - fromPt.x
                    y_size = self.points[i].y - fromPt.y
                    ratio = target_stroke_size/distance
                    to_x = x_size * ratio + fromPt.x
                    to_y = y_size * ratio + fromPt.y
                    new_points.append(GesturePoint(to_x, to_y))
                    target_index = i # Stopped at this point in the old list
                    break
            # If we somehow reach the end of the old point list without the new stroke
            # reaching the old stroke length, break the loop
            if self.stroke_length(new_points) < self.stroke_length():
                new_points.append(self.points[-1])
                break
        self.points = new_points
        return True

    def center_stroke(self, offset_x,  offset_y):
        '''
        center_stroke(offset_x=float, offset_y=float)
        Centers the stroke by offseting the points
        '''
        for point in self.points:
            point.x -= offset_x
            point.y -= offset_y

class Gesture:
    '''
    A python implementation of a gesture recognition algorithm by Oleg Dopertchouk
    http://www.gamedev.net/reference/articles/article2039.asp

    Implemented by Jeiel Aranal (chemikhazi@gmail.com), released into the public domain
    '''

    # Tolerance for evaluation using the '==' operator
    DEFAULT_TOLERANCE= 0.1

    def __init__(self, tolerance=None):
        '''
        Gesture([tolerance=float])
        Creates a new gesture with an optional matching tolerance value
        '''
        self.strokes = list()
        if tolerance is None:
            self.tolerance = Gesture.DEFAULT_TOLERANCE
        else:
            self.tolerance = tolerance

    def _scale_gesture(self):
        ''' Scales down the gesture to a unit of 1 '''
        # map() creates a list of min/max coordinates of the strokes
        # in the gesture and min()/max() pulls the lowest/highest value 
        min_x = min(map(lambda stroke: stroke.min_x, self.strokes))
        max_x = max(map(lambda stroke: stroke.max_x, self.strokes))
        min_y = min(map(lambda stroke: stroke.min_y, self.strokes))
        max_y = max(map(lambda stroke: stroke.max_y, self.strokes))
        x_len = max_x - min_x
        y_len = max_y - min_y
        scale_factor = max(x_len, y_len)
        if scale_factor <= 0.0:
            return False
        scale_factor = 1.0/scale_factor
        for stroke in self.strokes:
            stroke.scale_stroke(scale_factor)
        return True

    def _center_gesture(self):
        ''' Centers the Gesture,Point of the gesture '''
        total_x = 0.0
        total_y = 0.0
        total_points = 0

        for stroke in self.strokes:
            # adds up all the points inside the stroke
            stroke_y = reduce(lambda total, pt: total + pt.y, stroke.points, 0.0)
            stroke_x = reduce(lambda total, pt: total + pt.x, stroke.points, 0.0)
            total_y += stroke_y
            total_x += stroke_x
            total_points += len(stroke.points)
        if total_points == 0:
            return False
        # Average to get the offset
        total_x /= total_points
        total_y /= total_points
        # Apply the offset to the strokes
        for stroke in self.strokes:
            stroke.center_stroke(total_x, total_y)
        return True

    def add_stroke(self, point_list=None):
        '''
        add_stroke([point_list=list])
        Adds a stroke to the gesture and returns the Stroke instance
        Optional point_list argument is a list of the mouse points for the stroke
        '''
        self.strokes.append(GestureStroke())
        if isinstance(point_list, list) or isinstance(point_list, tuple):
            for point in point_list:
                if isinstance(point, GesturePoint):
                    self.strokes[-1].points.append(point)
                elif isinstance(point, list) or isinstance(point, tuple):
                    if len(point) < 2 or len(point) > 2:
                        raise ValueError("A stroke entry should only have 2 values")
                    self.strokes[-1].add_point(point[0], point[1])
                else:
                    raise TypeError("The point list should either be tuples of x and y or a list of GesturePoint")
        elif point_list is not None:
            raise ValueError("point_list should be a tuple/list")
        return self.strokes[-1]

    def normalize(self, stroke_samples=32):
        ''' Runs the gesture normalization algorithm and calculates the dot product with self '''
        if not self._scale_gesture() or not self._center_gesture():
            self.gesture_product = False
            return False
        for stroke in self.strokes:
            stroke.normalize_stroke(stroke_samples)
        self.gesture_product = self.dot_product(self)

    def dot_product(self, comparison_gesture):
        ''' Calculates the dot product of the gesture with another gesture '''
        if len(comparison_gesture.strokes) != len(self.strokes):
            return -1
        if getattr(comparison_gesture, 'gesture_product', True) is False or getattr(self, 'gesture_product', True) is False:
            return -1
        dot_product = 0.0
        for stroke_index, (my_stroke, cmp_stroke) in enumerate( zip(self.strokes, comparison_gesture.strokes) ):
            for pt_index, (my_point, cmp_point) in enumerate( zip(my_stroke.points, cmp_stroke.points) ):
                dot_product += my_point.x * cmp_point.x + my_point.y * cmp_point.y
        return dot_product

    def get_score(self, comparison_gesture):
        ''' Returns the matching score of the gesture against another gesture '''
        if isinstance(comparison_gesture, Gesture):
            score = self.dot_product(comparison_gesture)
            if score < 0:
                return score
            score /= math.sqrt(self.gesture_product * comparison_gesture.gesture_product)
            return score

    def __eq__(self, comparison_gesture):
        ''' Allows easy comparisons between gesture instances '''
        if isinstance(comparison_gesture, Gesture):
            # If the gestures don't have the same number of strokes, its definitely not the same gesture
            score = self.get_score(comparison_gesture)
            if score > (1.0 - self.tolerance) and score < (1.0 + self.tolerance):
                return True
            else:
                return False
        else:
            return NotImplemented

    def __ne__(self, comparison_gesture):
        result = self.__eq__(comparison_gesture)
        if result is NotImplemented:
            return result
        else:
            return not result
    def __lt__(self, comparison_gesture): raise TypeError("Gesture cannot be evaluated with <")
    def __gt__(self, comparison_gesture): raise TypeError("Gesture cannot be evaluated with >")
    def __le__(self, comparison_gesture): raise TypeError("Gesture cannot be evaluated with <=")
    def __ge__(self, comparison_gesture): raise TypeError("Gesture cannot be evaluated with >=")
