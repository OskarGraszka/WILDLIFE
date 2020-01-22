# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Wildlife
                                 A QGIS plugin
 This plugin helps to store wildlife observations.
                              -------------------
        begin                : 2017-11-11
        git sha              : $Format:%H$
        copyright            : (C) 2017 by PRYZMAP
        email                : biuro@pryzmap.pl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from builtins import object
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QObject, QDir, QDate, QTime, QDateTime#, QStyle
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMenu, QWidget, QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QVBoxLayout, QLabel
from qgis.PyQt.QtGui import QIcon, QPixmap, QPalette, QBrush, QColor, QFont, QCursor
from qgis.core import QgsVectorLayer, QgsProject, QgsPalLayerSettings, QgsMarkerSymbol, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsFeature, QgsFeatureRequest, QgsMapLayer, QgsGeometry, QgsFeatureRequest, QgsPointXY, QgsVectorDataProvider, QgsPropertyCollection, QgsProperty, QgsVectorLayerSimpleLabeling
import qgis.utils
from qgis.gui import QgsMapToolEmitPoint
from qgis.PyQt import QtCore
from qgis.PyQt import QtGui
import time
import math
from distutils.dir_util import copy_tree
import zipfile
import sys
import unicodedata

# Initialize Qt resources from file resources.py
from . import resources

# Import the code for the DockWidget
from .Wildlife_dockwidget import WildlifeDockWidget
import os.path
import os


class Wildlife(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Wildlife_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&PRYZMAP')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Wildlife')
        self.toolbar.setObjectName(u'Wildlife')

        #print "** INITIALIZING Wildlife"

        self.pluginIsActive = False
        self.dockwidget = None
        self.dockwidget = WildlifeDockWidget()
        
#-------------------------------------------------------------------------------
        
        self.canvas = self.iface.mapCanvas()
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        self.chosenOne = None
        
        
        self.dockwidget.palette().setBrush(QPalette.Highlight,QBrush(QColor(137, 206, 0)))
        labelfont= QFont( "Segoe UI", 7, QFont.Bold)
        self.dockwidget.catalogLine.setFont(labelfont)
            
        global ToolMode
        ToolMode = 'None'
        
        self.dockwidget.siedlisko.setEditable(True)
        
        global layerFotopulapka
        layerFotopulapka = QgsVectorLayer()
        global layerObserwacja
        layerObserwacja = QgsVectorLayer()
        global layerObserwacjaID
        global layerFotopulapkaID
        layerObserwacjaID=-99
        layerFotopulapkaID=-99
        
        self.dockwidget.btn_image.clicked.connect(self.chooseImages)
        self.dockwidget.x_1.clicked.connect(self.removeImage)
        self.dockwidget.x_2.clicked.connect(self.removeImage)
        self.dockwidget.x_3.clicked.connect(self.removeImage)
        self.dockwidget.tryb_p.clicked.connect(self.setTrybPrzegladania)
        self.dockwidget.tryb_o.clicked.connect(self.setNowaObserwacja)
        self.dockwidget.edytuj.clicked.connect(self.setTrybEdycji)
        self.dockwidget.ustawienia.clicked.connect(self.setUstawienia)
        self.dockwidget.position.clicked.connect(self.PointingPosition)
        self.dockwidget.gpx.clicked.connect(self.PointingGPX)
        self.clickTool.canvasClicked.connect(self.handleMouseDown)
        self.dockwidget.setDatabase.clicked.connect(self.setDatabaseCatalog)
        self.dockwidget.backup.clicked.connect(self.setBackupCatalog)
        self.dockwidget.backup_rar.clicked.connect(self.setBackupZipCatalog)
        self.dockwidget.pushButton_4.clicked.connect(self.saveAttributes)
        self.dockwidget.pushButton_5.clicked.connect(self.setTrybPrzegladania)
        self.dockwidget.comboBox_2.activated.connect(self.ComboActivated)
        self.dockwidget.rodzaj_obs.currentIndexChanged.connect(self.RodzajValueChanged)
        self.dockwidget.fotopulapka.clicked.connect(self.DisplayObservations)
        self.dockwidget.pushButton.clicked.connect(self.ChangeGatunekStack)
        self.dockwidget.pushButton_2.clicked.connect(self.ChangeGatunekStack)
        self.dockwidget.pushButton_3.clicked.connect(self.ChangeGatunekStack)
        self.dockwidget.pushButton_6.clicked.connect(self.deleteFeature)
        self.dockwidget.image_1.mousePressEvent = self.display1
        self.dockwidget.image_2.mousePressEvent = self.display2
        self.dockwidget.image_3.mousePressEvent = self.display3
        
        global ActualViewIDAndLayer
        ActualViewIDAndLayer = [-99,None]
        global ActualFotoID
        ActualFotoID = -99
        
        global DataPath
        DataPath = os.path.normpath(os.path.join(self.plugin_dir,'WILDLIFE_database'))
        
        global CurrentCoords
        CurrentCoords=[]
        
        global openDir
        openDir = QDir(self.plugin_dir).root()

        global images_list
        images_list = []
        global image_objects_array

        image_objects_array=[[self.dockwidget.image_1,self.dockwidget.x_1], 
                       [self.dockwidget.image_2,self.dockwidget.x_2], 
                       [self.dockwidget.image_3,self.dockwidget.x_3]]
        
        global image_objects_lists
        image_objects_lists = list(zip(*image_objects_array))
        for x in image_objects_lists[1]:
            x.setHidden(True)
        for label in image_objects_lists[0]:
            label.setHidden(True)
            
        self.setUstawienia()
        self.setActive(False)
        self.activateEdits(False)
        
        self.dockwidget.dateEdit.setDate(self.datagodzina()[0])
        self.dockwidget.timeEdit.setDisplayFormat("HH:mm")
        self.dockwidget.timeEdit.setTime(self.datagodzina()[1])
        
        global ListOfChangedLabellings
        ListOfChangedLabellings=[]
        
    def datagodzina(self):
        year=int(time.strftime("%Y"))
        month=int(time.strftime("%m"))
        day=int(time.strftime("%d"))
        hour=int(time.strftime("%H"))
        minute=int(time.strftime("%M"))
        
        data=QDate(year,month,day)
        godzina=QTime(hour,minute)
        
        return (data,godzina)
#-------------------------------------------------------------------------------
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Wildlife', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToDatabaseMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Wildlife/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Wildlife'),
            callback=self.run,
            parent=self.iface.mainWindow())


    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING Wildlife"

        # disconnects
        QgsProject.instance().layerWillBeRemoved.disconnect(self.layerWillBeRemoved)
        boolean = False
        listOfLayers=[]
        global layerFotopulapka
        global layerObserwacja
        global ListOfChangedLabellings
        layers = QgsProject.instance().mapLayers()
        for name, layer in layers.items():
            if layer == layerObserwacja or layer == layerFotopulapka:
                boolean = True
                listOfLayers.append(layer.id())
        if boolean == True:
            reply = QMessageBox.question(self.iface.mainWindow(), 'Ustawianie bazy danych', u"Czy chcesz usunąć elementy bazy danych z legendy?", QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                QgsProject.instance().removeMapLayers(listOfLayers)
                global ActualFotoID
                global ActualViewIDAndLayer
                ActualViewIDAndLayer =[-99,None]
                ActualFotoID = -99
        #
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        for layer in QgsProject.instance().mapLayersByName(u'wskazana pozycja'):
            QgsProject.instance().removeMapLayer(layer.id())
        for change in ListOfChangedLabellings:
            if change[0] in self.canvas.layers() and change[1] is not None:
                change[0].setLabeling(QgsVectorLayerSimpleLabeling(change[1]))
                change[0].setLabelsEnabled(False)
                change[0].triggerRepaint()
        del ListOfChangedLabellings[:]
        self.canvas.refresh()
        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        #print "** UNLOAD Wildlife"
        
        self.dockwidget.close()

        for action in self.actions:
            self.iface.removePluginDatabaseMenu(
                self.tr(u'&PRYZMAP'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

            
        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING Wildlife"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = WildlifeDockWidget()
                QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u"<b>self.dockwidget == None</b>")
            

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            
            txt_path=os.path.normpath(os.path.join(self.plugin_dir,'last_database_dir.txt'))
            if os.path.isfile(txt_path):
                text_file = open(txt_path, "r")
                path=text_file.readline()
                if os.path.isdir(os.path.normpath(path)):
                    self.setDatabase(path)
                else:
                    self.setDatabase(DataPath,True)
            else:
                self.setDatabase(DataPath,True)
            QgsProject.instance().layerWillBeRemoved.connect(self.layerWillBeRemoved)
#---------------------------------------------------------------------------


    def display1(self,event):
        self.displayPreview(self.dockwidget.image_1)
    def display2(self,event):
        self.displayPreview(self.dockwidget.image_2)
    def display3(self,event):
        self.displayPreview(self.dockwidget.image_3)
        
    def displayPreview(self,label):
        pixmap = QPixmap()
        if label == self.dockwidget.image_1:
            pixmap=images_list[0]
        elif label == self.dockwidget.image_2:
            pixmap=images_list[1]
        elif label == self.dockwidget.image_3:
            pixmap=images_list[2]
        self.photoWindow = PhotoWindow(pixmap)
        
    def chooseImages(self):
        global openDir
        add_images, __= QFileDialog.getOpenFileNames(None,u'Wybierz zdjęcia',openDir.absolutePath(),"Obrazy (*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff)")
        if add_images:
            openDir=QDir(add_images[0])
            for image in add_images:
                pixmap = QPixmap(image)
                images_list.append(pixmap)
            del images_list[3:]
            self.redrawImages()
        
    def redrawImages(self):
        for image in image_objects_lists[0]:
            image.clear()
            image.setHidden(True)
        for x in image_objects_lists[1]:
            x.setHidden(True)
        for image in images_list:
            pozycja=images_list.index(image)
            image_objects_array[pozycja][0].setAlignment(Qt.AlignCenter)
            image_objects_array[pozycja][0].setHidden(False)
            image_objects_array[pozycja][0].setPixmap(image.scaled(image_objects_array[pozycja][0].size(),Qt.KeepAspectRatio, Qt.SmoothTransformation))
            image_objects_array[pozycja][1].setHidden(False)
        if len(images_list)>2:
            self.dockwidget.btn_image.setEnabled(False)
        else:
            self.dockwidget.btn_image.setEnabled(True)
    def removeImage(self):
        index=image_objects_lists[1].index(self.dockwidget.sender())
        del images_list[index]
        self.redrawImages()
        
    def RodzajValueChanged(self):
        global layerFotopulapka
        global layerObserwacja
        if self.dockwidget.rodzaj_obs.currentText()==u'Fotopułapka':
            self.dockwidget.comboBox_2.setVisible(False)
            self.dockwidget.fotopulapka.setVisible(True)
            self.dockwidget.fotopulapka.setEnabled(True)
            self.dockwidget.przyblizona.setCheckState(Qt.Unchecked)
            self.dockwidget.przyblizona.setEnabled(False)
            self.dockwidget.licznosc.setValue(0)
            self.dockwidget.licznosc.setEnabled(False)
            self.dockwidget.kierunek.setCurrentIndex(0)
            self.dockwidget.kierunek.setEnabled(False)
            self.dockwidget.checkBox_5.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox_5.setEnabled(False)
            self.dockwidget.checkBox.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox.setEnabled(False)
            self.dockwidget.checkBox_2.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox_2.setEnabled(False)
            self.dockwidget.checkBox_3.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox_3.setEnabled(False)
            self.dockwidget.checkBox_4.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox_4.setEnabled(False)
            self.dockwidget.gatunek.clear()
            self.dockwidget.gatunek.setEnabled(False)
            self.dockwidget.pushButton.setEnabled(False)
            global images_list
            images_list = []
            self.redrawImages()
            self.dockwidget.btn_image.setEnabled(False)
        else:
            self.dockwidget.comboBox_2.setVisible(True)
            self.dockwidget.fotopulapka.setVisible(False)
            self.dockwidget.btn_image.setEnabled(True)
            self.dockwidget.przyblizona.setEnabled(True)
            self.dockwidget.licznosc.setEnabled(True)
            self.dockwidget.kierunek.setEnabled(True)
            self.dockwidget.checkBox_5.setEnabled(True)
            self.dockwidget.checkBox.setEnabled(True)
            self.dockwidget.checkBox_2.setEnabled(True)
            self.dockwidget.checkBox_3.setEnabled(True)
            self.dockwidget.checkBox_4.setEnabled(True)
            self.dockwidget.pushButton.setEnabled(True)
            self.dockwidget.gatunek.clear()
            self.dockwidget.gatunek.setEnabled(True)
            
            if self.dockwidget.rodzaj_obs.currentText()==u'Ptak':
                self.setUniquePtakGatunekValues()
            if self.dockwidget.rodzaj_obs.currentText()==u'Ssak':
                self.setUniqueSsakGatunekValues()
            
        if self.dockwidget.rodzaj_obs.isEnabled():
            self.dockwidget.fotopulapka.setEnabled(False)
            
    def ChangeGatunekStack(self):
        if self.dockwidget.sender()==self.dockwidget.pushButton:
            self.dockwidget.stackedWidget.setCurrentIndex(1)
            self.dockwidget.lineShort.setText(u'Skrót')
            self.dockwidget.lineFullName.setText(u'Pełna nazwa')
        elif self.dockwidget.sender()==self.dockwidget.pushButton_2:
            self.dockwidget.stackedWidget.setCurrentIndex(0)
            short=u''
            full=u''
            if self.dockwidget.lineShort.text()!=u'Skrót': short=self.dockwidget.lineShort.text()[:20]
            if self.dockwidget.lineFullName.text()!=u'Pełna nazwa': full=self.dockwidget.lineFullName.text()[:54]
            if self.dockwidget.rodzaj_obs.currentText()==u'Ptak':
                self.setUniquePtakGatunekValues([short,full])
                self.dockwidget.gatunek.setCurrentIndex(self.setGatunekIndexAfterAddNew('ptak',short,full))
            if self.dockwidget.rodzaj_obs.currentText()==u'Ssak':
                self.setUniqueSsakGatunekValues([short,full])
                self.dockwidget.gatunek.setCurrentIndex(self.setGatunekIndexAfterAddNew('ssak',short,full))
        elif self.dockwidget.sender()==self.dockwidget.pushButton_3:
            self.dockwidget.stackedWidget.setCurrentIndex(0)
            
    def unikey(self,seq):
        result=seq
        if isinstance(seq, str):
            result=self.replacechars(seq)
        elif isinstance(seq, (list, tuple)):
            result=self.replacechars(seq[1])
        return result
        
    def replacechars(self,string):
        string=str(unicodedata.normalize('NFKD', string).encode('ascii','backslashreplace'))
        pairs=[[u'ą',u'a~'],[u'Ą',u'A~'],[u'ć',u'c~'],[u'Ć',u'C~'],[u'ę',u'e~'],[u'Ę',u'E~'],[u'ł',u'l~'],[u'Ł',u'L~'],[u'ń',u'n~'],[u'Ń',u'N~'],[u'ó',u'o~'],[u'Ó',u'O~'],[u'ś',u's~'],[u'Ś',u'S~'],[u'ź',u'z}'],[u'Ź',u'Z}'],[u'ż',u'z~'],[u'Ż',u'Z~']]
        for pair in pairs:
            old = str(unicodedata.normalize('NFKD', pair[0]).encode('ascii','backslashreplace'))
            new = str(unicodedata.normalize('NFKD', pair[1]).encode('ascii','backslashreplace'))
            string=string.replace(old,new)
        return string

    def setUniquePtakGatunekValues(self,addedValue = None):
        global layerObserwacja
        self.dockwidget.gatunek.clear()
        global ListOfBirdSpecies
        ListOfBirdSpecies=[]
        for feature in layerObserwacja.getFeatures():
            if feature.attribute('rodzaj') == u'ptak':
                ListOfBirdSpecies.append([feature.attribute('gat_skrot'),feature.attribute('gatunek')])
        if addedValue is not None:
            ListOfBirdSpecies.append([addedValue[0],addedValue[1]])
        mergeuniques=[]
        uniques=[]
        
        for species in ListOfBirdSpecies:
            if species[0]== None:
                species[0]=u''
            if species[1]== None:
                species[1]=u''
            if not species[0]+'|'+species[1] in mergeuniques:
                mergeuniques.append(species[0]+'|'+species[1])
                uniques.append([species[0],species[1]])
        ListOfBirdSpecies=sorted(uniques, key=self.unikey)
        for species in ListOfBirdSpecies:
            species.append(ListOfBirdSpecies.index(species))
            self.dockwidget.gatunek.addItem(species[0]+' | '+species[1])
            
    def setUniqueSsakGatunekValues(self,addedValue = None):
        global layerObserwacja
        self.dockwidget.gatunek.clear()
        global ListOfMammalSpecies
        ListOfMammalSpecies=[]
        for feature in layerObserwacja.getFeatures():
            if feature.attribute('rodzaj') == u'ssak':
                ListOfMammalSpecies.append([feature.attribute('gat_skrot'),feature.attribute('gatunek')])
        if addedValue is not None:
            ListOfMammalSpecies.append([addedValue[0],addedValue[1]])
        mergeuniques=[]
        uniques=[]
        
        for species in ListOfMammalSpecies:
            if species[0]== None:
                species[0]=u''
            if species[1]== None:
                species[1]=u''
            if not species[0]+'|'+species[1] in mergeuniques:
                mergeuniques.append(species[0]+'|'+species[1])
                uniques.append([species[0],species[1]])
        ListOfMammalSpecies=sorted(uniques, key=self.unikey)
        for species in ListOfMammalSpecies:
            species.append(ListOfMammalSpecies.index(species))
            self.dockwidget.gatunek.addItem(species[0]+' | '+species[1])
            
    def setUniqueSiedliskoValues(self):
        global layerFotopulapka
        global layerObserwacja
        self.dockwidget.siedlisko.clear()
        ListOfValues=[]
        for layer in (layerFotopulapka,layerObserwacja):
            for feature in layer.getFeatures():
                ListOfValues.append(feature.attribute('siedlisko'))
        ListOfValues=set(ListOfValues)
        ListOfValues=sorted(ListOfValues, key=self.unikey)
        for value in ListOfValues:
            if value != None: self.dockwidget.siedlisko.addItem(value)
            else: self.dockwidget.siedlisko.addItem('')
        
    def setGatunekIndexAfterAddNew(self,rodzaj,short,full):
        global ListOfMammalSpecies
        global ListOfBirdSpecies
        ListOfSpecies=[]
        if rodzaj=='ptak': ListOfSpecies=ListOfBirdSpecies
        elif rodzaj=='ssak': ListOfSpecies=ListOfMammalSpecies
        index=0
        for species in ListOfSpecies:
            if short==species[0] and full==species[1]:
                index=species[2]
        return index
        
    def setGatunekIndex(self,feature):
        rodzaj=feature.attribute('rodzaj')
        global ListOfMammalSpecies
        global ListOfBirdSpecies
        ListOfSpecies=[]
        if rodzaj=='ptak': ListOfSpecies=ListOfBirdSpecies
        elif rodzaj=='ssak': ListOfSpecies=ListOfMammalSpecies
        else: QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u"Błąd w atrybucie 'rodzaj'")
        index=0
        for species in ListOfSpecies:
            if feature.attribute('gat_skrot')==species[0] and feature.attribute('gatunek')==species[1]:
                index=species[2]
        return index
            
    def setSiedliskoIndex(self,feature):
        index=0
        for numb in range(0,self.dockwidget.siedlisko.count()):
            if self.dockwidget.siedlisko.itemText(numb)==feature.attribute('siedlisko'): index=numb
        return index
                
    def setTrybPrzegladania(self):
        global ActualViewIDAndLayer
        global DatabasePath
        global layerFotopulapka
        global layerObserwacja
        global tempLayer
        for layer in QgsProject.instance().mapLayersByName(u'wskazana pozycja'):
            QgsProject.instance().removeMapLayer(layer.id())
        self.displayAttributes(ActualViewIDAndLayer[0],ActualViewIDAndLayer[1])
        self.dockwidget.stack.setCurrentIndex(1)
        self.setActive(False)
        self.SetToolMode('View')
        if ActualViewIDAndLayer ==[-99,None]: self.dockwidget.edytuj.setEnabled(False)
        self.dockwidget.fotopulapka.setEnabled(False)
        self.dockwidget.pushButton_6.setEnabled(True)
        self.dockwidget.stackedWidget.setCurrentIndex(0)
        self.SetSymbology(DataPath)
    def setTrybEdycji(self):
        self.dockwidget.stack.setCurrentIndex(1)
        self.setActive(True)
        self.SetToolMode('None')
        self.dockwidget.rodzaj_obs.setEnabled(False)
        global editionVariant
        editionVariant='edycja'
        if ActualViewIDAndLayer[1] == layerFotopulapka: self.dockwidget.btn_image.setEnabled(False)
        else: self.dockwidget.btn_image.setEnabled(True)
        self.dockwidget.pushButton_6.setEnabled(True)
    def setNowaObserwacja(self):
        self.dockwidget.komunikat.setText(u'Wprowadź nową obserwację')
        global ActualViewIDAndLayer
        self.displayAttributes(-99,None)
        self.dockwidget.stack.setCurrentIndex(1)
        self.setActive(True)
        self.SetToolMode('None')
        self.setUniqueSiedliskoValues()
        self.dockwidget.rodzaj_obs.setEnabled(True)
        self.dockwidget.rodzaj_obs.setCurrentIndex(1)
        global editionVariant
        editionVariant='nowy'
        self.dockwidget.pushButton_6.setEnabled(False)
    def setUstawienia(self):
        self.dockwidget.komunikat.setText(u'Ustawienia bazy danych')
        self.dockwidget.stack.setCurrentIndex(0)
        self.SetToolMode('None')
    def setActive(self,value):
        self.dockwidget.groupBox_7.setEnabled(value)
        self.dockwidget.groupBox_6.setEnabled(value)
        self.dockwidget.groupBox_5.setEnabled(value)
        self.dockwidget.groupBox_8.setEnabled(value)
        self.dockwidget.groupBox_2.setEnabled(value)
        self.dockwidget.groupBox.setEnabled(value)
        self.dockwidget.groupBox_3.setEnabled(value)
        self.dockwidget.groupBox_4.setEnabled(value)
        self.dockwidget.groupBox_9.setEnabled(value)
        self.dockwidget.groupBox_10.setEnabled(value)
        self.dockwidget.gpx.setEnabled(value)
        self.dockwidget.edytuj.setEnabled(not value)
        self.dockwidget.x_1.setEnabled(value)
        self.dockwidget.x_2.setEnabled(value)
        self.dockwidget.x_3.setEnabled(value)
        self.dockwidget.comboBox_2.setEnabled(value)
        self.dockwidget.fotopulapka.setEnabled(not value)
        
    def SetToolMode(self, mode):
        global ToolMode
        global ListOfChangedLabellings
        if ToolMode=='None':
            if self.chosenOne: self.chosenOne.close()
        if ToolMode=='GPX':
            if self.chosenOne: self.chosenOne.close()
            self.dockwidget.gpx.setStyleSheet("background-color: rgb(240, 240, 240);")
            for change in ListOfChangedLabellings:
                if change[0] in self.canvas.layers() and change[1] is not None:
                    change[0].setLabeling(QgsVectorLayerSimpleLabeling(change[1]))
                    change[0].setLabelsEnabled(False)
                    change[0].triggerRepaint()
            del ListOfChangedLabellings[:]
            self.canvas.refresh()
        elif ToolMode=='GetPos':
            if self.chosenOne: self.chosenOne.close()
            self.dockwidget.position.setStyleSheet('background-color: rgb(240, 240, 240);')
        elif ToolMode=='View':
            if self.chosenOne: self.chosenOne.close()
            self.dockwidget.tryb_p.setStyleSheet('background-color: rgb(240, 240, 240);')
        elif ToolMode=='ChooseFoto':
            self.dockwidget.comboBox_2.setStyleSheet('background-color: rgb(240, 240, 240);')
        if mode=='None':
            self.SetCursorActive(False)
            self.canvas.unsetMapTool(self.clickTool)
            ToolMode='None'
        elif mode =='GPX':
            if self.chosenOne: self.chosenOne.close()
            self.SetCursorActive(True)
            del ListOfChangedLabellings[:]
            for layer in self.canvas.layers():
                NamesList=[]
                if layer.type() != QgsMapLayer.VectorLayer:
                    continue
                if layer.storageType() != 'GPX':
                    continue
                if layer.geometryType() != 0:
                    continue
                for field in layer.fields():
                    NamesList.append(field.name())
                if 'name' in NamesList:
                    palyr = QgsPalLayerSettings()
                    props = QgsPropertyCollection()
                    layerlabel = QgsPalLayerSettings()
                    ListOfChangedLabellings.append([layer,QgsPalLayerSettings(layerlabel)])
                    palyr.enabled = True
                    palyr.drawLabels = True
                    palyr.fieldName = 'name'
                    palyr.placement = QgsPalLayerSettings.AroundPoint
                    props.setProperty(QgsPalLayerSettings.Size,QgsProperty.fromExpression('7.0'))
                    props.setProperty(QgsPalLayerSettings.ShapeDraw ,QgsProperty.fromValue(True))
                    props.setProperty(QgsPalLayerSettings.ShapeFillColor ,QgsProperty.fromExpression('color_rgba(137, 206, 0,100)'))
                    props.setProperty(QgsPalLayerSettings.ShapeStrokeColor  ,QgsProperty.fromExpression('color_rgba(0,0,0,255)'))
                    props.setProperty(QgsPalLayerSettings.ShapeStrokeWidth ,QgsProperty.fromExpression('0.2'))
                    props.setProperty(QgsPalLayerSettings.ShapeSizeX ,QgsProperty.fromExpression('1.0'))
                    props.setProperty(QgsPalLayerSettings.LabelDistance ,QgsProperty.fromExpression('2.0'))
                    palyr.setDataDefinedProperties(props)
                    layer.setLabeling(QgsVectorLayerSimpleLabeling(palyr))
                    layer.setLabelsEnabled(True)
                    layer.triggerRepaint()
            self.canvas.setMapTool(self.clickTool)
            
            print('autoFillBackground() : '+ str(self.dockwidget.gpx.autoFillBackground()) )
            self.dockwidget.gpx.setStyleSheet('background-color: rgb(137, 206, 0);')
            print('autoFillBackground() : '+ str(self.dockwidget.gpx.autoFillBackground()) )
            print('button color: '+str(self.dockwidget.gpx.palette().button().color().name()))
            print('autoFillBackground() : '+ str(self.dockwidget.gpx.autoFillBackground()) )
            
            self.dockwidget.komunikat.setText(u'Wskaż obiekt na warstwie GPX')
            for layer in QgsProject.instance().mapLayersByName(u'wskazana pozycja'):
                QgsProject.instance().removeMapLayer(layer.id())
            ToolMode='GPX'
        elif mode =='GetPos':
            if self.chosenOne: self.chosenOne.close()
            self.SetCursorActive(True)
            self.canvas.setMapTool(self.clickTool)
            self.dockwidget.position.setStyleSheet('background-color: rgb(137, 206, 0);')
            self.dockwidget.komunikat.setText(u'Wskaż pozycję na mapie')
            ToolMode='GetPos'
        elif mode =='View':
            if self.chosenOne: self.chosenOne.close()
            self.SetCursorActive(True)
            self.canvas.setMapTool(self.clickTool)
            self.dockwidget.tryb_p.setStyleSheet('background-color: rgb(137, 206, 0);')
            self.dockwidget.komunikat.setText(u'Wskaż obserwację lub fotopułapkę na mapie')
            ToolMode='View'
        elif mode =='ChooseFoto':
            self.SetCursorActive(True)
            self.canvas.setMapTool(self.clickTool)
            self.dockwidget.comboBox_2.setStyleSheet('background-color: rgb(137, 206, 0);')
            self.dockwidget.comboBox_2.setCurrentIndex(2)
            self.dockwidget.komunikat.setText(u'Wskaż fotopułapkę na mapie')
            ToolMode='ChooseFoto'
        self.dockwidget.gpx.setAutoFillBackground(True)
        self.dockwidget.position.setAutoFillBackground(True)
        self.dockwidget.tryb_p.setAutoFillBackground(True)
        self.dockwidget.comboBox_2.setAutoFillBackground(True)
    def SetCursorActive(self,bool):
        self.dockwidget.cursor.setEnabled(bool)
        if bool == True:
            self.dockwidget.cursor.setToolTip('Aktywne narzędzie mapowe')
        elif bool == False:
            self.dockwidget.cursor.setToolTip('Narzędzie mapowe nieaktywne')
    def PointingGPX(self):
        global ToolMode
        if ToolMode == 'GPX':
            self.SetToolMode('None')
        else:
            self.SetToolMode('GPX')
        self.canvas.refresh()
        
    def PointingPosition(self):
        global ToolMode
        if ToolMode=='GetPos':
            self.SetToolMode('None')
        else:
            self.SetToolMode('GetPos')

    def handleMouseDown(self, mouseEvent):
        layerData=[]
        global CurrentCoords
        global ToolMode
        global tempLayer
        global layerFotopulapka
        global layerObserwacja
        if ToolMode == 'GPX':
            for layer in self.canvas.layers():
                if layer.type() != QgsMapLayer.VectorLayer:
                    continue
                if layer.geometryType() != 0:
                    continue
                if layer.storageType() != 'GPX':
                    continue
                if layer.featureCount() == 0:
                    continue
                layer.removeSelection()

                shortestDistance = float("inf")
                closestFeatureId = -1
                for f in layer.getFeatures():
                    if f.geometry()==None:
                        continue
                    point = self.toCanvasCoordinates(layer,f.geometry().asPoint())
                    dist = math.sqrt((point.x()-mouseEvent.x())**2+(point.y()-mouseEvent.y())**2)
                    if dist < shortestDistance:
                        shortestDistance = dist
                        closestFeatureId = f.id()
                info = (layer, closestFeatureId, shortestDistance)
                pixelrange=20
                if shortestDistance <= self.iface.mapCanvas().mapUnitsPerPixel()*pixelrange:
                    layerData.append(info)

            if not len(layerData) > 0:
                # Looks like no vector layers were found
                self.dockwidget.komunikat.setText(u'Nie wskazano punktu na warstwie GPX')
            else:
                # Sort the layer information by shortest distance
                layerData.sort( key=lambda element: element[2] )
                # Select the closest feature
                layerWithClosestFeature, closestFeatureId, shortestDistance = layerData[0]
                layerWithClosestFeature.select( closestFeatureId )
                
                fields=layerWithClosestFeature.fields()
                for field in fields:
                    if field.name() =='name' and field.typeName()=='String':
                        self.dockwidget.opis.setText('Nazwa w GPX: '+layerWithClosestFeature.selectedFeatures()[0].attribute('name'))
                    if field.name() =='time' and field.typeName()=='DateTime':
                        data=layerWithClosestFeature.selectedFeatures()[0].attribute('time')
                        self.dockwidget.dateEdit.setDate(data.date())
                        self.dockwidget.timeEdit.setTime(data.time())
        
                iterator=layerWithClosestFeature.dataProvider().getFeatures(QgsFeatureRequest(closestFeatureId))
                for feature in iterator:
                    wspolrzedne=self.MakeWGSCoordsString(feature,layerWithClosestFeature)
                    CurrentCoords = [wspolrzedne[1],wspolrzedne[2]]
                    self.dockwidget.coords.setText(wspolrzedne[0])
                self.dockwidget.komunikat.setText(u'Pobrano dane ze wskazanego obiektu')
            self.SetToolMode('None')
        elif ToolMode == 'GetPos':
            CurrentCoords = [self.toWGSCoordinatesString(mouseEvent)[1],self.toWGSCoordinatesString(mouseEvent)[2]]
            self.dockwidget.coords.setText(self.toWGSCoordinatesString(mouseEvent)[0])
            for layer in QgsProject.instance().mapLayersByName(u'wskazana pozycja'):
                QgsProject.instance().removeMapLayer(layer.id())
            tempLayer=QgsVectorLayer("point?crs=epsg:4326&field=id:integer", u'wskazana pozycja' , "memory")
            symbol = QgsMarkerSymbol.createSimple({u'name': u'cross', u'color': u'red',u'outline_color': u'red',u'size': u'3'})
            tempLayer.renderer().setSymbol(symbol)
            tempLayer.startEditing()
            for feat in tempLayer.getFeatures():
                tempLayer.deleteFeature(feat.id())
            tempLayer.commitChanges()
            tempLayer.setReadOnly()
            point = QgsGeometry.fromPointXY(QgsPointXY(CurrentCoords[0],CurrentCoords[1]))
            caps = tempLayer.dataProvider().capabilities()
            if caps and QgsVectorDataProvider.AddFeatures: feat = QgsFeature(tempLayer.fields())
            feat.setGeometry(point)
            tempLayer.dataProvider().addFeatures([feat])
            QgsProject.instance().addMapLayer(tempLayer)
            self.dockwidget.komunikat.setText(u'Pobrano współrzędne')
            self.SetToolMode('None')
        elif ToolMode == 'View':
            self.dockwidget.komunikat.setText(u'Tryb przeglądania obserwacji')
            globallayerData=[]
            for layer in self.canvas.layers():
                if layer!=layerObserwacja and layer!=layerFotopulapka:
                    continue
                layer.removeSelection()
                shortestDistance = float("inf")
                closestFeatureId = -1
                pixelrange=20
                for f in layer.getFeatures():
                    if f.geometry()==None:
                        continue
                    point = self.toCanvasCoordinates(layer,f.geometry().asPoint())
                    dist = math.sqrt((point.x()-mouseEvent.x())**2+(point.y()-mouseEvent.y())**2)
                    if dist <= self.iface.mapCanvas().mapUnitsPerPixel()*pixelrange:
                        globalinfo = (layer, f.id())
                        globallayerData.append(globalinfo)
                        if dist < shortestDistance:
                            shortestDistance = dist
                            closestFeatureId = f.id()
                            info = (layer, closestFeatureId, shortestDistance)
                            layerData.append(info)
            if not len(layerData) > 0:
                self.dockwidget.komunikat.setText(u'Nie wskazano obserwacji')
            elif len(layerData) == 1:
                layerData.sort( key=lambda element: element[2] )
                layerWithClosestFeature, closestFeatureId, shortestDistance = layerData[0]
                self.displayAttributes(closestFeatureId,layerWithClosestFeature)
            else:
                ListToChoose = []
                for feature in globallayerData:
                    feat = QgsFeature()
                    for i in feature[0].dataProvider().getFeatures(QgsFeatureRequest(feature[1])):
                        feat=i
                    ListToChoose.append([feat,feature[0]])
                self.chosenOne=ChooseFeatureWindow(self,ListToChoose)
        elif ToolMode == 'ChooseFoto':
            self.dockwidget.komunikat.setText(u'Wskaż fotopułapkę na mapie')
            globallayerData=[]
            for layer in self.canvas.layers():
                if layer!=layerFotopulapka:
                    continue
                layer.removeSelection()
                shortestDistance = float("inf")
                closestFeatureId = -1
                pixelrange=20
                for f in layer.getFeatures():
                    if f.geometry()==None:
                        continue
                    point = self.toCanvasCoordinates(layer,f.geometry().asPoint())
                    dist = math.sqrt((point.x()-mouseEvent.x())**2+(point.y()-mouseEvent.y())**2)
                    if dist <= self.iface.mapCanvas().mapUnitsPerPixel()*pixelrange:
                        globalinfo = (layer, f.id())
                        globallayerData.append(globalinfo)
                        if dist < shortestDistance:
                            shortestDistance = dist
                            closestFeatureId = f.id()
                            info = (layer, closestFeatureId, shortestDistance)
                            layerData.append(info)
            if not len(layerData) > 0:
                self.dockwidget.komunikat.setText(u'Nie wskazano fotopułapki')
                self.dockwidget.comboBox_2.setCurrentIndex(0)
            elif len(layerData) == 1:
                layerData.sort( key=lambda element: element[2] )
                layerWithClosestFeature, closestFeatureId, shortestDistance = layerData[0]
                self.SetFotopulapka(closestFeatureId)
            else:
                ListToChoose = []
                for feature in globallayerData:
                    feat = QgsFeature()
                    for i in feature[0].dataProvider().getFeatures(QgsFeatureRequest(feature[1])):
                        feat=i
                    ListToChoose.append([feat,feature[0]])
                self.chosenOne=ChooseFeatureWindow(self,ListToChoose,True)
            global ActualFotoID
            self.SetToolMode('None')
        self.canvas.refresh()
    def MakeWGSCoordsString(self, feature, layer):
        if feature.geometry()==None:
            x,y=None,None
            string =u'Nieprawidłowe wspólrzędne'
            tablica=[string,x,y]
        else:
            x=feature.geometry().asPoint().x()
            y=feature.geometry().asPoint().y()
            if layer.crs() != QgsCoordinateReferenceSystem(4326):
                TransformationToWGS=QgsCoordinateTransform(canvasCRS,layerCRS,QgsProject.instance())
                point=TransformationToWGS.transform(x,y)
                x=point.x()
                y=point.y()
            if x > 0:
                lon=' E'
            elif x == 0:
                lon=''
            else:
                lon=' W'
            if y > 0:
                lat=' N'
            elif y == 0:
                lat=''
            else:
                lat=' S'
            print(lat)
            string = str(int(x))+u'\xb0'+str(int(math.modf(int(math.modf(x)[0]*60))[1]))+"'"+str(math.modf(math.modf(x)[0]*60)[0]*60)[0:4]+"''"+lon+'  '+str(int(y))+u'\xb0'+str(int(math.modf(int(math.modf(y)[0]*60))[1]))+"'"+str(math.modf(math.modf(y)[0]*60)[0]*60)[0:4]+"''"+lat
            tablica=[string,x,y]
        return tablica
        
    def toWGSCoordinatesString(self,position):
        try:
            canvasCRS = self.canvas.mapSettings().destinationCrs()
        except:
            canvasCRS = self.canvas.mapRenderer().destinationCrs()
        layerCRS=QgsCoordinateReferenceSystem(4326)
        TransformationToLayerCrs=QgsCoordinateTransform(canvasCRS,layerCRS,QgsProject.instance())
        point=TransformationToLayerCrs.transform(position.x(),position.y())
        x,y=point.x(),point.y()
        if x > 0:
            lon=' E'
        elif x == 0:
            lon=''
        else:
            lon=' W'
        if y > 0:
            lat=' N'
        elif y == 0:
            lat=''
        else:
            lat=' S'
        x2=abs(x)
        y2=abs(y)
        string = str(int(x2))+u'\xb0'+str(int(math.modf(int(math.modf(x2)[0]*60))[1]))+"'"+str(math.modf(math.modf(x2)[0]*60)[0]*60)[0:4]+"''"+lon+'  '+str(int(y2))+u'\xb0'+str(int(math.modf(int(math.modf(y2)[0]*60))[1]))+"'"+str(math.modf(math.modf(y2)[0]*60)[0]*60)[0:4]+"''"+lat
        tablica=[string,x,y]
        return tablica
        
    def toCanvasCoordinates(self, layer, position):
        try:
            canvasCRS = self.canvas.mapSettings().destinationCrs()
        except:
            canvasCRS = self.canvas.mapRenderer().destinationCrs()
        layerCRS=layer.crs()
        TransformationToCanvasCrs=QgsCoordinateTransform(layerCRS,canvasCRS,QgsProject.instance())
        point=TransformationToCanvasCrs.transform(position.x(),position.y())
        return point
        
    def setDatabaseCatalog(self):
        global DataPath
        if os.path.isdir(DataPath):
            default=os.path.split(DataPath)[0]
        elif os.path.isdir(self.dockwidget.catalogLine.text()):
            default=os.path.split(self.dockwidget.catalogLine.text())[0]
        elif os.path.isdir(os.path.normpath(os.path.join(self.plugin_dir,'WILDLIFE_database'))):
            default=self.plugin_dir
        else:
            default=os.path.normpath(QDir(self.plugin_dir).root().path())
        reply = QMessageBox.question(self.iface.mainWindow(), 'Ustawianie bazy danych', u"Na pewno chcesz ustawić nową bazę danych?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            global ActualViewIDAndLayer
            ActualViewIDAndLayer = [-99,None]
            global ActualFotoID
            ActualFotoID = -99
            catalog = QFileDialog.getExistingDirectory(None,u"Wskaż katalog 'WILDLIFE_database'",default,QFileDialog.ShowDirsOnly)
            self.setDatabase(catalog,True)
        
    def setBackupCatalog(self):
        catalog = QFileDialog.getExistingDirectory(None,u"Wskaż katalog docelowy",QDir(self.plugin_dir).root().path(),QFileDialog.ShowDirsOnly)
        if catalog is not None:
            withsufix='Wildlife_backup_'+self.datagodzina()[0].toString('yyyy_M_d')+'_'+self.datagodzina()[1].toString('h_mm')
            subcatalog=os.path.join(catalog,withsufix)
            os.mkdir(subcatalog)
            subcatalog=os.path.join(subcatalog,'WILDLIFE_database')
            global DataPath
            copy_tree(DataPath,subcatalog)
            
    def setBackupZipCatalog(self):
        catalog = QFileDialog.getExistingDirectory(None,u"Wskaż katalog docelowy",QDir(self.plugin_dir).root().path(),QFileDialog.ShowDirsOnly)
        if catalog is not None:
            zipname='Wildlife_backup_'+self.datagodzina()[0].toString('yyyy_M_d')+'_'+self.datagodzina()[1].toString('h_mm')+'.zip'
            rarpath=os.path.join(catalog,zipname)
            global DataPath
            relroot = os.path.abspath(os.path.join(DataPath, os.pardir))
            with zipfile.ZipFile(rarpath, "w", zipfile.ZIP_DEFLATED) as zip:
                for root, dirs, files in os.walk(DataPath):
                    # add directory (needed for empty dirs)
                    zip.write(root, os.path.relpath(root, relroot))
                    for file in files:
                        filename = os.path.join(root, file)
                        if os.path.isfile(filename): # regular files only
                            arcname = os.path.join(os.path.relpath(root, relroot), file)
                            zip.write(filename, arcname)
        
    def setDatabase(self, databasePath ,removePrevious = False):
        result=False
        if databasePath is None:
            databasePath = os.path.normpath(os.path.join(self.plugin_dir,'WILDLIFE_database'))
        if not os.path.isdir(databasePath) or os.path.split(databasePath)[1]!='WILDLIFE_database':
            self.setCatalogReport('katalogu','WILDLIFE_database')
        elif not os.path.isdir(os.path.join(databasePath,'shp')):
            self.setCatalogReport('katalogu','WILDLIFE_database\shp')
        elif not os.path.isdir(os.path.join(databasePath,'photos')):
            self.setCatalogReport('katalogu','WILDLIFE_database\photos')
        elif not os.path.isfile(os.path.join(databasePath,'shp','obserwacja.shp')):
            self.setCatalogReport('pliku','obserwacja.shp')
        elif not os.path.isfile(os.path.join(databasePath,'shp','fotopulapka.shp')):
            self.setCatalogReport('pliku','fotopulapka.shp')
        else:
            global DataPath
            PreviousDataPath = DataPath
            DataPath = databasePath
            remove= False
            boolean = False
            listOfLayers=[]
            global layerFotopulapka
            global layerObserwacja
            layers = QgsProject.instance().mapLayers()
            for name, layer in layers.items():
                if layer.name() == u'Obserwacja' or layer.name() == u'Fotopułapka':
                    boolean = True
            if removePrevious and boolean:
                reply = QMessageBox.question(self.iface.mainWindow(), 'Ustawianie bazy danych', u"Czy chcesz usunąć elementy poprzedniej bazy z legendy?", QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    remove= True
            self.addShapefiles(PreviousDataPath,DataPath,remove)
            self.dockwidget.komunikat.setText(u'Ustawiono bazę danych')
            text_file_path=os.path.normpath(os.path.join(self.plugin_dir,'last_database_dir.txt'))
            text_file = open(text_file_path, "w")
            text_file.write("%s" % DataPath)
            text_file.close()
            result=True
            self.dockwidget.catalogLine.setText(DataPath)
        return result
        
    def addShapefiles(self,PreviousDataPath,DatabasePath,Remove):
        if Remove:
            list=[]
            if os.path.isdir(PreviousDataPath):
                for layer in self.canvas.layers():
                    if layer.type() != QgsMapLayer.VectorLayer:
                        continue
                    if layer.geometryType() != 0:
                        continue
                    if layer.storageType() != 'ESRI Shapefile':
                        continue
                    if self.path_is_parent(PreviousDataPath,layer.source()):
                        list.append(layer.id())
            QgsProject.instance().removeMapLayers(list)
        layers = QgsProject.instance().mapLayers()
        fotopulapkaPath=os.path.join(DatabasePath,'shp','fotopulapka.shp')
        global layerFotopulapka
        layerFotopulapka = QgsVectorLayer(fotopulapkaPath, u'Fotopułapka', "ogr")
        global layerFotopulapkaID
        layerFotopulapkaID=layerFotopulapka.id()
        if not layerFotopulapka or not layerFotopulapka.isValid():
            QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u'<b>Błąd przy ładowaniu warstwy "Fotopułapka"</b>')
        else:
            add=True
            for name, layer in layers.items():
                if layer == layerFotopulapka:
                    add = False
                if layer != layerFotopulapka and layer.source() == layerFotopulapka.source() and Remove:
                    QgsProject.instance().removeMapLayers([layer.id()])
            if add:
                QgsProject.instance().addMapLayer(layerFotopulapka)
                self.activateEdits(True)
        obserwacjaPath=os.path.join(DatabasePath,'shp','obserwacja.shp')
        global layerObserwacja
        layerObserwacja = QgsVectorLayer(obserwacjaPath, u'Obserwacja', "ogr")
        global layerObserwacjaID
        layerObserwacjaID=layerObserwacja.id()
        if not layerObserwacja or not layerObserwacja.isValid():
            QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u'<b>Błąd przy ładowaniu warstwy "Obserwacja"</b>')
        else:
            add=True
            for name, layer in layers.items():
                if layer == layerObserwacja:
                    add = False
                if layer != layerObserwacja and layer.source() == layerObserwacja.source() and Remove:
                    QgsProject.instance().removeMapLayers([layer.id()])
            if add:
                QgsProject.instance().addMapLayer(layerObserwacja)
                self.activateEdits(True)
        self.SetSymbology(DatabasePath)
    def SetSymbology(self,DatabasePath):
        global layerObserwacja
        global layerFotopulapka
        palyr = QgsPalLayerSettings()
        props = QgsPropertyCollection()
        palyr.enabled = True
        palyr.drawLabels = True
        palyr.placement = QgsPalLayerSettings.AroundPoint
        props.setProperty(QgsPalLayerSettings.Family ,QgsProperty.fromExpression("'Segoe UI'"))
        props.setProperty(QgsPalLayerSettings.ShapeStrokeWidth ,QgsProperty.fromExpression('0.1'))
        palyr.fieldName = "to_string(%s)+%s" % ('"licznosc"','"gat_skrot"')
        palyr.isExpression = True
        props.setProperty(QgsPalLayerSettings.Size,QgsProperty.fromExpression('7.0'))
        props.setProperty(QgsPalLayerSettings.LabelDistance ,QgsProperty.fromExpression('0.7'))
        props.setProperty(QgsPalLayerSettings.ShapeDraw ,QgsProperty.fromValue(True))
        shape="if( %s  IS  'ptak' ,'circle','square')" % ('"rodzaj"')
        props.setProperty(QgsPalLayerSettings.ShapeKind,QgsProperty.fromExpression(shape))
        color="CASE WHEN  %s = 0  THEN 'white' WHEN  %s = 1 THEN 'orange' END" % ('"drapiez"','"drapiez"')
        props.setProperty(QgsPalLayerSettings.ShapeFillColor ,QgsProperty.fromExpression(color))
        props.setProperty(QgsPalLayerSettings.ShapeOpacity, QgsProperty.fromExpression('60'))
        props.setProperty(QgsPalLayerSettings.IsObstacle,QgsProperty.fromValue(True))
        props.setProperty(QgsPalLayerSettings.ScaleVisibility ,QgsProperty.fromValue(True))
        props.setProperty(QgsPalLayerSettings.MinimumScale,QgsProperty.fromExpression('500000'))
        props.setProperty(QgsPalLayerSettings.ObstacleFactor,QgsProperty.fromExpression('10.0'))
        palyr.setDataDefinedProperties(props)
        layerObserwacja.setLabeling(QgsVectorLayerSimpleLabeling(palyr))
        layerObserwacja.setLabelsEnabled(True)
        layerObserwacja.triggerRepaint()
        prefix=''
        #W QGIS2 wymagał tego tylko Mac
        #if sys.platform == "darwin":
        prefix='file:///'
        fothtml=u'''
<html>
<body style="height:30px;">
<table style="height:30px;">
<tr><td align="center" BGCOLOR="#BDBDBD"  style="border-width:1px;border-color:black;border-style:solid;"><font size="1,2"><b>[% "opis" %]</b></td></tr>
<tr><td align="center"  style="border-width:1px;border-color:black;border-style:solid;"><font size="1,2"><i>[% "siedlisko" %]</i></td></tr>
<tr><td align="center"  style="border-width:1px;border-color:black;border-style:solid;"><font size="1,2"><i>[% "datetime" %]</i></td></tr>
</table>
</body>
</html>'''
        layerFotopulapka.setMapTipTemplate(fothtml)
        path=os.path.join(DataPath,'photos')
        obshtml=u'''
<html style="height:120px;">
<base href="'''+prefix+path+'''\\">
<body>
<table style="height:120px;">
<tr>
<td  rowspan="2" BGCOLOR="#BDBDBD" align="center"  style="border-width:1px;border-color:black;border-style:solid; white-space:nowrap;"><font size="3" ><b>[% "licznosc" %][% "gat_skrot" %]</b></td>
<td  align="center"  style="border-width:1px;border-color:black;border-style:solid; white-space:nowrap;"><font size="0,8" ><b>[% if( "obserwacja" =1,'OBSERWACJA','------')%]</td>
<td  align="center"  style="border-width:1px;border-color:black;border-style:solid; white-space:nowrap;"><font size="0,8" ><b>[% if( "tropy" =1,'TROPY','------')%]</td>
<td rowspan="5" align="center"  style="border-width:1px;border-color:black;border-style:solid;"><font size="1,2" ><img src="[% if( "zdj_1" IS NULL ,'default.png',"zdj_1")%]" style="height:120px;"></td>
<td rowspan="5" align="center"  style="border-width:1px;border-color:black;border-style:solid;"><font size="1,2" ><img src="[% if( "zdj_2" IS NULL ,'default.png',"zdj_2")%]" style="height:120px;"></td>
<td rowspan="5" align="center"  style="border-width:1px;border-color:black;border-style:solid;"><font size="1,2" ><img src="[% if( "zdj_3" IS NULL ,'default.png',"zdj_3")%]" style="height:120px;"></td>
</tr>
<tr>
<td  align="center"  style="border-width:1px;border-color:black;border-style:solid;white-space:nowrap;"><font size="0,8" ><b>[% if( "odchody" =1,'ODCHODY','------')%]</td>
<td  align="center"  style="border-width:1px;border-color:black;border-style:solid; white-space:nowrap;"><font size="0,8" ><b>[% if( "inne" =1,'INNE','------')%]</td>
</tr>
<tr>
<td  align="center"  style="border-width:1px;border-color:black;border-style:solid; white-space:nowrap;"><font size="1,2" ><i>[% "gatunek" %]</i></td>
<td  align="center"  style="border-width:1px;border-color:black;border-style:solid; white-space:nowrap;"><font size="1,2" >[% if( "przyb" =1,'ok. '+to_string("licznosc") ,"licznosc") %]</td>
<td  align="center"  style="border-width:1px;border-color:black;border-style:solid; white-space:nowrap;"><font size="1,2" >[% if( "kierunek" =0,'----',"kierunek" )%]</td>
</tr>
<tr>
<td colspan="3"  align="center"  style="border-width:1px;border-color:black;border-style:solid;"><font size="1,2" >[% if( "opis" IS NULL,'------------',"opis" )%]</td>
</tr>
<tr>
<td  align="center"  style="border-width:1px;border-color:black;border-style:solid;"><font size="1,2" ><i>[% "siedlisko" %]</i></td>
<td colspan="2"  align="center"  style="border-width:1px;border-color:black;border-style:solid;"><font size="1,2" ><i>[% "datetime" %]</i></td>
</tr>
</table>
</body>
</html>
'''        
        layerObserwacja.setMapTipTemplate('')
        layerObserwacja.setMapTipTemplate(obshtml)
        
        obs_symbol = QgsMarkerSymbol.createSimple({u'name': u'circle', u'color': u'white',u'outline_color': u'black',u'size': u'1.4'})
        layerObserwacja.renderer().setSymbol(obs_symbol)
        self.iface.layerTreeView().refreshLayerSymbology(layerObserwacja.id())
        fot_symbol = QgsMarkerSymbol.createSimple({u'name': u'square', u'color': u'orange',u'outline_color': u'black',u'size': u'1.4'})
        layerFotopulapka.renderer().setSymbol(fot_symbol)
        self.iface.layerTreeView().refreshLayerSymbology(layerFotopulapka.id())
        self.canvas.refresh()
    def path_is_parent(self,directory, file):  
        directory = os.path.join(os.path.realpath(directory), '')
        file = os.path.realpath(file)
        return os.path.commonprefix([file, directory]) == directory
        
    def setCatalogReport(self,kind,name):
        self.dockwidget.komunikat.setText(u'Ustawienie bazy danych nie powiodło się')
        QMessageBox.warning( self.iface.mainWindow(),u"Błąd!", u"Nie znaleziono %s <i>%s</i>. Baza danych nie zostanie ustawiona." % (kind,name))
        
    def layerWillBeRemoved(self,lid):
        global layerObserwacjaID
        global layerFotopulapkaID
        if layerObserwacjaID == lid or layerFotopulapkaID == lid:
            self.activateEdits(False)
            global ActualViewIDAndLayer
            ActualViewIDAndLayer = [-99,None]
            global ActualFotoID
            ActualFotoID = -99
            self.dockwidget.komunikat.setText(u'Usunięto element bazy danych!')
            self.dockwidget.catalogLine.setText(u'')
            
    def activateEdits(self,boolean):
        if not boolean: self.setUstawienia()
        self.dockwidget.tryb_p.setEnabled(boolean)
        self.dockwidget.tryb_o.setEnabled(boolean)
        self.dockwidget.backup.setEnabled(boolean)
        self.dockwidget.backup_rar.setEnabled(boolean)
        
#----------------------------------------------------------------------------------------------------

    def saveAttributes(self):
        global editionVariant
        global ActualViewIDAndLayer
        global ActualFotoID
        global layerFotopulapka
        global layerObserwacja
        global CurrentCoords
        feat=QgsFeature()
        TempActualViewIDAndLayer=[]
        TempActualViewIDAndLayer.append(ActualViewIDAndLayer[0])
        TempActualViewIDAndLayer.append(ActualViewIDAndLayer[1])

        if editionVariant=='nowy':
            if self.dockwidget.rodzaj_obs.currentText()==u'Ssak' or self.dockwidget.rodzaj_obs.currentText()==u'Ptak':
                caps = layerObserwacja.dataProvider().capabilities()
                if caps and QgsVectorDataProvider.AddFeatures: feat = QgsFeature(layerObserwacja.fields())
                TempActualViewIDAndLayer[0]=feat.id()
                TempActualViewIDAndLayer[1]=layerObserwacja
            elif self.dockwidget.rodzaj_obs.currentText()==u'Fotopułapka':
                caps = layerFotopulapka.dataProvider().capabilities()
                if caps and QgsVectorDataProvider.AddFeatures: feat = QgsFeature(layerFotopulapka.fields())
                TempActualViewIDAndLayer[0]=feat.id()
                TempActualViewIDAndLayer[1]=layerFotopulapka
        elif editionVariant=='edycja':
            TempActualViewIDAndLayer[1].startEditing()
            for f in TempActualViewIDAndLayer[1].getFeatures():
                if f.id()==TempActualViewIDAndLayer[0]: feat=f
        if CurrentCoords != [] and self.dockwidget.coords.text() != '':
                point = QgsGeometry.fromPointXY(QgsPointXY(CurrentCoords[0],CurrentCoords[1]))
                feat.setGeometry(QgsGeometry())
                feat.setGeometry(point)
        feat.setAttribute('siedlisko', u'%s' % self.dockwidget.siedlisko.currentText())
        opis=self.dockwidget.opis.toPlainText()
        feat.setAttribute('opis',u'%s' % (opis))
        
        datetime=QDateTime()
        datetime.setTime(self.dockwidget.timeEdit.time())
        datetime.setDate(self.dockwidget.dateEdit.date())
        feat.setAttribute('datetime',datetime.toString('yyyy-MM-dd hh:mm:ss'))
        
        if TempActualViewIDAndLayer[1] == layerObserwacja:
            global ListOfMammalSpecies
            global ListOfBirdSpecies
            if ActualFotoID !=-99 and self.dockwidget.comboBox_2.currentIndex() !=0: feat.setAttribute('id_fotop', ActualFotoID)
            else: feat.setAttribute('id_fotop',-1)
            SpeciesList=[]
            if self.dockwidget.rodzaj_obs.currentIndex()==1:
                feat.setAttribute('rodzaj','ssak')
                SpeciesList=ListOfMammalSpecies
            elif self.dockwidget.rodzaj_obs.currentIndex()==2:
                feat.setAttribute('rodzaj','ptak')
                SpeciesList=ListOfBirdSpecies
            if len(SpeciesList)>0:
                if self.dockwidget.gatunek.currentIndex()==SpeciesList[self.dockwidget.gatunek.currentIndex()][2]:
                    species=SpeciesList[self.dockwidget.gatunek.currentIndex()]
                    feat.setAttribute('gat_skrot',u'%s' % species[0])
                    feat.setAttribute('gatunek',u'%s' % species[1])
            else:
                feat.setAttribute('gat_skrot',u'')
                feat.setAttribute('gatunek',u'')
            feat.setAttribute('licznosc',self.dockwidget.licznosc.value())
            feat.setAttribute('kierunek',self.setKierunek(self.dockwidget.kierunek.currentIndex()))
            if self.dockwidget.przyblizona.isChecked(): feat.setAttribute('przyb',1)
            else: feat.setAttribute('przyb',0)
            if self.dockwidget.checkBox_5.isChecked(): feat.setAttribute('drapiez',1)
            else: feat.setAttribute('drapiez',0)
            if self.dockwidget.checkBox.isChecked(): feat.setAttribute('obserwacja',1)
            else: feat.setAttribute('obserwacja',0)
            if self.dockwidget.checkBox_2.isChecked(): feat.setAttribute('tropy',1)
            else: feat.setAttribute('tropy',0)
            if self.dockwidget.checkBox_3.isChecked(): feat.setAttribute('odchody',1)
            else: feat.setAttribute('odchody',0)
            if self.dockwidget.checkBox_4.isChecked(): feat.setAttribute('inne',1)
            else: feat.setAttribute('inne',0)
        if feat.geometry()==None or feat.geometry().isEmpty():
            QMessageBox.warning( self.iface.mainWindow(),u"Nie można zapisać obserwacji/fotopułapki", u"<b>Obiektowi nie przypisano żadnch współrzędnych!")

        elif QMessageBox.question(self.iface.mainWindow(), 'Zapis danych', u"Na pewno chcesz zapisać lub zmienić dane?", QMessageBox.Yes, QMessageBox.No)== QMessageBox.Yes:
            ActualViewIDAndLayer[0]=TempActualViewIDAndLayer[0]
            ActualViewIDAndLayer[1]=TempActualViewIDAndLayer[1]
            if editionVariant=='nowy':
                (result, newFeatures) = ActualViewIDAndLayer[1].dataProvider().addFeatures([feat])
                ActualViewIDAndLayer[1].startEditing()
                ActualViewIDAndLayer[0]= newFeatures[0].id()
                for f in ActualViewIDAndLayer[1].getFeatures():
                    if f.id()==ActualViewIDAndLayer[0]:
                        feat=f
            
            if ActualViewIDAndLayer[1] == layerObserwacja:
                piclist=('zdj_1','zdj_2','zdj_3')
                global images_list
                global DataPath
                for index in range(0,3):
                    name=feat.attribute(piclist[index])
                    path=os.path.join(DataPath,'photos',str(name))
                    if os.path.isfile(path): os.remove(path)
                    feat.setAttribute(piclist[index],'')
                    if len(images_list) > index:
                        name='obs_'+str(ActualViewIDAndLayer[0])+'_'+str(index+1)+'.JPG'
                        pathname=os.path.join(DataPath,'photos',name)
                        pixmap=images_list[index]
                        pixmap.save(pathname, 'jpg')
                        feat.setAttribute(piclist[index],name)
                TempActualViewIDAndLayer[1].updateFeature(feat)

            if editionVariant=='edycja':
                TempActualViewIDAndLayer[1].updateFeature(feat)
            TempActualViewIDAndLayer[1].commitChanges()
            self.setTrybPrzegladania()
        
        TempActualViewIDAndLayer[1].rollBack()
        self.canvas.refresh()
                
    def ComboActivated(self,index):
        global ToolMode
        if index == 0:
             self.SetToolMode('None')
        elif index == 1:
            self.SetToolMode('None')
            global layerFotopulapka
            ListToChoose=[]
            for feature in layerFotopulapka.getFeatures():
                ListToChoose.append([feature,layerFotopulapka])
            self.chosenOne=ChooseFeatureWindow(self,ListToChoose,True)
            self.dockwidget.comboBox_2.setCurrentIndex(0)
        elif index == 2:
            if ToolMode=='ChooseFoto':
                self.SetToolMode('None')
            else:
                self.SetToolMode('ChooseFoto')
            self.dockwidget.comboBox_2.setCurrentIndex(0)
        else:
            self.SetToolMode('None')

    def DisplayObservations(self):
        global ActualViewIDAndLayer
        global layerFotopulapka
        global layerObserwacja
        if ActualViewIDAndLayer[0] != -99 and ActualViewIDAndLayer[1] == layerFotopulapka:
            ListToChoose=[]
            for feature in layerObserwacja.getFeatures():
                if feature.attribute('id_fotop') == ActualViewIDAndLayer[0]:
                    ListToChoose.append([feature,layerObserwacja])
            self.chosenOne=ChooseFeatureWindow(self,ListToChoose)
            
    def SetFotopulapka(self,FeatureId):
        global layerFotopulapka
        global ActualFotoID
        if self.dockwidget.comboBox_2.count() > 3:
            self.dockwidget.comboBox_2.setCurrentIndex(0)
            for n in range (3, self.dockwidget.comboBox_2.count()):
                self.dockwidget.comboBox_2.removeItem(n)
        layerFotopulapka.select(FeatureId)
        if type(layerFotopulapka.selectedFeatures()[0].attribute('opis')) == str: opis=layerFotopulapka.selectedFeatures()[0].attribute('opis')
        else: opis=''
        text = layerFotopulapka.selectedFeatures()[0].attribute('datetime') +' '+opis
        self.dockwidget.comboBox_2.addItem(text)
        newFont=QFont("FontFamily",italic=True)
        self.dockwidget.comboBox_2.setItemData(3, newFont, Qt.FontRole)
        self.dockwidget.comboBox_2.setCurrentIndex(3)
        self.dockwidget.groupBox_12.setStyleSheet('background-color: rgb(240, 240, 240);')
        ActualFotoID = FeatureId
        
    def deleteFeature(self):
        global layerFotopulapka
        global layerObserwacja
        global ActualViewIDAndLayer
        global DataPath
        caps=False
        if ActualViewIDAndLayer[1]==layerFotopulapka:
            caps = layerFotopulapka.dataProvider().capabilities()
        elif ActualViewIDAndLayer[1]==layerObserwacja:
            caps = layerObserwacja.dataProvider().capabilities()
        if QMessageBox.question(self.iface.mainWindow(), 'Usuwanie danych', u"Na pewno chcesz usunąć ten obiekt?", QMessageBox.Yes, QMessageBox.No)== QMessageBox.Yes and caps & QgsVectorDataProvider.DeleteFeatures:
            if ActualViewIDAndLayer[1]==layerFotopulapka:
                layerObserwacja.startEditing()
                for feature in layerObserwacja.getFeatures():
                    if feature.attribute('id_fotop')==ActualViewIDAndLayer[0]:
                        feature.setAttribute('id_fotop',-1)
                layerObserwacja.updateFeature(feature)
                layerObserwacja.commitChanges()
                layerFotopulapka.dataProvider().deleteFeatures([ActualViewIDAndLayer[0]])
            elif ActualViewIDAndLayer[1]==layerObserwacja:
                feature=-99
                for f in layerObserwacja.getFeatures():
                    if f.id()==ActualViewIDAndLayer[0]:
                        feature=f
                piclist=('zdj_1','zdj_2','zdj_3')
                for pic in piclist:
                    name=' '
                    if feature!=-99:
                        name=feature.attribute(pic)
                        path=os.path.join(DataPath,'photos',str(name))
                        if os.path.isfile(path): os.remove(path)
                layerObserwacja.dataProvider().deleteFeatures([ActualViewIDAndLayer[0]])
            ActualViewIDAndLayer = [-99,None]
            self.setTrybPrzegladania()
            self.canvas.refresh()
    def displayAttributes(self,id,layer):

        self.dockwidget.edytuj.setEnabled(True)
        self.dockwidget.rodzaj_obs.setCurrentIndex(2)  #after first attributes show, fotopulapka button is activating
        global ActualViewIDAndLayer
        global ActualFotoID
        global images_list
        global layerFotopulapka
        global layerObserwacja
        global CurrentCoords
        images_list = []
        add_images=[]
        self.redrawImages()
        self.dockwidget.gatunek.clear()
        self.dockwidget.siedlisko.clear()
        self.dockwidget.dateEdit.clear()
        self.dockwidget.coords.clear()
        layerFotopulapka.removeSelection()
        layerObserwacja.removeSelection()
        self.dockwidget.comboBox_2.setCurrentIndex(0)
        if self.dockwidget.comboBox_2.count() > 3:
            for n in range (3, self.dockwidget.comboBox_2.count()):
                self.dockwidget.comboBox_2.removeItem(n)
        if layer==None or not layer.isValid():
            self.dockwidget.rodzaj_obs.setCurrentIndex(0)
            self.dockwidget.przyblizona.setCheckState(Qt.Unchecked)
            self.dockwidget.licznosc.setValue(0)
            self.dockwidget.kierunek.setCurrentIndex(0)
            self.dockwidget.checkBox_5.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox_2.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox_3.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox_4.setCheckState(Qt.Unchecked)
            self.dockwidget.opis.clear()
            self.dockwidget.dateEdit.setDate(self.datagodzina()[0])
            self.dockwidget.timeEdit.setDisplayFormat("HH:mm")
            self.dockwidget.timeEdit.setTime(self.datagodzina()[1])
        else:
            layer.select(id)
            feat=layer.selectedFeatures()[0]
            self.setUniqueSiedliskoValues()
            self.dockwidget.siedlisko.setCurrentIndex(self.setSiedliskoIndex(feat))
            if feat.attribute('opis')== None:
                self.dockwidget.opis.setText('')
            else: self.dockwidget.opis.setText(str(feat.attribute('opis')))
            if feat.attribute('datetime') != None:
                date = QDate.fromString(feat.attribute('datetime')[0:10],'yyyy-MM-dd')
                self.dockwidget.dateEdit.setDate(date)
                time = QTime.fromString(feat.attribute('datetime')[11:],'hh:mm:ss')
                self.dockwidget.timeEdit.setTime(time)
            wspolrzedne=self.MakeWGSCoordsString(feat,layer)
            if wspolrzedne[1]==None or wspolrzedne[2]==None: CurrentCoords=[]
            else: CurrentCoords=[wspolrzedne[1],wspolrzedne[2]]
            self.dockwidget.coords.setText(wspolrzedne[0])
            if add_images:
                for image in add_images:
                    pixmap = QPixmap(image)
                    images_list.append(pixmap)
                self.redrawImages()
            self.dockwidget.btn_image.setEnabled(False)
            
        if layer==layerFotopulapka:
            ActualViewIDAndLayer = [id,layer]
            ActualFotoID = -99
            self.dockwidget.rodzaj_obs.setCurrentIndex(0)
            self.dockwidget.przyblizona.setCheckState(Qt.Unchecked)
            self.dockwidget.licznosc.setValue(0)
            self.dockwidget.kierunek.setCurrentIndex(0)
            self.dockwidget.checkBox_5.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox_2.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox_3.setCheckState(Qt.Unchecked)
            self.dockwidget.checkBox_4.setCheckState(Qt.Unchecked)
        elif layer==layerObserwacja:
            ActualViewIDAndLayer = [id,layer]
            if str(feat.attribute('id_fotop'))is not None:
                layerFotopulapka.removeSelection()
                fotID = None
                for Fotopulapka in layerFotopulapka.getFeatures():
                    if feat.attribute('id_fotop')==Fotopulapka.id(): fotID=Fotopulapka.id()
                if fotID is not None:
                    self.SetFotopulapka(fotID)
                    ActualFotoID = fotID
                else:
                    ActualFotoID = -99
            if feat.attribute('rodzaj')=='ptak':
                self.dockwidget.rodzaj_obs.setCurrentIndex(2)
                self.setUniquePtakGatunekValues()
            elif feat.attribute('rodzaj')=='ssak':
                self.dockwidget.rodzaj_obs.setCurrentIndex(1)
                self.setUniqueSsakGatunekValues()
            else: QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u"Nieprawidłowa wartość atrybutu <b>rodzaj</b>: %s"  % (feat.attribute('rodzaj')))
            if feat.attribute('przyb')==0: self.dockwidget.przyblizona.setCheckState(Qt.Unchecked)
            elif feat.attribute('przyb')==1: self.dockwidget.przyblizona.setCheckState(Qt.Checked)
            else: QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u"Nieprawidłowa wartość atrybutu <b>przyb</b>: %s"  % (feat.attribute('przyb')))
            if type(feat.attribute('licznosc'))==int: self.dockwidget.licznosc.setValue(feat.attribute('licznosc'))
            self.dockwidget.kierunek.setCurrentIndex(self.setKierunek(feat.attribute('kierunek')))
            if feat.attribute('drapiez')==0: self.dockwidget.checkBox_5.setCheckState(Qt.Unchecked)
            elif feat.attribute('drapiez')==1: self.dockwidget.checkBox_5.setCheckState(Qt.Checked)
            else: QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u"Nieprawidłowa wartość atrybutu <b>drapiez</b>: %s"  % (feat.attribute('drapiez')))
            if feat.attribute('obserwacja')==0: self.dockwidget.checkBox.setCheckState(Qt.Unchecked)
            elif feat.attribute('obserwacja')==1: self.dockwidget.checkBox.setCheckState(Qt.Checked)
            else: QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u"Nieprawidłowa wartość atrybutu <b>obserwacja</b>: %s"  % (feat.attribute('obserwacja')))
            if feat.attribute('tropy')==0: self.dockwidget.checkBox_2.setCheckState(Qt.Unchecked)
            elif feat.attribute('tropy')==1: self.dockwidget.checkBox_2.setCheckState(Qt.Checked)
            else: QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u"Nieprawidłowa wartość atrybutu <b>tropy</b>: %s"  % (feat.attribute('tropy')))
            if feat.attribute('odchody')==0: self.dockwidget.checkBox_3.setCheckState(Qt.Unchecked)
            elif feat.attribute('odchody')==1: self.dockwidget.checkBox_3.setCheckState(Qt.Checked)
            else: QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u"Nieprawidłowa wartość atrybutu <b>odchody</b>: %s"  % (feat.attribute('odchody')))
            if feat.attribute('inne')==0: self.dockwidget.checkBox_4.setCheckState(Qt.Unchecked)
            elif feat.attribute('inne')==1: self.dockwidget.checkBox_4.setCheckState(Qt.Checked)
            else: QMessageBox.warning( self.iface.mainWindow(),"Komunikat", u"Nieprawidłowa wartość atrybutu <b>inne</b>: %s"  % (feat.attribute('inne')))
            self.dockwidget.gatunek.setCurrentIndex(self.setGatunekIndex(feat))
            global DataPath
            for zdj in ('zdj_1','zdj_2','zdj_3'):
                name=feat.attribute(zdj)
                if not name or name is None or name==None or name=='':
                    continue
                if not os.path.isfile(os.path.join(DataPath,'photos',name)):
                    continue
                add_images.append(os.path.join(DataPath,'photos',feat.attribute(zdj)))
            for image in add_images:
                pixmap = QPixmap(image)
                images_list.append(pixmap)
            self.redrawImages()
        self.dockwidget.btn_image.setEnabled(False)
    def setKierunek(self,input):
        table=[[0,'brak'],[1,'W'],[2,'NW'],[3,'N'],[4,'NE'],[5,'E'],[6,'SE'],[7,'S'],[8,'SW']]
        output=0
        for kierunek in table:
            if input==kierunek[0]:
                output=kierunek[1]
                break
            elif input==kierunek[1]:
                output=kierunek[0]
                break
            else: output=0
        return output
class PhotoWindow(QWidget):
    def __init__(self,pixmap = None,title = None,parent = None):
        super(PhotoWindow, self).__init__(parent)
        plugin_dir = os.path.dirname(__file__)
        icon_path=os.path.join(plugin_dir,'icon.png')
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)
        self.setWindowTitle(u'Podgląd zdjęcia')
        self.layout(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()

        
    def layout(self,pixmap):
        picture = QLabel(self)
        picture.setPixmap(pixmap.scaled(self.size(),Qt.KeepAspectRatio, Qt.SmoothTransformation))

        verticalLayout = QVBoxLayout(self)
        verticalLayout.addWidget(picture)
        
class ChooseFeatureWindow(QWidget):
    def __init__(self,Wildlife = None,featuresList = None,Foto = False,parent = None):
        super(ChooseFeatureWindow, self).__init__(parent)
        plugin_dir = os.path.dirname(__file__)
        icon_path=os.path.join(plugin_dir,'icon.png')
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)
        self.setWindowTitle(u'Wybierz obiekt')
        self.setMaximumHeight(600)
        self.LoadTable(featuresList)
        p = self.mapFromGlobal(QCursor.pos())
        self.move(p)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        global SetFoto
        SetFoto = Foto
        self.show()
        self.featuresList=featuresList
        self.Wildlife=Wildlife

    def LoadTable(self,featuresList):
        
        global table
        global ToolMode
        table = QTableWidget()
        table.palette().setColor(12,QColor(137, 206, 0))
        table.cellClicked.connect(self.Click)
        table.setMouseTracking(True)
        table.cellEntered.connect(self.Entered)
        table.setColumnCount(6)
        for row in featuresList:
            feature=row[0]
            layer=row[1]
            currentRow = table.rowCount()
            table.insertRow(currentRow)
            table.setRowHeight(currentRow,18)
            itemLayer=QTableWidgetItem(layer.name())
            if layer.name()=='Obserwacja': itemLicznosc=QTableWidgetItem('%s' % (feature.attribute('licznosc')))
            else: itemLicznosc=QTableWidgetItem('')
            if layer.name()=='Obserwacja': itemSkrot=QTableWidgetItem('%s' % (feature.attribute('gat_skrot')))
            else: itemSkrot=QTableWidgetItem('')
            if layer.name()=='Obserwacja': itemGatunek=QTableWidgetItem('%s' % (feature.attribute('gatunek')))
            else: itemGatunek=QTableWidgetItem('')
            if type(feature.attribute('opis'))==str: Opis = u'%s' % feature.attribute('opis')
            else: Opis = u''
            if len(Opis) >= 60: Opis = Opis[:60]+'...'
            itemOpis = QTableWidgetItem('%s' % (Opis))
            itemDate = QTableWidgetItem('%s' % (feature.attribute('datetime')))
            
            for item in (itemLayer,itemLicznosc,itemSkrot,itemGatunek,itemOpis,itemDate):
                item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
                brush=QBrush()
                brush.setColor(QColor(240, 240, 240))
                item.setBackground(brush)
                item.setBackground(QColor(240, 240, 240))
                font=item.font()
                font.setPointSize(8)
                item.setFont(font)
                table.setItem(currentRow, (itemLayer,itemLicznosc,itemSkrot,itemGatunek,itemOpis,itemDate).index(item), item)
        
        table.resizeColumnsToContents()
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setCursor(Qt.PointingHandCursor)
        width=table.horizontalHeader().length()+2
        height=table.verticalHeader().length()+2
        table.horizontalHeader().hide()
        table.verticalHeader().hide()
        table.setFixedSize(width,height)
        verticalLayout = QVBoxLayout(self)
        verticalLayout.addWidget(table)
        self.adjustSize()
        self.setFixedSize(self.width(),self.height())

    def Entered(self,row,column):
        global table
        table.clearSelection()
        table.selectRow(row)
    def Click(self,row,column):
        closestFeatureId=self.featuresList[row][0].id()
        layerWithClosestFeature=self.featuresList[row][1]
        global Foto
        if SetFoto==False:
            self.Wildlife.displayAttributes(closestFeatureId,layerWithClosestFeature)
        else:
            self.Wildlife.SetFotopulapka(closestFeatureId)
        self.close()