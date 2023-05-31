// PioneerNavX.java
/*
 * PioneerNavigation Class Definition
 * Date: 18th Oct 2022
 * Description: Simple Navigation Class support for 2022 Assignment
 * Author: Terry Payne 
 * Modified by: Noushin Islam (Student no. 201508438)
 */
 
import com.cyberbotics.webots.controller.Motor;
import com.cyberbotics.webots.controller.Supervisor;
import com.cyberbotics.webots.controller.Node;

public class PioneerNavX {

  public static enum MoveState {
    STOP,
    FORWARD,
    ARC,
    WANDER,
    ROTATE,
    FOLLOW_WALL};

  private Supervisor robot;       // reference to the robot
  private Node robot_node;        // reference to the robot node
  private Pose robot_pose;        // the robots believed pose, based on real location
  private Motor left_motor;
  private Motor right_motor;
  private MoveState state;
  private PioneerProxSensors prox_sensors;
  
  private double velocity;
  private double max_vel;

  private double prev_error;
  private double total_error;

  private final double WHEEL_RADIUS = 0.0957; // in meters - found using CONFIGURE 
  private final double AXEL_LENGTH = 0.323;   // in meters - found using CONFIGURE


  // ==================================================================================
  // Constructor
  // ==================================================================================
  public PioneerNavX(Supervisor robot) {
    this.robot = robot;                       // reference to the robot
    this.robot_node = this.robot.getSelf();   // reference to the robot node
    this.robot_pose = this.get_real_pose();   // the robots believed pose, based on real location
    this.state = MoveState.STOP;

    // enable motors
    this.left_motor = robot.getMotor("left wheel");
    this.right_motor = robot.getMotor("right wheel");
    this.left_motor.setPosition(Double.POSITIVE_INFINITY);
    this.right_motor.setPosition(Double.POSITIVE_INFINITY);

    // Initialise motor velocity
    this.left_motor.setVelocity(0.0);
    this.right_motor.setVelocity(0.0);   

    this.max_vel = this.left_motor.getMaxVelocity();

    this.prev_error = 0;
    this.total_error = 0;
  } 

  public Pose get_real_pose() {
    if (this.robot_node == null)
      return new Pose(0,0,0);
      
    double[] realPos = robot_node.getPosition();
    double[] rot = this.robot_node.getOrientation(); // 3x3 Rotation matrix as vector of length 9
    double theta1 = Math.atan2(-rot[0], rot[3]);
    double halfPi = Math.PI/2;
    double theta2 = theta1 + halfPi;
    if (theta1 > halfPi)
        theta2 = -(3*halfPi)+theta1;
    
    return new Pose(realPos[0], realPos[1], theta2);
  }

  // ==============================================================
  // Code in the section below has been written by me
  // ==============================================================

  // returns a velocity value that is 0.2 times the maximum velocity of the robot
  public double rob_vel(){
    double vel = 0.2 * this.max_vel;
    return vel;
  }
  
  // returns a velocity value that is 0.1 times the maximum velocity of the robot
  public double rot_vel(){
    double vel = 0.1 * this.max_vel;
    return vel;
  }

  // returns the distance between two poses using the Pythagorean theorem
  public double distance(Pose p, Pose wp) {
    double dist;
    dist = Math.sqrt(Math.pow(p.getX() - wp.getX(),2) + Math.pow(p.getY() - wp.getY(),2));
    return dist;
  }

  // calculates the time it will take for the robot to travel a given distance at a given velocity
  // sets the velocity of the left and right motors to the same velocity achieving forward movement and thus setting the robot's state to "FORWARD"
  // returns the time it will take to travel the distance in ms
  public double distTime(double target_dist, double velocity) {
    double target_time;
    target_time = target_dist/(velocity*this.WHEEL_RADIUS);
    
    this.left_motor.setVelocity(velocity);
    this.right_motor.setVelocity(velocity);
    this.state = MoveState.FORWARD;
    
    target_time = 1000 * target_time;         
    return target_time;
  }
  
  // returns the rotation angle needed for the robot to face a target pose from its current pose
  public double rotation(Pose p, Pose wp) {
    double rotAngle;
    rotAngle = p.get_dtheta(Math.atan2((wp.getY() - p.getY()), (wp.getX() - p.getX())));
    return rotAngle;
  }

  // calculates the time it will take for the robot to rotate a given distance at a given velocity 
  // sets the velocity of the left and right motors according to the direction of rotation achieving a rotating movement and thus setting the robot's state to "ROTATE"
  // returns the time it will take to rotate in ms
  public double rotTime(double rot_dist, double velocity) {
    double target_time;
    target_time = (0.5 * this.AXEL_LENGTH * Math.abs(rot_dist))/(velocity*this.WHEEL_RADIUS);
    if (rot_dist < 0){
      left_motor.setVelocity(velocity);
      right_motor.setVelocity(-velocity);
    } else if (rot_dist > 0){ 
      left_motor.setVelocity(-velocity);
      right_motor.setVelocity(velocity);
    }
    this.state = MoveState.ROTATE;
    
    target_time = 1000 * target_time;    
    return target_time;
  }
  // ==============================================================

  // The following code is based on the avoid obstacle code supplied by the Webots
  // platform for the ePuck and allows the robot to wander randomly around the arena
  public void wander(PioneerProxSensors prox_sensors, double robot_linearvelocity) {

    double leftVel, rightVel;
    double wheel_av = (robot_linearvelocity/this.WHEEL_RADIUS);
    double left_vel = wheel_av;
    double right_vel = wheel_av;

    // detect obstacles
    boolean right_obstacle =
        prox_sensors.get_value(4) < 0.30 ||
        prox_sensors.get_value(5) < 0.25 ||
        prox_sensors.get_value(6) < 0.20 ||
        prox_sensors.get_value(7) < 0.15;
    boolean left_obstacle =
        prox_sensors.get_value(0) < 0.15 ||
        prox_sensors.get_value(1) < 0.20 ||
        prox_sensors.get_value(2) < 0.25 ||
        prox_sensors.get_value(3) < 0.30;

    if (left_obstacle)
      right_vel = -left_vel;
    else if (right_obstacle)
      left_vel = -right_vel;
      
    this.left_motor.setVelocity(left_vel);
    this.right_motor.setVelocity(right_vel);
    this.state = MoveState.WANDER;
  }

  public int arc(double icr_angle, double icr_r, double icr_omega) {
    double target_time = icr_angle / icr_omega;

    // Calculate each wheel velocity around ICR
    double vl = icr_omega * (icr_r - (this.AXEL_LENGTH / 2));
    double vr = icr_omega * (icr_r + (this.AXEL_LENGTH / 2));
        
    double leftwheel_av = (vl/this.WHEEL_RADIUS);
    double rightwheel_av = (vr/this.WHEEL_RADIUS);
        
    this.left_motor.setVelocity(leftwheel_av);
    this.right_motor.setVelocity(rightwheel_av);
    this.state = MoveState.ARC;

    // return target_time as millisecs          
    return (int) (1000.0*target_time);
  }  

  public void stop() {
    this.left_motor.setVelocity(0.0);
    this.right_motor.setVelocity(0.0);
    this.state = MoveState.STOP;
  }
  
  public MoveState getState() {
    return this.state;
  }

  public void set_velocity(double base, double control) {
    // base gives the velocity of the wheels in m/s
    // control is an adjustment on the main velocity
    double base_av = (base/this.WHEEL_RADIUS);
    double lv = base_av;
    double rv = base_av;
    
    if (control != 0) {
      double control_av = (control/this.WHEEL_RADIUS);
      // Check if we exceed max velocity and compensate
      double correction = 1;
      lv = base_av - control_av;
      rv = base_av + control_av;

      if (lv > this.max_vel) {
        correction = this.max_vel / lv;
        lv = lv * correction;
        rv = rv * correction;
      }
           
      if (rv > this.max_vel) {
        correction = this.max_vel / rv;
        lv = lv * correction;
        rv = rv * correction;
      }

    }
    this.left_motor.setVelocity(lv);
    this.right_motor.setVelocity(rv);
  }
  // ===================================================================================
  // The code below is taken from Lab5 for a wall following solution, however, 
  // as I have decided to follow a different approach, I have commented out this section.
  // ===================================================================================
  
  /*  private double pid(double error) {
    double kp = 0.6; // proportional weight (may need tuning)
    double kd = 3.0; // differential weight (may need tuning)
    double ki = 0.0; // integral weight (may need tuning)
    
    double prop = error;
    double diff = error - this.prev_error;
    this.total_error += error;

    double control = (kp * prop) + (ki * this.total_error) + (kd * diff);
    this.prev_error = error;
    
    return control;
  } 

  public void follow_wall(double robot_linearvelocity, double set_point, boolean right) {
    int direction_coeff = 1;
    double error;
    double control;
    double wall_dist;
   
    if (right) direction_coeff = -1;  // invert the values for the control
    
    if (Math.min(this.prox_sensors.get_value(1),
          Math.min(this.prox_sensors.get_value(2),
            Math.min(this.prox_sensors.get_value(3),
              Math.min(this.prox_sensors.get_value(4),
                Math.min(this.prox_sensors.get_value(5),
                  this.prox_sensors.get_value(6)))))) < set_point) 
      this.set_velocity(robot_linearvelocity/3, -0.2*direction_coeff);

    else {
      if (!right) wall_dist = Math.min(this.prox_sensors.get_value(1),
                                       this.prox_sensors.get_value(0));
      else wall_dist = Math.min(this.prox_sensors.get_value(7),
                                this.prox_sensors.get_value(8));
      // Running aproximately parallel to the wall
      if (wall_dist < this.prox_sensors.get_maxRange()) {
        error = wall_dist - set_point;
        control = this.pid(error);
        // adjust for right wall
        this.set_velocity(robot_linearvelocity, control*direction_coeff);
      } else {
        // No wall, so turn
        this.set_velocity(robot_linearvelocity, 0.08*direction_coeff);
      }
    }
    this.state = MoveState.FOLLOW_WALL;
  } */

}    