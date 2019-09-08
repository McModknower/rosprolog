#!/usr/bin/env python

import roslib; roslib.load_manifest('rosprolog')

import rospy
from rosprolog import rosprolog

if __name__ == '__main__':
    rospy.init_node('test_rosprolog')
    prolog = rosprolog.Prolog()
    query = prolog.query("member(A, [1, 2, 3, 4]), B = ['x', A]")
    for solution in query.solutions():
        print 'Found solution. A = %s, B = %s' % (solution['A'], solution['B'])
    query.finish()
