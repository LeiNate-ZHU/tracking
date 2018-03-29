import numpy
import math
from ellipse import Ellipse

class Cluster:

    def __init__(self, cells={}, min_ellipse_area=1):
        """
        Constructor 
        @param cells set of (i,j) tuples
        @param min_ellipse_area ellipse axes will be scaled to match 
                                min_ellipse_area or larger
        """
        # set of i,j cells 
        self.cells = cells

        # want the ellipse axes to scale to at least this area
        self.min_ellipse_area = min_ellipse_area

        # ellipse representing the "average" distribution
        # of cells
        self.ellipse = None

        # min/max indices of the box containing the set of points
        self.box = [[None, None], [None, None]]

        # compute the ellipse...
        self.update()
    

    def getNumberOfCells(self):
        """
        Get the number of cells
        @return number
        """
        return len(self.cells)


    def update(self):

        if len(self.cells) > 0:

            self.ellipse = Ellipse(self.cells, min_ellipse_area=self.min_ellipse_area)

            for dim in range(0, 2):
                self.box[0][dim] = numpy.min([c[dim] for c in self.cells])
                self.box[1][dim] = numpy.max([c[dim] for c in self.cells])



    def isCentreInsideOf(self, otherCluster):
        """
        Return True if this ellipse' centre is inside the other cluster's ellipse
        """
        return otherCluster.ellipse.isPointInside(self.ellipse.getCentre())


    def getCentre(self):
        """
        Get the centre 
        @return array 
        """
        return self.ellipse.getCentre()

   
    def getDistance(self, otherCluster):
        """
        Get the distance between the two clusters' centres
        @param otherCluster
        @return distance
        """
        d = self.ellipse.getCentre() - otherCluster.ellipse.getCentre()
        return numpy.sqrt(d.dot(d))


    def __mul__(self, otherCluster):
        """
        Overload of * operator, returns a cluster that is the intersection of 
        this and otherCluster
        @param otherCluster
        @return intersection of self with otherCluster
        """
        return Cluster(self.cells.intersection(otherCluster.cells))


    def __iadd__(self, otherCluster):
        """
        Overload of += operator, add othercluster cells to self
        @param otherCluster other cluster
        """
        self.cells = self.cells.union(otherCluster.cells)
        self.update()
        return self


    def writeFile(self, filename):
        """
        Write to netcdf file
        @param filename file name
        """
        import netCDF4
        iCoords, jCoords, ijValues = self.toArray()
        nc = netCDF4.Dataset(filename, 'w', format="NETCDF4")
        iDim = nc.createDimension('iDim', size=iCoords.shape[0])
        jDim = nc.createDimension('jDim', size=jCoords.shape[0])
        iVar = nc.createVariable('i', 'i4', dimensions=('iDim',))
        jVar = nc.createVariable('j', 'i4', dimensions=('jDim',))
        nbVar = nc.createVariable('nb', 'i4', dimensions=('iDim', 'jDim'))
        iVar[:] = iCoords
        jVar[:] = jCoords
        nbVar[:, :] = ijValues
        nc.close()

    def toArray(self, bounds=[]):
        """
        Convert this cluster to numpy (dense) array
        @bounds [[iMin, jMin], [iMax, jMax]]
        @return array of coordinates, array of zeros and ones
        """
        if len(self.cells) <= 0:
            # no op
            return numpy.array([]), numpy.array([]), numpy.array([])

        if not bounds:
            bounds = self.box
        iCoords = numpy.arange(bounds[0][0], bounds[1][0] + 1)
        jCoords = numpy.arange(bounds[0][1], bounds[1][1] + 1)
        ijValues = numpy.zeros((len(iCoords), len(jCoords)), numpy.int32)
        iMin, jMin = bounds[0]
        for c in self.cells:
            ijValues[c[0] - iMin, c[1] - jMin] = 1

        return iCoords, jCoords, ijValues

    def __repr__(self):
        """
        Print object
        """
        res = """
        Cluster: num cells = {} box = {} ellipse centre = {} a = {} b = {} transf = {}
        """.format(len(self.cells), self.box, \
            self.ellipse.centre, self.ellipse.a, self.ellipse.b, \
            self.ellipse.ij2AxesTransf)
        return res


#############################################################################################

def test1():
    cluster = Cluster({(-1, -2)})
    print('test1 {}'.format(cluster))
    #cluster.writeFile('test1.nc')

def testHorizLine():
    cluster = Cluster({(-1, -2), (0, -2), (1, -2), (2, -2)})
    print('testHorizLine {}'.format(cluster))

def testDipole():
    cluster = Cluster({(-2, 0), (2, 0)})
    print('testDipole {}'.format(cluster))

def testRectangle():
    cluster = Cluster({(i, 0) for i in range(3)}.union({(i, 1) for i in range(3)}))
    print('testRectangle {}'.format(cluster))

def testRectangleSlanted():
    cluster = Cluster({(i, 0) for i in range(4)}.union({(i - 1, 1) for i in range(4)}))
    print('testRectangleSlanted {}'.format(cluster))

def testRandom():
    import random
    random.seed(1234)
    cluster = Cluster({(random.randint(0, 200), random.randint(0, 100)) for i in range(500)})
    print('testRandom {}'.format(cluster))

def testPlusEqual():
    c0 = Cluster({(1,1), (2, 1)})
    c1 = Cluster({(1,1), (1, 2)})
    c0 += c1
    print 'testPlusEqual after merge: ', c0

def testTimes():
    c0 = Cluster({(1,1), (2, 1), (2, 2)})
    c1 = Cluster({(2, 2), (2, 3)})
    c2 = c0 * c1
    assert(c2.getNumberOfCells() == 1)
    print 'testTimes intersection: ', c2


if __name__ == '__main__':
    test1()
    testHorizLine()
    testDipole()
    testRectangle()
    testRectangleSlanted()
    testRandom()
    testPlusEqual()
    testTimes()

