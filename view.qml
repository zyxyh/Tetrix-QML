import QtQuick 2.5
import QtQuick.Window 2.2
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.1

Rectangle {

    id: root
    visible: true
    width: 380
    height: 415
    property var shapecolor:["aliceblue", "#CC6666", "#66CC66", "#6666CC","#CCCC66", "#CC66CC", "#66CCCC", "#DAAA00"]
    // "lightgray", "darkred", "blue", "green", "brown", "purple", "steelblue", "navy"
    property int score: 0
    property int curC;
    property int curR;
    property int curShape;
    /*
    property var table: null

    property var curPiece: null

    property var blocks: null
    property var currentBlocks: null
    property int xOffset;
    property int yOffset;
    property int score;
    */

    Rectangle {
        id: mainRect
        anchors.left: root.left
        anchors.top: root.top
        // anchors.bottom: root.bottom
        anchors.margins: 10
        width: 240
        height: 400
        border.width: 1
        border.color: "black"

        Repeater {
            id: repeater
            model: 12*20
            delegate: blockComponent
        }

        Component {
            id: blockComponent
            Rectangle {
                x: index%12*20+1
                y: Math.floor(index/12)*20+1
                width: 18
                height: 18
                radius: 2
                color: "aliceblue"
            }
        }
    }

        Rectangle {
            id: nextBlock
            anchors.top: parent.top
            anchors.left: mainRect.right
            anchors.right: parent.right
            anchors.margins: 10
            height: 120
            border.color: "black"

            Repeater {
                id: nextrepeater
                model: 4
                delegate: nextPieceComponent
            }

            Component {
                id: nextPieceComponent
                Rectangle {
                    width: 18
                    height: 18
                    radius: 2
                    x:60
                    y:60
                }
            }
        }

        Rectangle {
            id: scoreBlock
            anchors.top: nextBlock.bottom
            anchors.left: mainRect.right
            anchors.right: parent.right
            anchors.margins: 10
            height: 50
            border.color: "black"

            Text {
                anchors.centerIn: parent
                text: root.score
                font.pixelSize: parent.height-10
                color: "black"
            }
        }

        Button {
            id: startbtn
            anchors.top: scoreBlock.bottom
            anchors.left: mainRect.right
            anchors.right: parent.right
            anchors.margins: 10
            height: 50
            text: "Start"

            onClicked: {
                tetrix.newGame()
                timer.running = true
                timer.interval = 400
                timer.repeat = true

            }
        }

        Timer {
            id: timer

            onTriggered: {
                tetrix.timerEvent();
                root.refresh();
                root.nextbufrefresh();
            }
        }

        focus: true

        Keys.onPressed: {
            if(event.key === Qt.Key_Left){
                tetrix.left();
                root.refresh();
            }
            else if(event.key === Qt.Key_Right){
                tetrix.right();
                root.refresh();
            }
            else if(event.key === Qt.Key_Up){
                tetrix.rotateLeft();
                root.refresh();
            }
            else if(event.key === Qt.Key_Down){
                tetrix.down();
                root.refresh();
            }
            else if(event.key === Qt.Key_Space){
                tetrix.land();
                root.refresh();
            }
        }

/*
        MultiPointTouchArea {
            anchors.fill: parent
            mouseEnabled: true
            minimumTouchPoints: 1
            maximumTouchPoints: 1
            property var tracer: []

            touchPoints: [
                TouchPoint {
                    id: point
                }
            ]

            onReleased: {
                if(Math.abs(point.startX-point.x) > Math.abs(point.startY-point.y)) {
                    if(point.x > point.startX) {
                        tetrix.right();
                    } else {
                        tetrix.left()
                    }
                } else {
                    if(point.y > point.startY) {
                        tetrix.land()
                    } else {
                        tetrix.rotateLeft()
                    }
                }
            }
        }

        Component.onCompleted: {
            for(var index = 0;index<repeater.count;index++){
                repeater.itemAt(index).color = root.shapecolor[tetrix.getShapeAt(index)];
                }
        }
*/
        function update(){
            root.score = tetrix.getScore()
        }

        function nextbufrefresh() {
            var nextshapecolor = root.shapecolor[tetrix.getNextShape()]
            for(var index = 0;index<4;index++){
                nextrepeater.itemAt(index).color = nextshapecolor;
                nextrepeater.itemAt(index).x = tetrix.getnextPieceX(index)*20
                nextrepeater.itemAt(index).y = tetrix.getnextPieceY(index)*20
            }
        }

        function refresh(){
            root.score = tetrix.getScore()
            for(var index = 0;index<repeater.count;index++){
                repeater.itemAt(index).color = root.shapecolor[tetrix.getShapeAt(index)];
            }
            var clr = root.shapecolor[tetrix.getShape()]
            // console.log("QML Score, cur.color", root.score, clr)
            for(var i = 0;i<4; i++){
                var curindex = tetrix.getCurPieceIndex(i)
                // console.log("QML curindex,color", curindex, clr)
                if(curindex >= 0 && curindex < 240){
                    repeater.itemAt(curindex).color = clr
                }
            }
        }

}
