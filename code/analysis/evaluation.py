

def eval_this():
    # input_file_name = "2500-originalpos.txt"
    # output_file_name = "analytic-originalpos.txt"
    input_file_name = "final/log_file_4ghast-0-01_eps_09alpha_04gamma.txt"
    output_file_name = "final/log_file_4ghast-0-01_eps_09alpha_04gamma-output.txt"

    number_of_dead = 0
    number_of_iteration = 0
    longest_episode = 0

    last_dead = 0
    cum_survival_rate = []

    current_reward = 0

    number_of_dodge_per_episode = 0

    current_dodge_streak = 0
    current_hit_streak = 0

    best_dodge_streak = 0
    best_dodge_streak_episode = 0
    best_hit_streak = 0
    best_hit_streak_episode = 0

    is_dodging_streak = True

    current_fireball_number = 0

    last_episode_list = []

    num_episode = 0
    current_length = 0.0

    '''
    Sample:
    Did: move_right Reward: -31.6999995 State: (0, 1.75, -0.25)
    rand: move_forward ,current state: (0, 1.75, -0.25) [('nothing', 0), ('move_left', 0), ('move_backward', 0), ('move_forward', 0), ('move_right', 0)]
    reward : -31.6999995
    Episode 0 length: 6.9880001545
    Last Reward :  -17.5
    Loading mission from ghast_survival_mission_extended.xml
    Iteration 1 Learning Q-Table
    No Fireball!------------------------------------------------------
    # of fireballs: 5
    Last Reward :  -17.5
    '''
    with open(output_file_name, "w") as output_file:
        for line in open(input_file_name).readlines():
            if not line.strip():
                continue

            if line.startswith("Loading"):
                if number_of_iteration != 0:
                    temp = last_dead
                    last_dead = current_fireball_number
                    survival_time = last_dead-temp
                    survival_rate = float(number_of_dodge_per_episode) / survival_time

                    if survival_time > longest_episode:
                        longest_episode = survival_time

                    # printing stuff after each dead:

                    print "#############################################################################"
                    print "Episode : ", temp, "-", last_dead, " : ", survival_time
                    print "Longest Episode : ", longest_episode
                    print "Survival Rate : ", number_of_dodge_per_episode, "/", survival_time, " : ", survival_rate
                    cum_survival_rate.append(survival_rate)

                    last_episode_list.append(last_dead)

                    current_hit_streak = 0
                    current_dodge_streak = 0

                    number_of_dead += 1

                number_of_dodge_per_episode = 0 # reset
                continue

            if line.startswith("# of fireballs"):
                current_fireball_number = line.split(": ", 1)[1]
                current_fireball_number = int(current_fireball_number)
                continue

            if line.startswith("Episode"):
                num_episode += 1
                current_length = line.split(": ", 1)[1]
                output_file.writelines(str(num_episode) + ' ' + str(current_length) + '\n')
                continue

            if line.startswith("Iteration"):
                number_of_iteration += 1
                continue

            if line.startswith("Last Reward"):
                current_reward = line.split(" :  ", 1)[1]
                current_reward = float(current_reward)
                # write to txt for diagram:
                # output_file.writelines(str(current_fireball_number) + ' ' + str(current_reward) + '\n')

                ############
                # Analysis:#
                ############

                # get hit:
                if current_reward < 0:
                    if is_dodging_streak:
                        is_dodging_streak = False
                        current_hit_streak = 0
                    current_hit_streak += 1
                    if current_hit_streak > best_hit_streak:
                        best_hit_streak = current_hit_streak
                        best_hit_streak_episode = number_of_iteration
                        print "new hit Record! ", best_hit_streak, " at episode :", best_hit_streak_episode

                # successful dodge:
                if current_reward >= 0:
                    number_of_dodge_per_episode += 1

                    if not is_dodging_streak:
                        is_dodging_streak = True
                        current_dodge_streak = 0
                    current_dodge_streak += 1
                    if current_dodge_streak > best_dodge_streak:
                        best_dodge_streak = current_dodge_streak
                        best_dodge_streak_episode = number_of_iteration
                        print "new dodge Record! ", best_dodge_streak, " at episode : ", best_dodge_streak_episode

                continue

        # printing report:
        if last_dead != number_of_iteration: # remaining episodes
            survival_time = current_fireball_number - last_dead
            survival_rate = float(number_of_dodge_per_episode) / survival_time

            if survival_time > longest_episode:
                longest_episode = survival_time

            # printing stuff after each dead:
            print "#############################################################################"
            print "Remaining Episode : ", last_dead, "-", number_of_iteration, " : ", survival_time
            print "Longest Episode   : ", longest_episode
            print "Survival Rate     : ", number_of_dodge_per_episode, "/", survival_time, " : ", survival_rate

        print ""
        print "#############################################################################"
        print "Longest Episodes               : ", longest_episode
        print "Total iteration                : ", number_of_iteration
        print "number of Dead during this run : ", number_of_dead
        print "average survival rate          : ", sum(cum_survival_rate) / number_of_dead
        print "Best dodge streak! ", best_dodge_streak, " at episode : ", best_dodge_streak_episode
        print "Best hit streak! ", best_hit_streak, " at episode :", best_hit_streak_episode
        print "Survival Rates                 : ",  ['%.5f' % elem for elem in cum_survival_rate]
        print "Last Dead List                 : ", last_episode_list
if __name__ == "__main__":
    eval_this()

