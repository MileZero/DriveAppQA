import json, requests, sys

orgId = "3e59b207-cea5-4b00-8035-eed1ae26e566"
routeId = "4a36c49c-694d-4001-beb7-4455b13d39fb"
packageIdList0 = []
jobIdList0 = []
barcodeList0 = []
packageIdList = []
jobIdList = []
barcodeList = []
jobid_barcodeId_dict = {}
stopn_pkgid_dict = {}
packageid_jobid_dict = {}

def getStopsList(routeId):
    routeRequest = requests.get("http://alamo.stage.milezero.com/alamo-war/api/plannedroutes/stopdetails/{}".format(routeId))
    res = routeRequest.json()
    routeStopDetail = res["routeStopDetail"]

    if (routeStopDetail["routeState"] == "FAILURE_DURING_SUBMISSION"):
       print("routeId to be re-executed : {}".format(routeId))
    stops = routeStopDetail["stops"]
    return stops

def getPackageIdList(stops):
    i = 1
    for package in stops[0]["stopPackages"]:
        #if package["packageId"] not in packageIdList:
        packageIdList0.append(package["packageId"])
    #packageIdList0 = stop[0]["stopPackages"]["packageId"]

    for stop in stops[1:-1]:
        print('stop{}'.format(i))
        packageIdListinner = []
        for package in stop["stopPackages"]:
            #if package["packageId"] not in packageIdList:
            print(package["packageId"])
            packageIdList.append(package["packageId"])
            packageIdListinner.append(package["packageId"])
        stopn_pkgid_dict["stop"+str(i)] = packageIdListinner
        i = i+1
    print("stopn_pkgid_dict")
    print(stopn_pkgid_dict)
    return packageIdList


def getJobIdList(packageIdList):
    for packageId in packageIdList:
        jobRequest = requests.get("http://switchboard.stage.milezero.com/switchboard-war/api/package?keyType=pi&keyValue={}".format(packageId)).json()
        packageRecords = jobRequest["packageRecords"]
        

        for packageRecord in packageRecords:
            jobIdList.append(packageRecord["planningDetails"]["jobId"])
            barcodeList.append(packageRecord["packageDetails"]["shipmentBarcode"])
            packageid_jobid_dict[packageId] = packageRecord["planningDetails"]["jobId"]
            jobid_barcodeId_dict[packageRecord["planningDetails"]["jobId"]] = packageRecord["packageDetails"]["shipmentBarcode"]

    print('========packageid_jobid_dict========')
    print(packageid_jobid_dict)
    print('========jobid_barcodeId_dict========')
    print(jobid_barcodeId_dict)
    return jobIdList


def jobStateCheck(jobIdList):
    jobStates0 = ['PICK_UP']
    jobStates=['ARRIVE', 'SCAN','SIGN','DELIVER']

    for key in stopn_pkgid_dict:
        pkg_id_list = stopn_pkgid_dict[key]

        for pkg_id in pkg_id_list:
            job_id = packageid_jobid_dict[pkg_id]
            StateRequest = requests.get("http://earp.stage.milezero.com/earp-server/api/v2/3e59b207-cea5-4b00-8035-eed1ae26e566/jobs/{}".format(job_id)).json()
            trackingEvents = StateRequest["trackingEvents"]

            for jobState in trackingEvents:
                if jobState['jobState'] in jobStates and jobState['completionState'] == 'DONE':
                    print("{}, Barcode:{} and {} is completed successfully".format(key,
                        jobid_barcodeId_dict[job_id], jobState['jobState']))





#    for jobId in jobIdList:
#        StateRequest = requests.get("http://earp.stage.milezero.com/earp-server/api/v2/3e59b207-cea5-4b00-8035-eed1ae26e566/jobs/{}".format(jobId)).json()
#        trackingEvents = StateRequest["trackingEvents"]

#        for jobState in trackingEvents:
#            if jobState['jobState'] in jobStates and jobState['completionState'] == 'DONE':
                
#                pkg_ids = []
#                pkg_ids.append(list(packageid_jobid_dict.keys())[list(packageid_jobid_dict.values()).index(jobId)])
                
#                print(stopn_pkgid_dict)
#                print("{}, Barcode:{} and {} is completed successfully".format(
#                    list(stopn_pkgid_dict.keys())[list(stopn_pkgid_dict.values()).index(pkg_ids)],
#                    jobid_barcodeId_dict[jobId], jobState['jobState']))



stops = getStopsList(routeId)
packageIdList = getPackageIdList(stops)
jobIdList = getJobIdList(packageIdList)
jobStateCheck(jobIdList)

#def printJobStates():

#def getPickupstatus:
    #stops = getStopsList(routeId)


print('***barcodelist***')
print(barcodeList)
print("***packagelist***")
print(packageIdList)