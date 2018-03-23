import numpy
import matplotlib
import time
#from time_connected_clusters import TimeConnectedClusters, extractClusters
from time_connected_clusters import TimeConnectedClusters
#from extractClusters import ExtractClusters
from cluster import Cluster
from scipy import ndimage
from skimage.morphology import watershed
import cv2


"""
Test TimeConnectedClusters
"""

def testRectangle():
    rectangle = {(2, 3), (3, 3), (4, 3), (2, 4), (3, 4), (4, 4)}
    clusters = [Cluster(rectangle)]

    tcc = TimeConnectedClusters()
    tcc.addTime(clusters)
    print tcc
    tcc.addTime(clusters)
    print tcc
    tcc.writeFile('rectangle.nc', i_minmax=(0, 10), j_minmax=(0, 8))


def testIndRectangles():
    rect1 = {(2, 3), (3, 3), (4, 3), (2, 4), (3, 4), (4, 4)}
    rect2 = {(6, 3), (7, 3), (8, 3), (6, 4), (7, 4), (8, 4)}
    rect3 = {(3, 4), (4, 4), (5, 4), (3, 5), (4, 5), (5, 5)}

    tcc = TimeConnectedClusters()
    tcc.addTime([Cluster(rect1), Cluster(rect2)])
    print tcc
    tcc.addTime([Cluster(rect3)])
    print tcc
    tcc.writeFile('independant_rectangles.nc', i_minmax=(0, 10), j_minmax=(0, 8))


def testTwoMergingRectangles():
    print '='*70
    print 'testTwoMergingRectangles'
    print '-'*70
    rect0 = {(2, 3), (3, 3), (4, 3), (2, 4), (3, 4), (4, 4),(2, 5), (3, 5), (4, 5)}
    rect1 = {(6, 3), (7, 3), (8, 3), (6, 4), (7, 4), (8, 4),(6, 5), (6, 5), (6, 5)}
    rect2 = {(3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (3, 4), (4, 4), (5, 4), (6, 4), 
             (7, 4), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5)}
    c0, c1, c2 = Cluster(rect0), Cluster(rect1), Cluster(rect2)
    if c0.isCentreInsideOf(c2):
        print 'c0 is inside c2'
    if c1.isCentreInsideOf(c2):
        print 'c1 is inside c2'
    if c1.isCentreInsideOf(c0):
        print 'c1 is inside c0'
    if c2.isCentreInsideOf(c0):
        print 'c2 is inside c0'
    # Should have only one track because cluster 0 and 1 at t=0 merge at t=1. Should 
    # pass into fuse    # Prob: cluster 0 at=0 does not become cluster 1
    tcc = TimeConnectedClusters()
    tcc.addTime([c0, c1])
    print tcc
    tcc.addTime([c2])
    print tcc
    tcc.writeFile('two_merging_rectangles.nc', i_minmax=(0, 10), j_minmax=(0, 8))
    assert(tcc.getNumberOfTracks() == 1)


def testOnlyFuse():
    print '='*70
    print 'testOnlyFuse'
    print '-'*70
    rect0 = {(2, 3), (3, 3), (2, 4), (3, 4), (2, 5), (3, 5)}
    rect1 = {(7, 3), (8, 3), (7, 4), (8, 4), (7, 5), (8, 5)}
    rect2 = {(2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), 
             (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), 
             (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5)}
    c0 = Cluster(rect0)
    c1 = Cluster(rect1)
    c2 = Cluster(rect2)
    # Simplest fuse test: no forward tracking possible (center of rect3 can't 
    # be inside ellipse of cluster 1 or 2, but centers of clusters 1 and 2 should be 
    # inside ellipse of cluster 3
    # Result expected: all clusters should get same id: 1 ==> connectivity [{0: [0, 1], 1: [2]}]
    # Problem : cluster 2 keeps its id
    tcc = TimeConnectedClusters()
    print 'time step {}: adding cluster with centre {} and {}'.format(tcc.getNumberOfTimeSteps(),
                                                                       c0.getCentre(), 
                                                                       c1.getCentre())
    tcc.addTime([c1, c2])
    print tcc

    if c2.isCentreInsideOf(c0):
        print 'c2 is inside c0'
    if c2.isCentreInsideOf(c1):
        print 'c2 is inside c1'
    if c0.isCentreInsideOf(c2):
        print 'c0 is inside c2'
    if c1.isCentreInsideOf(c2):
        print 'c1 is inside c2'
    print 'time step {}: adding cluster with centre {}'.format(tcc.getNumberOfTimeSteps(),
                                                                       c2.getCentre())
    tcc.addTime([c2])
    print tcc
    tcc.writeFile('only_fuse.nc', i_minmax=(0, 10), j_minmax=(0, 8))
    assert(tcc.getNumberOfTracks() == 1)
    assert(tcc.getNumberOfTimeSteps() == 2)


def testOnlySplit():
    rect1 = {(2, 3), (3, 3), (2, 4), (3, 4), (2, 5), (3, 5)}
    rect2 = {(7, 3), (8, 3), (7, 4), (8, 4), (7, 5), (8, 5)}
    rect3 = {(2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5)}
    # Simplest split test : no backward tracking possible (center of rect3 can't be inside ellipse of cluster 1 or 2, but centers of clusters 1 and 2 should be inside ellipse of cluster 3
    # Result expected: all clusters should get same id: 1 ==> connectivity [{0: [0], 1: [1, 2]}]
    # Problem : cluster 2 keeps its id
    tcc = TimeConnectedClusters()
    tcc.addTime([Cluster(rect3)])
    print tcc
    tcc.addTime([Cluster(rect1), Cluster(rect2)])
    print tcc
    tcc.writeFile('only_split.nc', i_minmax=(0, 10), j_minmax=(0, 8))


def testSplittingInTwo():
    rect1 = {(3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9)}
    circ2 = {(3, 8), (3, 9), (4, 7), (4, 8), (4, 10), (5, 7), (5, 8), (5, 9), (5, 10), (6, 8), (6, 9)}
    circ3 = {(3, 3), (4, 2), (4, 3), (4, 4), (5, 3)}
    tcc = TimeConnectedClusters()
    tcc.addTime([Cluster(rect1)])
    print tcc
    tcc.addTime([Cluster(circ2), Cluster(circ3)])
    print tcc
    tcc.writeFile('splitting_in_two.nc', i_minmax=(0, 10), j_minmax=(0, 8))
    # expected result: 
    # Because centre of circ2 and circ3 are inside ellipse of rect1, the result
    # should be [{0: [rect1], 1: [circ2, circ3]} 
    # Currently fusing, test if rect1's centre is inside ellipse of circ2 or circ3 (should not be). 
    # But even if it is, fuse should be active because it will try to fuse with itself


def extractClusters(data, thresh_min, thresh_max):
    """ 
    Extract clusters from an image data
    @param data
    @param thresh_min
    @param thresh_max
    @return list of clusters
    """
    # remove data below minimum threshold
    ma_data = numpy.ma.masked_where(data <= thresh_min, data)
    # building black and white image with lower threshold to create borders for watershed
    tmp_data = ma_data.filled(fill_value=0)
    tmp_data[numpy.where(tmp_data !=0)] = 255 
    bw_data = tmp_data.astype(numpy.uint8)
    border = cv2.dilate(bw_data, None, iterations=5)
    border -= cv2.erode(border, None)

    # remove data below minimum threshold
    ma_conv = numpy.ma.masked_where(data <= thresh_max, data)
    # building black and white image with high threshold to serve as markers for watershed..
    tmp_conv = ma_conv.filled(fill_value=0)
    tmp_conv[numpy.where(tmp_conv !=0)] = 255 
    bw_conv = tmp_conv.astype(numpy.uint8)
    markers = ndimage.label(bw_conv, structure=numpy.ones((3, 3)))[0]
    # add border on image with high threshold to tell the watershed where it should fill in
    markers[border == 255] = 255 
    # labels each feature
    labels = watershed(-data, markers, mask=bw_data)

    # load into clusters
    res = []
    for idVal in range(1, labels.max()+1):
        iVals, jVals = numpy.where(labels == idVal)
        numVals = len(iVals)
        if numVals > 0:
            cells = [(iVals[i], jVals[i]) for i in range(len(iVals))]
            # store this cluster as a list with one element (so far). Each.
            # element will have its own ID
            res.append(Cluster(cells))
    return res


def testDigits():
    """
    Checking that we can create a time connected cluster from image
    """
    lats = numpy.arange(0, 20)
    lons = numpy.arange(0, 50)
    data = numpy.zeros((len(lats), len(lons)), numpy.float64)
    # create a cluster
    data[10:10+5, 10] = 5
    data[2:4, 5:5+4] = 3
    data[4:6, 5:5+4] = 1
    data[6:8, 5:5+4] = 3
    data[3, 12] = 5
    data[5, 15] = 2
#    print data
    # Version with Class
#    clusters = extractClusters.extractPoints(numpy.flipud(data), thresh_min=0., thresh_max=2.5)
    # Version inside testTimeConnecteClusters
    clusters = extractClusters(numpy.flipud(data), thresh_min=0., thresh_max=2.5)
    print clusters

    tcc = TimeConnectedClusters()

    # add a couple of times
    tcc.addTime(clusters)
    #tcc.addTime(clusters)

    print tcc

    # write to file
    tcc.writeFile('digits.nc', i_minmax=(0, len(lats)), j_minmax=(0, len(lons)))


if __name__ == '__main__':
    #testRectangle()
    #testIndRectangles()
    #testTwoMergingRectangles()
    #testOnlyFuse()
    #testOnlySplit()
    #testSplittingInTwo()
    testDigits()