# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'param_setting_panel.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(388, 686)
        self.verticalLayout_2 = QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pb_para_setting_panel_implement = QPushButton(Form)
        self.pb_para_setting_panel_implement.setObjectName(u"pb_para_setting_panel_implement")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_para_setting_panel_implement.sizePolicy().hasHeightForWidth())
        self.pb_para_setting_panel_implement.setSizePolicy(sizePolicy)
        self.pb_para_setting_panel_implement.setMinimumSize(QSize(100, 100))

        self.horizontalLayout_2.addWidget(self.pb_para_setting_panel_implement)

        self.pb_para_setting_panel_reset = QPushButton(Form)
        self.pb_para_setting_panel_reset.setObjectName(u"pb_para_setting_panel_reset")
        self.pb_para_setting_panel_reset.setMinimumSize(QSize(100, 100))

        self.horizontalLayout_2.addWidget(self.pb_para_setting_panel_reset)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.comboBox = QComboBox(self.groupBox)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.gridLayout_2.addWidget(self.comboBox, 2, 1, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.cb_stft_overlap = QComboBox(self.groupBox)
        self.cb_stft_overlap.addItem("")
        self.cb_stft_overlap.addItem("")
        self.cb_stft_overlap.addItem("")
        self.cb_stft_overlap.addItem("")
        self.cb_stft_overlap.setObjectName(u"cb_stft_overlap")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cb_stft_overlap.sizePolicy().hasHeightForWidth())
        self.cb_stft_overlap.setSizePolicy(sizePolicy1)

        self.gridLayout_2.addWidget(self.cb_stft_overlap, 0, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)

        self.cb_stft_colormap = QComboBox(self.groupBox)
        self.cb_stft_colormap.addItem("")
        self.cb_stft_colormap.addItem("")
        self.cb_stft_colormap.addItem("")
        self.cb_stft_colormap.addItem("")
        self.cb_stft_colormap.addItem("")
        self.cb_stft_colormap.addItem("")
        self.cb_stft_colormap.setObjectName(u"cb_stft_colormap")

        self.gridLayout_2.addWidget(self.cb_stft_colormap, 3, 1, 1, 1)

        self.cb_stft_window = QComboBox(self.groupBox)
        self.cb_stft_window.addItem("")
        self.cb_stft_window.addItem("")
        self.cb_stft_window.addItem("")
        self.cb_stft_window.addItem("")
        self.cb_stft_window.addItem("")
        self.cb_stft_window.setObjectName(u"cb_stft_window")

        self.gridLayout_2.addWidget(self.cb_stft_window, 1, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)


        self.horizontalLayout.addWidget(self.groupBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.retranslateUi(Form)

        self.comboBox.setCurrentIndex(3)
        self.cb_stft_overlap.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pb_para_setting_panel_implement.setText(QCoreApplication.translate("Form", u"\u6267\u884c", None))
        self.pb_para_setting_panel_reset.setText(QCoreApplication.translate("Form", u"\u91cd\u7f6e", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"\u9891\u8c31\u63a7\u5236", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Form", u"128", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Form", u"256", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("Form", u"512", None))
        self.comboBox.setItemText(3, QCoreApplication.translate("Form", u"1024", None))
        self.comboBox.setItemText(4, QCoreApplication.translate("Form", u"2048", None))
        self.comboBox.setItemText(5, QCoreApplication.translate("Form", u"4096", None))
        self.comboBox.setItemText(6, QCoreApplication.translate("Form", u"9192", None))

        self.label_2.setText(QCoreApplication.translate("Form", u"\u7a97\u51fd\u6570(Window)", None))
        self.cb_stft_overlap.setItemText(0, QCoreApplication.translate("Form", u"0%", None))
        self.cb_stft_overlap.setItemText(1, QCoreApplication.translate("Form", u"25%", None))
        self.cb_stft_overlap.setItemText(2, QCoreApplication.translate("Form", u"50%", None))
        self.cb_stft_overlap.setItemText(3, QCoreApplication.translate("Form", u"75%", None))

        self.label_3.setText(QCoreApplication.translate("Form", u"NFFT", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u91cd\u53e0\u7387(Overlap)", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u9891\u8c31\u989c\u8272\u6620\u5c04(Colormap)", None))
        self.cb_stft_colormap.setItemText(0, QCoreApplication.translate("Form", u"inferno", None))
        self.cb_stft_colormap.setItemText(1, QCoreApplication.translate("Form", u"turbo", None))
        self.cb_stft_colormap.setItemText(2, QCoreApplication.translate("Form", u"plasma", None))
        self.cb_stft_colormap.setItemText(3, QCoreApplication.translate("Form", u"viridis", None))
        self.cb_stft_colormap.setItemText(4, QCoreApplication.translate("Form", u"cividis", None))
        self.cb_stft_colormap.setItemText(5, QCoreApplication.translate("Form", u"magma", None))

        self.cb_stft_window.setItemText(0, QCoreApplication.translate("Form", u"hann", None))
        self.cb_stft_window.setItemText(1, QCoreApplication.translate("Form", u"hamming", None))
        self.cb_stft_window.setItemText(2, QCoreApplication.translate("Form", u"triang", None))
        self.cb_stft_window.setItemText(3, QCoreApplication.translate("Form", u"boxcar", None))
        self.cb_stft_window.setItemText(4, QCoreApplication.translate("Form", u"blackman", None))

    # retranslateUi

