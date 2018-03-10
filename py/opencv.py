import cv2
import numpy as np
import itertools
import matplotlib.pyplot as mpl
def getContours(clusters):
        copy_clusters=clusters.copy()
        int_cnts=[]
        for label in np.unique(clusters):
                mask = np.zeros(clusters.shape, dtype="uint8")
                mask[clusters == label] = 255
                cnts, hierarchy = \
                        cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
                int_cnts.append(cnts)
        list_contours=list(itertools.chain.from_iterable(int_cnts))
        return copy_clusters, list_contours

def getEllipse(clusters, list_contours):
        for index,cnt in enumerate(list_contours):
                map_ellipse=np.ones(clusters.shape).astype(np.uint8)
                cimg = np.zeros_like(clusters)
                cv2.drawContours(cimg, list_contours, index, color=255, thickness=-1)
                ellipse=cv2.fitEllipse(cnt)
                cv2.ellipse(map_ellipse,ellipse,(255,0,0))
        return map_ellipse

# test
domain = (30, 40)
clusters = np.zeros(domain, np.int32)

# define the cells where something special happens
for j in range(10):
        for i in range(14):
                clusters[i + j, i] = 1

copy_clusters, list_contours = getContours(clusters)
map_ellipse = getEllipse(copy_clusters, list_contours)
