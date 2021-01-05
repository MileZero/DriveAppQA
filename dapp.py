import json, requests, sys
#routeId = "4a36c49c-694d-4001-beb7-4455b13d39fb"

def getPackageIdList(routeId):
    routeRequest = requests.get("http://alamo."+executionType+".milezero.com/alamo-war/api/plannedroutes/stopdetails/{}".format(routeId))
    res = routeRequest.json()
    routeStopDetail = res["routeStopDetail"]
    if (routeStopDetail["routeState"] == "FAILURE_DURING_SUBMISSION"):
        print("routeId to be re-executed : {}".format(routeId))
    stops = routeStopDetail["stops"]
    for stop in stops:
        print('{}'.format(stop["id"]))
        if stop["id"]=="stop0":
            continue
        for package in stop["stopPackages"]:
            if("packageId" not in package):
                continue
            getJobId(package["packageId"])

def getJobId(packageId):
    jobRequest = requests.get("http://switchboard."+executionType+".milezero.com/switchboard-war/api/package?keyType=pi&keyValue={}".format(packageId)).json()
    packageRecords = jobRequest["packageRecords"]
    for packageRecord in packageRecords:
        print(' {}'.format(packageRecord["packageDetails"]["shipmentBarcode"]))
        checkJob(packageRecord["planningDetails"]["jobId"])

def checkJob(jobId):
    jobStates=['PICK_UP','SCAN','SIGN','DELIVER']
    response = requests.get("http://earp."+executionType+".milezero.com/earp-server/api/v2/3e59b207-cea5-4b00-8035-eed1ae26e566/jobs/{}".format(jobId)).json()
    trackingEvents = response["trackingEvents"]
    #print("Events For {} ".format(jobId))
    for jobState in trackingEvents:
        if jobState['jobState'] in jobStates:
            print("  {} -> {} ".format(jobState['jobState'], jobState['completionState']))

def jobStateCheck(jobIdList):
    jobStates=['PICK_UP','SCAN','SIGN','DELIVER']
    for jobId in jobIdList:
        response = requests.get("http://earp."+executionType+".milezero.com/earp-server/api/v2/3e59b207-cea5-4b00-8035-eed1ae26e566/jobs/{}".format(jobId)).json()
        trackingEvents = response["trackingEvents"]
        print("Events For {} ".format(jobId))
        for jobState in trackingEvents:
            if jobState['jobState'] in jobStates:
                print(" {} -> {} ".format(jobState['jobState'], jobState['completionState']))

def getJobIdList(packageIdList):
    for packageId in packageIdList:
        jobRequest = requests.get("http://switchboard."+executionType+".milezero.com/switchboard-war/api/package?keyType=pi&keyValue={}".format(packageId)).json()
        packageRecords = jobRequest["packageRecords"]
        for packageRecord in packageRecords:
            jobIdList.append(packageRecord["planningDetails"]["jobId"])
    return jobIdList


if(len(sys.argv)!=3):
    print("Usage format: dapp.py stage/prod routeId")
    sys.exit(1)

executionType = sys.argv[1]
routeId = sys.argv[2]
getPackageIdList(routeId)