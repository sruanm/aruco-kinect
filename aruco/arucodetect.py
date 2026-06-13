import rclpy
from rclpy.qos import QoSProfile
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class ArucoPoseEstimationNode(Node):
    def __init__(self):
        super().__init__('aruco_pose_estimation_node')
        self.bridge = CvBridge()
        self.image_sub = self.create_subscription(Image, 'rgb/image_raw', self.image_callback, 10)
        self.image_pub = self.create_publisher(Image, 'image_display', QoSProfile(depth=10))
        

        # Matriz de câmera (K)
        self.camera_matrix = np.array([[438.783367, 0.000000, 305.593336],
                                [0.000000, 437.302876, 243.738352],
                                [0.000000, 0.000000, 1.000000]])

        # Coeficientes de distorção (k1, k2, p1, p2, k3)
        self.distortion_coefficients = np.array([-0.361976, 0.110510, 0.001014, 0.000505, 0.000000])



    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        cv = self.pose_estimation(cv_image)
        self.image_pub.publish(self.bridge.cv2_to_imgmsg(cv, encoding="bgr8"))


        #self.get_logger().info(f'Aruco Info: {info}')

    def pose_estimation(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
        #parameters = cv2.aruco.DetectorParameters_create()
        parameters = cv2.aruco.DetectorParameters()
        
        corners, ids, rejected_img_points = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        if ids is not None:
            for i in range(len(ids)):
                rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners[i], 0.02, self.camera_matrix, self.distortion_coefficients)

                cv2.aruco.drawDetectedMarkers(frame, corners)
                ArucoCenter = []
                ArucoArea = []


                for (markerCorner,markerID) in zip(corners, ids):

                    corners = markerCorner.reshape((4, 2))
                    (topLeft, topRight, bottomRight, bottomLeft) = corners
                
                    topRight = (int(topRight[0]), int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                    topLeft = (int(topLeft[0]), int(topLeft[1]))

                    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    cY = int((topLeft[1] + bottomRight[1]) / 2.0)

                    w = ((bottomRight[0] - bottomLeft[0])**2 + (bottomRight[1] - bottomLeft[1])**2 )**(1/2)
                    h = ((bottomLeft[0] - topLeft[0])**2 + (bottomLeft[1] - topLeft[1])**2)**(1/2)
                    area = (w * h)

                    ArucoCenter.append([cX,cY])
                    ArucoArea.append(area)

                    if len(ArucoArea) != 0:
                        i = ArucoArea.index(max(ArucoArea))

                        info = [ArucoCenter[i], ArucoArea[i]]
                    else:

                        info = [ [0,0] , 0]

                #cv2.aruco.drawAxis(frame, self.camera_matrix, self.distortion_coefficients, rvec, tvec, 0.1)

                # Process tvec and rvec as needed
                self.get_logger().info(f'ArUco {ids[i]} - Translation: {tvec}, Rotation: {rvec}')

        return frame
def main(args=None):
    rclpy.init(args=args)
    node = ArucoPoseEstimationNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()