

def eval_this():
    # input_file_name = "2500-originalpos.txt"
    # output_file_name = "analytic-originalpos.txt"
    input_file_name = "2500-fireball.txt"
    output_file_name = "analytic-fireball.txt"

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

    '''
    Sample:
    Iteration 1281 Learning Q-Table
    best: move_right current state : (2, 2, -24) -100.0 [('nothing', -51.0), ('move_right', 151.46697134926632)]
    best: move_right current state : (2, 2, -24) -100.0 [('nothing', -51.0), ('move_right', 151.46697134926632)]
    best: move_right current state : (1, 0.75, -18) -26.5339353272 [('nothing', 0), ('move_left', 0), ('move_right', 353.74113040985725)]
    best: nothing current state : (0, -2, -8) 150 [('nothing', 208.2794183799413), ('move_left', 0), ('move_right', 0)]
    Reward: 278
    '''
    with open(output_file_name, "w") as output_file:
        for line in open(input_file_name).readlines():
            if not line.strip():
                continue

            if line.startswith("Loading"):
                if number_of_iteration != 0:
                    temp = last_dead
                    last_dead = number_of_iteration
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

                    current_hit_streak = 0
                    current_dodge_streak = 0

                    number_of_dead += 1

                number_of_dodge_per_episode = 0 # reset
                continue

            if line.startswith("Iteration"):
                number_of_iteration += 1
                continue

            if line.startswith("Reward"):
                current_reward = line.split(": ", 1)[1]
                current_reward = int(current_reward)
                # write to txt for diagram:
                output_file.writelines(str(number_of_iteration) + ' ' + str(current_reward) + '\n')

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
            survival_time = number_of_iteration - last_dead
            survival_rate = float(number_of_dodge_per_episode) / survival_time

            if survival_time > longest_episode:
                longest_episode = survival_time

            # printing stuff after each dead:
            print "#############################################################################"
            print "Remaining Episode : ", temp, "-", number_of_iteration, " : ", survival_time
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

if __name__ == "__main__":
    eval_this()

