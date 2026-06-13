from setuptools import setup

package_name = 'aruco'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rubi',
    maintainer_email='ruan.macs@gmail.com',
    description='ROS 2 package for ArUco marker detection and pose estimation using the Azure Kinect depth camera.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "aruco = aruco.arucodetect:main"
        ],
    },
)
