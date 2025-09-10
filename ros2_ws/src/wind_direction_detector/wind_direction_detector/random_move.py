import rclpy
from rclpy.node import Node
from thymiodirect import Connection
from thymiodirect import Thymio
from std_msgs.msg import String
import time
import random
import datetime

class RandomRobotMove(Node):
    def __init__(self):
        super().__init__('random_move')
        print("Initializing Thymio Robot")
        port = Connection.serial_default_port()
        th = Thymio(serial_port=port,
                    on_connect=lambda node_id: print(f'Thymio {node_id} is connected'))
        # Connect to Robot
        th.connect()
        self.robot = th[th.first_node()]
        self.start_time_ = time.time()

        # Delay to allow robot initialization of all variables
        time.sleep(1)
        # b) print all variables
        print(th.variables(th.first_node()))
        print("Robot connected")
        self.stop_bool = False
        self.timer = self.create_timer(0.1, self.random_move)
        self.get_logger().info("Robot Control Node started.")
        self.consecutive_ir_hits = 0
        self.runtime = 600

    def random_move(self):
        if self.stop_bool:
            print("Stoping Robot")
            self.stop()
        self.move_forward()
        if self.stop_bool:
                print("Stopping Robot")
                self.stop()
        if bool(random.getrandbits(1)):
            self.rotate_right()
        else:
            self.rotate_left()
        if time.time() - self.start_time_ > self.runtime:
            self.stop_bool = True
            self.robot['leds.top'] = [0, 0, 32]
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            self.get_logger().info(f"robot move: excetion raised at {current_time}")
            raise Exception
    
    def on_arena_edge(self):
        if self.robot is not None:
            # print(f"Prox 0: {self.robot['prox.ground.delta'][0]}, Prox 1: {self.robot['prox.ground.delta'][1]}")
            if self.robot['prox.ground.delta'][0] > 800  or self.robot['prox.ground.delta'][1] > 800:
                return True
        return False
    
    def move_forward(self):
        if self.robot is not None:
            move_time = 20
            start_time= time.time()
            # counter = 25000
            while (time.time() - start_time) < move_time:
                if self.check_stop_all_motion():
                    print("stop all motion: move forward")
                    self.stop_bool = True
                    break
                self.robot['motor.left.target'] = 100
                self.robot['motor.right.target'] = 100
                if self.on_arena_edge():
                    print('on arena edge')
                    self.collision_avoidance()
                    continue
                if self.obstacle_ahead():
                    print('collision avoidance')
                    self.collision_avoidance()
                    continue
                # counter -= 1

            else:
                self.robot['motor.left.target'] = 0
                self.robot['motor.right.target'] = 0
    
    def rotate_right(self):
        if self.robot is not None:
            move_time = 3
            start_time= time.time()
            # counter = 3000
            while (time.time() - start_time) < move_time:
                if self.check_stop_all_motion():
                    print("stop all motion: rotate right")
                    self.stop_bool = True
                    break
                self.robot['motor.left.target'] = 200
                self.robot['motor.right.target'] = -200
                if self.on_arena_edge():
                    print('on arena edge')
                    self.collision_avoidance()
                    continue
                if self.obstacle_ahead():
                    print('collision avoidance')
                    self.collision_avoidance()
                    continue
                # counter -= 1
            else:
                self.robot['motor.left.target'] = 0
                self.robot['motor.right.target'] = 0
    
    def rotate_left(self):
        if self.robot is not None:
            move_time = 3
            start_time= time.time()
            # counter = 3000
            while (time.time() - start_time) < move_time:
                if self.check_stop_all_motion():
                    print("stop all motion: rotate left")
                    self.stop_bool = True
                    break
                self.robot['motor.left.target'] = -200
                self.robot['motor.right.target'] = 200
                if self.on_arena_edge():
                    print('on arena edge')
                    self.collision_avoidance()
                    continue
                if self.obstacle_ahead():
                    print('collision avoidance')
                    self.collision_avoidance()
                    continue
                # counter -= 1
            else:
                # print("robot stop")
                self.robot['motor.left.target'] = 0
                self.robot['motor.right.target'] = 0
    
    def move_back(self):
        if self.robot is not None:
            move_time = 6
            start_time= time.time()
            # counter = 20000
            while (time.time() - start_time) < move_time:
                if self.check_stop_all_motion():
                    print("stop all motion: move back")
                    self.stop_bool = True
                    break
                if self.robot['prox.horizontal'][5] > 600 or self.robot['prox.horizontal'][6] > 600:
                    self.stop()
                    continue
                self.robot['motor.left.target'] = -200
                self.robot['motor.right.target'] = -200
                # counter -= 1
            else:
                # print("robot stop")
                self.robot['motor.left.target'] = 0
                self.robot['motor.right.target'] = 0

    def check_stop_all_motion(self):
        if self.robot is not None:
            # print(f"Prox 0: {self.robot['prox.ground.delta'][0]}, Prox 1: {self.robot['prox.ground.delta'][1]}")
            if self.robot['prox.ground.delta'][0] < 10 or self.robot['prox.ground.delta'][1] < 10:
                print("Robot lifted")
                return True
        return False

    def stop(self):
        if self.robot is not None:
            self.robot['motor.left.target'] = 0
            self.robot['motor.right.target'] = 0
    
    def collision_avoidance(self):
        if self.robot is not None:
            print("Starting Collision avoidance")
            self.robot['leds.top'] = [32, 0, 0]
            counter = 3000
            print("Move back")
            while counter > 0:
                if self.robot['prox.horizontal'][5] > 600 or self.robot['prox.horizontal'][6] > 600:
                    self.stop()
                    continue
                self.robot['motor.left.target'] = -200
                self.robot['motor.right.target'] = -200
                counter -= 1
            counter = 3000
            print("Turn")
            while counter > 0:
                self.robot['motor.left.target'] = -350
                self.robot['motor.right.target'] = 350
                counter -= 1
            self.robot['leds.top'] = [0, 32, 0]

    def obstacle_ahead(self):
        if self.robot is not None:
            readings = self.robot['prox.horizontal'][:5]
            # print(readings)
            if any(r > 800 for r in readings):
                self.consecutive_ir_hits += 1
                # print(f"IR hits: {self.consecutive_ir_hits}")
                # Temporal filtering as IR strobes from Vicon system trigger collision avoidance
                if self.consecutive_ir_hits > 600:
                    # print("consecutive hits: ", self.consecutive_ir_hits)
                    print(f"Prox 0: {self.robot['prox.horizontal'][0]}, Prox 1: {self.robot['prox.horizontal'][1]},  Prox 2: {self.robot['prox.horizontal'][2]}, Prox 3: {self.robot['prox.horizontal'][3]}")
                    return True
            else:
                if self.consecutive_ir_hits > 0:
                    print("consecutive hits: ", self.consecutive_ir_hits)
                self.consecutive_ir_hits = 0
        return False
    
def main(args=None):
    rclpy.init(args=args)

    random_robot_move = RandomRobotMove()

    try:
        rclpy.spin(random_robot_move)
    except KeyboardInterrupt:
        random_robot_move.get_logger().info("Shutting down node...")
        random_robot_move.stop()
    except Exception:
        random_robot_move.get_logger().info("Exception, shutting down")
        random_robot_move.stop()
    finally:
        random_robot_move.stop()
        random_robot_move.destroy_node()
        rclpy.shutdown()


# if __name__ == '__main__':
#     main()


        
