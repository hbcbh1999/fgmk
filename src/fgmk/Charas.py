import os
import sys
import json
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, QtCore, QtWidgets
from fgmk import TileXtra, actionDialog, TXWdgt, fifl, TileCharaset
from fgmk.flowlayout import FlowLayout as FlowLayout

# moves will be step and face, for all possibilities TileCharaset.facing
# so a radio to select move or face and for buttons - one for each direction.
# also a follow chara option will be added next and a random movement

moves = {"move":TileCharaset.facing , "face":TileCharaset.facing, "random":"move", "follow": "player"}

class CharasFormat(TileCharaset.BaseFormat):
    def __init__( self ):
        super().__init__()

        self.new()

    def new(self):
        self.jsonTree = { "Charas": {} }

    def addChara(self, name, charaset = "", actions = {"type":[1,0],"list":[]}, movements=[], properties={"nocolision":0}):

        self.jsonTree["Charas"][name]= {    "charaset": charaset,
                                            "actions":actions,
                                            "movements":movements,
                                            "properties":properties
                                            }

    def addMovements(self, name, movements):
        self.jsonTree["Charas"][name]["movements"] = movements

    def addActions(self, name, actions):
        self.jsonTree["Charas"][name]["actions"] = actions

    def getCharaset(self,name):
        return self.jsonTree["Charas"][name]["charaset"]



class MoveButtons(QWidget):
    buttonup = pyqtSignal()
    buttondown = pyqtSignal()
    buttonleft = pyqtSignal()
    buttonright = pyqtSignal()

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.Grid = QGridLayout(self)

        self.Grid.setHorizontalSpacing(0)
        self.Grid.setVerticalSpacing(0)
        self.Grid.setSpacing(0)
        self.Grid.setContentsMargins(0, 0, 0, 0)

        self.setFixedSize(150, 150)

        self.dirbuttons = []
        self.signal = {}
        self.signal["up"] = self.buttonup
        self.signal["down"] = self.buttondown
        self.signal["left"] = self.buttonleft
        self.signal["right"] = self.buttonright

        for i in TileCharaset.facing:
            self.dirbuttons.append(QPushButton(i))
            self.dirbuttons[-1].setObjectName(i)
            self.dirbuttons[-1].setFixedSize(50, 50)
            self.dirbuttons[-1].clicked.connect(self.bclicked)
            if i == "up":
                self.Grid.addWidget(self.dirbuttons[-1], 0, 1)
            if i == "down":
                self.Grid.addWidget(self.dirbuttons[-1], 2, 1)
            if i == "left":
                self.Grid.addWidget(self.dirbuttons[-1], 1, 0)
            if i == "right":
                self.Grid.addWidget(self.dirbuttons[-1], 1, 2)

    def bclicked(self):
        direction = str(self.sender().objectName())
        self.signal[direction].emit()

class MoveItem(QtWidgets.QListWidgetItem):
    def __init__(self, moveorface, direction = ""):
        super().__init__(moveorface+direction)

        if (direction == ""):
            self.direction = moveorface[4:]
            self.moveorface = moveorface[0:4]
        else:
            self.moveorface = moveorface
            self.direction = direction
        movearray = [str(self.moveorface) , str(self.direction)]
        self.setData(Qt.UserRole, movearray)

    def getMarray(self):
        #movearray = self.data(Qt.UserRole).toPyObject() #this was python2
        #python3 doesn't need toPyObject (and doesn't work with it)
        movearray = self.data(Qt.UserRole)
        return [str(movearray[0]),str(movearray[1])]

class PropertiesWidget(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.VBox = QVBoxLayout(self)
        self.nocolision = QCheckBox("igone colision")
        self.nocolision.setToolTip("This makes the object ignore the colision map.")
        self.nocolision.setCheckState(Qt.Unchecked)

        self.propertys =  {}
        self.propertys['nocolision']=self.nocolision

        for key in self.propertys:
            self.VBox.addWidget(self.propertys[key])

        self.clear()

    def setList(self,listToSet):
        for propertyy in listToSet:
            if(propertyy == 'nocolision'):
                if(listToSet[propertyy]==0 or listToSet[propertyy]==False):
                    self.propertys[propertyy].setCheckState(Qt.Unchecked)
                else:
                    self.propertys[propertyy].setCheckState(Qt.Checked)

    def clear(self):
        for propertyy in self.propertys:
            if(propertyy == 'nocolision'):
                self.propertys[propertyy].setCheckState(Qt.Unchecked)

    def getValue(self):
        properties = {}
        for key in self.propertys:
            properties[key] = self.propertys[key].isChecked()

        return properties


class MoveWidget(QWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.VBox = QVBoxLayout(self)
        self.dirButtons = MoveButtons()
        self.dirButtons.buttonup.connect(self.upbclick)
        self.dirButtons.buttondown.connect(self.downbclick)
        self.dirButtons.buttonleft.connect(self.leftbclick)
        self.dirButtons.buttonright.connect(self.rightbclick)

        self.radiomove = QRadioButton("move")
        self.radioface = QRadioButton("face")
        self.random = QPushButton("random")
        self.follow = QPushButton("follow")


        self.radioface.setToolTip("Face a direction is when a chara looks at certain direction.")
        self.follow.setToolTip("Chara will make one movement or face in the player direction.")
        self.random.setToolTip("Chara will face or move in a random direction, one time.")


        self.random.clicked.connect(self.randombclick)
        self.follow.clicked.connect(self.followbclick)

        self.movList = QListWidget(self)
        self.movList.setDragDropMode(QAbstractItemView.InternalMove)

        self.deselectbutton = QPushButton("deselect")
        self.deletebutton = QPushButton("delete")

        self.deselectbutton.clicked.connect(self.deselectbclick)
        self.deletebutton.clicked.connect(self.deletebclick)

        HBoxB = QHBoxLayout()
        HBoxB.addWidget(self.deselectbutton)
        HBoxB.addWidget(self.deletebutton)

        VBoxR = QVBoxLayout()

        VBoxR.addWidget(self.radiomove)
        VBoxR.addWidget(self.radioface)
        VBoxR.addWidget(self.random)
        VBoxR.addWidget(self.follow)

        HBoxT = QHBoxLayout()
        HBoxT.addWidget(self.dirButtons)
        HBoxT.addLayout(VBoxR)

        self.VBox.addLayout(HBoxT)
        self.VBox.addWidget(self.movList)
        self.VBox.addLayout(HBoxB)

        self.radiomove.toggle()

    def setList(self,listToSet):
        self.movList.clear()
        for move in listToSet:
            print(move)
            self.movList.addItem(MoveItem(move[0],move[1]))

    def clear(self):
        self.movList.clear()

    def getValue(self):
        movements = []
        for itemIndex in range(self.movList.count()):
            itemArray = self.movList.item(itemIndex).getMarray()
            movements.append(itemArray)

        return movements

    def deletebclick(self):
        if(self.movList.selectedItems()):
            for item in self.movList.selectedItems():
                itemIndex = self.movList.row(item)
                self.movList.takeItem(itemIndex)
        else:
            for itemIndex in range(self.movList.count()):
                self.movList.takeItem(0)


    def deselectbclick(self):
        for i in range(self.movList.count()):
            item = self.movList.item(i)
            self.movList.setItemSelected(item, False)
        #self.getValue()

    def randombclick(self):
        if(self.radioface.isChecked()):
            self.movList.addItem(MoveItem("facerandom"))
        else:
            self.movList.addItem(MoveItem("moverandom"))

    def followbclick(self):
        if(self.radioface.isChecked()):
            self.movList.addItem(MoveItem("facefollow"))
        else:
            self.movList.addItem(MoveItem("movefollow"))

    def upbclick(self):
        if(self.radioface.isChecked()):
            self.movList.addItem(MoveItem("faceup"))
        else:
            self.movList.addItem(MoveItem("moveup"))

    def downbclick(self):
        if(self.radioface.isChecked()):
            self.movList.addItem(MoveItem("facedown"))
        else:
            self.movList.addItem(MoveItem("movedown"))

    def leftbclick(self):
        if(self.radioface.isChecked()):
            self.movList.addItem(MoveItem("faceleft"))
        else:
            self.movList.addItem(MoveItem("moveleft"))

    def rightbclick(self):
        if(self.radioface.isChecked()):
            self.movList.addItem(MoveItem("faceright"))
        else:
            self.movList.addItem(MoveItem("moveright"))

class ActionsWidget(QWidget):
    def __init__(self, parent=None, ssettings={}, ischara=False , **kwargs):
        super().__init__(parent, **kwargs)

        self.ssettings = ssettings
        self.parent = parent
        self.ischara = ischara

        self.HBox = QHBoxLayout(self)
        self.HBox.setAlignment(Qt.AlignTop)

        self.labelActionList = QLabel("List of Actions:")
        self.ActionList = QListWidget(self)

        VBoxActionList = QVBoxLayout()
        VBoxButtons = QVBoxLayout()

        self.addActionButton = QPushButton("Add Action", self)
        self.editActionButton = QPushButton("Edit Action", self)
        self.removeActionButton = QPushButton("Remove Action", self)
        self.deselectActionButton = QPushButton("Deselect Actions", self)

        self.checkboxes = []
        self.checkboxes.append(QCheckBox("on click", self))
        self.checkboxes.append(QCheckBox("on over", self))

        self.addActionButton.clicked.connect(self.addAction)
        self.editActionButton.clicked.connect(self.editAction)
        self.removeActionButton.clicked.connect(self.removeAction)
        self.deselectActionButton.clicked.connect(self.deselectAction)

        self.HBox.addLayout(VBoxActionList)
        self.HBox.addLayout(VBoxButtons)

        VBoxActionList.addWidget(self.labelActionList)
        VBoxActionList.addWidget(self.ActionList)

        VBoxButtons.addWidget(self.addActionButton)
        VBoxButtons.addWidget(self.editActionButton)
        VBoxButtons.addWidget(self.removeActionButton)
        VBoxButtons.addWidget(self.deselectActionButton)

        self.checkboxes[0].setCheckState(Qt.Checked)
        self.checkboxes[1].setCheckState(Qt.Unchecked)

        for checkbox in self.checkboxes:
            VBoxButtons.addWidget(checkbox)

        self.ActionList.setDragDropMode(QAbstractItemView.InternalMove)

        self.ActionList.itemSelectionChanged.connect(self.enableButtonsBecauseActionList)

        ActionListModel = self.ActionList.model()
        ActionListModel.layoutChanged.connect(self.updateActionFromWidget)

        if(self.ssettings == {} ):
            self.ssettings["gamefolder"] = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),"../Game/"))

    def setList(self,actionToSet):
        atype = actionToSet['type']
        for i in range(len(atype)):
            if(atype[i]):
                self.checkboxes[i].setCheckState(Qt.Checked)
            else:
                self.checkboxes[i].setCheckState(Qt.Unchecked)

        listToSet = actionToSet['list']
        self.ActionList.clear()
        for action in listToSet:
            self.ActionList.addItem(TileXtra.actionItem(action))

    def clear(self):
        self.ActionList.clear()

    def setAllState(self, state):
        self.addActionButton.setEnabled(state)
        self.removeActionButton.setEnabled(state)
        self.ActionList.setEnabled(state)
        self.labelActionList.setEnabled(state)
        self.deselectActionButton.setEnabled(state)
        self.editActionButton.setEnabled(state)
        self.enableButtonsBecauseActionList()

    def updateActionFromWidget(self):
        i = 0
        while i < self.ActionList.count():
            item = self.ActionList.item(i)
            actionToAdd = item.getAction()
            i += 1

    def editAction(self):
        indexOfAction = self.ActionList.row(self.ActionList.selectedItems()[0])
        selecteditem = self.ActionList.selectedItems()[0]
        actionParamToEdit = selecteditem.getAction()

        actionToEdit = actionParamToEdit[0]
        paramOfEdit = actionParamToEdit[1]

        paramArrayOfEdit = paramOfEdit.split(';')

        newDialogFromName = getattr(actionDialog, str(actionToEdit))

        self.myActionsDialog = newDialogFromName(self.ssettings["gamefolder"],self,paramArrayOfEdit,True)
        if self.myActionsDialog.exec_() == QtWidgets.QDialog.Accepted:
            returnActDlg = str(self.myActionsDialog.getValue())

            actionToAdd = [actionToEdit,str(returnActDlg)]

            self.ActionList.takeItem(indexOfAction)
            self.ActionList.insertItem(indexOfAction,TileXtra.actionItem(actionToAdd))

    def deselectAction(self):
        for i in range(self.ActionList.count()):
            item = self.ActionList.item(i)
            self.ActionList.setItemSelected(item, False)

    def addAction(self):
        self.myActionsWidget = TXWdgt.ActionsWidget(self.ssettings,self,self.ischara)
        if self.myActionsWidget.exec_() == QtWidgets.QDialog.Accepted:
            actionToAdd = self.myActionsWidget.getValue()

            if not self.ActionList.selectedItems():
                self.ActionList.addItem(TileXtra.actionItem(actionToAdd))
            else:
                indexOfAction = self.ActionList.row(self.ActionList.selectedItems()[0])
                self.ActionList.insertItem(indexOfAction,TileXtra.actionItem(actionToAdd))

    def removeAction(self):
        for item in self.ActionList.selectedItems():
            itemIndex = self.ActionList.row(item)
            self.ActionList.takeItem(itemIndex)

    def enableButtonsBecauseActionList(self):
        enable = True
        if (self.ActionList.currentItem() is None):
            enable = False
        else:
            if (self.ActionList.currentItem().isSelected() == False):
                enable = False

        if (enable):
            self.removeActionButton.setEnabled(True)
            self.deselectActionButton.setEnabled(True)
            self.editActionButton.setEnabled(True)
        else:
            self.removeActionButton.setEnabled(False)
            self.editActionButton.setEnabled(False)
            self.deselectActionButton.setEnabled(False)

    def getValue(self):

        allactions = []
        for itemIndex in range(self.ActionList.count()):
            allactions.append(self.ActionList.item(itemIndex).getAction())

        onclick = self.checkboxes[0].isChecked()
        onover = self.checkboxes[1].isChecked()

        actiontype = [onclick,onover]

        returnvalue = {'list':allactions, 'type':actiontype }

        return returnvalue

class CharaItem(QtWidgets.QListWidgetItem):
    def __init__(self, aname, jsonTree = {}):
        super().__init__(aname)

        if(jsonTree == {}):
             jsonTree = {'movements': [], 'actions': {'type': [], 'list': []}, 'charaset': ''}

        self.aname = aname
        self.jsonTree = jsonTree

class CharaList(QWidget):
    SelectionChanged = pyqtSignal()

    def __init__(self, parent=None, ssettings={}, **kwargs):
        super().__init__(parent, **kwargs)

        self.VBox = QVBoxLayout(self)

        self.charaslist = QListWidget()
        self.charaentry = QLineEdit()
        self.addbutton = QPushButton("add")
        self.delbutton = QPushButton("del")

        self.addbutton.clicked.connect(self.charaslistAddAction)
        self.delbutton.clicked.connect(self.charaslistDelAction)
        self.charaslist.itemSelectionChanged.connect(self.charaslistSelectionChanged)
        self.charaentry.returnPressed.connect(self.charaslistAddAction)

        HBox = QHBoxLayout()
        HBox.addWidget(self.charaentry)
        HBox.addWidget(self.addbutton)
        HBox.addWidget(self.delbutton)

        self.VBox.addLayout(HBox)
        self.VBox.addWidget(self.charaslist)
        self.charaslistSelectionChanged()

    def charaslistAddAction(self):
        charaName = str(self.charaentry.text()).strip()
        if (len(charaName)>0):
            for itemIndex in range(self.charaslist.count()):
                if (str(self.charaslist.item(itemIndex).aname) == charaName):
                    return

            self.charaslist.addItem(CharaItem(charaName))

    def charaslistDelAction(self):
        if (len(self.charaslist.selectedItems())>0):
            for item in self.charaslist.selectedItems():
                itemIndex = self.charaslist.row(item)
                self.charaslist.takeItem(itemIndex)

    def charaslistSelectionChanged(self):
        if (len(self.charaslist.selectedItems())>0):
            jsonTree = self.charaslist.selectedItems()[0].jsonTree
            name = self.charaslist.selectedItems()[0].aname
            self.returnvalue = {"name": name, "jsonTree":jsonTree}
        else:
            self.returnvalue = {'name': None,  'jsonTree':{'charaset':"",'actions':{},'movements':[],'properties':{}}}

        self.SelectionChanged.emit()

    def setSelected(self,jsonTree):
        if (len(self.charaslist.selectedItems())>0):
            self.charaslist.selectedItems()[0].jsonTree = jsonTree

    def setItem(self,itemTree):
        for itemIndex in range(self.charaslist.count()):
            if (str(self.charaslist.item(itemIndex).aname) == itemTree["name"]):
                self.charaslist.item(itemIndex).jsonTree = itemTree["jsonTree"]


    def clear(self):
        self.charaslist.clear()

    def getCharas(self):
        self.charaslistSelectionChanged()
        charas = CharasFormat()
        for itemIndex in range(self.charaslist.count()):
            charaname = str(self.charaslist.item(itemIndex).aname)
            jt = self.charaslist.item(itemIndex).jsonTree
            print(jt)
            charas.addChara(charaname,jt["charaset"],jt["actions"],jt["movements"],jt["properties"])

        return charas

    def deselect(self):
        for i in range(self.charaslist.count()):
            item = self.charaslist.item(i)
            self.charaslist.setItemSelected(item, False)

    def setList(self,dictToSet):
        self.charaslist.clear()
        for chara in dictToSet:
            charaName = chara
            jsonTree = dictToSet[chara]
            self.charaslist.addItem(CharaItem(charaName,jsonTree))

class CharaSelector(QWidget):
    def __init__(self, parent=None, ssettings={}, **kwargs):
        super().__init__(parent, **kwargs)

        self.ssettings = ssettings

        self.layout = QHBoxLayout(self)
        self.csetprev = TileCharaset.CharasetPreviewer(self,ssettings)
        self.charaqlist = QListWidget()

        self.charaqlist.itemSelectionChanged.connect(self.selectionChanged)

        self.layout.addWidget(self.csetprev)
        self.layout.addWidget(self.charaqlist)

    def update(self):

        if "gamefolder" in self.ssettings:
            if (self.ssettings["gamefolder"] != ""):
                filetoopen = os.path.join(self.ssettings["gamefolder"],fifl.DESCRIPTORS,fifl.CHARAS)
                self.__Open(filetoopen)

                self.csetprev.update()

        if self.charaqlist.count() > 0:
            self.charaqlist.setCurrentRow(0)

    def setList(self,dictToSet):
        self.charaqlist.clear()
        for chara in dictToSet:
            charaName = chara
            jsonTree = dictToSet[chara]
            self.charaqlist.addItem(CharaItem(charaName,jsonTree))

    def __Open(self,charafile = None):
        if(charafile == None):
            charafile = self.charafile

        self.charafile = charafile
        charas = CharasFormat()
        charas.load(charafile)
        self.setList(charas.jsonTree["Charas"])

    def selectionChanged(self):
        if(self.charaqlist.selectedItems()):
            charaset = str(self.charaqlist.selectedItems()[0].jsonTree["charaset"])
            self.csetprev.select(charaset)

    def getSelected(self):
        if(self.charaqlist.selectedItems()):
            charaname = str(self.charaqlist.selectedItems()[0].aname)
            return charaname
        else:
            return None


class MiniCharaTile(QWidget):
    def __init__(self, parent=None, ssettings={}, chara="", position=(0,0), **kwargs):
        super().__init__(parent, **kwargs)

        self.chara = chara
        self.position = position

        if "gamefolder" in ssettings:
            filetoopen = os.path.join(ssettings["gamefolder"],fifl.DESCRIPTORS,fifl.CHARAS)
            charas = self.__Open(filetoopen)
            charaset = charas.getCharaset(chara)

            self.csetprev = TileCharaset.CharasetPreviewer(self,ssettings,None,1)
            self.csetprev.select(charaset)
            self.whsize = self.csetprev.whsize
            self.setFixedSize(self.whsize)

        else:
            return False

        self.setToolTip(chara)

    clicked = pyqtSignal()
    rightClicked = pyqtSignal()

    def stop(self):
        self.csetprev.stop()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            self.clicked.emit()

    def __Open(self,charafile = None):
        if(charafile == None):
            charafile = self.charafile

        self.charafile = charafile
        charas = CharasFormat()
        charas.load(charafile)
        return charas



class CharaEditor(QDialog):
    def __init__(self, parent=None, ssettings={}, **kwargs):
        super().__init__(parent, **kwargs)

        self.layout = QHBoxLayout(self)

        self.charalist = CharaList()
        self.csetSelector = TileCharaset.CharasetSelector(self, ssettings)
        self.movement = MoveWidget()
        self.properties = PropertiesWidget()

        self.actions = ActionsWidget(parent,ssettings,True)
        self.actions.setAllState(True)
        self.reopen = QPushButton("Reopen", self)
        self.reopen.clicked.connect(self.reopenfile)
        self.save = QPushButton("Save", self)
        self.save.clicked.connect(self.savefile)

        HBoxRS = QHBoxLayout()
        HBoxRS.addWidget(self.reopen)
        HBoxRS.addWidget(self.save)

        VBox = QVBoxLayout()
        VBox.addWidget(self.charalist)
        VBox.addLayout(HBoxRS)
        VBox.addWidget(self.properties)

        self.layout.addLayout(VBox)
        self.layout.addWidget(self.csetSelector)
        self.layout.addWidget(self.movement)
        self.layout.addWidget(self.actions)

        self.charalist.SelectionChanged.connect(self.charaSelectionChanged)

        self.oldSelection = self.charalist.returnvalue

        if "gamefolder" in ssettings:
            filetoopen = os.path.join(ssettings["gamefolder"],fifl.DESCRIPTORS,fifl.CHARAS)
            self.__Open(filetoopen)

    def reopenfile(self):
        self.__Open()

    def savefile(self):
        self.__Save()


    def __Open(self,charafile = None):
        if(charafile == None):
            charafile = self.charafile

        self.charafile = charafile
        charas = CharasFormat()
        charas.load(charafile)
        self.charalist.setList(charas.jsonTree["Charas"])

    def __Save(self,charafile = None):
        if(charafile == None):
            charafile = self.charafile

        charas = self.charalist.getCharas()
        charas.save(charafile)


    def getAll(self):
        charas = {}
        charas = self.charalist.getCharas()
        print(charas.jsonTree)


    def charaSelectionChanged(self):
        newSelection = self.charalist.returnvalue

        if(self.oldSelection['name'] == None):
            self.oldSelection['name'] = newSelection['name']
        else:
            charaset = self.csetSelector.getValue()
            movements = self.movement.getValue()
            actions = self.actions.getValue()
            properties = self.properties.getValue()
            self.oldSelection["jsonTree"] = { "charaset":charaset,"movements":movements,"actions":actions, "properties":properties }
            self.charalist.setItem(self.oldSelection)

        if(newSelection['jsonTree'] == {}):
            self.movement.clear()
            self.actions.clear()
            self.csetSelector.reset()
            self.properties.clear()
        else:
            self.csetSelector.select(newSelection['jsonTree']['charaset'])
            self.movement.setList(newSelection['jsonTree']['movements'])
            self.actions.setList(newSelection['jsonTree']['actions'])
            self.properties.setList(newSelection['jsonTree']['properties'])

        self.oldSelection = newSelection


if __name__=="__main__":
    from sys import argv, exit

    a=QApplication(argv)
    #m=CharaEditor()
    #m=MoveWidget()
    #m=CharaSelector()
    m=MiniCharaTile(None,{"gamefolder":"basegame"},"WeirdGuy")
    a.processEvents()
    m.show()
    m.raise_()
    exit(a.exec_())