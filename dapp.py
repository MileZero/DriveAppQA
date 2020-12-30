import json, requests, sys

orgId = "3e59b207-cea5-4b00-8035-eed1ae26e566"
routeId = "4a36c49c-694d-4001-beb7-4455b13d39fb"
packageIdList = []
jobIdList = []

def getPackageIdList(routeId):
    routeRequest = requests.get("http://alamo.stage.milezero.com/alamo-war/api/plannedroutes/stopdetails/{}".format(routeId))
    res = routeRequest.json()
    routeStopDetail = res["routeStopDetail"]

    if (routeStopDetail["routeState"] == "FAILURE_DURING_SUBMISSION"):
        print("routeId to be re-executed : {}".format(routeId))
    stops = routeStopDetail["stops"]
    i = 0
    for stop in stops[:-1]:
        print('stop {}'.format(i))
        i = i+1
        for package in stop["stopPackages"]:
            if package["packageId"] not in packageIdList:
                print(package["packageId"])
                packageIdList.append(package["packageId"])
    return packageIdList


def getJobIdList(packageIdList):
    for packageId in packageIdList:
        jobRequest = requests.get("http://switchboard.stage.milezero.com/switchboard-war/api/package?keyType=pi&keyValue={}".format(packageId)).json()
        packageRecords = jobRequest["packageRecords"]

        for packageRecord in packageRecords:
            jobIdList.append(packageRecord["planningDetails"]["jobId"])
    return jobIdList


def jobStateCheck(jobIdList):
    jobStates=['PICK_UP','SCAN','SIGN','DELIVER']



    for jobId in jobIdList:
        StateRequest = requests.get("http://earp.stage.milezero.com/earp-server/api/v2/3e59b207-cea5-4b00-8035-eed1ae26e566/jobs/{}".format(jobId)).json()
        trackingEvents = StateRequest["trackingEvents"]

        for jobState in trackingEvents:
            if jobState['jobState'] in jobStates and jobState['completionState'] == 'DONE':
                print("{} and {} is completed successfully".format(jobId, jobState['jobState']))



packageIdList = getPackageIdList(routeId)
jobIdList = getJobIdList(packageIdList)
jobStateCheck(jobIdList)