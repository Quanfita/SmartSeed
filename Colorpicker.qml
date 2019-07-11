import QtQuick 1.1
Rectangle{
    id:colorComponent
    signal colorChange(string colorValue)
    width:256+16+16+16+64
    height:256
    function initUI(colorValue){
        var xPos,yPos,yHPos
        var middleValue
        var redValue=parseInt(colorValue.slice(1,3),16)
        var greenValue=parseInt(colorValue.slice(3,5),16)
        var blueValue=parseInt(colorValue.slice(5,7),16)
//        console.log(redValue,greenValue,blueValue)
        var minValue=Math.min(redValue,greenValue,blueValue)
        var maxValue=Math.max(redValue,greenValue,blueValue)
        xPos=255-Math.floor(minValue*lRect.width/(maxValue+1))
        yPos=255-Math.floor((maxValue)*lRect.height/256)
//        console.log(xPos,yPos,minValue,maxValue)

        redValue=Math.floor(redValue*255/maxValue)
        greenValue=Math.floor(greenValue*255/maxValue)
        blueValue=Math.floor(blueValue*255/maxValue)

        minValue=Math.min(redValue,greenValue,blueValue)
        maxValue=Math.max(redValue,greenValue,blueValue)

        var tmp1
        var tmp2
        var x

        if(maxValue===redValue)
        {
            if(greenValue===minValue)
            {
                middleValue=blueValue
                tmp1=256-middleValue
                tmp2=256-minValue
                x=Math.floor(256-256*tmp1/tmp2)
                redValue=0xff
                greenValue=0
                blueValue=x

                slider.y=5*(hRectms.height/6)+(0xff-blueValue)*(hRectms.height/6)/0xff
//                console.log(slider.y)
            }else{
                middleValue=greenValue
                tmp1=256-middleValue
                tmp2=256-minValue
                x=Math.floor(256-256*tmp1/tmp2)
                redValue=0xff
                greenValue=x
                blueValue=0

                slider.y=greenValue*(hRectms.height/6)/0xff
//                console.log(slider.y)
            }
        }else if(maxValue===greenValue)
        {
            if(redValue===minValue)
            {
                middleValue=blueValue
                tmp1=256-middleValue
                tmp2=256-minValue
                x=Math.floor(256-256*tmp1/tmp2)
                redValue=0
                greenValue=0xff
                blueValue=x
                slider.y=2*(hRectms.height/6)+blueValue*(hRectms.height/6)/0xff
            }else{
                middleValue=redValue
                tmp1=256-middleValue
                tmp2=256-minValue
                x=Math.floor(256-256*tmp1/tmp2)
                redValue=x
                greenValue=0xff
                blueValue=0

                slider.y=(hRectms.height/6)+(0xff-redValue)*(hRectms.height/6)/0xff
//                console.log(slider.y)
            }
        }else if(maxValue===blueValue)
        {
            if(greenValue===minValue)
            {
                middleValue=redValue
                tmp1=256-middleValue
                tmp2=256-minValue
                x=Math.floor(256-256*tmp1/tmp2)
                redValue=x
                greenValue=0
                blueValue=0xff
                slider.y=4*(hRectms.height/6)+(redValue)*(hRectms.height/6)/0xff
            }else{
                middleValue=greenValue
                tmp1=256-middleValue
                tmp2=256-minValue
                x=Math.floor(256-256*tmp1/tmp2)
                redValue=0
                greenValue=x
                blueValue=0xff

                slider.y=3*(hRectms.height/6)+(0xff-greenValue)*(hRectms.height/6)/0xff
            }
        }

//        console.log(redValue,greenValue,blueValue)  //OK
        lRectms.xPos=xPos
        lRectms.yPos=yPos
        lRectms.setColor()
    }
    Component.onCompleted:{
        initUI("#5c8916")
    }

    Rectangle{
        id:sRect
        width: 256
        height: 256
        rotation :90
        gradient: Gradient {
            GradientStop {id: sv; position: 0.0; color: "#ff0000" }
            GradientStop { position: 1; color: "#ffffff" }
        }
    }
    Rectangle{
        id:lRect
        width: 256
        height: 256
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#00000000" }
            GradientStop { position: 1; color: "#ff000000" }
        }
        Rectangle{
            id:colorRadius
            property real xPos: 0
            property real yPos: 0
            x:xPos
            y:yPos
            width:12
            height:12
            radius: 6
            color:"transparent"
            border.width: 2
            border.color: {
                if((xPos<parent.width/2) && (yPos<parent.height/2))
                    return "#333333"
                else
                    return "#ffffff"
            }
            Connections{
                target:colorComponent
                onColorChange:{
                    colorRadius.xPos=lRectms.xPos-colorRadius.width/2
                    colorRadius.yPos=lRectms.yPos-colorRadius.height/2
                }
            }
        }

        MouseArea{
            id:lRectms
            property int redValue: 0
            property int greenValue: 0
            property int blueValue: 0
            property string hValue: ""
            property real xPos: 0
            property real yPos: 0
            hoverEnabled: true
            anchors.fill: parent
            function setColor(){
                hValue=sv.color
                redValue=parseInt(hValue.slice(1,3),16)
                greenValue=parseInt(hValue.slice(3,5),16)
                blueValue=parseInt(hValue.slice(5,7),16)
//brightness
                redValue=redValue*(width-yPos)/width
                greenValue=greenValue*(width-yPos)/width
                blueValue=blueValue*(width-yPos)/width
//saturability
                var maxValue=Math.max(redValue,greenValue,blueValue)
                redValue=redValue+(width-xPos)*(maxValue-redValue)/width
                greenValue=greenValue+(width-xPos)*(maxValue-greenValue)/width
                blueValue=blueValue+(width-xPos)*(maxValue-blueValue)/width

                if(yPos==255)
                {
                    redValue=0
                    greenValue=0
                    blueValue=0
                }else if((xPos==0) && (yPos==0)){
                    redValue=255
                    greenValue=255
                    blueValue=255
                }

                hValue="#"
                if(redValue<16)
                    hValue+=("0"+redValue.toString(16))
                else
                    hValue+=redValue.toString(16)
                if(greenValue<16)
                    hValue+=("0"+greenValue.toString(16))
                else
                    hValue+=greenValue.toString(16)
                if(blueValue<16)
                    hValue+=("0"+blueValue.toString(16))
                else
                    hValue+=blueValue.toString(16)
                selectRect.color=hValue

                colorComponent.colorChange(hValue)
            }
            onPositionChanged: {
                if(pressed)
                {
                    if((mouseX<width) && (mouseX>=0))
                        if((mouseY<height) && (mouseY>=0))
                        {
                            xPos=mouseX
                            yPos=mouseY
                            setColor()
                        }
                }
            }
            onClicked: {
                xPos=mouseX
                yPos=mouseY
                setColor()
            }
        }
    }

    Rectangle {
        id:hRect
        anchors.left: lRect.right
        anchors.leftMargin: 16
        anchors.top: lRect.top
        width: 16; height: 256
        gradient: Gradient {
             GradientStop { position: 0.0; color: "#ff0000" }
             GradientStop { position: 0.0625; color: "#ff6000" }
             GradientStop { position: 0.125; color: "#ffc000" }
             GradientStop { position: 0.1875; color: "#deff00" }
             GradientStop { position: 0.25; color: "#7eff00" }
             GradientStop { position: 0.3125; color: "#1eff00" }
             GradientStop { position: 0.375; color: "#00ff42" }
             GradientStop { position: 0.4375; color: "#00ffa2" }
             GradientStop { position: 0.5; color: "#00fcff" }
             GradientStop { position: 0.5625; color: "#009cff" }
             GradientStop { position: 0.625; color: "#003cff" }
             GradientStop { position: 0.6875; color: "#2400ff" }
             GradientStop { position: 0.75; color: "#8400ff" }
             GradientStop { position: 0.8125; color: "#e400ff" }
             GradientStop { position: 0.875; color: "#ff00ba" }
             GradientStop { position: 0.9375; color: "#ff005a" }
             GradientStop { position: 1.0; color: "#ff0000" }
         }

        MouseArea{
            id:hRectms
            property real yValue: 0
            property int region:0
            property real yValueSub:0
            property int yColorValue:0
            property string colorValue: ""
            anchors.fill: parent
            function setHue(){
                var tmp
                region=Math.floor(yValue/(height/6))
                yValueSub=yValue-region*(height/6)
                yColorValue=yValueSub/(height/6)*0xff
                switch(region)
                {
                default:
                case 0:         //#FF0000---#FFFF00
                    if(yColorValue<16)
                        colorValue="#FF"+"0"+yColorValue.toString(16)+"00"
                    else
                        colorValue="#FF"+yColorValue.toString(16)+"00"
                    break;
                case 1:         //#FFFF00---#00FF00
                    tmp=0xff-yColorValue
                    if(tmp<16)
                        colorValue="#"+"0"+tmp.toString(16)+"FF"+"00"
                    else
                        colorValue="#"+tmp.toString(16)+"FF"+"00"
                    break;
                case 2:         //#00FF00---#00FFFF
                    if(yColorValue<16)
                        colorValue="#00"+"FF"+"0"+yColorValue.toString(16)
                    else
                        colorValue="#00"+"FF"+yColorValue.toString(16)
                    break;
                case 3:         //#00FFFF---#0000FF
                    tmp=0xff-yColorValue
                    if(tmp<16)
                        colorValue="#00"+"0"+tmp.toString(16)+"FF"
                    else
                        colorValue="#00"+tmp.toString(16)+"FF"
                    break;
                case 4:         //#0000FF---#FF00FF
                    if(yColorValue<16)
                        colorValue="#0"+yColorValue.toString(16)+"00"+"FF"
                    else
                        colorValue="#"+yColorValue.toString(16)+"00"+"FF"
                    break;
                case 5:         //#FF00FF---#FF0000
                    tmp=0xff-yColorValue
                    if(tmp<16)
                        colorValue="#FF"+"00"+"0"+tmp.toString(16)
                    else
                        colorValue="#FF"+"00"+tmp.toString(16)
                    break;

                }
                sv.color=colorValue
                lRectms.setColor()
            }
            onClicked: {
                if(mouseY>(hRect.height-slider.height))
                    slider.y=hRect.height-slider.height
                else
                    slider.y=mouseY
            }
        }
        Rectangle{
            id:slider
            width:parent.width+6
            height:6
            x:-3
            y:0
            color:"black"
            MouseArea{
                anchors.fill: parent
                anchors.margins: -3
                drag.target: slider; drag.axis: Drag.YAxis
                drag.minimumY: 0; drag.maximumY: hRect.height-slider.height
            }
            onYChanged: {
                hRectms.yValue=slider.y
                hRectms.setHue()
            }
        }
     }
    Rectangle{
        id:selectRect
        anchors.top: hRect.top
        anchors.left: hRect.right
        anchors.leftMargin: 16
        width:64
        height:64
        color:"red"
    }
//    Column{
//        id:colorInputLayout
//        anchors.left:selectRect.left
//        anchors.top: selectRect.bottom
//        anchors.topMargin: 16
//        spacing:3
//        Row{
//            spacing: 3
//            Text{
//                text:qsTr("R:")
//                font.pixelSize: 16
//                font.family: "微软雅黑"

//            }
//            Rectangle{
//                width: 36
//                height:20
//                border.width: 1
//                border.color: "black"
//                TextInput{
//                    anchors.horizontalCenter: parent.horizontalCenter
//                    anchors.verticalCenter: parent.verticalCenter
//                    selectByMouse: true
//                    text:"0"
//                    font.pixelSize: 14
//                    font.family: "微软雅黑"
//                }
//            }
//        }
//        Row{
//            spacing: 3
//            Text{
//                text:qsTr("G:")
//                font.pixelSize: 16
//                font.family: "微软雅黑"

//            }
//            Rectangle{
//                width: 36
//                height:20
//                border.width: 1
//                border.color: "black"
//                TextInput{
//                    anchors.horizontalCenter: parent.horizontalCenter
//                    anchors.verticalCenter: parent.verticalCenter
//                    selectByMouse: true
//                    text:"0"
//                    font.pixelSize: 14
//                    font.family: "微软雅黑"
//                }
//            }
//        }
//        Row{
//            spacing: 3
//            Text{
//                text:qsTr("B:")
//                font.pixelSize: 16
//                font.family: "微软雅黑"

//            }
//            Rectangle{
//                width: 36
//                height:20
//                border.width: 1
//                border.color: "black"
//                TextInput{
//                    anchors.horizontalCenter: parent.horizontalCenter
//                    anchors.verticalCenter: parent.verticalCenter
//                    selectByMouse: true
//                    text:"0"
//                    font.pixelSize: 14
//                    font.family: "微软雅黑"
//                }
//            }
//        }
//        Row{
//            spacing: 3
//            Text{
//                text:qsTr("#")
//                font.pixelSize: 16
//                font.family: "微软雅黑"

//            }
//            Rectangle{
//                width: 36
//                height:20
//                border.width: 1
//                border.color: "black"
//                TextInput{
//                    anchors.horizontalCenter: parent.horizontalCenter
//                    anchors.verticalCenter: parent.verticalCenter
//                    selectByMouse: true
//                    text:"0"
//                    font.pixelSize: 14
//                    font.family: "微软雅黑"
//                }
//            }
//        }
//    }
}


