#!/usr/bin/env python3
"""
Test Mecanum Wheel Kinematics

Visualizes and tests the mecanum wheel kinematics calculations.
"""

import rospy
from geometry_msgs.msg import Twist
import time


def test_movement(pub, vx, vy, omega, duration, description):
    """Send a movement command for a duration"""
    print(f"\n{description}")
    print(f"  Command: vx={vx}, vy={vy}, omega={omega}")
    
    twist = Twist()
    twist.linear.x = vx
    twist.linear.y = vy
    twist.angular.z = omega
    
    start_time = time.time()
    rate = rospy.Rate(10)
    
    while time.time() - start_time < duration and not rospy.is_shutdown():
        pub.publish(twist)
        rate.sleep()
    
    # Stop
    twist.linear.x = 0
    twist.linear.y = 0
    twist.angular.z = 0
    pub.publish(twist)
    time.sleep(0.5)


def main():
    rospy.init_node('mecanum_tester', anonymous=True)
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    
    print("=" * 50)
    print("MECANUM WHEEL KINEMATICS TEST")
    print("=" * 50)
    print("\nWaiting for connection...")
    time.sleep(2)
    
    # Test sequences
    tests = [
        # (vx, vy, omega, duration, description)
        (0.5, 0.0, 0.0, 2.0, "Test 1: Forward"),
        (-0.5, 0.0, 0.0, 2.0, "Test 2: Backward"),
        (0.0, 0.5, 0.0, 2.0, "Test 3: Strafe Left"),
        (0.0, -0.5, 0.0, 2.0, "Test 4: Strafe Right"),
        (0.35, 0.35, 0.0, 2.0, "Test 5: Diagonal Left-Up"),
        (0.35, -0.35, 0.0, 2.0, "Test 6: Diagonal Right-Up"),
        (-0.35, 0.35, 0.0, 2.0, "Test 7: Diagonal Left-Down"),
        (-0.35, -0.35, 0.0, 2.0, "Test 8: Diagonal Right-Down"),
        (0.0, 0.0, 0.5, 2.0, "Test 9: Rotate CCW"),
        (0.0, 0.0, -0.5, 2.0, "Test 10: Rotate CW"),
    ]
    
    for vx, vy, omega, duration, desc in tests:
        test_movement(pub, vx, vy, omega, duration, desc)
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
