#!/usr/bin/python

####
# Import class Movement
from motion_movement import Movement

import linecache

####
# Call Movement

OUT_FILE='out_times.txt'

output_lines= len(linecache.getlines(OUT_FILE))
print "existing lines: %s" % output_lines
f = open(OUT_FILE,'a')

(x_init_pos, y_init_pos, yaw_init_pos,
 x_dest_pos, y_dest_pos, yaw_dest_pos)= [float(x.strip()) for x in 
    linecache.getlines('parameters.txt')]

print "About to run for the following parameters:"
print "X  : %s - %s" % (x_init_pos, x_dest_pos)
print "Y  : %s - %s" % (y_init_pos, y_dest_pos)
print "Yaw: %s - %s" % (yaw_init_pos, yaw_dest_pos)

counter= 1
x_pos= x_init_pos

def linspace(a, b, delta):
    return [a + i * delta for i in xrange(((b - a) / delta) + 1)]

xs = linspace(x_init_pos, x_dest_pos, 0.25)
ys = linspace(y_init_pos, y_dest_pos, 0.25)
yaws = linspace(yaw_init_pos, yaw_dest_pos, 45.0)
print "x:  ", xs
print "y:  ", ys
print "yaw:", yaws

for x_pos in xs:
    for y_pos in ys:
        for yaw in yaws:
            if not (y_pos == 0.0):
                if counter > output_lines:
                    print "running %s, %s, %s" % (x_pos, y_pos, yaw)
                    move= Movement(0,0,0,x_pos,y_pos,yaw)
                    results= move.run()
                    print >>f, counter, '- (', x_pos, ',', y_pos, ',', yaw, ') - [', results[0], ',' ,results[1], ',', results[2], ']'
                    print '(', x_pos, ',', y_pos, ',', yaw, ') - [', results[0], ',' ,results[1], ',', results[2], ']'
                    f.flush()
                print "skipping %s, %s, %s" % (x_pos, y_pos, yaw)
                counter += 1

