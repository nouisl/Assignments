// File: MyAssignmentController.java
// Date: 22nd Dec 2022
// Description: Controller file
// Author: Terry Payne 
// Modified by: Noushin Islam (Student no. 201508438)
// Modifications: added waypoints and changed the control loop

// ==============================================================
// COMP329 2022 Programming Assignment
// ==============================================================
// 
// The aim of the assignment is to move the robot around the arena in such a way
// as to generate an occupancy grid map of the arena itself.  Full details can be
// found on CANVAS for COMP329
//
// Only add code to the controller file - do not modify the other java files in this project.
// You can add code (such as constants, instance variables, initialisation etc) anywhere in 
// the file, but the navigation itself that occurs in the main loop shoudl be done after checking
// the current pose, and having updated the two displays.
//
// Note that the size of the occup[ancy grid can be changed (see below) as well as the update
// frequency of the map, adn whether or not a map is generated.  Changing these values may be
// useful during the debugging phase, but ensure that the solution you submit generates an
// occupancy grid map of size 100x100 cells (with a recommended update frequency of 2).
//
// ==============================================================


import com.cyberbotics.webots.controller.Supervisor;
import com.cyberbotics.webots.controller.Camera;

// Here is the main class of your controller.
// This class defines how to initialize and how to run your controller.
public class MyAssignmentController {

  public static void main(String[] args) {

    Supervisor robot = new Supervisor();

    // get the time step of the current world.
    int timeStep = (int) Math.round(robot.getBasicTimeStep());
    double time_elapsed = 0;
    double target_time = 0;
    boolean moving = false; 
    double distance_time = 0;  
    double distance = 0;
    double rotation_time = 0;  
    double rotation = 0;
    
    Camera camera = robot.getCamera("camera");
    if (camera != null)
      camera.enable(timeStep);

    PioneerNavX nav = new PioneerNavX(robot);
    Pose my_pose = nav.get_real_pose();
    PioneerProxSensors prox_sensors = new PioneerProxSensors(robot, "sensor_display", my_pose);

    double robot_velocity = nav.rob_vel();
    double rotation_velocity = nav.rot_vel();

    // 2nd argument determines how many cells per meter of the arena.
    // Use 20 for testing navigation, but 50 for high-quality map (slow)
    OccupancyGrid ogrid = new OccupancyGrid(robot, 20, "occupancy_grid_display", my_pose, prox_sensors);

    // integer i to count the waypoints
    int i = 0;

    // all waypoints used for this project specific map
    Pose wp1 = new Pose (0.5, 2.2, 0);
    Pose wp2 = new Pose (0.5, -0.7, 0);
    Pose wp3 = new Pose (-0.3, -0.7, 0);
    Pose wp4 = new Pose (-0.3, 1.25, 0);
    Pose wp5 = new Pose (-2.1, 1.25, 0);
    Pose wp6 = new Pose (-2.1, 0.5, 0);
    Pose wp7 = new Pose (-1.1, 0.5, 0);
    Pose wp8 = new Pose (-1.1, -0.7, 0);
    Pose wp9 = new Pose (-2.0, -0.7, 0);
    Pose wp10 = new Pose (-2.0, -1.5, 0);
    Pose wp11 = new Pose (0.0, -2.2, 0);
    Pose wp12 = new Pose (2.0, -1.5, 0);
    Pose wp13 = new Pose (2.0, -0.7, 0);
    Pose wp14 = new Pose (0.5, -0.7, 0);
    Pose wp15 = new Pose (-2.0, -0.7, 0);
    Pose wp16 = new Pose (-2.0, -1.5, 0);
    Pose wp17 = new Pose (0.0, -2.2, 0);
    Pose wp18 = new Pose (2.0, -1.5, 0);
    Pose wp19 = new Pose (2.0, -0.7, 0);
    Pose wp20 = new Pose (2.0, 1.1, 0);
    Pose wp21 = new Pose (0.5, 1.1, 0);
    Pose wp22 = new Pose (0.5, -0.7, 0);
    Pose wp23 = new Pose (2.0, -0.7, 0);
    Pose wp24 = new Pose (2.0, 1.1, 0);
    Pose wp25 = new Pose (0.5, 1.1, 0);
    Pose wp26 = new Pose (0.5, 2.0, 0);
    Pose wp27 = new Pose (2.2, 2.0, 0); 

    // path consisting of all manually set waypoints
    Pose[] path = {wp1, wp2, wp3, wp4, wp5, wp6, wp7, wp8, wp9, wp10, wp11, wp12, wp13, wp14, wp15, wp16, wp17, wp18, wp19, wp20, wp21, wp22, wp23, wp24, wp25, wp26, wp27};

    // define schedule
    PioneerNavX.MoveState state = PioneerNavX.MoveState.FORWARD; // current state

    while (robot.step(timeStep) != -1 && i < 27) {
      my_pose = nav.get_real_pose();
      prox_sensors.set_pose(my_pose);
      prox_sensors.paint();  // Render sensor Display
      
      ogrid.set_pose(my_pose);
      ogrid.map();
      ogrid.paint();

      switch (state) {
        // if the state variable is "FORWARD", the code checks if the robot is currently moving
        case FORWARD:
          if (moving == true) {
            // if it is moving, it checks if the elapsed time is greater than the time it should take for the robot to reach its next waypoint
            if (time_elapsed > distance_time) {
              // if the elapsed time is greater than the time needed to reach the waypoint, the robot is stopped, moving set to false and state set to "ROTATE"
              nav.stop();
              moving = false;
              state = PioneerNavX.MoveState.ROTATE;
              time_elapsed = 0;
            } else {
              // if the elapsed time is not greater than the time needed to reach the waypoint, the code increments time_elapsed by timeStep
              time_elapsed += timeStep;
            }
          } else {
            // if the robot is not currently moving, it calculates the distance and the time needed to the next waypoint 
            // the nav.distTime() method initiates forward movement and the variable moving is set to true
            distance = nav.distance(my_pose, path[i]);
            distance_time = nav.distTime(distance, robot_velocity);
            moving = true;             
          }
          break;
        
        // if the state variable is "ROTATE", the code checks if the robot is currently moving
        case ROTATE:
          if (moving == true) {
            // if it is moving, it checks if the elapsed time is greater than the time it should take for the robot to rotate to its next waypoint
            if (time_elapsed > rotation_time) {
              // if the elapsed time is greater than the time needed to rotate to its next waypoint, the robot is stopped, moving is set to false and state set to "FORWARD"
              nav.stop();
              moving = false;
              state = PioneerNavX.MoveState.FORWARD;
              time_elapsed = 0;
            } else {     
              // if the elapsed time is not greater than the time needed to rotate to its next waypoint, the code increments time_elapsed by timeStep
              time_elapsed += timeStep;   
            }
          } else {
            // if the robot is not currently moving, it checks if the current waypoint is the last one in the path
            if (i<26){
              // if the robot has not reached the last waypoint in the path, it increments the waypoint index, i, by 1 
              // calculates the rotation angle and time needed to reach the next waypoint
              // the nav.rotTime() method initiates rotation movement and the variable moving is set to true
              i++;
              rotation = nav.rotation(my_pose, path[i]);
              rotation_time = nav.rotTime(rotation, rotation_velocity);
              moving = true;
            } else {
              // if the robot has reached the last waypoint in the path then the robot stops and the controller is exited successfully
              i++;
              System.out.println("the end");
              nav.stop();
            }
          } 
          break;      
         }
    };
    // Enter here exit cleanup code.
  }
}
