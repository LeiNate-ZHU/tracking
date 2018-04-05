import numpy
import math
"""
A Class that computes the ellipse of a cloud of points
"""

class Ellipse:

    def __init__(self, cells, min_ellipse_axis=10):
        """
        Constructor 
        @param cells set of (i,j) tuples, must have at least one cell
        @param min_ellipse_axis min axis length 
        """
        n = len(cells)
        area = float(n)

        inertia = numpy.zeros((2, 2), numpy.float64)

        # centre of cluster
        self.centre = []

        # average radii from the centre
        self.a = 0.
        self.b = 0.

        # from the axes to ij 
        self.axes2ijTransf = numpy.array([[1., 0.], [0., 1.]])
        # from ij to the axes (inverse of the above
        self.ij2AxesTransf = numpy.transpose(self.axes2ijTransf)

        iCentre = numpy.sum([c[0] for c in cells]) / area
        jCentre = numpy.sum([c[1] for c in cells]) / area
        self.centre = numpy.array([iCentre, jCentre])

        # compute inertia tensor (symmetric)
        for i in range(2):
            ci = self.centre[i]
            for j in range(2):
                cj = self.centre[j]
                inertia[i, j] = numpy.sum( \
                        [(ij[i] - ci)*(ij[j] - cj) for ij in cells])

        # the set of eigenvectors is the rotation matrix from ij space to the 
        # inertial tensor's principal axes
        eigenvals, self.axes2ijTransf = numpy.linalg.eig(inertia)
        self.ij2AxesTransf = numpy.transpose(self.axes2ijTransf)

        # get the angle:
        self.angle = -math.atan2(self.ij2AxesTransf[0, 1], self.ij2AxesTransf[0, 0])*180./numpy.pi

        # average radii from the centre
        a, b = numpy.sqrt(eigenvals)
        self.a = max(0.5, a)
        self.b = max(0.5, b)

        # compute the total area
        area = len(cells)

	    # extend the axis to match the cluster's area
        const = math.sqrt(area /(math.pi * self.a * self.b))
        a *= const
        b *= const
        self.a *= const
        self.b *= const

        # add halo to the axes if need be
        #self.aExt = max(min_ellipse_axis, self.a)
        #self.bExt = max(min_ellipse_axis, self.b)
        # smootg transition
        self.aExt = min_ellipse_axis*math.exp(-a) + self.a
        self.bExt = min_ellipse_axis*math.exp(-b) + self.b



    def getPolyline(self, numSegments=32):
        """
        Return the ellipse as a segmented line
        @return iPts, jPts arrays
        """
        iPts, jPts = [], []
        dt = 2 * math.pi / float(numSegments)
        for i in range(numSegments + 1):
            th = i * dt
            x = self.a * math.cos(th)
            y = self.b * math.sin(th)
            # rotate back to i,j coordinates
            ij = self.axes2ijTransf.dot([x, y])
            ij += self.centre
            iPts.append(ij[0])
            jPts.append(ij[1])
        return iPts, jPts


    def getPolylineExt(self, numSegments=32):
        """
        Return the extended ellipse as a segmented line
        @return iPts, jPts arrays
        """
        iPts, jPts = [], []
        dt = 2 * math.pi / float(numSegments)
        for i in range(numSegments + 1):
            th = i * dt
            x = self.aExt * math.cos(th)
            y = self.bExt * math.sin(th)
            # rotate back to i,j coordinates
            ij = self.axes2ijTransf.dot([x, y])
            ij += self.centre
            iPts.append(ij[0])
            jPts.append(ij[1])
        return iPts, jPts


    def __repr__(self):
        """
        Print object
        """
        res = """
        Ellipse: centre = {} a = {} b = {} rotation = {} angle = {}
        """.format(self.centre, self.a, self.b, self.ij2AxesTransf, self.angle)
        return res


    def getCentre(self):
        """
        Get the barycentric centre
        """
        return self.centre


    def isPointInside(self, point):
        """
        Check if point is inside ellipse
        @param point point in j, j index space
        @return True if inside, False if outside or on the boundary
        """
        
        # rotate the coordinates to align them to the principal axes
        ptPrimeAbs = self.ij2AxesTransf.dot(point - self.centre)
        eps = 1.e-12

        if (ptPrimeAbs[0]/(self.a + eps))**2 + (ptPrimeAbs[1]/(self.b + eps))**2 < 1.0:
            # inside
            return True

        return False


    def isPointInsideExt(self, point):
        """
        Check if point is inside extended ellipse
        @param point point in j, j index space
        @return True if inside, False if outside or on the boundary
        """
  
        # rotate the coordinates to align them to the principal axes
        ptPrimeAbs = self.ij2AxesTransf.dot(point - self.centre)
        eps = 1.e-12

        if (ptPrimeAbs[0]/self.aExt)**2 + (ptPrimeAbs[1]/self.bExt)**2 < 1.0:
            # inside
            return True

        return False



    def show(self, points=[], cells={}, show=True):
        """
        Plots the ellipse
        @param points set of points to be shown as inside (stars) or outside (x)
        """
        from matplotlib import pylab
        import matplotlib

        fig, ax = pylab.subplots()

        # show the cells
        patches = []
        for c in cells:
            i, j = c
            pts = numpy.array([[i-0.5, j-0.5], [i+0.5, j-0.5], [i+0.5, j+0.5], [i-0.5, j+0.5]])
            patch = matplotlib.patches.Polygon(pts, closed=True)
            patches.append(patch)
        p = matplotlib.collections.PatchCollection(patches, alpha=0.4)
        ax.add_collection(p)

        # plot the ellipse
        iPts, jPts = self.getPolyline()
        pylab.plot(iPts, jPts, 'r-')
        iPts, jPts = self.getPolylineExt()
        pylab.plot(iPts, jPts, 'b--')

        # add points (stars if inside, crosses if outside)
        pointsInside = []
        pointsOutside = []
        for p in points:
            if self.isPointInside(p):
                pointsInside.append(p)
            else:
                pointsOutside.append(p)
        pylab.plot([p[0] for p in pointsOutside], [p[1] for p in pointsOutside], 'kx')
        pylab.plot([p[0] for p in pointsInside], [p[1] for p in pointsInside], 'cs')

        # label, title, ...
        pylab.xlabel('i')
        pylab.ylabel('j')
        if show:
            pylab.show()

#############################################################################################
def test0():
    # test zero set
    ell = Ellipse({})
    print(ell)

def test1():
    # test zero set
    ell = Ellipse({(-2, 1)})
    print(ell)

def testRectangle():
    ell = Ellipse({(i, 0) for i in range(3)}.union({(i, 1) for i in range(3)}))
    print(ell)

    pts = []
    # these points should be inside
    pt = numpy.array([1., 0.5])
    assert(ell.isPointInside(pt))
    pts.append(pt)

    pt = numpy.array([1.8, 0.5])
    assert(ell.isPointInside(pt))
    pts.append(pt)

    pt = numpy.array([1., 0.99])
    assert(ell.isPointInside(pt))
    pts.append(pt)

    # these points should be outside
    pt = numpy.array([1.82, 0.5])
    #assert(not ell.isPointInside(pt))
    pts.append(pt)

    pt = numpy.array([1., 1.01])
    #assert(not ell.isPointInside(pt))
    pts.append(pt)

    #ell.show(pts)


def testRectangleSlanted():
    import random
    random.seed(1234)

    cells = {(i, 0) for i in range(4)}.union({(i - 1, 1) for i in range(4)})
    ell = Ellipse(cells)
    print(ell)

    # create lots of random points
    pts = [numpy.array([-2. + 6*random.random(), -1. + 3*random.random()]) for i in range(1000)]

    ell.show(pts, cells)


def testRandom():
    import random
    random.seed(1234)
    ell = Ellipse({(random.randint(0, 200), random.randint(0, 100)) for i in range(500)})
    print(ell)


def testMinEllipseAxis(axis=1):
    cells = {(i, 0) for i in range(4)}.union({(i - 1, 1) for i in range(4)})
    ell = Ellipse(cells, min_ellipse_axis=axis)
    ell.show()
    

def testMinEllipseAreaBig():
    cells = {(i, 0) for i in range(4)}.union({(i - 1, 1) for i in range(4)})
    ell = Ellipse(cells, min_ellipse_axis=120)
    ell.show()


if __name__ == '__main__':
#    test0()
#    test1()
#    testRectangle()
#    testRectangleSlanted()
#    testRandom()
#    testMinEllipseAxis(axis=1)
#    testMinEllipseAxis(axis=12)
    testMinEllipseAxis(axis=300)
