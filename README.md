# Dynamic Foraging Task
- [Dynamic Foraging Task](#dynamic-foraging-task)
- [Prerequisites](#prerequisites)
  - [Software](#software)
  - [Hardware](#hardware)
- [Deployment](#deployment)
  - [Bonsai](#bonsai)
  - [Python GUI](#python-gui)
- [Information Flow](#information-flow)
- [Usage of Python GUI](#usage-of-python-gui)
  - [Menu](#menu)
  - [Toolbars](#toolbars)
  - [Training Parameters](#training-parameters)
  - [Water Calibration](#water-calibration)
  - [Laser Calibration](#laser-calibration)
  - [Optogenetics](#optogenetics)
  - [Camera](#camera)
  - [Visualization](#Visualization)
  - [Motor Stage](#motor-stage)
- [Output JSON Format](#output-json-format)
- [Development](#development)

## Prerequisites
### Software
- Windows 10 or 11
- [ftdi driver](https://ftdichip.com/drivers/) (serial port drivers for HARP devices)
- [NI-DAQmax 19.0](https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html#484356) (for running optogenetics through NI-daq)
- [Spinnaker SDK version 1.29.0.5](https://www.flir.com/products/spinnaker-sdk/) (driver for FLIR camera)
- Python package:
  - numpy
  - scipy
  - matplotlib
  - PyQt5
  - pandas
  - [pyosc3](https://github.com/glopesdev/pyosc3.git@master)

### Hardware
- Harp behavior board
- Harp sound card
- Sound amplifier
- Harp synchronization board
  
## Deployment

### Bonsai

- Run **setup.cmd** in the **dynamic-foraging-task\bonsai** folder to install the bonsai and related packages (you only need to do it once).
- Run the foraging bonsai workflow in the folder **dynamic-foraging-task\src\workflows** to start Bonsai.

### Python GUI

- Run the **Foraging.py** in the folder **dynamic-foraging-task\src\foraging_gui** to start the GUI

## Information Flow

![image](https://github.com/AllenNeuralDynamics/dynamic-foraging-task/assets/109394934/8b669d0d-c6aa-4abc-a41a-309ce6200fc0)


## Usage of Python GUI

### Menu

#### File
- **New**: Clear the training parameters 
- **Open**: Open an existing session and visualization
- **Save**: Save the current session into json/mat format
- **Exit**: Close the current GUI
- **Clear**: Clear the training parameters
- **Force Save**:S ave the current session whether completed or not
#### Tools
- **Water calibration**: Open the water calibration dialogue
- **Laser calibration**: Open the laser calibration dialogue
- **Snipping**: Open the snipping tools
#### Visualization
- **Lick distribution**: Open the lick analysis dialogue
#### Control
- **Optogenetics**: Open the optogenetics dialogue
- **Camera**: Open the camera dialogue
- **Motor stage**: Open the Newscale stage dialogue to control the movement of lick sprouts
- **Manipulator**: Open the Newscale stage to control the movement of probe
- **Connect bonsai**: Connect the bonsai through OSC message
- **Start**: Start the GUI
- **New session**: Restart a new session
- **Restart logging**:
  - **Temporary logging**: Logging to a temporary folder (determined by the **temporary_video_folder** in the **ForagingSettings.json** )
  - **Formal logging**: Logging to a standard folder structure (determined by the **log_folder** in the **ForagingSettings.json** )
  - **Openg logging folder**: Open the current logging folder
- **Open behavior folder**: Open the folder to save the current behavior Json file
#### Settings
- **Open setting folder**: Open the default settings folder
#### Help

### Toolbars (copy of some useful functions from the Menu)
- **New**
- **Open**
- **Save**
- **Snipping**
- **Camera**
- **Motor stage**
- **Manipulator**
- **Water calibration**
- **Optogenetics**
- **Laser calibration**

### Training Parameters
#### Animal/task/tower information
- **Name**: The animal name used by individual users.
- **ID**: The animal ID.
- **Experimenter**: The experimenter who run this session.
- **Task**: There are currently five tasks supported (**Coupled Baiting**;**Uncoupled Baiting**;**Coupled Without Baiting**;**Uncoupled Without Baiting**;**RewardN**).
- **Tower**: The current tower (can be set by **current_box** in **ForagingSettings.json**).
#### Trial related parameters
- **training stage**: Select the training stage parameters. These parameters can be saved in **TrainingStagePar.json** through "**Save training**" button. They are task dependent. 
- **randomness**: There are **exponential** and **even distribution** available. This random generator will be applied to generate **Block length**/**ITI**/**Delay period**.
- **L(s)**: The left valve open time. The **L(s)** and **L(ul)** are dependent on each other, and the relationship is determined by the water calibration.
- **L(ul)**: The estimated water volume given by the left valve under the **L(s)**.
- **R(s)**: Similar as the **L(s)**, but for right valve.
- **R(ul)**: Similar as the **L(ul)**, but for left valve.
- **Give left**: Manually give water to the left valve
- **Give right**: Manually give water to the right valve
- **sum (base reward probability)**: The total reward probability.
- **family**: Currently, we use four reward families [[[8,1],[6, 1],[3, 1],[1, 1]],[[8, 1], [1, 1]],[[1,0],[.9,.1],[.8,.2],[.7,.3],[.6,.4],[.5,.5]],[[6, 1],[3, 1],[1, 1]]].
- **#of pairs**: Number of reward pairs you want to show under that family.
- **uncoupled reward**: Reward probabilities used by **Uncoupled Without Baiting** and **Uncoupled Baiting**. The reward probability of 0.1 cannot occur on both sides at the same time. 
### Water Calibration

(Your content here)

### Laser Calibration

(Your content here)

### Optogenetics

(Your content here)

### Camera

(Your content here)

### Motor Stage

(Your content here)

## Output NWB Format
### Task structure
- **animal_response**:'The response of the animal. 0, left choice; 1, right choice; 2, no response'
- **rewarded_historyL**:'The reward history of left lick port'
- **rewarded_historyR**: 'The reward history of right lick port'
- **delay_start_time**: 'The delay start time'
- **goCue_start_time**: 'The go cue start time'
- **reward_outcome_time**: 'The reward outcome time (reward/no reward/no response)'
### Training paramters 
#### Behavior structure
- **bait_left**:'Whether the current left lickport has a bait or not'
- **bait_right**:'Whether the current right lickport has a bait or not'
- **base_reward_probability_sum**:'The summation of left and right reward probability'
- **reward_probabilityL**:'The reward probability of left lick port'
- **reward_probabilityR**:'The reward probability of right lick port'
- **left_valve_open_time**:'The left valve open time'
- **right_valve_open_time**:'The right valve open time'
#### Block
- **block_beta**:'The beta of exponential distribution to generate the block length'
- **block_min**:'The minimum length allowed for each block'
- **block_max**:'The maxmum length allowed for each block'
- **min_reward_each_block**:'The minimum reward allowed for each block'
#### Delay duration
- **delay_beta**:'The beta of exponential distribution to generate the delay duration(s)'
- **delay_min**:'The minimum duration(s) allowed for each delay'
- **delay_max**:'The maxmum duration(s) allowed for each delay'
- **delay_duration**:'The expected time duration between delay start and go cue start'
#### ITI duration
- **ITI_beta**:'The beta of exponential distribution to generate the ITI duration(s)'
- **ITI_min**:'The minimum duration(s) allowed for each ITI'
- **ITI_max**:'The maxmum duration(s) allowed for each ITI'
- **ITI_duration**:'The expected time duration between trial start and ITI start'
#### Response duration
- **response_duration**:'The maximum time that the animal must make a choce in order to get a reward'
#### Reward consumption duration
- **reward_consumption_duration**:'The duration for the animal to consume the reward'
#### Auto water
- **auto_water**:'Whether the current trial was a auto water trial or not'
#### Optogenetics
- **laser_on_trial**:'Trials with laser stimulation'
- **laser_wavelength**:'The wavelength of laser or LED'
- **laser_location**:'The target brain areas'
- **laser_power**:'The laser power(mw)'
- **laser_duration**:'The laser duration'
- **laser_condition**:'The laser on is conditioned on LaserCondition'
- **laser_condition_probability**:'The laser on is conditioned on LaserCondition with a probability LaserConditionPro'
- **laser_start**:'Laser start is aligned to an event'
- **laser_start_offset**:'Laser start is aligned to an event with an offset'
- **laser_end**:'Laser end is aligned to an event'
- **laser_end_offset**:'Laser end is aligned to an event with an offset'
- **laser_protocol**:'The laser waveform'
- **laser_frequency**:'The laser waveform frequency'
- **laser_rampingdown**:'The ramping down time of the laser'
- **laser_pulse_duration**:'The pulse duration for Pulse protocol'
#### Left/right lick time; give left/right reward time
- **B_LeftRewardDeliveryTime**:'The reward delivery time of the left lick port'
- **B_RightRewardDeliveryTime**:'The reward delivery time of the right lick port'
- **B_LeftLickTime**:'The time of left licks'
- **B_RightLickTime**:'The time of left licks'
  
## Development
