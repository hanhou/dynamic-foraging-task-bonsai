# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CalibrationLaser.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CalibrationLaser(object):
    def setupUi(self, CalibrationLaser):
        CalibrationLaser.setObjectName("CalibrationLaser")
        CalibrationLaser.resize(1167, 300)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CalibrationLaser.sizePolicy().hasHeightForWidth())
        CalibrationLaser.setSizePolicy(sizePolicy)
        self.Frequency_1 = QtWidgets.QLineEdit(CalibrationLaser)
        self.Frequency_1.setGeometry(QtCore.QRect(448, 80, 41, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Frequency_1.sizePolicy().hasHeightForWidth())
        self.Frequency_1.setSizePolicy(sizePolicy)
        self.Frequency_1.setObjectName("Frequency_1")
        self.Protocol_1 = QtWidgets.QComboBox(CalibrationLaser)
        self.Protocol_1.setGeometry(QtCore.QRect(271, 80, 80, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Protocol_1.sizePolicy().hasHeightForWidth())
        self.Protocol_1.setSizePolicy(sizePolicy)
        self.Protocol_1.setObjectName("Protocol_1")
        self.Protocol_1.addItem("")
        self.Protocol_1.addItem("")
        self.Protocol_1.addItem("")
        self.Location_1 = QtWidgets.QComboBox(CalibrationLaser)
        self.Location_1.setGeometry(QtCore.QRect(441, 40, 80, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Location_1.sizePolicy().hasHeightForWidth())
        self.Location_1.setSizePolicy(sizePolicy)
        self.Location_1.setObjectName("Location_1")
        self.Location_1.addItem("")
        self.Location_1.addItem("")
        self.Location_1.addItem("")
        self.Location_1.addItem("")
        self.label1_12 = QtWidgets.QLabel(CalibrationLaser)
        self.label1_12.setGeometry(QtCore.QRect(214, 80, 51, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1_12.sizePolicy().hasHeightForWidth())
        self.label1_12.setSizePolicy(sizePolicy)
        self.label1_12.setTextFormat(QtCore.Qt.AutoText)
        self.label1_12.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label1_12.setObjectName("label1_12")
        self.label1_14 = QtWidgets.QLabel(CalibrationLaser)
        self.label1_14.setGeometry(QtCore.QRect(565, 80, 51, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1_14.sizePolicy().hasHeightForWidth())
        self.label1_14.setSizePolicy(sizePolicy)
        self.label1_14.setTextFormat(QtCore.Qt.AutoText)
        self.label1_14.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label1_14.setObjectName("label1_14")
        self.LaserPower_1 = QtWidgets.QComboBox(CalibrationLaser)
        self.LaserPower_1.setGeometry(QtCore.QRect(623, 40, 80, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LaserPower_1.sizePolicy().hasHeightForWidth())
        self.LaserPower_1.setSizePolicy(sizePolicy)
        self.LaserPower_1.setObjectName("LaserPower_1")
        self.LaserPower_1.addItem("")
        self.LaserPower_1.addItem("")
        self.LaserPower_1.addItem("")
        self.LaserPower_1.addItem("")
        self.LaserPower_1.addItem("")
        self.LaserPower_1.addItem("")
        self.Duration_1 = QtWidgets.QLineEdit(CalibrationLaser)
        self.Duration_1.setGeometry(QtCore.QRect(801, 40, 41, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Duration_1.sizePolicy().hasHeightForWidth())
        self.Duration_1.setSizePolicy(sizePolicy)
        self.Duration_1.setObjectName("Duration_1")
        self.RD_1 = QtWidgets.QLineEdit(CalibrationLaser)
        self.RD_1.setGeometry(QtCore.QRect(623, 80, 41, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RD_1.sizePolicy().hasHeightForWidth())
        self.RD_1.setSizePolicy(sizePolicy)
        self.RD_1.setObjectName("RD_1")
        self.Laser_1 = QtWidgets.QComboBox(CalibrationLaser)
        self.Laser_1.setGeometry(QtCore.QRect(271, 40, 80, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Laser_1.sizePolicy().hasHeightForWidth())
        self.Laser_1.setSizePolicy(sizePolicy)
        self.Laser_1.setObjectName("Laser_1")
        self.Laser_1.addItem("")
        self.Laser_1.addItem("")
        self.Laser_1.addItem("")
        self.Laser_1.addItem("")
        self.Laser_1.addItem("")
        self.label1_1 = QtWidgets.QLabel(CalibrationLaser)
        self.label1_1.setGeometry(QtCore.QRect(231, 40, 41, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1_1.sizePolicy().hasHeightForWidth())
        self.label1_1.setSizePolicy(sizePolicy)
        self.label1_1.setObjectName("label1_1")
        self.PulseDur_1 = QtWidgets.QLineEdit(CalibrationLaser)
        self.PulseDur_1.setEnabled(False)
        self.PulseDur_1.setGeometry(QtCore.QRect(801, 80, 41, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PulseDur_1.sizePolicy().hasHeightForWidth())
        self.PulseDur_1.setSizePolicy(sizePolicy)
        self.PulseDur_1.setReadOnly(False)
        self.PulseDur_1.setObjectName("PulseDur_1")
        self.label1_13 = QtWidgets.QLabel(CalibrationLaser)
        self.label1_13.setGeometry(QtCore.QRect(371, 80, 71, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1_13.sizePolicy().hasHeightForWidth())
        self.label1_13.setSizePolicy(sizePolicy)
        self.label1_13.setTextFormat(QtCore.Qt.AutoText)
        self.label1_13.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label1_13.setObjectName("label1_13")
        self.label1_2 = QtWidgets.QLabel(CalibrationLaser)
        self.label1_2.setGeometry(QtCore.QRect(387, 40, 48, 16))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1_2.sizePolicy().hasHeightForWidth())
        self.label1_2.setSizePolicy(sizePolicy)
        self.label1_2.setTextFormat(QtCore.Qt.AutoText)
        self.label1_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label1_2.setObjectName("label1_2")
        self.label1_15 = QtWidgets.QLabel(CalibrationLaser)
        self.label1_15.setEnabled(False)
        self.label1_15.setGeometry(QtCore.QRect(728, 80, 71, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1_15.sizePolicy().hasHeightForWidth())
        self.label1_15.setSizePolicy(sizePolicy)
        self.label1_15.setTextFormat(QtCore.Qt.AutoText)
        self.label1_15.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label1_15.setObjectName("label1_15")
        self.label1_5 = QtWidgets.QLabel(CalibrationLaser)
        self.label1_5.setGeometry(QtCore.QRect(728, 40, 67, 16))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1_5.sizePolicy().hasHeightForWidth())
        self.label1_5.setSizePolicy(sizePolicy)
        self.label1_5.setTextFormat(QtCore.Qt.AutoText)
        self.label1_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label1_5.setObjectName("label1_5")
        self.label1_3 = QtWidgets.QLabel(CalibrationLaser)
        self.label1_3.setGeometry(QtCore.QRect(550, 40, 67, 16))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1_3.sizePolicy().hasHeightForWidth())
        self.label1_3.setSizePolicy(sizePolicy)
        self.label1_3.setTextFormat(QtCore.Qt.AutoText)
        self.label1_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label1_3.setObjectName("label1_3")
        self.Open = QtWidgets.QPushButton(CalibrationLaser)
        self.Open.setGeometry(QtCore.QRect(60, 80, 131, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Open.sizePolicy().hasHeightForWidth())
        self.Open.setSizePolicy(sizePolicy)
        self.Open.setCheckable(True)
        self.Open.setObjectName("Open")
        self.KeepOpen = QtWidgets.QPushButton(CalibrationLaser)
        self.KeepOpen.setGeometry(QtCore.QRect(60, 120, 131, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.KeepOpen.sizePolicy().hasHeightForWidth())
        self.KeepOpen.setSizePolicy(sizePolicy)
        self.KeepOpen.setCheckable(True)
        self.KeepOpen.setObjectName("KeepOpen")
        self.label1_16 = QtWidgets.QLabel(CalibrationLaser)
        self.label1_16.setEnabled(False)
        self.label1_16.setGeometry(QtCore.QRect(70, 240, 111, 20))
        self.label1_16.setObjectName("label1_16")
        self.SampleFrequency = QtWidgets.QLineEdit(CalibrationLaser)
        self.SampleFrequency.setEnabled(False)
        self.SampleFrequency.setGeometry(QtCore.QRect(170, 240, 61, 20))
        self.SampleFrequency.setObjectName("SampleFrequency")
        self.CopyFromOpto = QtWidgets.QPushButton(CalibrationLaser)
        self.CopyFromOpto.setGeometry(QtCore.QRect(60, 40, 131, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CopyFromOpto.sizePolicy().hasHeightForWidth())
        self.CopyFromOpto.setSizePolicy(sizePolicy)
        self.CopyFromOpto.setCheckable(False)
        self.CopyFromOpto.setObjectName("CopyFromOpto")
        self.label1_17 = QtWidgets.QLabel(CalibrationLaser)
        self.label1_17.setGeometry(QtCore.QRect(860, 40, 151, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label1_17.sizePolicy().hasHeightForWidth())
        self.label1_17.setSizePolicy(sizePolicy)
        self.label1_17.setTextFormat(QtCore.Qt.AutoText)
        self.label1_17.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label1_17.setObjectName("label1_17")
        self.LaserPowerMeasured = QtWidgets.QLineEdit(CalibrationLaser)
        self.LaserPowerMeasured.setGeometry(QtCore.QRect(1020, 40, 41, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LaserPowerMeasured.sizePolicy().hasHeightForWidth())
        self.LaserPowerMeasured.setSizePolicy(sizePolicy)
        self.LaserPowerMeasured.setText("")
        self.LaserPowerMeasured.setObjectName("LaserPowerMeasured")
        self.Save = QtWidgets.QPushButton(CalibrationLaser)
        self.Save.setGeometry(QtCore.QRect(890, 80, 171, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Save.sizePolicy().hasHeightForWidth())
        self.Save.setSizePolicy(sizePolicy)
        self.Save.setCheckable(True)
        self.Save.setObjectName("Save")

        self.retranslateUi(CalibrationLaser)
        self.Location_1.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(CalibrationLaser)

    def retranslateUi(self, CalibrationLaser):
        _translate = QtCore.QCoreApplication.translate
        CalibrationLaser.setWindowTitle(_translate("CalibrationLaser", "Laser calibration"))
        self.Frequency_1.setText(_translate("CalibrationLaser", "40"))
        self.Protocol_1.setItemText(0, _translate("CalibrationLaser", "Sine"))
        self.Protocol_1.setItemText(1, _translate("CalibrationLaser", "Pulse"))
        self.Protocol_1.setItemText(2, _translate("CalibrationLaser", "Constant"))
        self.Location_1.setItemText(0, _translate("CalibrationLaser", "Both"))
        self.Location_1.setItemText(1, _translate("CalibrationLaser", "Left"))
        self.Location_1.setItemText(2, _translate("CalibrationLaser", "Right"))
        self.Location_1.setItemText(3, _translate("CalibrationLaser", "NA"))
        self.label1_12.setText(_translate("CalibrationLaser", "protocol="))
        self.label1_14.setText(_translate("CalibrationLaser", "RD (s)="))
        self.LaserPower_1.setItemText(0, _translate("CalibrationLaser", "0 mw"))
        self.LaserPower_1.setItemText(1, _translate("CalibrationLaser", "1 mw"))
        self.LaserPower_1.setItemText(2, _translate("CalibrationLaser", "1.5 mw"))
        self.LaserPower_1.setItemText(3, _translate("CalibrationLaser", "2 mw"))
        self.LaserPower_1.setItemText(4, _translate("CalibrationLaser", "2.5 mw"))
        self.LaserPower_1.setItemText(5, _translate("CalibrationLaser", "3 mw"))
        self.Duration_1.setText(_translate("CalibrationLaser", "10"))
        self.RD_1.setText(_translate("CalibrationLaser", "1"))
        self.Laser_1.setItemText(0, _translate("CalibrationLaser", "Blue"))
        self.Laser_1.setItemText(1, _translate("CalibrationLaser", "Red"))
        self.Laser_1.setItemText(2, _translate("CalibrationLaser", "Orange"))
        self.Laser_1.setItemText(3, _translate("CalibrationLaser", "Green"))
        self.Laser_1.setItemText(4, _translate("CalibrationLaser", "NA"))
        self.label1_1.setText(_translate("CalibrationLaser", "Laser="))
        self.PulseDur_1.setText(_translate("CalibrationLaser", "0.002"))
        self.label1_13.setText(_translate("CalibrationLaser", "frequency="))
        self.label1_2.setText(_translate("CalibrationLaser", "location="))
        self.label1_15.setText(_translate("CalibrationLaser", "pulse dur(s)="))
        self.label1_5.setText(_translate("CalibrationLaser", "duration (s)="))
        self.label1_3.setText(_translate("CalibrationLaser", "laser power="))
        self.Open.setText(_translate("CalibrationLaser", "open"))
        self.KeepOpen.setText(_translate("CalibrationLaser", "Keep open (without RD)"))
        self.label1_16.setText(_translate("CalibrationLaser", "Sample frequency="))
        self.SampleFrequency.setText(_translate("CalibrationLaser", "5000"))
        self.CopyFromOpto.setText(_translate("CalibrationLaser", "Copy from optogenetics"))
        self.label1_17.setText(_translate("CalibrationLaser", "Laser power measured (mw)="))
        self.Save.setText(_translate("CalibrationLaser", "Save"))
