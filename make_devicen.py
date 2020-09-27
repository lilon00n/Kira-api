def make_devicen(p, colors):
    strColors = ""
    transformFuncN = "%Device N \n"

    n = len(colors)
    k = n + n*3 - 1
    adds = n-1

    for color in colors:
        transformFuncN = transformFuncN + str(color["l"]) + " " + str(
            color["a"]) + " " + str(color["ba"]) + " % kcolor: "+color["name"]+" \n"

        strColors = strColors+"{"+color["name"]+"} "

    transformFuncN = transformFuncN+"% Blend L values\n"
    for x in range(n):
        transformFuncN = transformFuncN + \
            str(k)+" index " + str(n*3-2*x) + " index mul \n"

    for x in range(adds):
        transformFuncN = transformFuncN+"add "
    transformFuncN = transformFuncN+"\n"
    transformFuncN = transformFuncN+str(k+2)+" 1 roll % Bottom: L\n"
    transformFuncN = transformFuncN+"% Blend a values\n"
    for x in range(n):
        transformFuncN = transformFuncN + \
            str(k)+" index " + str((n*3-1)-2*x) + " index mul \n"
    for x in range(adds):
        transformFuncN = transformFuncN+"add "
    transformFuncN = transformFuncN+"\n"
    transformFuncN = transformFuncN+str(k+2)+" 1 roll % Bottom: a\n"
    transformFuncN = transformFuncN+"% Blend b values\n"
    for x in range(n):
        transformFuncN = transformFuncN + \
            str(k)+" index " + str((n*3-2)-2*x) + " index mul \n"
    for x in range(adds):
        transformFuncN = transformFuncN+"add "
    transformFuncN = transformFuncN+"\n"
    transformFuncN = transformFuncN+str(k+2)+" 1 roll % Bottom: b\n"
    pops = k+1
    for x in range(pops):
        transformFuncN = transformFuncN+"pop "
    transformFuncN = transformFuncN+"\n"

    devicen = p.create_devicen(
        "names={"+strColors+"} alternate=lab transform={{" + transformFuncN + "}} ")
    return devicen
