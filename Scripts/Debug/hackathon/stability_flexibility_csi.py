import psyneulink as pnl
import psyneulink.core.llvm as pnlvm

import numpy as np
import random
import pytest
import pandas as pd

# Define function to generate a counterbalanced trial sequence with a specified switch trial frequency
def generateTrialSequence(N, Frequency):

    # Compute trial number
    nTotalTrials = N
    switchFrequency = Frequency

    nSwitchTrials = int(nTotalTrials * switchFrequency)
    nRepeatTrials = int(nTotalTrials - nSwitchTrials)

    # Determine task transitions
    transitions = [1] * nSwitchTrials + [0] * nRepeatTrials
    order = np.random.permutation(list(range(nTotalTrials)))
    transitions[:] = [transitions[i] for i in order]

    # Determine stimuli with 50% congruent trials
    stimuli = [[1, 1]] * int(nSwitchTrials/4) + [[1, -1]] * int(nSwitchTrials/4) + [[-1, -1]] * int(nSwitchTrials/4) + [[-1, 1]] * int(nSwitchTrials/4) + \
              [[1, 1]] * int(nRepeatTrials/4) + [[1, -1]] * int(nRepeatTrials/4) + [[-1, -1]] * int(nRepeatTrials/4) + [[-1, 1]] * int(nRepeatTrials/4)
    stimuli[:] = [stimuli[i] for i in order]

    # Determine cue-stimulus intervals
    CSI = [60] * int(nSwitchTrials / 8) + [80] * int(nSwitchTrials / 8) + \
          [60] * int(nSwitchTrials / 8) + [80] * int(nSwitchTrials / 8) + \
          [60] * int(nSwitchTrials / 8) + [80] * int(nSwitchTrials / 8) + \
          [60] * int(nSwitchTrials / 8) + [80] * int(nSwitchTrials / 8) + \
          [60] * int(nRepeatTrials / 8) + [80] * int(nRepeatTrials / 8) + \
          [60] * int(nRepeatTrials / 8) + [80] * int(nRepeatTrials / 8) + \
          [60] * int(nRepeatTrials / 8) + [80] * int(nRepeatTrials / 8) + \
          [60] * int(nRepeatTrials / 8) + [80] * int(nRepeatTrials / 8)
    CSI[:] = [CSI[i] for i in order]

    # Set the task order
    tasks = [[1, 0]] * (nTotalTrials + 1)
    for i in list(range(nTotalTrials)):
        if transitions[i] == 0:
            tasks[i + 1] = tasks[i]
        if transitions[i] == 1:
            if tasks[i] == [1, 0]:
                tasks[i + 1] = [0, 1]
            if tasks[i] == [0, 1]:
                tasks[i + 1] = [1, 0]
    tasks = tasks[1:]

    # # Check whether combinations of transitions, stimuli and CSIs are counterbalanced

    # # This is used later to check whether trials are counterbalanced
    # stimuli_type = [1] * int(nSwitchTrials/4) + [2] * int(nSwitchTrials/4) + [3] * int(nSwitchTrials/4) + [4] * int(nSwitchTrials/4) + \
    #           [1] * int(nRepeatTrials/4) + [2] * int(nRepeatTrials/4) + [3] * int(nRepeatTrials/4) + [4] * int(nRepeatTrials/4)
    # stimuli_type[:] = [stimuli_type[i] for i in order]

    # Trials = pd.DataFrame({'TrialType': transitions,
    #                        'Stimuli': stimuli_type,
    #                        'CSI': CSI
    #                        }, columns= ['TrialType', 'Stimuli', 'CSI'])
    #
    # trial_counts = Trials.pivot_table(index=['TrialType', 'Stimuli', 'CSI'], aggfunc='size')
    # print (trial_counts)

    return tasks, stimuli, CSI


# Stability-Flexibility Model

GAIN = 1
LEAK = 1
COMP = 7.5

AUTOMATICITY = .15 # Automaticity Weight

STARTING_POINT = 0.0  # Starting Point
THRESHOLD = 0.2  # Threshold
NOISE = 0.1  # Noise
SCALE = 1 # Scales DDM inputs so threshold can be set to 1

# Task Layer: [Color, Motion] {0, 1} Mutually Exclusive
# Origin Node
taskLayer = pnl.TransferMechanism(size=2,
                                  function=pnl.Linear(slope=1, intercept=0),
                                  output_ports=[pnl.RESULT],
                                  name='Task Input [I1, I2]')

# Stimulus Layer: [Color Stimulus, Motion Stimulus]
# Origin Node
stimulusInfo = pnl.TransferMechanism(size=2,
                                     function=pnl.Linear(slope=1, intercept=0),
                                     output_ports=[pnl.RESULT],
                                     name="Stimulus Input [S1, S2]")

# Cue-To-Stimulus Interval Layer
# Origin Node
# cueInterval = pnl.TransferMechanism(size=1,
#                                     function=pnl.Linear(slope=1, intercept=0),
#                                     output_ports=[pnl.RESULT],
#                                     name='Cue-Stimulus Interval')

# Control Module Layer: [Color Activation, Motion Activation]
controlModule = pnl.LCAMechanism(size=2,
                                 function=pnl.Logistic(gain=GAIN),
                                 leak=LEAK,
                                 competition=COMP,
                                 noise=0,
                                 termination_measure=pnl.TimeScale.TRIAL,
                                 termination_threshold=60,
                                 time_step_size=.1,
                                 name='Task Activations [Act1, Act2]')

# Control Mechanism Setting Cue-To-Stimulus Interval
# csiController = pnl.ControlMechanism(monitor_for_control=cueInterval,
#                                      control_signals=[(pnl.TERMINATION_THRESHOLD, controlModule)],
#                                      modulation=pnl.OVERRIDE)

# Hadamard product of controlModule and Stimulus Information
nonAutomaticComponent = pnl.TransferMechanism(size=2,
                                              function=pnl.Linear(slope=1, intercept=0),
                                              input_ports=pnl.InputPort(combine=pnl.PRODUCT),
                                              output_ports=[pnl.RESULT],
                                              name='Non-Automatic Component [S1*Act1, S2*Act2]')

# Multiply Stimulus Input by the automaticity weight
congruenceWeighting = pnl.TransferMechanism(size=2,
                                            function=pnl.Linear(slope=AUTOMATICITY, intercept=0),
                                            output_ports=[pnl.RESULT],
                                            name="Automaticity-weighted Stimulus Input [w*S1, w*S2]")

# Summation of nonAutomatic and Automatic Components
ddmCombination = pnl.TransferMechanism(size=1,
                                       function=pnl.Linear(slope=1, intercept=0),
                                       input_ports=pnl.InputPort(combine=pnl.SUM),
                                       output_ports=[pnl.RESULT],
                                       name="Drift = (w*S1 + w*S2) + (S1*Act1 + S2*Act2)")

# Scale DDM inputs to smaller value
ddmInputScale = pnl.TransferMechanism(size=1,
                                      function=pnl.Linear(slope=SCALE, intercept=0),
                                      output_ports=[pnl.RESULT],
                                      name='Scaled DDM Input')

# Decision Module
decisionMaker = pnl.DDM(function=pnl.DriftDiffusionIntegrator(starting_point=STARTING_POINT,
                                                              threshold=THRESHOLD,
                                                              noise=NOISE,
                                                              time_step_size=0.001),
                        reset_stateful_function_when=pnl.AtTrialStart(),
                        output_ports=[pnl.DECISION_VARIABLE, pnl.RESPONSE_TIME],
                        name='DDM')

taskLayer.set_log_conditions([pnl.RESULT])
stimulusInfo.set_log_conditions([pnl.RESULT])
#controlModule.set_log_conditions([pnl.RESULT, 'termination_threshold'])
controlModule.set_log_conditions([pnl.RESULT])
nonAutomaticComponent.set_log_conditions([pnl.RESULT])
congruenceWeighting.set_log_conditions([pnl.RESULT])
ddmCombination.set_log_conditions([pnl.RESULT])
ddmInputScale.set_log_conditions([pnl.RESULT])
decisionMaker.set_log_conditions([pnl.DECISION_VARIABLE, pnl.RESPONSE_TIME])

# Composition Creation
stabilityFlexibility = pnl.Composition(controller_mode=pnl.BEFORE)

# Node Creation
stabilityFlexibility.add_node(taskLayer)
stabilityFlexibility.add_node(stimulusInfo)
# stabilityFlexibility.add_node(cueInterval)
stabilityFlexibility.add_node(controlModule)
# stabilityFlexibility.add_node(csiController)
stabilityFlexibility.add_node(nonAutomaticComponent)
stabilityFlexibility.add_node(congruenceWeighting)
stabilityFlexibility.add_node(ddmCombination)
stabilityFlexibility.add_node(ddmInputScale)
stabilityFlexibility.add_node(decisionMaker)

# Projection Creation
stabilityFlexibility.add_projection(sender=taskLayer, receiver=controlModule)
stabilityFlexibility.add_projection(sender=controlModule, receiver=nonAutomaticComponent)
stabilityFlexibility.add_projection(sender=stimulusInfo, receiver=nonAutomaticComponent)
stabilityFlexibility.add_projection(sender=stimulusInfo, receiver=congruenceWeighting)
stabilityFlexibility.add_projection(sender=nonAutomaticComponent, receiver=ddmCombination)
stabilityFlexibility.add_projection(sender=congruenceWeighting, receiver=ddmCombination)
stabilityFlexibility.add_projection(sender=ddmCombination, receiver=ddmInputScale)
stabilityFlexibility.add_projection(sender=ddmInputScale, receiver=decisionMaker)



# Hot-fix currently necessary to allow control module and DDM to execute in parallel in compiled mode
# We need two gates in order to output both values (decision and response) from the ddm
decisionGate = pnl.ProcessingMechanism(size=1, name="DECISION_GATE")
stabilityFlexibility.add_node(decisionGate)

responseGate = pnl.ProcessingMechanism(size=1, name="RESPONSE_GATE")
stabilityFlexibility.add_node(responseGate)

stabilityFlexibility.add_projection(sender=decisionMaker.output_ports[0], receiver=decisionGate)
stabilityFlexibility.add_projection(sender=decisionMaker.output_ports[1], receiver=responseGate)

# Sets scheduler conditions, so that the gates are not executed (and hence the composition doesn't finish) until decisionMaker is finished
stabilityFlexibility.scheduler.add_condition(decisionGate, pnl.WhenFinished(decisionMaker))
stabilityFlexibility.scheduler.add_condition(responseGate, pnl.WhenFinished(decisionMaker))

# Origin Node Inputs
USE_GPU = True

taskTrain, stimulusTrain, cueTrain = generateTrialSequence(80, 0.5)

taskTrain = np.array([[1.0, 0.0], [0., 1.], [1., 0.]])
stimulusTrain = np.array([[-1.,  1.], [ 1.,  1.], [-1., -1.]])
cueTrain = np.array([60., 60., 80.])

# inputs = {taskLayer: taskTrain, stimulusInfo: stimulusTrain, cueInterval: cueTrain}
inputs = {taskLayer: taskTrain, stimulusInfo: stimulusTrain}


# stabilityFlexibility.show_graph()

if not USE_GPU:
    stabilityFlexibility.run(inputs, bin_execute=True)

    import time
    t0 = time.time()
    stabilityFlexibility.run(inputs, bin_execute="LLVMRun", )

    res = stabilityFlexibility.results
else:
    ocm_mode = "PTX"

    search_range = pnl.SampleSpec(start=1.0, stop=7.5, step=0.001)
    control_signal = pnl.ControlSignal(projections=[('competition', controlModule)],
                                       variable=1.0,
                                       allocation_samples=search_range,
                                       intensity_cost_function=pnl.Linear(slope=0.))

    objective_mech = pnl.ObjectiveMechanism(monitor=[responseGate])
    ocm = pnl.OptimizationControlMechanism(agent_rep=stabilityFlexibility,
                                           features=[stimulusInfo.input_port],
                                           objective_mechanism=objective_mech,
                                           function=pnl.GridSearch(),
                                           control_signals=[control_signal],
                                           comp_execution_mode=ocm_mode)
    # objective_mech.log.set_log_conditions(pnl.OUTCOME)

    stabilityFlexibility.add_controller(ocm)

    import time

    t0 = time.time()
    stabilityFlexibility.run(inputs, bin_execute='Python-PTX')
    print(f"Elapsed: {time.time() - t0}")

# taskLayer.log.print_entries()
# stimulusInfo.log.print_entries()
# controlModule.log.print_entries()
# nonAutomaticComponent.log.print_entries()
# congruenceWeighting.log.print_entries()
# ddmCombination.log.print_entries()
# ddmInputScale.log.print_entries()
# decisionMaker.log.print_entries()

# from matplotlib import pyplot as plt
# ddm_log = ddmInputScale.log.nparray_dictionary()
# lca_log = controlModule.log.nparray_dictionary()
# plt.plot(lca_log['Composition-0']['RESULT'][:,0], lw=2, color='orange')
# plt.plot(lca_log['Composition-0']['RESULT'][:,1], lw=2, color='red')
# plt.plot(ddm_log['Composition-0']['RESULT'], lw=2, color='green')
#
# for trial in stabilityFlexibility.results:
#     print(trial)
