def make_devicen(colors):
        strColors=""
        transformFunc2 =  """% DeviceN transform function for N=2 in CIE L*a*b* color space\n
        % CLab color values of input colors must be listed here:\n
        50.45 77.14 34.26				% kcolor 1: Rojo especial \n
        26.19 31.34 -20.99			% ñcolor 2: PANTONE 261 C\n
        % Bblend L values\n
        7 index 6 index mul	% t1*L1\n
        7 index 4 index mul	% t2*L2\n
        add\n
        9 1 roll				% vbottom: L\n
        % Bblend a values\n
        7 index 5 index mul	% t1*a1\n
        7 index 3 index mul	% t2*a2\n
        add\n
        9 1 roll				% vbottom: a\n
        % Bblend b values\n
        7 index 4 index mul	% t1*b1\n
        7 index 2 index mul	% t2*b2\n
        add\n
        9 1 roll				% bottom: b\n
        pop pop pop pop pop pop pop pop\n"""

        transformFuncN= "%Device N \n"

        n=len(colors)
        k= n+ n*3 -1
        adds= n-1

        for color in colors:
            transformFuncN = transformFuncN+ str(color["l"]) +" " +str(color["a"]) + " " +str(color["ba"]) + " % kcolor: "+color["name"]+" \n"

            strColors=strColors+"{"+color["name"]+"} "
        
        transformFuncN=transformFuncN+"% Blend L values\n"
        for x in range(n):
            transformFuncN=transformFuncN+str(k)+" index " +str(n*3-2*x) +" index mul \n"
        
        for x in range(adds):
            transformFuncN=transformFuncN+"add "  
        transformFuncN=transformFuncN+"\n"
        transformFuncN=transformFuncN+str(k+2)+" 1 roll % Bottom: L\n" 
        transformFuncN=transformFuncN+"% Blend a values\n"
        for x in range(n):
            transformFuncN=transformFuncN+str(k)+" index " +str((n*3-1)-2*x) +" index mul \n"
        for x in range(adds):
            transformFuncN=transformFuncN+"add " 
        transformFuncN=transformFuncN+"\n"
        transformFuncN=transformFuncN+str(k+2)+" 1 roll % Bottom: a\n"    
        transformFuncN=transformFuncN+"% Blend b values\n"
        for x in range(n):
            transformFuncN=transformFuncN+str(k)+" index " +str((n*3-2)-2*x) +" index mul \n"
        for x in range(adds):
            transformFuncN=transformFuncN+"add "     
        transformFuncN=transformFuncN+"\n"
        transformFuncN=transformFuncN+str(k+2)+" 1 roll % Bottom: b\n"    
        pops=k+1
        for x in range(pops):
            transformFuncN=transformFuncN+"pop "     
        transformFuncN=transformFuncN+"\n"
        print(transformFuncN)

        devicen = p.create_devicen("names={"+strColors+"} alternate=lab transform={{" + transformFuncN + "}} ");
        return devicen
    