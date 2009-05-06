/*
 * File:          
 * Date:          
 * Description:   
 * Author:        
 * Modifications: 
 */

#include <stdio.h>
#include <math.h>

#include <ode/ode.h>
#include <plugins/physics.h>

const float BALL_INIT_Z = 0.043;            // distance above ground for ball center

dBodyID ball;                               // physics ball object id
int steps = 0;                              // counter for steps
int kick = 0;                               // counter for kicks

#define NUM_KICK_ANGLES 5
float kick_angles[NUM_KICK_ANGLES];         // angles of kicks

const float steps_between_kicks = 100;      // steps between kicks
const float KICK_FORCE = 5.0;              // force to kick - 5.0 is already pretty high.

// webots_physics_init
// ===================
//
// Called once on initialization
//
void webots_physics_init(dWorldID world, dSpaceID space, dJointGroupID contactJointGroup) {
    int i;
    ball = dWebotsGetBodyFromDEF("BALL");
    if (ball == NULL) {
        printf("missing BALL in your wbt file - please define or remove this plugin.\n");
    }
    for (i = 0 ; i < NUM_KICK_ANGLES ; ++i) {
        kick_angles[i] = -M_PI/6 + (M_PI / 3) * i / NUM_KICK_ANGLES;
    }
  /*
   * Get ODE object from the .wbt model, e.g.
   *   dBodyID body1 = dWebotsGetBodyFromDEF("MY_ROBOT");
   *   dBodyID body2 = dWebotsGetBodyFromDEF("MY_SERVO");
   *   dGeomID geom2 = dWebotsGetGeomFromDEF("MY_SERVO");
   * If an object is not found in the .wbt world, the function returns NULL.
   * Your code should correcly handle the NULL cases because otherwise a segmentation fault will crash Webots.
   *
   * This function is also often used to add joints to the simulation, e.g.
   *   dJointID joint = dJointCreateBall(world, 0);
   *   dJointAttach(joint, body1, body2);
   *   ...
   */
}

void webots_physics_step() {
    float angle;
    if (ball == NULL) return; // safety - we report in webots_physics_init
    steps ++;
    if (steps % (int)steps_between_kicks == 50) {
        kick = (kick + 1) % NUM_KICK_ANGLES;
        angle = kick_angles[kick];
        // zero velocity and angular velocity from previous kick / hits
        dBodySetLinearVel(ball, 0.0, 0.0, 0.0);
        dBodySetAngularVel(ball, 0.0, 0.0, 0.0);
        dBodySetPosition(ball, 0.0, BALL_INIT_Z, 0.0);
        dBodyAddForce(ball, KICK_FORCE * cos(angle), 0.0/*up*/, KICK_FORCE * sin(angle));
    }
  /*
   * Do here what needs to be done at every time step, e.g. add forces to bodies
   *   dBodyAddForce(body1, f[0], f[1], f[2]);
   *   ...
   */
}

void webots_physics_draw() {
  /*
   * This function can optionally be used to add OpenGL graphics to the 3D view, e.g.
   *   glDisable(GL_LIGHTING);
   *   glLineWidth(2);
   *   glBegin(GL_LINES);
   *   glColor3f(1, 1, 0);
   *   glVertex3f(0, 0, 0);
   *   glVertex3f(0, 1, 0);
   *   glEnd();
   *   glLineWidth(1);
   *   glEnable(GL_LIGHTING);
   */
}

int webots_physics_collide(dGeomID g1, dGeomID g2) {
  /*
   * This function needs to be implemented if you want to overide Webots collision detection.
   * It must return 1 if the collision was handled and 0 otherwise. 
   * Note that contact joints should be added to the contactJointGroup, e.g.
   *   n = dCollide(g1, g2, MAX_CONTACTS, &contact[0].geom, sizeof(dContact));
   *   ...
   *   dJointCreateContact(world, contactJointGroup, &contact[i])
   *   dJointAttach(contactJoint, body1, body2);
   *   ...
   */
  return 0;
}

void webots_physics_cleanup() {
  /*
   * Here you need to free any memory you allocated in above, close files, etc.
   * You do not need to free any ODE object, they will be freed by Webots.
   */
}
