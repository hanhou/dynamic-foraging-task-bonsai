import sys, os,traceback,json,time,subprocess,math
import numpy as np
from datetime import date,timedelta,datetime
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox,QFileDialog,QVBoxLayout,QLineEdit,QWidget,QSizePolicy
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtCore import QThreadPool,Qt,QMetaObject
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from scipy.io import savemat, loadmat
from ForagingGUI import Ui_ForagingGUI
import rigcontrol
from pyOSC3.OSC3 import OSCStreamingClient
from Visualization import PlotV,PlotLickDistribution
from Dialogs import OptogeneticsDialog,WaterCalibrationDialog,CameraDialog,ManipulatorDialog,MotorStageDialog,LaserCalibrationDialog,LickStaDialog
from MyFunctions import GenerateTrials, Worker
import warnings
import json 
#warnings.filterwarnings("ignore")

class NumpyEncoder(json.JSONEncoder):
    #def default(self, obj):
    #    if isinstance(obj, np.ndarray):
    #        return obj.tolist()
    #   return json.JSONEncoder.default(self, obj)
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert NumPy array to a list
        if isinstance(obj, np.integer):
            return int(obj)  # Convert np.int32 to a regular int
        if isinstance(obj, np.float64) and np.isnan(obj):
            return 'NaN'  # Represent NaN as a string
        return super(NumpyEncoder, self).default(obj)
    
class Window(QMainWindow, Ui_ForagingGUI):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.SettingFolder=os.path.join(os.path.expanduser("~"), "Documents","ForagingSettings")
        self.SettingFile=os.path.join(self.SettingFolder,'ForagingSettings.json')
        self._GetSettings()
        if len(sys.argv)==1:
            self.setWindowTitle("Foraging")
            self.LaserCalibrationFiles=os.path.join(self.SettingFolder,'LaserCalibration.json')
            self.WaterCalibrationFiles=os.path.join(self.SettingFolder,'WaterCalibration.json')
            self.WaterCalibrationParFiles=os.path.join(self.SettingFolder,'WaterCalibrationPar.json')
            self.TrainingStageFiles=os.path.join(self.SettingFolder,'TrainingStagePar.json') # The training phase is shared and not differentiated by tower
        else:
            if self.current_box=='':
                self.setWindowTitle("Foraging"+'_'+str(sys.argv[1]))
            else:
                self.setWindowTitle("Foraging"+'_'+self.current_box)
            self.LaserCalibrationFiles=os.path.join(self.SettingFolder,'LaserCalibration_'+str(sys.argv[1])+'.json')
            self.WaterCalibrationFiles=os.path.join(self.SettingFolder,'WaterCalibration_'+str(sys.argv[1])+'.json')
            self.WaterCalibrationParFiles=os.path.join(self.SettingFolder,'WaterCalibrationPar_'+str(sys.argv[1])+'.json')
            self.TrainingStageFiles=os.path.join(self.SettingFolder,'TrainingStagePar.json')
        try:
            self._GetLaserCalibration()
        except:
            pass
        try:
            self._GetWaterCalibration()
        except:
            pass
        self.StartANewSession=1 # to decide if should start a new session
        self.ToInitializeVisual=1
        self.FigureUpdateTooSlow=0 # if the FigureUpdateTooSlow is true, using different process to update figures
        self.ANewTrial=1 # permission to start a new trial
        self.UpdateParameters=1 # permission to update parameters
        self.Visualization.setTitle(str(date.today()))
        self.loggingstarted=-1
        try: 
            self._InitializeBonsai()
            self.InitializeBonsaiSuccessfully=1
        except Exception as e:
            print('An error occurred:', str(e))
            self.InitializeBonsaiSuccessfully=0
            self.WarningLabel_2.setText('Start without bonsai connected!')
            self.WarningLabel_2.setStyleSheet("color: red;")
        self.threadpool=QThreadPool() # get animal response
        self.threadpool2=QThreadPool() # get animal lick
        self.threadpool3=QThreadPool() # visualization
        self.threadpool4=QThreadPool() # for generating a new trial
        self.threadpool5=QThreadPool() # for starting the trial loop
        self.OpenOptogenetics=0
        self.WaterCalibration=0
        self.LaserCalibration=0
        self.Camera=0
        self.MotorStage=0
        self.Manipulator=0
        self.NewTrialRewardOrder=0
        self.LickSta=0
        self.LickSta_ToInitializeVisual=1
        self._Optogenetics() # open the optogenetics panel
        self._LaserCalibration() # to open the laser calibration panel
        self._WaterCalibration() # to open the water calibration panel
        self._Camera()
        self.RewardFamilies=[[[8,1],[6, 1],[3, 1],[1, 1]],[[8, 1], [1, 1]],[[1,0],[.9,.1],[.8,.2],[.7,.3],[.6,.4],[.5,.5]],[[6, 1],[3, 1],[1, 1]]]
        self.WaterPerRewardedTrial=0.005 
        self._ShowRewardPairs() # show reward pairs
        self._GetTrainingParameters() # get initial training parameters
        self.connectSignalsSlots()
        self._Task()
        self._TrainingStage()
        self.keyPressEvent()
        self._WaterVolumnManage2()
        self._LickSta()
        self.ManualWaterVolume=[0,0]
    def connectSignalsSlots(self):
        '''Define callbacks'''
        self.action_About.triggered.connect(self._about)
        self.action_Camera.triggered.connect(self._Camera)
        self.action_Optogenetics.triggered.connect(self._Optogenetics)
        self.action_Manipulator.triggered.connect(self._Manipulator)
        self.action_MotorStage.triggered.connect(self._MotorStage)
        self.actionLicks_sta.triggered.connect(self._LickSta)
        self.action_Calibration.triggered.connect(self._WaterCalibration)
        self.actionLaser_Calibration.triggered.connect(self._LaserCalibration)
        self.action_Snipping.triggered.connect(self._Snipping)
        self.action_Open.triggered.connect(self._Open)
        self.action_Save.triggered.connect(self._Save)
        self.actionForce_save.triggered.connect(self._ForceSave)
        self.action_Exit.triggered.connect(self._Exit)
        self.action_New.triggered.connect(self._New)
        self.action_Clear.triggered.connect(self._Clear)
        self.action_Start.triggered.connect(self.Start.click)
        self.action_NewSession.triggered.connect(self.NewSession.click)
        self.actionConnectBonsai.triggered.connect(self._InitializeBonsai)
        self.Load.clicked.connect(self._Open)
        self.Save.clicked.connect(self._Save)
        self.Clear.clicked.connect(self._Clear)
        self.Start.clicked.connect(self._Start)
        self.GiveLeft.clicked.connect(self._GiveLeft)
        self.GiveRight.clicked.connect(self._GiveRight)
        self.NewSession.clicked.connect(self._NewSession)
        self.AutoReward.clicked.connect(self._AutoReward)
        self.NextBlock.clicked.connect(self._NextBlock)
        self.OptogeneticsB.activated.connect(self._OptogeneticsB) # turn on/off optogenetics
        self.UncoupledReward.textChanged.connect(self._ShowRewardPairs)
        self.UncoupledReward.returnPressed.connect(self._ShowRewardPairs)
        self.Task.currentIndexChanged.connect(self._ShowRewardPairs)
        self.Task.currentIndexChanged.connect(self._Task)
        self.AdvancedBlockAuto.currentIndexChanged.connect(self._AdvancedBlockAuto)
        self.TotalWater.textChanged.connect(self._SuggestedWater)
        self.Randomness.currentIndexChanged.connect(self._Randomness)
        self.TrainingStage.currentIndexChanged.connect(self._TrainingStage)
        self.TrainingStage.activated.connect(self._TrainingStage)
        self.SaveTraining.clicked.connect(self._SaveTraining)
        self.actionTemporary_Logging.triggered.connect(self._startTemporaryLogging)
        self.actionFormal_logging.triggered.connect(self._startFormalLogging)
        self.actionOpen_logging_folder.triggered.connect(self._OpenLoggingFolder)
        self.actionOpen_behavior_folder.triggered.connect(self._OpenBehaviorFolder)
        self.actionOpenSettingFolder.triggered.connect(self._OpenSettingFolder)
        self.LeftValue.textChanged.connect(self._WaterVolumnManage1)
        self.RightValue.textChanged.connect(self._WaterVolumnManage1)
        self.GiveWaterL.textChanged.connect(self._WaterVolumnManage1)
        self.GiveWaterR.textChanged.connect(self._WaterVolumnManage1)
        self.LeftValue_volume.textChanged.connect(self._WaterVolumnManage2)
        self.RightValue_volume.textChanged.connect(self._WaterVolumnManage2)
        self.GiveWaterL_volume.textChanged.connect(self._WaterVolumnManage2)
        self.GiveWaterR_volume.textChanged.connect(self._WaterVolumnManage2)
        self.ShowNotes.setStyleSheet("background-color: #F0F0F0;")
        # check the change of all of the QLineEdit, QDoubleSpinBox and QSpinBox
        for container in [self.TrainingParameters, self.centralwidget, self.Opto_dialog]:
            # Iterate over each child of the container that is a QLineEdit or QDoubleSpinBox
            for child in container.findChildren((QtWidgets.QLineEdit,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox)):        
                child.textChanged.connect(self._CheckTextChange)
        # Opto_dialog can not detect natural enter press, so returnPressed is used here. 
        for container in [self.Opto_dialog]:
            # Iterate over each child of the container that is a QLineEdit or QDoubleSpinBox
            for child in container.findChildren((QtWidgets.QLineEdit)):        
                child.returnPressed.connect(self.keyPressEvent)

    def _restartlogging(self,log_folder=None):
        '''Restarting logging'''
        # stop the current session except it is a new session
        if self.StartANewSession==1 and self.ANewTrial==1:
            pass
        else:
            self._StopCurrentSession()
        if log_folder is None:
            # formal logging
            loggingtype=0
            self._GetSaveFileName()
            log_folder=os.path.join(self.log_folder,self.Tower.currentText(),self.AnimalName.text())
            base_name=os.path.splitext(os.path.basename(self.SaveFileJson))[0]
            current_time = datetime.now()
            formatted_datetime = current_time.strftime("%Y-%m-%d_%H-%M-%S")
            log_folder=os.path.join(log_folder,base_name,formatted_datetime)
        else:
            # temporary logging
            loggingtype=1
            current_time = datetime.now()
            formatted_datetime = current_time.strftime("%Y-%m-%d_%H-%M-%S")
            log_folder=os.path.join(log_folder,formatted_datetime)
        # stop the logging first
        self.Channel.StopLogging('s')
        self.Channel.StartLogging(log_folder)
        Rec=self.Channel.receive()
        if Rec[0].address=='/loggerstarted':
            pass
        if loggingtype==0:
            # formal logging
            self.loggingstarted=0
        elif loggingtype==1:
            # temporary logging
            self.loggingstarted=1
        return log_folder
    def _GetLaserCalibration(self):
        '''Get the laser calibration results'''
        if os.path.exists(self.LaserCalibrationFiles):
            with open(self.LaserCalibrationFiles, 'r') as f:
                self.LaserCalibrationResults = json.load(f)
                #sorted_dates = sorted(self.LaserCalibrationResults.keys(), key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
                sorted_dates = sorted(self.LaserCalibrationResults.keys(), key=self._custom_sort_key)
                self.RecentLaserCalibration=self.LaserCalibrationResults[sorted_dates[-1]]
                self.RecentCalibrationDate=sorted_dates[-1]
    
    def _GetWaterCalibration(self):
        '''Get the laser calibration results'''
        if os.path.exists(self.WaterCalibrationFiles):
            with open(self.WaterCalibrationFiles, 'r') as f:
                self.WaterCalibrationResults = json.load(f)
                #sorted_dates = sorted(self.LaserCalibrationResults.keys(), key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
                sorted_dates = sorted(self.WaterCalibrationResults.keys(), key=self._custom_sort_key)
                self.RecentWaterCalibration=self.WaterCalibrationResults[sorted_dates[-1]]
                self.RecentWaterCalibrationDate=sorted_dates[-1]

    def _custom_sort_key(self,key):
        if '_' in key:
            date_part, number_part = key.rsplit('_', 1)
            return (date_part, int(number_part))
        else:
            return (key, 0)

    def _GetSettings(self):
        '''Get default settings'''
        try:
            if os.path.exists(self.SettingFile):
                # Open the JSON settings file
                with open(self.SettingFile, 'r') as f:
                    Settings = json.load(f)
                if 'default_saveFolder' in Settings:
                    self.default_saveFolder=Settings['default_saveFolder']
                else:
                    self.default_saveFolder=os.path.join(os.path.expanduser("~"), "Documents")+'\\'
                if 'current_box' in Settings:
                    self.current_box=Settings['current_box']
                else:
                    self.current_box=''
                if 'log_folder' in Settings:
                    self.log_folder=Settings['log_folder']
                else:
                    self.log_folder=os.path.join(os.path.expanduser("~"), "Documents",'log')
                if 'temporary_video_folder' in Settings:
                    self.temporary_video_folder=Settings['temporary_video_folder']
                else:
                    self.temporary_video_folder=os.path.join(os.path.expanduser("~"), "Documents",'temporaryvideo')
            else:
                self.default_saveFolder=os.path.join(os.path.expanduser("~"), "Documents")+'\\'
                self.current_box=''
                self.log_folder=os.path.join(os.path.expanduser("~"), "Documents",'log')
                self.temporary_video_folder=os.path.join(os.path.expanduser("~"), "Documents",'temporaryvideo')
        except:
            self.default_saveFolder=os.path.join(os.path.expanduser("~"), "Documents")+'\\'
            self.current_box=''
        if len(sys.argv)==1:
            towertag=''
        else:
            towertag=str(sys.argv[1])
        if self.current_box in ['Green','Blue','Red','Yellow']:
            self.current_box=self.current_box+'-'+towertag
        # set the current tower automatically
        index = self.Tower.findText(self.current_box)
        if index != -1:
            self.Tower.setCurrentIndex(index)
    def _InitializeBonsai(self):
        '''Initianizing osc messages'''
        self.ip = "127.0.0.1"
        if len(sys.argv)==1:
            self.request_port = 4002
            self.request_port2 = 4003
            self.request_port3 = 4004
            self.request_port4 = 4005
        else:
            bonsai_tag = int(sys.argv[1])
            self.bonsai_tag=bonsai_tag
            # determine ports for different bonsai_tag
            if bonsai_tag==1:
                self.request_port = 4002
                self.request_port2 = 4003
                self.request_port3 = 4004
                self.request_port4 = 4005
            elif bonsai_tag==2:
                self.request_port = 4012
                self.request_port2 = 4013
                self.request_port3 = 4014
                self.request_port4 = 4015
            elif bonsai_tag==3:
                self.request_port = 4022
                self.request_port2 = 4023
                self.request_port3 = 4024
                self.request_port4 = 4025
            elif bonsai_tag==4:
                self.request_port = 4032
                self.request_port2 = 4033
                self.request_port3 = 4034
                self.request_port4 = 4035
            else:
                self.request_port = 4002
                self.request_port2 = 4003
                self.request_port3 = 4004
                self.request_port4 = 4005
        # normal behavior events
        self.client = OSCStreamingClient()  # Create client 
        self.client.connect((self.ip, self.request_port))
        self.Channel = rigcontrol.RigClient(self.client)
        # licks, LeftRewardDeliveryTime and RightRewardDeliveryTime 
        self.client2 = OSCStreamingClient()  
        self.client2.connect((self.ip, self.request_port2))
        self.Channel2 = rigcontrol.RigClient(self.client2)
        # manually give water
        self.client3 = OSCStreamingClient()  # Create client
        self.client3.connect((self.ip, self.request_port3))
        self.Channel3 = rigcontrol.RigClient(self.client3)
        # specific for transfering optogenetics waveform
        self.client4 = OSCStreamingClient()  # Create client
        self.client4.connect((self.ip, self.request_port4))
        self.Channel4 = rigcontrol.RigClient(self.client4)
        # clear previous events
        while not self.Channel.msgs.empty():
            self.Channel.receive()
        while not self.Channel2.msgs.empty():
            self.Channel2.receive()
        while not self.Channel3.msgs.empty():
            self.Channel3.receive()
        while not self.Channel4.msgs.empty():
            self.Channel4.receive()
        self.WarningLabel_2.setText('')
        self.WarningLabel_2.setStyleSheet("color: gray;")
        self.InitializeBonsaiSuccessfully=1
    def _OpenSettingFolder(self):
        '''Open the setting folder'''
        try:
            subprocess.Popen(['explorer', self.SettingFolder])
        except:
            pass
    def _ForceSave(self):
        '''Save whether the current trial is complete or not'''
        self._Save(ForceSave=1)
    def _WaterVolumnManage1(self):
        '''Change the water volume based on the valve open time'''
        self.LeftValue.textChanged.disconnect(self._WaterVolumnManage1)
        self.RightValue.textChanged.disconnect(self._WaterVolumnManage1)
        self.GiveWaterL.textChanged.disconnect(self._WaterVolumnManage1)
        self.GiveWaterR.textChanged.disconnect(self._WaterVolumnManage1)
        self.LeftValue_volume.textChanged.disconnect(self._WaterVolumnManage2)
        self.RightValue_volume.textChanged.disconnect(self._WaterVolumnManage2)
        self.GiveWaterL_volume.textChanged.disconnect(self._WaterVolumnManage2)
        self.GiveWaterR_volume.textChanged.disconnect(self._WaterVolumnManage2)
        # use the latest calibration result
        if hasattr(self, 'WaterCalibration_dialog'):
            if hasattr(self.WaterCalibration_dialog, 'PlotM'):
                if  hasattr(self.WaterCalibration_dialog.PlotM, 'FittingResults'):
                    FittingResults=self.WaterCalibration_dialog.PlotM.FittingResults
                    tag=1
        if tag==1:
            self._GetLatestFitting(FittingResults)
            self._ValvetimeVolumnTransformation(widget2=self.LeftValue_volume,widget1=self.LeftValue,direction=1,valve='Left')
            self._ValvetimeVolumnTransformation(widget2=self.RightValue_volume,widget1=self.RightValue,direction=1,valve='Right')
            self._ValvetimeVolumnTransformation(widget2=self.GiveWaterL_volume,widget1=self.GiveWaterL,direction=1,valve='Left')
            self._ValvetimeVolumnTransformation(widget2=self.GiveWaterR_volume,widget1=self.GiveWaterR,direction=1,valve='Right')
            self.LeftValue_volume.setEnabled(True)
            self.RightValue_volume.setEnabled(True)
            self.GiveWaterL_volume.setEnabled(True)
            self.GiveWaterR_volume.setEnabled(True)
            self.label_28.setEnabled(True)
            self.label_29.setEnabled(True)
        else:
            self.LeftValue_volume.setEnabled(False)
            self.RightValue_volume.setEnabled(False)
            self.GiveWaterL_volume.setEnabled(False)
            self.GiveWaterR_volume.setEnabled(False)
            self.label_28.setEnabled(False)
            self.label_29.setEnabled(False)
        self.LeftValue.textChanged.connect(self._WaterVolumnManage1)
        self.RightValue.textChanged.connect(self._WaterVolumnManage1)
        self.GiveWaterL.textChanged.connect(self._WaterVolumnManage1)
        self.GiveWaterR.textChanged.connect(self._WaterVolumnManage1)
        self.LeftValue_volume.textChanged.connect(self._WaterVolumnManage2)
        self.RightValue_volume.textChanged.connect(self._WaterVolumnManage2)
        self.GiveWaterL_volume.textChanged.connect(self._WaterVolumnManage2)
        self.GiveWaterR_volume.textChanged.connect(self._WaterVolumnManage2)

    def _WaterVolumnManage2(self):
        '''Change the valve open time based on the water volume'''
        self.LeftValue.textChanged.disconnect(self._WaterVolumnManage1)
        self.RightValue.textChanged.disconnect(self._WaterVolumnManage1)
        self.GiveWaterL.textChanged.disconnect(self._WaterVolumnManage1)
        self.GiveWaterR.textChanged.disconnect(self._WaterVolumnManage1)
        self.LeftValue_volume.textChanged.disconnect(self._WaterVolumnManage2)
        self.RightValue_volume.textChanged.disconnect(self._WaterVolumnManage2)
        self.GiveWaterL_volume.textChanged.disconnect(self._WaterVolumnManage2)
        self.GiveWaterR_volume.textChanged.disconnect(self._WaterVolumnManage2)
        # use the latest calibration result
        if hasattr(self, 'WaterCalibration_dialog'):
            if hasattr(self.WaterCalibration_dialog, 'PlotM'):
                if  hasattr(self.WaterCalibration_dialog.PlotM, 'FittingResults'):
                    FittingResults=self.WaterCalibration_dialog.PlotM.FittingResults
                    tag=1
        if tag==1:
            self._GetLatestFitting(FittingResults)
            self._ValvetimeVolumnTransformation(widget1=self.LeftValue_volume,widget2=self.LeftValue,direction=-1,valve='Left')
            self._ValvetimeVolumnTransformation(widget1=self.RightValue_volume,widget2=self.RightValue,direction=-1,valve='Right')
            self._ValvetimeVolumnTransformation(widget1=self.GiveWaterL_volume,widget2=self.GiveWaterL,direction=-1,valve='Left')
            self._ValvetimeVolumnTransformation(widget1=self.GiveWaterR_volume,widget2=self.GiveWaterR,direction=-1,valve='Right')
        else:
            self.LeftValue_volume.setEnabled(False)
            self.RightValue_volume.setEnabled(False)
            self.GiveWaterL_volume.setEnabled(False)
            self.GiveWaterR_volume.setEnabled(False)
            self.label_28.setEnabled(False)
            self.label_29.setEnabled(False)
        self.LeftValue.textChanged.connect(self._WaterVolumnManage1)
        self.RightValue.textChanged.connect(self._WaterVolumnManage1)
        self.GiveWaterL.textChanged.connect(self._WaterVolumnManage1)
        self.GiveWaterR.textChanged.connect(self._WaterVolumnManage1)
        self.LeftValue_volume.textChanged.connect(self._WaterVolumnManage2)
        self.RightValue_volume.textChanged.connect(self._WaterVolumnManage2)
        self.GiveWaterL_volume.textChanged.connect(self._WaterVolumnManage2)
        self.GiveWaterR_volume.textChanged.connect(self._WaterVolumnManage2)

    def _ValvetimeVolumnTransformation(self,widget1,widget2,direction,valve):
        '''Transformation between valve open time the the water volume'''
        # widget1 is the source widget and widget2 is the target widget
        try:
            if valve not in self.latest_fitting:
                # disable the widget
                if direction==1:
                    widget2.setEnabled(False)
                elif direction==-1:
                    widget1.setEnabled(False)
                return
            else:
                widget2.setEnabled(True)
                widget1.setEnabled(True)
            if direction==1:
                widget2.setValue(float(widget1.text())*self.latest_fitting[valve][0]+self.latest_fitting[valve][1])
            elif direction==-1:
                widget2.setValue((float(widget1.text())-self.latest_fitting[valve][1])/self.latest_fitting[valve][0])
        except:
            pass

    def _GetLatestFitting(self,FittingResults):
        '''Get the latest fitting results from water calibration'''
        latest_fitting={}
        sorted_dates = sorted(FittingResults.keys(), key=self._custom_sort_key)
        sorted_dates=sorted_dates[::-1]
        for current_date in sorted_dates:
            if 'Left' in FittingResults[current_date]:
                latest_fitting['Left']=FittingResults[current_date]['Left']
                break
        for current_date in sorted_dates:
            if 'Right' in FittingResults[current_date]:
                latest_fitting['Right']=FittingResults[current_date]['Right']
                break
        self.latest_fitting=latest_fitting

    def _OpenBehaviorFolder(self):
        '''Open the the current behavior folder'''
        self._GetSaveFileName()
        folder_name=os.path.dirname(self.SaveFileJson)
        try:
            subprocess.Popen(['explorer', folder_name])
        except:
            pass
    def _OpenLoggingFolder(self):
        '''Open the logging folder'''
        self.Camera_dialog._OpenSaveFolder()
    def _startTemporaryLogging(self):
        '''Restart the temporary logging'''
        self.Ot_log_folder=self._restartlogging(self.temporary_video_folder)
    def _startFormalLogging(self):
        '''Restart the formal logging'''
        self.Ot_log_folder=self._restartlogging()
    def _TrainingStage(self):
        '''Change the parameters automatically based on training stage and task'''
        self.WarningLabel_SaveTrainingStage.setText('')
        self.WarningLabel_SaveTrainingStage.setStyleSheet("color: none;")
        # load the prestored training stage parameters
        self._LoadTrainingPar()
        # set the training parameters in the GUI
        widget_dict = {w.objectName(): w for w in self.TrainingParameters.findChildren((QtWidgets.QPushButton,QtWidgets.QLineEdit,QtWidgets.QTextEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox))}
        Task=self.Task.currentText()
        CurrentTrainingStage=self.TrainingStage.currentText()
        try:
            for key in widget_dict.keys():
                if Task not in self.TrainingStagePar:
                    continue
                elif CurrentTrainingStage not in self.TrainingStagePar[Task]:
                    continue
                if key in self.TrainingStagePar[Task][CurrentTrainingStage]:
                    # skip some keys
                    if key=='ExtraWater' or key=='WeightBefore' or key=='WeightAfter' or key=='SuggestedWater':
                        self.ExtraWater.setText('')
                        continue
                    widget = widget_dict[key]
                    try: # load the paramter used by last trial
                        value=np.array([self.TrainingStagePar[Task][CurrentTrainingStage][key]])
                        Tag=0
                    except: # sometimes we only have training parameters, no behavior parameters
                        value=self.TrainingStagePar[Task][CurrentTrainingStage][key]
                        Tag=1
                    if isinstance(widget, QtWidgets.QPushButton):
                        pass
                    if type(value)==bool:
                        Tag=1
                    else:
                        if len(value)==0:
                            value=np.array([''], dtype='<U1')
                            Tag=0
                    if type(value)==np.ndarray:
                        Tag=0
                    if isinstance(widget, QtWidgets.QLineEdit):
                        if Tag==0:
                            widget.setText(value[-1])
                        elif Tag==1:
                            widget.setText(value)
                    elif isinstance(widget, QtWidgets.QComboBox):
                        if Tag==0:
                            index = widget.findText(value[-1])
                        elif Tag==1:
                            index = widget.findText(value)
                        if index != -1:
                            widget.setCurrentIndex(index)
                    elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                        if Tag==0:
                            widget.setValue(float(value[-1]))
                        elif Tag==1:
                            widget.setValue(float(value))
                    elif isinstance(widget, QtWidgets.QSpinBox):
                        if Tag==0:
                            widget.setValue(int(value[-1]))
                        elif Tag==1:
                            widget.setValue(int(value))
                    elif isinstance(widget, QtWidgets.QTextEdit):
                        if Tag==0:
                            widget.setText(value[-1])
                        elif Tag==1:
                            widget.setText(value)
                    elif isinstance(widget, QtWidgets.QPushButton):
                        if key=='AutoReward':
                            if Tag==0:
                                widget.setChecked(bool(value[-1]))
                            elif Tag==1:
                                widget.setChecked(value)
                            self._AutoReward()
                else:
                    widget = widget_dict[key]
                    if not (isinstance(widget, QtWidgets.QComboBox) or isinstance(widget, QtWidgets.QPushButton)):
                        widget.clear()
        except Exception as e:
            # Catch the exception and print error information
            print("An error occurred:")
            print(traceback.format_exc())
        
    def _SaveTraining(self):
        '''Save the training stage parameters'''
        # load the pre-stored training stage parameters
        self._LoadTrainingPar()
        # get the current training stage parameters
        widget_dict = {w.objectName(): w for w in self.TrainingParameters.findChildren((QtWidgets.QPushButton,QtWidgets.QLineEdit,QtWidgets.QTextEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox))}
        Task=self.Task.currentText()
        CurrentTrainingStage=self.TrainingStage.currentText()
        for key in widget_dict.keys():
            widget = widget_dict[key]
            if Task not in self.TrainingStagePar:
                self.TrainingStagePar[Task]={}
            if CurrentTrainingStage not in self.TrainingStagePar[Task]:
                self.TrainingStagePar[Task][CurrentTrainingStage]={}
            if isinstance(widget, QtWidgets.QPushButton):
                self.TrainingStagePar[Task][CurrentTrainingStage][widget.objectName()]=widget.isChecked()
            elif isinstance(widget, QtWidgets.QTextEdit):
                self.TrainingStagePar[Task][CurrentTrainingStage][widget.objectName()]=widget.toPlainText()
            elif isinstance(widget, QtWidgets.QDoubleSpinBox) or isinstance(widget, QtWidgets.QLineEdit)  or isinstance(widget, QtWidgets.QSpinBox):
                self.TrainingStagePar[Task][CurrentTrainingStage][widget.objectName()]=widget.text()
            elif isinstance(widget, QtWidgets.QComboBox):
                self.TrainingStagePar[Task][CurrentTrainingStage][widget.objectName()]=widget.currentText()
        # save
        if not os.path.exists(os.path.dirname(self.TrainingStageFiles)):
            os.makedirs(os.path.dirname(self.TrainingStageFiles))
        with open(self.TrainingStageFiles, "w") as file:
            json.dump(self.TrainingStagePar, file,indent=4) 
        self.WarningLabel_SaveTrainingStage.setText('Training stage parameters were saved!')
        self.WarningLabel_SaveTrainingStage.setStyleSheet("color: red;")
        self.SaveTraining.setChecked(False)
    def _LoadTrainingPar(self):
        '''load the training stage parameters'''
        self.TrainingStagePar={}
        if os.path.exists(self.TrainingStageFiles):
            with open(self.TrainingStageFiles, 'r') as f:
                self.TrainingStagePar = json.load(f)
    def _Randomness(self):
        '''enable/disable some fields in the Block/Delay Period/ITI'''
        if self.Randomness.currentText()=='Exponential':
            self.label_14.setEnabled(True)
            self.label_18.setEnabled(True)
            self.label_39.setEnabled(True)
            self.BlockBeta.setEnabled(True)
            self.DelayBeta.setEnabled(True)
            self.ITIBeta.setEnabled(True)
            if self.Task.currentText()!='RewardN':
                self.BlockBeta.setStyleSheet("color: black;border: 1px solid gray;background-color: white;")
                self.label_14.setStyleSheet("color: black;background-color: white;")
        elif self.Randomness.currentText()=='Even':
            self.label_14.setEnabled(False)
            self.label_18.setEnabled(False)
            self.label_39.setEnabled(False)
            self.BlockBeta.setEnabled(False)
            self.DelayBeta.setEnabled(False)
            self.ITIBeta.setEnabled(False)
            if self.Task.currentText()!='RewardN':
                border_color = "rgb(100, 100, 100,80)"
                border_style = "1px solid " + border_color
                self.BlockBeta.setStyleSheet(f"color: gray;border:{border_style};background-color: rgba(0, 0, 0, 0);")
                self.label_14.setStyleSheet("color: gray;background-color: rgba(0, 0, 0, 0);")
    def _AdvancedBlockAuto(self):
        '''enable/disable some fields in the AdvancedBlockAuto'''
        if self.AdvancedBlockAuto.currentText()=='off':
            self.label_54.setEnabled(False)
            self.label_60.setEnabled(False)
            self.SwitchThr.setEnabled(False)
            self.PointsInARow.setEnabled(False)
        else:
            self.label_54.setEnabled(True)
            self.label_60.setEnabled(True)
            self.SwitchThr.setEnabled(True)
            self.PointsInARow.setEnabled(True)
    def keyPressEvent(self, event=None):
        '''Enter press to allow change of parameters'''
        # Get the parameters before change
        if hasattr(self, 'GeneratedTrials') and self.ToInitializeVisual==0: # use the current GUI paramters when no session starts running
            Parameters=self.GeneratedTrials
        else:
            Parameters=self
        if event==None:
            event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, Qt.Key_Return, Qt.KeyboardModifiers())
        if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            # handle the return key press event here
            print("Parameter changes confirmed!")
            # prevent the default behavior of the return key press event
            event.accept()
            self.UpdateParameters=1 # Changes are allowed
            # change color to black
            for container in [self.TrainingParameters, self.centralwidget, self.Opto_dialog]:
                # Iterate over each child of the container that is a QLineEdit or QDoubleSpinBox
                for child in container.findChildren((QtWidgets.QLineEdit,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox)):
                    if child.objectName()=='qt_spinbox_lineedit':
                        continue
                    if child.isEnabled()==False:
                        continue
                    child.setStyleSheet('color: black;')
                    child.setStyleSheet('background-color: white;')
                    if child.objectName()=='AnimalName' and child.text()=='':
                        child.setText(getattr(Parameters, 'TP_'+child.objectName()))
                        continue
                    if child.objectName()=='Experimenter' or child.objectName()=='TotalWater' or child.objectName()=='AnimalName' or child.objectName()=='WeightBefore'  or child.objectName()=='WeightAfter' or child.objectName()=='ExtraWater':
                        continue
                    if child.objectName()=='UncoupledReward':
                        Correct=self._CheckFormat(child)
                        if Correct ==0: # incorrect format; don't change
                            child.setText(getattr(Parameters, 'TP_'+child.objectName()))
                        continue
                    # check valid for empty condition
                    try:
                        # it's valid float
                        float(child.text())
                    except Exception as e:
                        print('An error occurred:', str(e))
                        if isinstance(child, QtWidgets.QDoubleSpinBox):
                            child.setValue(float(getattr(Parameters, 'TP_'+child.objectName())))
                        elif isinstance(child, QtWidgets.QSpinBox):
                            child.setValue(int(getattr(Parameters, 'TP_'+child.objectName())))
                        else:
                            # Invalid float. Do not change the parameter
                            child.setText(getattr(Parameters, 'TP_'+child.objectName()))
            # update the current training parameters
            self._GetTrainingParameters()
    
    def _CheckTextChange(self):
        '''Check if the text change is reasonable'''
        # Get the parameters before change
        if hasattr(self, 'GeneratedTrials'):
            Parameters=self.GeneratedTrials
        else:
            Parameters=self
        for container in [self.TrainingParameters, self.centralwidget, self.Opto_dialog]:
            # Iterate over each child of the container that is a QLineEdit or QDoubleSpinBox
            for child in container.findChildren((QtWidgets.QLineEdit,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox)):
                if child.objectName()=='qt_spinbox_lineedit' or child.isEnabled()==False: # I don't understand where the qt_spinbox_lineedit comes from. 
                    continue
                if (child.objectName()=='RewardFamily' or child.objectName()=='RewardPairsN' or child.objectName()=='BaseRewardSum') and (child.text()!=''):
                    Correct=self._CheckFormat(child)
                    if Correct ==0: # incorrect format; don't change
                        child.setText(getattr(Parameters, 'TP_'+child.objectName()))
                    self._ShowRewardPairs()
                try:
                    if getattr(Parameters, 'TP_'+child.objectName())!=child.text() :
                        self.Continue=0
                        if child.objectName()=='Experimenter' or child.objectName()=='AnimalName' or child.objectName()=='UncoupledReward' or child.objectName()=='WeightBefore'  or child.objectName()=='WeightAfter' or child.objectName()=='ExtraWater':
                            child.setStyleSheet('color: red;')
                            self.Continue=1
                        if child.text()=='': # If it's empty, changing the background color and waiting for the confirming
                            self.UpdateParameters=0
                            child.setStyleSheet('background-color: red;')
                            self.Continue=1
                        if child.objectName()=='RunLength' or child.objectName()=='WindowSize' or child.objectName()=='StepSize':
                            if child.text()=='':
                                child.setValue(int(getattr(Parameters, 'TP_'+child.objectName())))
                                child.setStyleSheet('color: black;')
                                child.setStyleSheet('background-color: white;')
                        if self.Continue==1:
                            continue
                        child.setStyleSheet('color: red;')
                        try:
                            # it's valid float
                            float(child.text())
                            self.UpdateParameters=0 # Changes are not allowed until press is typed
                        except Exception as e:
                            print('An error occurred:', str(e))
                            # Invalid float. Do not change the parameter
                            if isinstance(child, QtWidgets.QDoubleSpinBox):
                                child.setValue(float(getattr(Parameters, 'TP_'+child.objectName())))
                            elif isinstance(child, QtWidgets.QSpinBox):
                                child.setValue(int(getattr(Parameters, 'TP_'+child.objectName())))
                            else:
                                child.setText(getattr(Parameters, 'TP_'+child.objectName()))
                            child.setText(getattr(Parameters, 'TP_'+child.objectName()))
                            child.setStyleSheet('color: black;')
                            self.UpdateParameters=1
                    else:
                        child.setStyleSheet('color: black;')
                        child.setStyleSheet('background-color: white;')
                except:
                    pass
    def _CheckFormat(self,child):
        '''Check if the input format is correct'''
        if child.objectName()=='RewardFamily': # When we change the RewardFamily, sometimes the RewardPairsN is larger than available reward pairs in this family. 
            try:
                self.RewardFamilies[int(self.RewardFamily.text())-1]
                if int(self.RewardPairsN.text())>len(self.RewardFamilies[int(self.RewardFamily.text())-1]):
                    self.RewardPairsN.setText(str(len(self.RewardFamilies[int(self.RewardFamily.text())-1])))
                return 1
            except Exception as e:
                print('An error occurred:', str(e))
                return 0
        if child.objectName()=='RewardFamily' or child.objectName()=='RewardPairsN' or child.objectName()=='BaseRewardSum':
            try:
                self.RewardPairs=self.RewardFamilies[int(self.RewardFamily.text())-1][:int(self.RewardPairsN.text())]
                if int(self.RewardPairsN.text())>len(self.RewardFamilies[int(self.RewardFamily.text())-1]):
                    return 0
                else:
                    return 1
            except Exception as e: 
                print('An error occurred:', str(e))
                return 0
        if child.objectName()=='UncoupledReward':
            try:
                input_string=self.UncoupledReward.text()
                if input_string=='': # do not permit empty uncoupled reward
                    return 0
                # remove any square brackets and spaces from the string
                input_string = input_string.replace('[','').replace(']','').replace(',', ' ')
                # split the remaining string into a list of individual numbers
                num_list = input_string.split()
                # convert each number in the list to a float
                num_list = [float(num) for num in num_list]
                # create a numpy array from the list of numbers
                self.RewardProb=np.array(num_list)
                return 1
            except Exception as e: 
                print('An error occurred:', str(e))
                return 0
        else:
            return 1
        
    def _SuggestedWater(self):
        '''Change suggested water based on total water'''
        try:
            self.T_SuggestedWater=float(self.TotalWater.text())-float(self.GeneratedTrials.BS_TotalReward)
            self.SuggestedWater.setText(str(np.round(self.T_SuggestedWater,3)))
        except Exception as e:
            print('An error occurred:', str(e))
            self.SuggestedWater.setText(self.TotalWater.text())

    def _GetTrainingParameters(self):
        '''Get training parameters'''
        # Iterate over each container to find child widgets and store their values in self
        for container in [self.TrainingParameters, self.centralwidget, self.Opto_dialog]:
            # Iterate over each child of the container that is a QLineEdit or QDoubleSpinBox
            for child in container.findChildren((QtWidgets.QLineEdit, QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox)):
                if child.objectName()=='qt_spinbox_lineedit':
                    continue
                # Set an attribute in self with the name 'TP_' followed by the child's object name
                # and store the child's text value
                setattr(self, 'TP_'+child.objectName(), child.text())
            # Iterate over each child of the container that is a QComboBox
            for child in container.findChildren(QtWidgets.QComboBox):
                # Set an attribute in self with the name 'TP_' followed by the child's object name
                # and store the child's current text value
                setattr(self, 'TP_'+child.objectName(), child.currentText())
            # Iterate over each child of the container that is a QPushButton
            for child in container.findChildren(QtWidgets.QPushButton):
                # Set an attribute in self with the name 'TP_' followed by the child's object name
                # and store whether the child is checked or not
                setattr(self, 'TP_'+child.objectName(), child.isChecked())
    def _Task(self):
        '''hide and show some fields based on the task type'''
        self.label_43.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
        self.ITIIncrease.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
        if self.Task.currentText() in ['Coupled Baiting','Coupled Without Baiting']:
            self.label_6.setEnabled(True)
            self.label_7.setEnabled(True)
            self.label_8.setEnabled(True)
            self.BaseRewardSum.setEnabled(True)
            self.RewardPairsN.setEnabled(True)
            self.RewardFamily.setEnabled(True)
            self.label_20.setEnabled(False)
            self.UncoupledReward.setEnabled(False)
            self.label_6.setStyleSheet("color: black;")
            self.label_7.setStyleSheet("color: black;")
            self.label_8.setStyleSheet("color: black;")
            self.BaseRewardSum.setStyleSheet("color: black;""border: 1px solid gray;")
            self.RewardPairsN.setStyleSheet("color: black;""border: 1px solid gray;")
            self.RewardFamily.setStyleSheet("color: black;""border: 1px solid gray;")
            self.label_20.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.UncoupledReward.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            # block
            if self.Randomness.currentText()=='Exponential':
                self.BlockBeta.setEnabled(True)
                self.BlockBeta.setStyleSheet("color: black;""border: 1px solid gray;")
                self.label_14.setStyleSheet("color: black;background-color: rgba(0, 0, 0, 0)")
            else:
                self.BlockBeta.setEnabled(False)
                self.BlockBeta.setStyleSheet("color: gray;""border: 1px solid gray;")
                self.label_14.setStyleSheet("color: gray;")
            self.label_12.setEnabled(True)
            self.label_11.setEnabled(True)
            self.BlockBeta.setEnabled(True)
            self.BlockMin.setEnabled(True)
            self.BlockMax.setEnabled(True)
            self.label_12.setStyleSheet("color: black;")
            self.label_11.setStyleSheet("color: black;")
            self.BlockBeta.setStyleSheet("color: black;""border: 1px solid gray;")
            self.BlockMin.setStyleSheet("color: black;""border: 1px solid gray;")
            self.BlockMax.setStyleSheet("color: black;""border: 1px solid gray;")
            self.label_27.setEnabled(False)
            self.InitiallyInactiveN.setEnabled(False)
            self.label_27.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.InitiallyInactiveN.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.InitiallyInactiveN.setGeometry(QtCore.QRect(1081, 23, 80, 20))
            # change name of min reward each block
            self.label_13.setText('min reward each block=')
            self.BlockMinReward.setText('0')
            # change the position of RewardN=/min reward each block=
            self.BlockMinReward.setGeometry(QtCore.QRect(863, 128, 80, 20))
            self.label_13.setGeometry(QtCore.QRect(711, 128, 146, 16))
            # move auto-reward
            self.IncludeAutoReward.setGeometry(QtCore.QRect(1080, 128, 80, 20))
            self.label_26.setGeometry(QtCore.QRect(929, 128, 146, 16))
            # set block length to the default value
            self.BlockMin.setText('20')
            self.BlockMax.setText('60')
        elif self.Task.currentText() in ['Uncoupled Baiting','Uncoupled Without Baiting']:
            border_color = "rgb(100, 100, 100,80)"
            border_style = "1px solid " + border_color
            self.label_6.setEnabled(False)
            self.label_7.setEnabled(False)
            self.label_8.setEnabled(False)
            self.BaseRewardSum.setEnabled(False)
            self.RewardPairsN.setEnabled(False)
            self.RewardFamily.setEnabled(False)
            self.label_20.setEnabled(True)
            self.UncoupledReward.setEnabled(True)
            self.label_6.setStyleSheet("color: gray;")
            self.label_7.setStyleSheet("color: gray;")
            self.label_8.setStyleSheet("color: gray;")
            self.BaseRewardSum.setStyleSheet(f"color: gray;background-color: rgba(0, 0, 0, 0);border: 1px solid gray;border:{border_style};")
            self.RewardPairsN.setStyleSheet(f"color: gray;background-color: rgba(0, 0, 0, 0);border: 1px solid gray;border:{border_style};")
            self.RewardFamily.setStyleSheet(f"color: gray;background-color: rgba(0, 0, 0, 0);border: 1px solid gray;border:{border_style};")
            self.label_20.setStyleSheet("color: black;")
            self.UncoupledReward.setStyleSheet("color: black;""border: 1px solid gray;")
            # block
            if self.Randomness.currentText()=='Exponential':
                self.BlockBeta.setEnabled(True)
                self.BlockBeta.setStyleSheet("color: black;""border: 1px solid gray;")
                self.label_14.setStyleSheet("color: black;")
            else:
                self.BlockBeta.setEnabled(False)
                self.BlockBeta.setStyleSheet("color: gray;""border: 1px solid gray;")
                self.label_14.setStyleSheet("color: gray;")
            self.label_12.setEnabled(True)
            self.label_11.setEnabled(True)
            self.BlockBeta.setEnabled(True)
            self.BlockMin.setEnabled(True)
            self.BlockMax.setEnabled(True)
            self.label_12.setStyleSheet("color: black;")
            self.label_11.setStyleSheet("color: black;")
            self.BlockBeta.setStyleSheet("color: black;""border: 1px solid gray;")
            self.BlockMin.setStyleSheet("color: black;""border: 1px solid gray;")
            self.BlockMax.setStyleSheet("color: black;""border: 1px solid gray;")
            self.label_27.setEnabled(False)
            self.InitiallyInactiveN.setEnabled(False)
            self.label_27.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.InitiallyInactiveN.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.InitiallyInactiveN.setGeometry(QtCore.QRect(1081, 23, 80, 20))
            # change name of min reward each block
            self.label_13.setText('min reward each block=')
            self.BlockMinReward.setText('0')
            # change the position of RewardN=/min reward each block=
            self.BlockMinReward.setGeometry(QtCore.QRect(863, 128, 80, 20))
            self.label_13.setGeometry(QtCore.QRect(711, 128, 146, 16))
            # move auto-reward
            self.IncludeAutoReward.setGeometry(QtCore.QRect(1080, 128, 80, 20))
            self.label_26.setGeometry(QtCore.QRect(929, 128, 146, 16))
            # set block length to the default value
            self.BlockMin.setText('20')
            self.BlockMax.setText('60')
        elif self.Task.currentText() in ['RewardN']:
            self.label_6.setEnabled(True)
            self.label_7.setEnabled(True)
            self.label_8.setEnabled(True)
            self.BaseRewardSum.setEnabled(True)
            self.RewardPairsN.setEnabled(True)
            self.RewardFamily.setEnabled(True)
            self.label_20.setEnabled(False)
            self.UncoupledReward.setEnabled(False)
            self.label_6.setStyleSheet("color: black;")
            self.label_7.setStyleSheet("color: black;")
            self.label_8.setStyleSheet("color: black;")
            self.BaseRewardSum.setStyleSheet("color: black;""border: 1px solid gray;")
            self.RewardPairsN.setStyleSheet("color: black;""border: 1px solid gray;")
            self.RewardFamily.setStyleSheet("color: black;""border: 1px solid gray;")
            self.label_20.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.UncoupledReward.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            # block
            self.label_14.setEnabled(False)
            self.label_12.setEnabled(False)
            self.label_11.setEnabled(False)
            self.BlockBeta.setEnabled(False)
            self.BlockMin.setEnabled(False)
            self.BlockMax.setEnabled(False)
            self.label_14.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.label_12.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.label_11.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.BlockBeta.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.BlockMin.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            self.BlockMax.setStyleSheet("background-color: rgba(0, 0, 0, 0); color: rgba(0, 0, 0, 0);""border: none;")
            # block; no reward when initially active
            self.label_27.setEnabled(True)
            self.InitiallyInactiveN.setEnabled(True)
            self.label_27.setStyleSheet("color: black;")
            self.InitiallyInactiveN.setStyleSheet("color: black;""border: 1px solid gray;")
            self.InitiallyInactiveN.setGeometry(QtCore.QRect(403, 128, 80, 20))
            # change name of min reward each block
            self.label_13.setText('RewardN=')
            self.BlockMinReward.setText('5')
            # change the position of RewardN=/min reward each block=
            self.BlockMinReward.setGeometry(QtCore.QRect(191, 128, 80, 20))
            self.label_13.setGeometry(QtCore.QRect(40, 128, 146, 16))
            # move auto-reward
            self.IncludeAutoReward.setGeometry(QtCore.QRect(614, 128, 80, 20))
            self.label_26.setGeometry(QtCore.QRect(460, 128, 146, 16))
            # set block length to be 1
            self.BlockMin.setText('1')
            self.BlockMax.setText('1')
        self._Randomness()

    def _ShowRewardPairs(self):
        '''Show reward pairs'''
        try:
            if self.Task.currentText() in ['Coupled Baiting','Coupled Without Baiting','RewardN']:
                self.RewardPairs=self.RewardFamilies[int(self.RewardFamily.text())-1][:int(self.RewardPairsN.text())]
                self.RewardProb=np.array(self.RewardPairs)/np.expand_dims(np.sum(self.RewardPairs,axis=1),axis=1)*float(self.BaseRewardSum.text())
                if hasattr(self, 'GeneratedTrials'):
                    self.ShowRewardPairs.setText('Reward pairs: '+str(np.round(self.RewardProb,2))+'\n\n'+'Current pair: '+str(np.round(self.GeneratedTrials.B_RewardProHistory[:,self.GeneratedTrials.B_CurrentTrialN],2))) 
                else:
                    self.ShowRewardPairs.setText('Reward pairs: '+str(np.round(self.RewardProb,2))+'\n\n'+'Current pair: ') 
            elif self.Task.currentText() in ['Uncoupled Baiting','Uncoupled Without Baiting']:
                input_string=self.UncoupledReward.text()
                # remove any square brackets and spaces from the string
                input_string = input_string.replace('[','').replace(']','').replace(',', ' ')
                # split the remaining string into a list of individual numbers
                num_list = input_string.split()
                # convert each number in the list to a float
                num_list = [float(num) for num in num_list]
                # create a numpy array from the list of numbers
                self.RewardProb=np.array(num_list)
                if hasattr(self, 'GeneratedTrials'):
                    self.ShowRewardPairs.setText('Reward pairs: '+str(np.round(self.RewardProb,2))+'\n\n'+'Current pair: '+str(np.round(self.GeneratedTrials.B_RewardProHistory[:,self.GeneratedTrials.B_CurrentTrialN],2))) 
                else:
                    self.ShowRewardPairs.setText('Reward pairs: '+str(np.round(self.RewardProb,2))+'\n\n'+'Current pair: ') 
        except Exception as e:
            # Catch the exception and print error information
            print("An error occurred:",str(e))
    def closeEvent(self, event):
        # disable close icon
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.show()
        self._StopCurrentSession() # stop the current session first
         # enable close icon
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
        self.show()
        reply = QMessageBox.question(self, 'Foraging Close', 'Do you want to save the current result?',QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self._Save()
            event.accept()
            self.Start.setChecked(False)
            if self.InitializeBonsaiSuccessfully==1:
                self.client.close()
                self.client2.close()
                self.client3.close()
                self.client4.close()
            self.Opto_dialog.close()
            print('Window closed')
        elif reply == QMessageBox.No:
            event.accept()
            self.Start.setChecked(False)
            if self.InitializeBonsaiSuccessfully==1:
                self.client.close()
                self.client2.close()
                self.client3.close()
                self.client4.close()
            print('Window closed')
            self.Opto_dialog.close()
        else:
            event.ignore()
    def _Exit(self):
        '''Close the GUI'''
        response = QMessageBox.question(self,'Save and Exit:', "Do you want to save the current result?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,QMessageBox.Yes)
        if response==QMessageBox.Yes:
            self._Save()
            self.close()
        elif response==QMessageBox.No:
            self.close()
    def _Snipping(self):
        '''Open the snipping tool'''
        os.system("start %windir%\system32\SnippingTool.exe") 
    def _Optogenetics(self):
        '''will be triggered when the optogenetics icon is pressed'''
        if self.OpenOptogenetics==0:
            self.Opto_dialog = OptogeneticsDialog(MainWindow=self)
            self.OpenOptogenetics=1
        if self.action_Optogenetics.isChecked()==True:
            self.Opto_dialog.show()
        else:
            self.Opto_dialog.hide()
    def _Camera(self):
        '''Open the camera. It's not available now'''
        if self.Camera==0:
            self.Camera_dialog = CameraDialog(MainWindow=self)
            self.Camera=1
        if self.action_Camera.isChecked()==True:
            self.Camera_dialog.show()
        else:
            self.Camera_dialog.hide()
    def _Manipulator(self):
        if self.Manipulator==0:
            self.ManipulatoB_dialog = ManipulatorDialog(MainWindow=self)
            self.Manipulator=1
        if self.action_Manipulator.isChecked()==True:
            self.ManipulatoB_dialog.show()
        else:
            self.ManipulatoB_dialog.hide()
    def _WaterCalibration(self):
        if self.WaterCalibration==0:
            self.WaterCalibration_dialog = WaterCalibrationDialog(MainWindow=self)
            self.WaterCalibration=1
        if self.action_Calibration.isChecked()==True:
            self.WaterCalibration_dialog.show()
        else:
            self.WaterCalibration_dialog.hide()
    def _LaserCalibration(self):
        if self.LaserCalibration==0:
            self.LaserCalibration_dialog = LaserCalibrationDialog(MainWindow=self)
            self.LaserCalibration=1
        if self.actionLaser_Calibration.isChecked()==True:
            self.LaserCalibration_dialog.show()
        else:
            self.LaserCalibration_dialog.hide()
    def _MotorStage(self):
        if self.MotorStage==0:
            self.MotorStage_dialog = MotorStageDialog(MainWindow=self)
            self.MotorStage=1
        if self.action_MotorStage.isChecked()==True:
            self.MotorStage_dialog.show()
        else:
            self.MotorStage_dialog.hide()
    def _LickSta(self):
        '''Licks statistics'''
        if self.LickSta==0:
            self.LickSta_dialog = LickStaDialog(MainWindow=self)
            self.LickSta=1
            self.LickSta_dialog.setWindowTitle("Licks statistics")
        if self.actionLicks_sta.isChecked()==True:
            self.LickSta_dialog.show()
        else:
            self.LickSta_dialog.hide()
        if self.LickSta_ToInitializeVisual==1: # only run once
            PlotLick=PlotLickDistribution()
            self.PlotLick=PlotLick
            layout=self.LickSta_dialog.VisuLicksStatistics.layout()
            if layout is not None:
                for i in reversed(range(layout.count())):
                    layout.itemAt(i).widget().setParent(None)
                layout.invalidate()
            if layout is None:
                layout=QVBoxLayout(self.LickSta_dialog.VisuLicksStatistics)
            toolbar = NavigationToolbar(PlotLick, self)
            toolbar.setMaximumHeight(20)
            toolbar.setMaximumWidth(300)
            layout.addWidget(toolbar)
            layout.addWidget(PlotLick)
            self.LickSta_ToInitializeVisual=0
        try:
            self.PlotLick._Update(GeneratedTrials=self.GeneratedTrials)
        except:
            pass
    def _about(self):
        QMessageBox.about(
            self,
            "Foraging",
            "<p>Version 1</p>"
            "<p>Date: Dec 1, 2022</p>"
            "<p>Behavior control</p>"
            "<p>Visualization</p>"
            "<p>Analysis</p>"
            "<p></p>",
        )
   
    def _Save(self,ForceSave=0):
        if ForceSave==0:
            self._StopCurrentSession() # stop the current session first
        if self.WeightBefore.text()=='' or self.WeightAfter.text()=='' or self.ExtraWater.text()=='':
            response = QMessageBox.question(self,'Save without weight or extra water:', "Do you want to save without weight or extra water information provided?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,QMessageBox.Yes)
            if response==QMessageBox.Yes:
                pass
                self.WarningLabel.setText('Saving without weight or extra water!')
                self.WarningLabel.setStyleSheet("color: red;")
            elif response==QMessageBox.No:
                return
            elif response==QMessageBox.Cancel:
                return
        # this should be improved in the future. Need to get the last LeftRewardDeliveryTime and RightRewardDeliveryTime
        if hasattr(self, 'GeneratedTrials'):
            self.GeneratedTrials._GetLicks(self.Channel2)
        
        #ParamsFile = os.path.join(self.default_saveFolder, self.AnimalName.text(), f'{self.AnimalName.text()}_{date.today()}.json')
        self._GetSaveFileName()
        Names = QFileDialog.getSaveFileName(self, 'Save File',self.SaveFileJson,"JSON files (*.json);;MAT files (*.mat);;JSON parameters (*_par.json)")
        if Names[1]=='JSON parameters (*_par.json)':
            self.SaveFile=Names[0].replace('.json', '_par.json')
        else:
            self.SaveFile=Names[0]
        if self.SaveFile == '':
            self.WarningLabel.setText('Discard saving!')
            self.WarningLabel.setStyleSheet("color: red;")
        if self.SaveFile != '':
            if hasattr(self, 'GeneratedTrials'):
                if hasattr(self.GeneratedTrials, 'Obj'):
                    Obj=self.GeneratedTrials.Obj
                else:
                    Obj={}
            else:
                Obj={}
            widget_dict = {w.objectName(): w for w in self.centralwidget.findChildren((QtWidgets.QPushButton,QtWidgets.QLineEdit,QtWidgets.QTextEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox))}
            widget_dict.update({w.objectName(): w for w in self.TrainingParameters.findChildren(QtWidgets.QDoubleSpinBox)})
            self._Concat(widget_dict,Obj,'None')
            if hasattr(self, 'LaserCalibration_dialog'):
                widget_dict_LaserCalibration={w.objectName(): w for w in self.LaserCalibration_dialog.findChildren((QtWidgets.QPushButton,QtWidgets.QLineEdit,QtWidgets.QTextEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox))} 
                self._Concat(widget_dict_LaserCalibration,Obj,'LaserCalibration_dialog')
            if hasattr(self, 'Opto_dialog'):
                widget_dict_opto={w.objectName(): w for w in self.Opto_dialog.findChildren((QtWidgets.QPushButton,QtWidgets.QLineEdit,QtWidgets.QTextEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox))}
                self._Concat(widget_dict_opto,Obj,'Opto_dialog')
            if hasattr(self, 'Camera_dialog'):
                widget_dict_camera={w.objectName(): w for w in self.Camera_dialog.findChildren((QtWidgets.QPushButton,QtWidgets.QLineEdit,QtWidgets.QTextEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox))}
                self._Concat(widget_dict_camera,Obj,'Camera_dialog')
            
            Obj2=Obj.copy()
            # save behavor events
            if hasattr(self, 'GeneratedTrials'):
                # Do something if self has the GeneratedTrials attribute
                # Iterate over all attributes of the GeneratedTrials object
                for attr_name in dir(self.GeneratedTrials):
                    if attr_name.startswith('B_') or attr_name.startswith('BS_'):
                        if attr_name=='B_RewardFamilies' and self.SaveFile.endswith('.mat'):
                            pass
                        else:
                            Value=getattr(self.GeneratedTrials, attr_name)
                            try:
                                if math.isnan(Value):
                                    Obj[attr_name]='nan'
                                else:
                                    Obj[attr_name]=Value
                            except:
                                Obj[attr_name]=Value
            # save other events, e.g. session start time
            for attr_name in dir(self):
                if attr_name.startswith('Other_'):
                    Obj[attr_name] = getattr(self, attr_name)
            # save laser calibration results (only for the calibration session)
            if hasattr(self, 'LaserCalibration_dialog'):
                # Do something if self has the GeneratedTrials attribute
                # Iterate over all attributes of the GeneratedTrials object
                for attr_name in dir(self.LaserCalibration_dialog):
                    if attr_name.startswith('LCM_'):
                        Obj[attr_name] = getattr(self.LaserCalibration_dialog, attr_name)
            # save laser calibration results from the json file
            if hasattr(self, 'LaserCalibrationResults'):
                self._GetLaserCalibration()
                try:
                    Obj['LaserCalibrationResults']=self.LaserCalibrationResults
                except:
                    pass
            # save water calibration results
            if hasattr(self, 'WaterCalibrationResults'):
                self._GetWaterCalibration()
                try:
                    Obj['WaterCalibrationResults']=self.WaterCalibrationResults
                except:
                    pass
            # save ohter fields start with Ot_
            for attr_name in dir(self):
                if attr_name.startswith('Ot_'):
                    Obj[attr_name]=getattr(self, attr_name)
            # save Json or mat
            if self.SaveFile.endswith('.mat'):
            # Save data to a .mat file
                savemat(self.SaveFile, Obj) 
            elif self.SaveFile.endswith('par.json'):
                with open(self.SaveFile, "w") as outfile:
                    json.dump(Obj2, outfile, indent=4, cls=NumpyEncoder)
            elif self.SaveFile.endswith('.json'):
                with open(self.SaveFile, "w") as outfile:
                    json.dump(Obj, outfile, indent=4, cls=NumpyEncoder)
            # close the camera
            if self.Camera_dialog.AutoControl.currentText()=='Yes':
                self.Camera_dialog.StartCamera.setChecked(False)
                self.Camera_dialog._StartCamera()

    def _GetSaveFileName(self):
        '''Get the name of the save file'''
        SaveFileMat = os.path.join(self.default_saveFolder, self.Tower.currentText(),self.AnimalName.text(), f'{self.AnimalName.text()}_{date.today()}.mat')
        SaveFileJson= os.path.join(self.default_saveFolder, self.Tower.currentText(),self.AnimalName.text(), f'{self.AnimalName.text()}_{date.today()}.json')
        SaveFileParJson= os.path.join(self.default_saveFolder, self.Tower.currentText(),self.AnimalName.text(), f'{self.AnimalName.text()}_{date.today()}_par.json')
        if not os.path.exists(os.path.dirname(SaveFileJson)):
            os.makedirs(os.path.dirname(SaveFileJson))
            print(f"Created new folder: {os.path.dirname(SaveFileJson)}")
        N=0
        while 1:
            if os.path.isfile(SaveFileMat) or os.path.isfile(SaveFileJson)or os.path.isfile(SaveFileParJson):
                N=N+1
                SaveFileMat=os.path.join(self.default_saveFolder, self.Tower.currentText(),self.AnimalName.text(), f'{self.AnimalName.text()}_{date.today()}_{N}.mat')
                SaveFileJson=os.path.join(self.default_saveFolder, self.Tower.currentText(),self.AnimalName.text(), f'{self.AnimalName.text()}_{date.today()}_{N}.json')
                SaveFileParJson=os.path.join(self.default_saveFolder, self.Tower.currentText(),self.AnimalName.text(), f'{self.AnimalName.text()}_{date.today()}_{N}_par.json')
            else:
                break
        self.SaveFileMat=SaveFileMat
        self.SaveFileJson=SaveFileJson
        self.SaveFileParJson=SaveFileParJson
    def _Concat(self,widget_dict,Obj,keyname):
        '''Help manage save different dialogs'''
        if keyname=='None':
            for key in widget_dict.keys():
                widget = widget_dict[key]
                if isinstance(widget, QtWidgets.QPushButton):
                    Obj[widget.objectName()]=widget.isChecked()
                elif isinstance(widget, QtWidgets.QTextEdit):
                    Obj[widget.objectName()]=widget.toPlainText()
                elif isinstance(widget, QtWidgets.QDoubleSpinBox) or isinstance(widget, QtWidgets.QLineEdit)  or isinstance(widget, QtWidgets.QSpinBox):
                    Obj[widget.objectName()]=widget.text()
                elif isinstance(widget, QtWidgets.QComboBox):
                    Obj[widget.objectName()]=widget.currentText()
        else:
            Obj[keyname]={}
            for key in widget_dict.keys():
                widget = widget_dict[key]
                if key=='Frequency_1':
                    pass
                if isinstance(widget, QtWidgets.QPushButton):
                    Obj[keyname][widget.objectName()]=widget.isChecked()
                elif isinstance(widget, QtWidgets.QTextEdit):
                    Obj[keyname][widget.objectName()]=widget.toPlainText()
                elif isinstance(widget, QtWidgets.QDoubleSpinBox) or isinstance(widget, QtWidgets.QLineEdit)  or isinstance(widget, QtWidgets.QSpinBox):
                    Obj[keyname][widget.objectName()]=widget.text()
                elif isinstance(widget, QtWidgets.QComboBox):
                    Obj[keyname][widget.objectName()]=widget.currentText()
        return Obj
    def _Open(self):
        self._StopCurrentSession() # stop current session first
        self.NewSession.setChecked(True)
        Reply=self._NewSession()
        if Reply == QMessageBox.Yes or Reply == QMessageBox.No:
            self.NewSession.setDisabled(True) # You must start a NewSession after loading a new file, and you can't continue that session
        elif Reply == QMessageBox.Cancel:
            return
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', self.default_saveFolder+'\\'+self.Tower.currentText(), "Behavior JSON files (*.json);;Behavior MAT files (*.mat);;JSON parameters (*_par.json)")
        self.fname=fname
        if fname:
            if fname.endswith('.mat'):
                Obj = loadmat(fname)
            elif fname.endswith('.json'):
                f = open (fname, "r")
                Obj = json.loads(f.read())
                f.close()
            self.Obj = Obj
            widget_dict = {w.objectName(): w for w in self.centralwidget.findChildren((QtWidgets.QPushButton,QtWidgets.QLineEdit,QtWidgets.QTextEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox))}
            widget_dict.update({w.objectName(): w for w in self.TrainingParameters.findChildren(QtWidgets.QDoubleSpinBox)})
            widget_dict.update({w.objectName(): w for w in self.Opto_dialog.findChildren((QtWidgets.QLineEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox))})  # update optogenetics parameters from the loaded file
            if hasattr(self, 'LaserCalibration_dialog'):
                widget_dict.update({w.objectName(): w for w in self.LaserCalibration_dialog.findChildren((QtWidgets.QLineEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox))})  
            if hasattr(self, 'Opto_dialog'):
                widget_dict.update({w.objectName(): w for w in self.Opto_dialog.findChildren((QtWidgets.QPushButton,QtWidgets.QLineEdit,QtWidgets.QTextEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox))})
            if hasattr(self, 'Camera_dialog'):
                widget_dict.update({w.objectName(): w for w in self.Camera_dialog.findChildren((QtWidgets.QPushButton,QtWidgets.QLineEdit,QtWidgets.QTextEdit, QtWidgets.QComboBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox))})
            try:
                for key in widget_dict.keys():
                    try:
                        widget = widget_dict[key]
                        if widget.parent().objectName()=='Optogenetics':
                            CurrentObj=Obj['Opto_dialog']
                        elif widget.parent().objectName()=='Camera':
                            CurrentObj=Obj['Camera_dialog']
                        elif widget.parent().objectName()=='CalibrationLaser':
                            CurrentObj=Obj['LaserCalibration_dialog']
                        else:
                            CurrentObj=Obj.copy()
                    except:
                        continue
                    if key in CurrentObj:
                        # skip some keys
                        if key=='ExtraWater' or key=='WeightBefore' or key=='WeightAfter' or key=='SuggestedWater' or key=='Start':
                            self.ExtraWater.setText('')
                            continue
                        widget = widget_dict[key]
                        try: # load the paramter used by last trial
                            value=np.array([CurrentObj['TP_'+key][-2]])
                            Tag=0
                        except: # sometimes we only have training parameters, no behavior parameters
                            value=CurrentObj[key]
                            Tag=1
                        if isinstance(widget, QtWidgets.QPushButton):
                            pass
                        if type(value)==bool:
                            Tag=1
                        else:
                            if len(value)==0:
                                value=np.array([''], dtype='<U1')
                                Tag=0
                        if type(value)==np.ndarray:
                            Tag=0
                        if isinstance(widget, QtWidgets.QLineEdit):
                            if Tag==0:
                                widget.setText(value[-1])
                            elif Tag==1:
                                widget.setText(value)
                        elif isinstance(widget, QtWidgets.QComboBox):
                            if Tag==0:
                                index = widget.findText(value[-1])
                            elif Tag==1:
                                index = widget.findText(value)
                            if index != -1:
                                widget.setCurrentIndex(index)
                        elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                            if Tag==0:
                                widget.setValue(float(value[-1]))
                            elif Tag==1:
                                widget.setValue(float(value))
                        elif isinstance(widget, QtWidgets.QSpinBox):
                            if Tag==0:
                                widget.setValue(int(value[-1]))
                            elif Tag==1:
                                widget.setValue(int(value))
                        elif isinstance(widget, QtWidgets.QTextEdit):
                            if Tag==0:
                                widget.setText(value[-1])
                            elif Tag==1:
                                widget.setText(value)
                        elif isinstance(widget, QtWidgets.QPushButton):
                            if Tag==0:
                                widget.setChecked(bool(value[-1]))
                            elif Tag==1:
                                widget.setChecked(value)
                            if key=='AutoReward':
                                self._AutoReward()
                            if key=='NextBlock':
                                self._NextBlock()
                    else:
                        widget = widget_dict[key]
                        if not (isinstance(widget, QtWidgets.QComboBox) or isinstance(widget, QtWidgets.QPushButton)):
                            widget.clear()
            except Exception as e:
                # Catch the exception and print error information
                print("An error occurred:")
                print(traceback.format_exc())
            try:
                # visualization when loading the data
                self._LoadVisualization()
            except Exception as e:
                # Catch the exception and print error information
                print("An error occurred:",str(e))
                print(traceback.format_exc())
                # delete GeneratedTrials
                del self.GeneratedTrials
            # show basic information
            if 'Other_inforTitle' in Obj:
                self.infor.setTitle(Obj['Other_inforTitle'])
            if 'Other_BasicTitle' in Obj:
                self.Basic.setTitle(Obj['Other_BasicTitle'])
            if 'Other_BasicText' in Obj:
                self.ShowBasic.setText(Obj['Other_BasicText'])
        else:
            self.NewSession.setDisabled(False)

    def _LoadVisualization(self):
        '''To visulize the training when loading a session'''
        self.ToInitializeVisual=1
        Obj=self.Obj
        self.GeneratedTrials=GenerateTrials(self)
        # Iterate over all attributes of the GeneratedTrials object
        for attr_name in dir(self.GeneratedTrials):
            if attr_name in Obj.keys():
                try:
                    # Get the value of the attribute from Obj
                    if attr_name.startswith('TP_'):
                        value = Obj[attr_name][-1]
                    else:
                        value = Obj[attr_name]
                    # transfer list to numpy array
                    if type(getattr(self.GeneratedTrials,attr_name))== np.ndarray:
                        value=np.array(value)
                    # Set the attribute in the GeneratedTrials object
                    setattr(self.GeneratedTrials, attr_name, value)
                except:
                    pass
        if self.GeneratedTrials.B_AnimalResponseHistory.size==0:
            del self.GeneratedTrials
            return
        # for mat file
        if self.fname.endswith('.mat'):
            # this is a bug to use the scipy.io.loadmat or savemat (it will change the dimension of the nparray)
            self.GeneratedTrials.B_AnimalResponseHistory=self.GeneratedTrials.B_AnimalResponseHistory[0]
            self.GeneratedTrials.B_TrialStartTime=self.GeneratedTrials.B_TrialStartTime[0]
            self.GeneratedTrials.B_DelayStartTime=self.GeneratedTrials.B_DelayStartTime[0]
            self.GeneratedTrials.B_TrialEndTime=self.GeneratedTrials.B_TrialEndTime[0]
            self.GeneratedTrials.B_GoCueTime=self.GeneratedTrials.B_GoCueTime[0]
            self.GeneratedTrials.B_RewardOutcomeTime=self.GeneratedTrials.B_RewardOutcomeTime[0]
            #self.GeneratedTrials._GenerateATrial(self.Channel4)
            
        PlotM=PlotV(win=self,GeneratedTrials=self.GeneratedTrials,width=5, height=4)
        layout=self.Visualization.layout()
        if layout is not None:
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().setParent(None)
            layout.invalidate()
        layout=self.Visualization.layout()
        if layout is None:
            layout=QVBoxLayout(self.Visualization)
        toolbar = NavigationToolbar(PlotM, self)
        toolbar.setMaximumHeight(20)
        toolbar.setMaximumWidth(300)
        layout.addWidget(toolbar)
        layout.addWidget(PlotM)
        PlotM._Update(GeneratedTrials=self.GeneratedTrials)
        self.PlotLick._Update(GeneratedTrials=self.GeneratedTrials)
    def _Clear(self):
        reply = QMessageBox.question(self, 'Clear parameters:', 'Do you want to clear training parameters?',QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            for child in self.TrainingParameters.findChildren(QtWidgets.QLineEdit)+ self.centralwidget.findChildren(QtWidgets.QLineEdit):
                if child.isEnabled():
                    child.clear()
        else:
            pass

    def _New(self):
        self._Clear()

    def _AutoReward(self):
        if self.AutoReward.isChecked():
            self.AutoReward.setStyleSheet("background-color : green;")
        else:
            self.AutoReward.setStyleSheet("background-color : none")
    def _NextBlock(self):
        if self.NextBlock.isChecked():
            self.NextBlock.setStyleSheet("background-color : green;")
        else:
            self.NextBlock.setStyleSheet("background-color : none")
    def _NewSession(self):
        if self.NewSession.isChecked():
            if self.ToInitializeVisual==0: # Do not ask to save when no session starts running
                reply = QMessageBox.question(self, 'New Session:', 'Do you want to save the current result?',QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            else:
                reply=QMessageBox.No
            if reply == QMessageBox.Yes:
                self.NewSession.setStyleSheet("background-color : green;")
                self.Start.setStyleSheet("background-color : none")
                self._Save()
                self.Start.setChecked(False)
                self.StartANewSession=1
                print('Saved')
            elif reply == QMessageBox.No:
                self.NewSession.setStyleSheet("background-color : green;")
                self.Start.setStyleSheet("background-color : none")
                self.Start.setChecked(False)
                self.StartANewSession=1
            else:
                self.NewSession.setChecked(False)
                pass
        else:
            self.NewSession.setStyleSheet("background-color : none")
            reply=QMessageBox.Cancel
        return reply

    def _AskSave(self):
        reply = QMessageBox.question(self, 'New Session:', 'Do you want to save the current result?',QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self._Save()
            print('Saved')
        elif reply == QMessageBox.No:
            pass
        else:
            pass
        
    def _StopCurrentSession(self):
        # stop the current session
        self.Start.setStyleSheet("background-color : green;")
        self.Start.setStyleSheet("background-color : none")
        self.Start.setChecked(False)
        # waiting for the finish of the last trial
        if self.ANewTrial==0:
            self.WarningLabel.setText('Waiting for the finish of the last trial!')
            self.WarningLabel.setStyleSheet("color: red;")
            while 1:
                QApplication.processEvents()
                if self.ANewTrial==1:
                    self.WarningLabel.setText('')
                    self.WarningLabel.setStyleSheet("color: red;")
                    break
    def _thread_complete(self):
        '''complete of a trial'''
        if self.NewTrialRewardOrder==0:
            self.GeneratedTrials._GenerateATrial(self.Channel4)
        self.ANewTrial=1
    def _thread_complete2(self):
        '''complete of receive licks'''
        self.ToReceiveLicks=1
    def _thread_complete3(self):
        '''complete of update figures'''
        self.ToUpdateFigure=1
    def _thread_complete4(self):
        '''complete of generating a trial'''
        self.ToGenerateATrial=1
    def _Start(self):
        '''start trial loop'''
        self.WarningLabel_SaveTrainingStage.setText('')
        self.WarningLabel_SaveTrainingStage.setStyleSheet("color: none;")
        self.NewSession.setDisabled(False)
        if self.Start.isChecked():
            self.keyPressEvent()
            # change button color and mark the state change
            self.Start.setStyleSheet("background-color : green;")
            self.NewSession.setStyleSheet("background-color : none")
            self.NewSession.setChecked(False)
            self.WarningLabel.setText('')
            self.WarningLabel.setStyleSheet("color: none;")
        else:
            self.Start.setStyleSheet("background-color : none")
            ''' # update graph when session is stopped
            try:
                time.sleep(self.GeneratedTrials.B_ITIHistory[-1]+3)
                self.PlotM._Update(GeneratedTrials=self.GeneratedTrials)
            except:
                pass
            '''
        # waiting for the finish of the last trial
        if self.StartANewSession==1 and self.ANewTrial==0:
            self.WarningLabel.setText('Waiting for the finish of the last trial!')
            self.WarningLabel.setStyleSheet("color: red;")
            while 1:
                QApplication.processEvents()
                if self.ANewTrial==1:
                    self.WarningLabel.setText('')
                    self.WarningLabel.setStyleSheet("color: red;")
                    break
        # to see if we should start a new session
        if self.StartANewSession==1 and self.ANewTrial==1:
            self.WarningLabel.setText('')
            self.WarningLabel.setStyleSheet("color: gray;")
            # start a new logging
            self.Ot_log_folder=self._restartlogging()
            # start the camera during the begginning of each session
            if self.Camera_dialog.AutoControl.currentText()=='Yes':
                self.Camera_dialog.StartCamera.setChecked(True)
                self.Camera_dialog._StartCamera()
            self.SessionStartTime=datetime.now()
            self.Other_SessionStartTime=str(self.SessionStartTime) # for saving
            GeneratedTrials=GenerateTrials(self)
            self.GeneratedTrials=GeneratedTrials
            self.StartANewSession=0
            PlotM=PlotV(win=self,GeneratedTrials=GeneratedTrials,width=5, height=4)
            PlotM.finish=1
            self.PlotM=PlotM
            #generate the first trial outside the loop, only for new session
            self.ToReceiveLicks=1
            self.ToUpdateFigure=1
            self.ToGenerateATrial=1
            self.ToInitializeVisual=1
            GeneratedTrials._GenerateATrial(self.Channel4)
            # delete licks from the previous session
            GeneratedTrials._DeletePreviousLicks(self.Channel2)
        else:
            GeneratedTrials=self.GeneratedTrials

        if self.ToInitializeVisual==1: # only run once
            self.PlotM=PlotM
            layout=self.Visualization.layout()
            if layout is not None:
                for i in reversed(range(layout.count())):
                    layout.itemAt(i).widget().setParent(None)
                layout.invalidate()
            if layout is None:
                layout=QVBoxLayout(self.Visualization)
            toolbar = NavigationToolbar(PlotM, self)
            toolbar.setMaximumHeight(20)
            toolbar.setMaximumWidth(300)
            layout.addWidget(toolbar)
            layout.addWidget(PlotM)
            self.ToInitializeVisual=0
            # create workers
            worker1 = Worker(GeneratedTrials._GetAnimalResponse,self.Channel,self.Channel3,self.Channel4)
            worker1.signals.finished.connect(self._thread_complete)
            workerLick = Worker(GeneratedTrials._GetLicks,self.Channel2)
            workerLick.signals.finished.connect(self._thread_complete2)
            workerPlot = Worker(PlotM._Update,GeneratedTrials=GeneratedTrials,Channel=self.Channel2)
            workerPlot.signals.finished.connect(self._thread_complete3)
            workerGenerateAtrial = Worker(GeneratedTrials._GenerateATrial,self.Channel4)
            workerGenerateAtrial.signals.finished.connect(self._thread_complete4)
            workerStartTrialLoop = Worker(self._StartTrialLoop,GeneratedTrials,worker1,workerPlot,workerGenerateAtrial)
            workerStartTrialLoop1 = Worker(self._StartTrialLoop1,GeneratedTrials)
            self.worker1=worker1
            self.workerLick=workerLick
            self.workerPlot=workerPlot
            self.workerGenerateAtrial=workerGenerateAtrial
            self.workerStartTrialLoop=workerStartTrialLoop
            self.workerStartTrialLoop1=workerStartTrialLoop1
        else:
            PlotM=self.PlotM
            worker1=self.worker1
            workerLick=self.workerLick
            workerPlot=self.workerPlot
            workerGenerateAtrial=self.workerGenerateAtrial
            workerStartTrialLoop=self.workerStartTrialLoop
            workerStartTrialLoop1=self.workerStartTrialLoop1
        
        self._StartTrialLoop(GeneratedTrials,worker1)
        '''
        self.test=1
        if self.test==1:
            self._StartTrialLoop(GeneratedTrials,worker1,workerPlot,workerGenerateAtrial)
        else:
            self.threadpool5.start(workerStartTrialLoop) # I just found the QApplication.processEvents() was better to reduce delay time between trial end the the next trial start 
        '''
    def _StartTrialLoop(self,GeneratedTrials,worker1):
        while self.Start.isChecked():
            QApplication.processEvents()
            if self.ANewTrial==1 and self.Start.isChecked(): 
                self.ANewTrial=0 # can start a new trial when we receive the trial end signal from Bonsai
                GeneratedTrials.B_CurrentTrialN+=1
                print('Current trial: '+str(GeneratedTrials.B_CurrentTrialN+1))
                if not (self.GeneratedTrials.TP_AutoReward  or int(self.GeneratedTrials.TP_BlockMinReward)>0):
                    # generate a new trial and get reward
                    self.NewTrialRewardOrder=1
                else:
                    # get reward and generate a new trial
                    self.NewTrialRewardOrder=0     
                #initiate the generated trial
                GeneratedTrials._InitiateATrial(self.Channel,self.Channel4)
                #receive licks and update figures
                self.PlotM._Update(GeneratedTrials=GeneratedTrials,Channel=self.Channel2)
                # update licks statistics
                if self.actionLicks_sta.isChecked():
                    self.PlotLick._Update(GeneratedTrials=GeneratedTrials)
                #get the response of the animal using a different thread
                self.threadpool.start(worker1)
                #generate a new trial
                if self.NewTrialRewardOrder==1:
                    GeneratedTrials._GenerateATrial(self.Channel4)     

    def _StartTrialLoop1(self,GeneratedTrials,worker1,workerPlot,workerGenerateAtrial):
        while self.Start.isChecked():
            QApplication.processEvents()
            if self.ANewTrial==1 and self.ToGenerateATrial==1 and self.Start.isChecked(): 
                self.ANewTrial=0 # can start a new trial when we receive the trial end signal from Bonsai
                GeneratedTrials.B_CurrentTrialN+=1
                print('Current trial: '+str(GeneratedTrials.B_CurrentTrialN+1))
                if not (self.GeneratedTrials.TP_AutoReward  or int(self.GeneratedTrials.TP_BlockMinReward)>0):
                    # generate new trial and get reward
                    self.NewTrialRewardOrder=1
                else:
                    # get reward and generate new trial
                    self.NewTrialRewardOrder=0     
                #initiate the generated trial
                GeneratedTrials._InitiateATrial(self.Channel,self.Channel4)
                #receive licks and update figures
                if self.test==1:
                    self.PlotM._Update(GeneratedTrials=GeneratedTrials,Channel=self.Channel2)
                else:
                    if self.ToUpdateFigure==1:
                        self.ToUpdateFigure=0
                        self.threadpool3.start(workerPlot)
                #get the response of the animal using a different thread
                self.threadpool.start(worker1)
                '''
                if self.test==1:
                    self.ANewTrial=1
                    GeneratedTrials.GetResponseFinish=0
                    GeneratedTrials._GetAnimalResponse(self.Channel,self.Channel3,self.Channel4)
                else:
                    GeneratedTrials.GetResponseFinish=0
                    self.threadpool.start(worker1)
                '''
                #generate a new trial
                if self.test==1:
                    self.ToGenerateATrial=1
                    GeneratedTrials._GenerateATrial(self.Channel4)
                else:
                    self.ToGenerateATrial=0
                    self.threadpool4.start(workerGenerateAtrial)
                
    def _OptogeneticsB(self):
        ''' optogenetics control in the main window'''
        if self.OptogeneticsB.currentText()=='on':
            self._Optogenetics() # press the optogenetics icon
            self.action_Optogenetics.setChecked(True)
            self.Opto_dialog.show()
            self.label_18.setEnabled(False)
            self.label_15.setEnabled(False)
            self.label_17.setEnabled(False)
            self.DelayBeta.setEnabled(False)
            self.DelayMin.setEnabled(False)
            self.DelayMax.setEnabled(False)
        else:
            self.action_Optogenetics.setChecked(False)
            self.Opto_dialog.hide()
            self.label_18.setEnabled(True)
            self.label_15.setEnabled(True)
            self.label_17.setEnabled(True)
            self.DelayBeta.setEnabled(True)
            self.DelayMin.setEnabled(True)
            self.DelayMax.setEnabled(True)
    def _GiveLeft(self):
        '''manually give left water'''
        self.Channel.LeftValue(float(self.TP_GiveWaterL)*1000)
        time.sleep(0.01) 
        self.Channel3.ManualWater_Left(int(1))
        self.Channel.LeftValue(float(self.TP_LeftValue)*1000)
        self.ManualWaterVolume[0]=self.ManualWaterVolume[0]+float(self.TP_GiveWaterL_volume)/1000
        self._UpdateSuggestedWater(float(self.TP_GiveWaterL_volume)/1000)
    
    def _GiveRight(self):
        '''manually give right water'''
        self.Channel.RightValue(float(self.TP_GiveWaterR)*1000)
        time.sleep(0.01) 
        self.Channel3.ManualWater_Right(int(1))
        self.Channel.RightValue(float(self.TP_RightValue)*1000)
        self.ManualWaterVolume[1]=self.ManualWaterVolume[1]+float(self.TP_GiveWaterR_volume)/1000
        self._UpdateSuggestedWater(float(self.TP_GiveWaterR_volume)/1000)

    def _UpdateSuggestedWater(self,ManualWater=0):
        '''Update the suggested water from the manually give water'''
        Tag=0
        if self.TotalWater.text()!='':
            # self.BS_TotalReward: normal rewards and auto rewards
            if hasattr(self,'GeneratedTrials'):
                if hasattr(self.GeneratedTrials,'BS_TotalReward'):
                    self.B_SuggestedWater=float(self.TotalWater.text())-float(self.GeneratedTrials.BS_TotalReward)/1000-np.sum(self.ManualWaterVolume)
                    self.SuggestedWater.setText(str(np.round(self.B_SuggestedWater,3)))
                else:
                    Tag=1
            else:
                Tag=1
            if Tag==1:
                if self.SuggestedWater.text()=='':
                    SuggestedWater=float(self.TotalWater.text())
                else:
                    SuggestedWater=float(self.SuggestedWater.text())
                self.B_SuggestedWater=SuggestedWater-ManualWater
                self.SuggestedWater.setText(str(np.round(self.B_SuggestedWater,3)))

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling,1)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps,True)
    QApplication.setAttribute(Qt.AA_DisableHighDpiScaling,False)
    QApplication.setAttribute(Qt.AA_Use96Dpi,False)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    # Run your application's event loop and stop after closing all windows
    sys.exit(app.exec())
