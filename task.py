import numpy as np
from physics_sim import PhysicsSim


class Task():
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_velocities=None, 
        init_angle_velocities=None, runtime=5., target_pos=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 
        self.action_repeat = 3

        self.state_size = self.action_repeat * 6
        self.action_low = 0
        self.action_high = 500  # Original: 900 Reduced to smooth take-off
        self.action_size = 4
        self.done = False  # Default it to False

        # Goal
        self.target_pos = target_pos if target_pos is not None else np.array([0., 0., 10.]) 

    def get_reward(self):
        """Uses current pose of sim to return reward."""
        # reward = 1.-.3*(abs(self.sim.pose[:3] - self.target_pos)).sum()  # Original reward function

        # Measure distance in vertical direction from target (take-off)
        #x_dev = .1 * (self.sim.pose[0] - self.target_pos[0])**2
        #y_dev = .1 * (self.sim.pose[1] - self.target_pos[1])**2
        z_dev = (self.sim.pose[2] - self.target_pos[2])**2

        cont_reward = 1.5  # Give a continuing reward of 1.5

        vertical_vel = 0.5*(self.sim.v[2]) # Giving a reward/punish for vertical velocity

        # penalize crash as per review comment
        crash = 0
        if self.done and self.sim.time < self.sim.runtime:
            crash = -10

        deviation = z_dev  # + x_dev + y_dev

        reward = np.clip((cont_reward + vertical_vel + deviation + crash), -1, 1)  # Normalized the rewards between -1 and 1

        return reward

    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        for _ in range(self.action_repeat):
            self.done = self.sim.next_timestep(rotor_speeds)  # update the sim pose and velocities
            reward += self.get_reward() 
            pose_all.append(self.sim.pose)
        next_state = np.concatenate(pose_all)
        return next_state, reward, self.done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = np.concatenate([self.sim.pose] * self.action_repeat) 
        return state
