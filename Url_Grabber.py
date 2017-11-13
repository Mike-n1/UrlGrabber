import re
import os.path
import sys
import argparse


def version_info():
    VER = 'URL Grabber Version 1.0.0'
    AUTH = 'Author: n1'
    print "=========================================="
    print "  _    _ _____  _         _____           _     _               "
    print " | |  | |  __ \| |       / ____|         | |   | |              "
    print " | |  | | |__) | |      | |  __ _ __ __ _| |__ | |__   ___ _ __ "
    print " | |  | |  _  /| |      | | |_ | '__/ _` | '_ \| '_ \ / _ \ '__|"
    print " | |__| | | \ \| |____  | |__| | | | (_| | |_) | |_) |  __/ |   "
    print "  \____/|_|  \_\______|  \_____|_|  \__,_|_.__/|_.__/ \___|_|   "
    print "                                                             "
    print VER
    print AUTH
    print "==========================================="

def searchUrls(file):
    file = file.replace("\\","/")
    currentFile = open(file, "r").read()
    defaultUrlMask = "/{controller}/{action}"
    configTypes = {"Api": "WebApiConfig.cs", "Route": "RouteConfig.cs"}
    classInfo = re.findall(classPattern, currentFile)
    if not classInfo:
        return
    if classInfo[0][1] == "ApiController":
        configPath = file[:file.find('/Controllers/')] + "/App_Start/"+configTypes['Api']
        currentRoutePattern = configRoutesPattern['apiConfig']
    else:
        configPath = file[:file.find('/Controllers/')]+"/App_Start/"+configTypes['Route']
        currentRoutePattern = configRoutesPattern['routeConfig']
    try:
        configFile = open(configPath, "r").read()
        currentPathPattern = re.findall(currentRoutePattern, configFile)[0]
    except Exception:
        currentPathPattern = defaultUrlMask
    finded1 = re.findall(routePrefixPattern,currentFile)
    finded2 = re.findall(routeBeforeClassPattern, currentFile)
    if finded1:
        makeUrl(finded1[0], currentFile, 'classWithRoutePrefix', classInfo[0][0],  configMask = currentPathPattern)
        return
    elif finded2:
        routeMask = finded2[0].replace('[','{')
        routeMask = routeMask.replace(']','}')
        makeUrl(routeMask, currentFile, 'methodType', classInfo[0][0], configMask = currentPathPattern)
        return
    else:
        finded3 = re.findall(routeBeforeFunctPattern, currentFile)
        finded4 = re.findall(methodPattern, currentFile)
        if finded3:
            makeUrl('', currentFile, 'routeBeforeFunc', classInfo[0][0], configMask = currentPathPattern)
        if finded4:
            makeUrl(currentPathPattern, currentFile, 'methodType', classInfo[0][0], configMask = currentPathPattern)


def secondSearch(funcs, type, file):
    if type == 'methodType':
        finds = re.findall(methodPattern, file)
        newFuncList = []
        ret = []
        for f in finds:
            if (f[1]+" ({})".format(f[2])) not in funcs:
                ret.append(f)
                newFuncList.append(f[1]+" ({})".format(f[2]))
        newFuncList = funcs + newFuncList
        if newFuncList != funcs:
            ret += secondSearch(newFuncList, 'defaultPublic', file)
        return ret
    if type == 'defaultPublic':
        finds = re.findall(publicFuncPattren, file)
        ret = []
        for f in finds:
            if ((f[0] + " ({})".format(f[1])) not in funcs):
                f_temp = tuple(['HttpGet or HttpPost'] + list(f))
                ret.append(f_temp)
        return ret



def makeUrl(urlMask, file, type, classname = None, configMask = None):
    if type == "classWithRoutePrefix":
        finds = re.findall(routeBeforeFunctPattern, file)
        funcList = []
        for find in finds:
            finalUrl = "/{}/{}".format(urlMask, find[0])+" ({})".format(find[2])
            URLS.append(finalUrl)
            funcList.append(find[1]+" ({})".format(find[2]))
        withMethod = secondSearch(funcList, 'methodType', file)
        if withMethod:
            for u in withMethod:
                finalUrl = configMask.replace("{controller}", classname)
                finalUrl = finalUrl.replace("{action}", u[1])
                URLS.append(u[0]+" => "+"/"+finalUrl.strip("/")+" ({})".format(u[2]))
        return

    elif type == "methodType":
        finds = re.findall(methodPattern, file)
        funcList = []
        for find in finds:
            funcList.append(find[1] + " ({})".format(find[2]))
            method = find[0]
            args = find[2]
            finalUrl = urlMask.replace("{controller}", classname)
            finalUrl = finalUrl.replace("{action}", find[1])
            URLS.append(method+" => "+"/"+finalUrl.strip("/")+" ({})".format(args))
    elif type == "routeBeforeFunc":
        funcList = []
        finds = re.findall(routeBeforeFunctPattern, file)
        for find in finds:
            funcList.append(find[1] + " ({})".format(find[2]))
            finalUrl = "/"+find[0]
            URLS.append(finalUrl)
    withMethod = secondSearch(funcList, 'defaultPublic', file)
    if withMethod:
        for u in withMethod:
            finalUrl = configMask.replace("{controller}", classname)
            finalUrl = finalUrl.replace("{action}", u[1])
            URLS.append(u[0] + " => " + "/" + finalUrl.strip("/") + " ({})".format(u[2]))

def step((ext), dirname, names):
    ext = ext.lower()

    for name in names:
        if name.lower().endswith(ext):
            searchUrls(os.path.join(dirname, name))


classPattern = r"class\s([\w]+)Controller\s*:\s*([a-zA-z]*Controller)"
configRoutesPattern = {"apiConfig": "Routes\.MapHttpRoute\([\S\s]+routeTemplate:[\s]*\"([\w{}\/]+)\"+[\S\s]+\)", "routeConfig":"routes\.MapRoute\([\S\s]+url:[\s]*\"([\w{}\/]+)\"+[\S\s]+\)"}
routePrefixPattern = r"\[RoutePrefix\(\"([\w\/]+)\"\)\][\s]+(?:[\/]*\[.*\][\s]+)*public class"
routeBeforeClassPattern = r"\[Route\(\"([\w\[\]/]+)\"\)\][\s]+public.*class[ ]"
routeBeforeFunctPattern = r"\[Route\(\"([\w]+)\"\)\][\s]+(?:[\/]*\[.*\][\s]+)*public[\s\w<>]+\s([\w]+)\(([\w\s,=?]*)\)"
methodPattern = r"\[(HttpGet|HttpPost|HttpDelete|HttpPut|HttpHead|HttpOptions|HttpPatch)\][\s]+(?:[\/]*\[.*\][\s]+)*public[\s\w<>]+\s([\w]+)\(([\w\s,=?\.]*)\)"
publicFuncPattren = r"public[\s\w<>]+\s([\w]+)\(([\w\s,=?\.]*)\)"

URLS = []
EXTEN = '.cs'

if __name__ == "__main__":
    parse = argparse.ArgumentParser()
    parse.add_argument('-v', '--version', action='store_true', default=False, help='Version Information')
    parse.add_argument('-d', '--dir', type=str, default='', help='Target Directory')
    parse.add_argument('-o', '--out_file', type=str, default='', help='Specify output file')
    args = parse.parse_args()

    if len(sys.argv) <= 1:
        parse.print_help()
        sys.exit(0)

    if args.version:
        version_info()

    if args.dir:
        version_info()
        os.path.walk(args.dir, step, (EXTEN))
        URLS.sort()
        URLS = set(URLS)
        if args.out_file != '':
            fl = open(args.out_file, "w")
            for i in URLS:
                fl.write(i+"\n")
            fl.close()
        for i in URLS:
            print i
        print "\n"
        print "{} urls found".format(len(URLS))
        exit()