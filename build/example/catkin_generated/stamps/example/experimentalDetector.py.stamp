import cv2
import numpy as np
from sklearn.cluster import DBSCAN
from typing import Literal

class Detector(object):
    def __init__(self) -> None:
        srcPoints = np.array([[230, 220], 
                              [410, 220],
                              [640, 480], 
                              [0, 480]], dtype = np.float32)

        self.srcPoints = srcPoints

        ratio = 2 / 5
        minX = srcPoints[:, 0].min()
        maxX = srcPoints[:, 0].max()
        minY = srcPoints[:, 1].min()    
        maxY = srcPoints[:, 1].max()
        self.perspectiveHeight = int(maxY - minY)
        self.perspectiveWidth = int((maxX - minX) * ratio)

        dstPoints = np.array([[int(minX * ratio), 0], 
                              [int(maxX * ratio), 0], 
                              [int(maxX * ratio), self.perspectiveHeight], 
                              [int(minX * ratio), self.perspectiveHeight]], dtype=np.float32)
        self.dstPoints = dstPoints

        self.warpMat = cv2.getPerspectiveTransform(srcPoints, dstPoints)
        self.invWarpMat = cv2.getPerspectiveTransform(dstPoints, srcPoints)

        lowerOffset = 52
        upperOffset = 72
        maskHeight = 35
        self.maskVehicleFrame = np.array([[lowerOffset, self.perspectiveHeight],
                                          [self.perspectiveWidth - lowerOffset, self.perspectiveHeight],
                                          [self.perspectiveWidth - upperOffset, self.perspectiveHeight - maskHeight],
                                          [upperOffset, self.perspectiveHeight - maskHeight]])

    def detection(self, image):
        warpImage = cv2.warpPerspective(image, self.warpMat, (self.perspectiveWidth, self.perspectiveHeight), flags = cv2.INTER_LANCZOS4)

        edgeImage = self.edgeDetector(warpImage)
        points = np.array(np.where(edgeImage == 255)).T

        angle = np.pi / 2
        if len(points):
            clusters, clustersPos = self.groupPoints(points, minDist = 1, minPoints = 30) # Filter out disjoint lane
            try:
                clusters, clustersPos = self.groupPoints(np.vstack(clusters), minDist = 20)
            except:...
            

            angle = self.midlaneFinder(clusters, clustersPos, 20)
            self.directionDraw(warpImage, angle, 100, (self.perspectiveWidth // 2, self.perspectiveHeight))
            self.directionDraw(image, angle, 100, (image.shape[1] // 2, image.shape[0]))
                
        self.pointDrawer(self.srcPoints, image)
        cv2.imshow("Warp Image with line detector", warpImage)
        cv2.imshow("Original Image with line detector", image)
        return angle * 180 / np.pi

    @staticmethod
    def directionDraw(image, angle, length, position):
        dx = length * np.cos(angle) 
        dy = length * np.sin(angle)

        start = position
        end = (int(start[0] + dx), int(start[1] - dy))
        dim = len(image.shape)
        if dim == 3: cv2.line(image, start, end, (0, 255, 0), 2, cv2.LINE_AA)
        elif dim == 2: cv2.line(image, start, end, 255, 2, cv2.LINE_AA)

    @staticmethod
    def pointDrawer(points: np.ndarray, frame: np.ndarray) -> None:
        dim = len(frame.shape)
        for point in points:
            if dim == 3:
                cv2.circle(frame, (int(point[0]), int(point[1])), 3, (255, 0, 0), cv2.FILLED)
            elif dim == 2:
                cv2.circle(frame, (int(point[0]), int(point[1])), 3, 125, cv2.FILLED)

    def midlaneFinder(self, 
                      clusters: np.ndarray, 
                      clustersPosition: np.ndarray, 
                      partition: int,
                      mode: Literal['mean', 'closest', "furthest"] = 'mean') -> float:

        frameRight = np.zeros((self.perspectiveHeight, self.perspectiveWidth))
        frameLeft = frameRight.copy()
        frame = np.zeros((self.perspectiveHeight, self.perspectiveWidth))
        for points, pos in zip(clusters, clustersPosition):   
            if pos[0] > self.perspectiveWidth / 2:
                frameRight[points[:, 0], points[:, 1]] = 255
            else: frameLeft[points[:, 0], points[:, 1]] = 255
            frame[points[:, 0], points[:, 1]] = 255
            
        compressLeft = np.where(frameLeft.reshape(partition, -1, frameLeft.shape[1]).mean(1) > 0, 255, 0).astype(np.uint8)
        compressRight = np.where(frameRight.reshape(partition, -1, frameRight.shape[1]).mean(1) > 0, 255, 0).astype(np.uint8)

        deltaY = frameLeft.shape[0] / partition
        
        leftCompressionPoints = []
        rightCompressionPoints = []
        for idx, (rowLeft, rowRight) in enumerate(zip(compressLeft, compressRight)):
            leftPoints = np.array(np.where(rowLeft == 255)).T
            rightPoints = np.array(np.where(rowRight == 255)).T
            
            if len(leftPoints) == 0: leftCompressionPoints += [[np.inf, int(deltaY * (idx + .5))]]
            else:
                _, position = self.groupPoints(leftPoints, 1, 0)
                leftCompressionPoints += [[np.mean(position), int(deltaY * (idx + .5))]]
            if len(rightPoints) == 0: rightCompressionPoints += [[np.inf, int(deltaY * (idx + .5))]]
            else:
                _, position = self.groupPoints(rightPoints, 1, 0)
                rightCompressionPoints += [[np.mean(position), int(deltaY * (idx + .5))]]
                
        leftCompressionPoints = np.asarray(leftCompressionPoints)
        rightCompressionPoints = np.asarray(rightCompressionPoints)

        midPoints = (leftCompressionPoints + rightCompressionPoints) / 2
        midPoints = midPoints[np.isinf(midPoints.sum(1)) == False]
        infRightPos = np.isinf(rightCompressionPoints.sum(1))
        infLeftPos = np.isinf(leftCompressionPoints.sum(1))
        allInfRight = np.all(infRightPos)
        allInfLeft = np.all(infLeftPos)
        
        self.pointDrawer(clustersPosition, frame)
        
        angle = np.pi / 2
        if len(midPoints) != 0:
            if mode == 'closest':
                choosenPoint = midPoints[-1]
            elif mode == 'furthest':
                choosenPoint = midPoints[0]
            elif mode == "mean":
                choosenPoint = midPoints.mean(0)
            else: raise ValueError("Only furthest, mean, closest] mode are allowed") 

            diff = choosenPoint - np.array([self.perspectiveWidth // 2, self.perspectiveHeight])
            angle = np.arctan2(-diff[1], diff[0])
            self.pointDrawer([midPoints.mean(0)], frame)
        
        elif allInfLeft == True and allInfRight == False:    
            rightCompressionPoints = rightCompressionPoints[~infRightPos]
            if len(rightCompressionPoints) > 2:
                diff = rightCompressionPoints[:-1] - rightCompressionPoints[1:]
                angle = np.arctan2(-diff[:, 1], diff[:, 0]).mean()
            
        elif allInfLeft == False and allInfRight == True:
            leftCompressionPoints = leftCompressionPoints[~infLeftPos]
            if len(rightCompressionPoints) > 2:
                diff = leftCompressionPoints[:-1] - leftCompressionPoints[1:]
                angle = np.arctan2(-diff[:, 1], diff[:, 0]).mean()
        
        self.directionDraw(frame, angle, 100, np.array([self.perspectiveWidth // 2, self.perspectiveHeight]))
        cv2.imshow("", frame)
        return angle
        

    @staticmethod        
    def groupPoints(points: np.ndarray, minDist = 1, minPoints: int = 0, maxPoints: int = np.inf):
        dbscan = DBSCAN(eps = minDist, min_samples = 1).fit(points)
        labels = dbscan.labels_

        uniqueLabels = np.unique(labels)
        uniqueLabels = uniqueLabels[uniqueLabels != -1]
        clusters = []
        clustersPosition = []
        for label in uniqueLabels:
            mask = labels == label
            clusterPoints = points[mask]

            if minPoints <= len(clusterPoints) <= maxPoints:
                clusters.append(clusterPoints)
                clustersPosition.append(clusterPoints[:, ::-1].mean(axis = 0).astype(int))
                
        return clusters, clustersPosition

    def edgeDetector(self, image):
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurImage = cv2.GaussianBlur(grayImage, (5, 5), 3)

        _, binary = cv2.threshold(blurImage, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        binary = np.where(np.abs(cv2.Scharr(binary, cv2.CV_64F, 1, 0)) > 0, 255, 0).astype(np.uint8)

        mask = cv2.fillPoly(np.zeros_like(binary), [self.maskVehicleFrame], 255) # Mask out the hood of vehicle
        binary = np.where(mask == 255, 0, binary)
        return binary