####
# Import class Movement
from motion_movement import Movement

import linecache

####
# Call Movement

OUT_FILE='out_times.txt'

output_lines= len(linecache.getlines('out_times.txt'))
f = open(OUT_FILE,'a+')

(x_init_pos, y_init_pos, yaw_init_pos,
 x_dest_pos, y_dest_pos, yaw_dest_pos)= [float(x.strip()) for x in 
    linecache.getlines('parameters.txt')]

counter= 1
x_pos= x_init_pos
while x_pos <= x_dest_pos:
    y_pos= y_init_pos
    while y_pos <= y_dest_pos:
        yaw= yaw_init_pos
        while yaw <= yaw_dest_pos:
            if not (y_pos == 0.0):
                if counter > output_lines:
                    move= Movement(0,0,0,x_pos,y_pos,yaw)
                    results= move.run()
                    print >>f, counter, '- (', x_pos, ',', y_pos, ',', yaw, ') - [', results[0], ',' ,results[1], ',', results[2], ']'
                    print '(', x_pos, ',', y_pos, ',', yaw, ') - [', results[0], ',' ,results[1], ',', results[2], ']'
                    f.flush()
                counter += 1
            yaw = yaw + 45
        y_pos = y_pos + 0.25
    x_pos = x_pos + 0.25

