# Dibujo colores
        for index, color in enumerate(colorsJson, start=0):    
            ceros=""
            cero7=""
            cero5=""
            cero2=""
            for x in range(len(colorsJson)):
                if (x==index):
                    ceros= ceros +"1 "            
                    cero7= cero7 +"0.7 "            
                    cero5= cero5 +"0.5 "            
                    cero2= cero2 +"0.2 "            
                else:
                    ceros= ceros +"0 "
                    cero7= cero7 +"0 "
                    cero5= cero5 +"0 "
                    cero2= cero2 +"0 "
            optlist = "fontname=Arial fontsize=" + str(fsize)+ " encoding=unicode fillcolor={devicen " + str(devicen)+" "+ ceros +"}"
            print(optlist)
            textline = color["name"]
            textwidth = p.info_textline(textline, "width", optlist)

            p.fit_textline(textline, xGen-textwidth, y, optlist)

            p.fit_textline(color["inkCov"]+"%", xGen+20, y, optlist)
            
            p.set_graphics_option("fillcolor={ devicen " + str(devicen)+" "+ ceros +"}")
            p.rect(xGen+2, y+4, colorSize, 4)
            p.fill()
            p.set_graphics_option("fillcolor={ devicen " + str(devicen)+" "+ cero7 +"}")
            p.rect(xGen+2, y, colorSize, 4)
            p.fill()
            p.set_graphics_option("fillcolor={ devicen " + str(devicen)+" "+ cero5 +"}")
            p.rect(xGen+2+colorSize, y+4, colorSize, 4)
            p.fill()
            p.set_graphics_option("fillcolor={ devicen " + str(devicen)+" "+ cero2 +"}")
            p.rect(xGen+2+colorSize, y, colorSize, 4)
            p.fill()

            p.set_graphics_option("strokecolor={ devicen " + str(devicen)+" "+ ceros +"}")
            

            # Dibujo la linea separdora
            p.moveto(2*crop_size*72/25.4 + nalawidth , y-2)
            p.lineto(xGen + colorSize*2+percentageWidth,y-2)
            p.stroke()

            y=y-textHeight-8
