##############################################################################################
# ******  Chain-of-faults(stuck-at-value) - LC-Assertive+ReactioTime **********
##############################################################################################
import os, sys
import traci
from datetime import datetime, date, time
import pandas as pd
import numpy
import random
# Setting environment variable SUMO_HOME
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
##############################################################################################
# ****************          Function for Golden Run and Output Log                ************
##############################################################################################
def SUFI_golden_run():
    # sumoCmd: select run mode (sumo or sumo-gui), choose sumocfg file to be run, and define output files
    sumoCmd = ["sumo", "-c", "SumoRun.config.sumocfg",
               "--tripinfo-output", "outputG/--Golden Run_tripinfo.xml",
               "--fcd-output", "outputG/--Golden run_fcd.xml",
               "--netstate-dump", "outputG/--Golden Run_Dump.xml",
               "--full-output", "outputG/--Golden Run_Full.xml",
               "--amitran-output", "outputG/--Golden Run_Trajectory.xml",
               "--lanechange-output", "outputG/--Golden Run_lanechange.xml",
               "--error-log", "outputG/--Golden Run_Error.xml"
               ]
    print("SUFI Experiment Run is in Progress ...\n\n")
    traci.start(sumoCmd)
    time_step = 0
    # Run the simulation until all vehicles have arrived
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if time_step == 100:  # 100 refers to time 10s in the simulation
            default_value_LC_assertive = traci.vehicle.getParameter('5', "laneChangeModel.lcAssertive")
        time_step += 1
    traci.close()
    return default_value_LC_assertive
##############################################################################################
# ****************       Function for Fault Injection Run and Output Log          ************
##############################################################################################
def SUFI_fault_injection_run(Initation_time, Target_vehicle, Target_parameter, Target_value, Target_vehicle_2, Target_parameter_2, Target_value_2):
    sumoCmd = ["sumo", "-c", "SumoRun.config.sumocfg",
             "--tripinfo-output","output/--Nr ={: }  t ={:.2f}  lc ={:.2f} tripinfo.xml".format(Ex_Nr, Injection_time, Injected_value),
             "--fcd-output", "output/--Nr ={: }  t ={:.2f}  lc ={:.2f} fcd.xml".format(Ex_Nr, Injection_time, Injected_value),
             "--netstate-dump", "output/--Nr ={: }  t ={:.2f}  lc ={:.2f} Dump.xml".format(Ex_Nr, Injection_time, Injected_value),
             "--full-output", "output/--Nr ={: }  t ={:.2f}  lc ={:.2f} Full.xml".format(Ex_Nr, Injection_time, Injected_value),
             "--amitran-output", "output/--Nr ={: }  t ={:.2f}  lc ={:.2f} Trajectory.xml".format(Ex_Nr, Injection_time, Injected_value),
             "--lanechange-output", "output/--Nr ={: }  t ={:.2f}  lc ={:.2f} lanechange.xml".format(Ex_Nr, Injection_time, Injected_value),
             "--error-log", "output/--Nr ={: }  t ={:.2f}  lc ={:.2f} Error.xml".format(Ex_Nr, Injection_time, Injected_value)
               ]
    print("SUFI Experiment Run is in Progress ...\n\n")
    traci.start(sumoCmd)
    time_step = 0
    # Run the simulation until all vehicles have arrived
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if time_step == Initation_time:
            traci.vehicle.setParameter(Target_vehicle, Target_parameter, Target_value)
            traci.vehicle.setParameter(Target_vehicle_2, Target_parameter_2, Target_value_2)
        time_step += 1
    traci.close()
##############################################################################################
# *************        Function for Fault Injection Campaign Data Log          ***************
##############################################################################################
def SUFI_compaign_data_log():
    # Record data in a csv file
    df = pd.DataFrame(
        {
            'Ex Number': LIST_Ex_Nr,
            'Injection_time': LIST_Injection_time,
            'Step_number': LIST_Step_number,
            'Injected_value': LIST_Injected_value,
            'Step_number_2': LIST_Step_number_2,
            'Injected_value_2': LIST_Injected_value_2,
            'Run_status': LIST_Run_status
        }
    )
    # Current Time
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H.%M.%S")
    df.to_csv("Fault Injection Campaign Log _{}.csv".format(current_time))
    print("Current Time =", now)
##############################################################################################
# *************                 Fault Injection Campaign Setup                 ***************
##############################################################################################
# Lists for log fault injection campaign data
LIST_Ex_Nr = []
LIST_Injection_time = []
LIST_Injected_value = []
LIST_Injected_value_2 = []
LIST_Step_number = []
LIST_Step_number_2 = []
LIST_Run_status = []
Ex_Nr = 0 # Number of experiment (Nr)
# run golden experiment:
Default_value = SUFI_golden_run()
# Value selection for fault injection and experiment run
for t in numpy.arange(11.0, 14.5, 0.5): # Loop for fault injection TIME interval
    Injection_time = round(t, 3)
    Step_number = 0 # Counts the step of the experiment
    for i in range(100): # Loop to define how many times to select a random value for each Initiation_time
        value = random.randrange(2, 1001) # Random value selection for target parameter
        Step_number_2 = 0  # Counts the step of the experiment for inner loop
        for Reaction_time in numpy.arange(0.2, 5.1, 0.2): # Define interval for the Reaction Time parameter
            Reaction_time = round(Reaction_time, 3)
            LIST_Injection_time.append(Injection_time)
            print("\n\n", "Iteration Number:  Injection_time _ step = ", Injection_time, "_", i)
            Step_number += 1
            Step_number_2 += 1
            LIST_Step_number.append(Step_number)
            LIST_Step_number_2.append(Step_number_2)
            Ex_Nr += 1
            LIST_Ex_Nr.append(Ex_Nr)
            print("Ex Number = ", Ex_Nr)
            LIST_Injected_value.append(value)
            LIST_Injected_value_2.append(Reaction_time)
            print("Selected faulty value = ", value, "\n =====================================")
            Injected_value = value
            Injected_value_2 = Reaction_time
            # run fault injection experiment:
            Initation_time = Injection_time * 10   # 10 is multiplied because of time_step (in sumoconfig we set it to 0.1)
            Target_vehicle = '5'
            Target_vehicle_2 = '5'
            Target_parameter = "laneChangeModel.lcAssertive"
            Target_parameter_2 = "device.driverstate.maximalReactionTime"
            Target_value = str(Injected_value)
            Target_value_2 = str(Injected_value_2)
            try:
                SUFI_fault_injection_run(Initation_time, Target_vehicle, Target_parameter, Target_value, Target_vehicle_2, Target_parameter_2, Target_value_2)
                LIST_Run_status.append('Successful')
            except Exception as err:
                print("Something went wrong")
                traci.close(False)
                LIST_Run_status.append('Failed')

# Log the fault injection campaign data
SUFI_compaign_data_log()




