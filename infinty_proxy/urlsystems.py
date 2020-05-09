#
# /systems URL handling
#
# This module is the most complicated and where all of the interesting
# interaction with the thermostat happens.
#

import copy
from datetime import datetime
import logging
import xml.etree.ElementTree as ET

from httpobj import HttpRequest, HttpResponse, addUrl



# This is data shared between the API module and this one.  It lives here since
# the interaction with the thermostat is more critical than the API side and so
# these variables are tightly coupled with this module.

# The serial number of the thermostat
activeThermostatId = None
# Raw XML tree from the device's configuration last uploaded to us (../config
# URL).  Also required to send updated configuration since we will use the
# last known configuration and modify it as needed.
configFromDevice = None
# Parsed status of zones
statusZones = {}
# Parsed configuration of zones
configZones = {}
# Some parsed status of device for API module to use
currentMode = None
tempUnits = None

# The API module updates these variables for this module to use to send
# configuration changes to the device.  Once the configuration has been
# sent to the device (next time it polls for an update) these variables
# are reset back to None
pendingActionHold = None
pendingActionActivity = None
pendingActionTemp = None
pendingActionUntil = None













# Information about the device (serial numbers and modules) but not
# current configuration.
def urlSystemsProfile(request):

	xmlBodyStr = request.bodyDict["data"][0]

	logging.debug("  SN={}".format(request.pathDict["serialNumber"]))
	logging.debug("  body={}".format(xmlBodyStr))

	response = HttpResponse.okResponse()

	response.headers.append(("Cache-Control", "private"))
	response.addServerHeader()
	response.addRequestContextHeader()
	response.addAccessControlHeader()
	response.addDateHeader()
	response.addContentLengthHeader(0)

	return response

addUrl("/systems/(?P<serialNumber>.+)/profile$", urlSystemsProfile)



# Device tells us the dealer information that has been programmed into the
# device.  (We do not send back any information.)
def urlSystemsDealer(request):

    xmlBodyStr = request.bodyDict["data"][0]

    logging.debug("  SN={}".format(request.pathDict["serialNumber"]))
    logging.debug("  body={}".format(xmlBodyStr))

    response = HttpResponse.okResponse()

    response.headers.append(("Cache-Control", "private"))
    response.headers.append(("Etag", "\"00f5713108d7b88afec10590\""))
    response.addServerHeader()
    response.addRequestContextHeader()
    response.addAccessControlHeader()
    response.addDateHeader()
    response.addContentLengthHeader(0)

    return response

addUrl("/systems/(?P<serialNumber>.+)/dealer$", urlSystemsDealer)



# Device tells us about its internal furance devices (built-in heating?)
def urlSystemsIDUConfig(request):

    xmlBodyStr = request.bodyDict["data"][0]

    logging.debug("  SN={}".format(request.pathDict["serialNumber"]))
    logging.debug("  body={}".format(xmlBodyStr))

    response = HttpResponse.okResponse()

    response.headers.append(("Cache-Control", "private"))
    response.headers.append(("Etag", "\"0357dfbd08d7b88aff27ec1e\""))
    response.addServerHeader()
    response.addRequestContextHeader()
    response.addAccessControlHeader()
    response.addDateHeader()
    response.addContentLengthHeader(0)

    return response

addUrl("/systems/(?P<serialNumber>.+)/idu_config$", urlSystemsIDUConfig)



# Device tells us about its external furnace devices (air conditioning? secondary
# heating or cooling systems?)
def urlSystemsODUConfig(request):

    xmlBodyStr = request.bodyDict["data"][0]

    logging.debug("  SN={}".format(request.pathDict["serialNumber"]))
    logging.debug("  body={}".format(xmlBodyStr))

    response = HttpResponse.okResponse()

    response.headers.append(("Cache-Control", "private"))
    response.headers.append(("Etag", "\"039f3ffe08d7b88aff98b843\""))
    response.addServerHeader()
    response.addRequestContextHeader()
    response.addAccessControlHeader()
    response.addDateHeader()
    response.addContentLengthHeader(0)

    return response

addUrl("/systems/(?P<serialNumber>.+)/odu_config$", urlSystemsODUConfig)



# Device tells us current status, such as temperature, humidity, current
# schedule activity, temp set points, and if it is running.  We can respond
# with a list of booleans to ask the device to make another /systems call
# soon, such as to download updated configuration.  We can also adjust the
# rate at which it polls for the various /systems calls here.
def makeSystemsStatusResponse(request, serverHasChanges, configHasChanges):

	serialNumber = request.pathDict["serialNumber"]

	statusRoot = ET.Element("status")

	statusRoot.set("version", "1.42")
	statusRoot.set("xmlns:atom", "http://www.w3.org/2005/Atom")

	atomLink = ET.Element("atom:link")
	atomLink.set("rel", "self")
	atomLink.set("href", "http://www.api.ing.carrier.com/systems/" + serialNumber + "/status")
	statusRoot.append(atomLink)

	atomLink = ET.Element("atom:link")
	atomLink.set("rel", "http://www.api.ing.carrier.com/rels/system")
	atomLink.set("href", "http://www.api.ing.carrier.com/systems/" + serialNumber)
	statusRoot.append(atomLink)

	tsEl = ET.Element("timestamp")
	tsEl.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
	statusRoot.append(tsEl)

	el = ET.Element("pingRate")
	el.text = "10"
	statusRoot.append(el)

	el = ET.Element("iduStatusPingRate")
	el.text = "93600"
	statusRoot.append(el)

	el = ET.Element("iduFaultsPingRate")
	el.text = "86400"
	statusRoot.append(el)

	el = ET.Element("oduStatusPingRate")
	el.text = "90000"
	statusRoot.append(el)

	el = ET.Element("oduFaultsPingRate")
	el.text = "82800"
	statusRoot.append(el)

	el = ET.Element("historyPingRate")
	el.text = "75600"
	statusRoot.append(el)

	el = ET.Element("equipEventsPingRate")
	el.text = "79200"
	statusRoot.append(el)

	el = ET.Element("rootCausePingRate")
	el.text = "72000"
	statusRoot.append(el)

	el = ET.Element("serverHasChanges")
	if serverHasChanges:
		el.text = "true"
	else:
		el.text = "false"
	statusRoot.append(el)

	el = ET.Element("configHasChanges")
	if configHasChanges:
		el.text = "true"
	else:
		el.text = "false"
	statusRoot.append(el)

	el = ET.Element("dealerHasChanges")
	el.text = "false"
	statusRoot.append(el)

	el = ET.Element("dealerLogoHasChanges")
	el.text = "false"
	statusRoot.append(el)

	el = ET.Element("oduConfigHasChanges")
	el.text = "false"
	statusRoot.append(el)

	el = ET.Element("iduConfigHasChanges")
	el.text = "false"
	statusRoot.append(el)

	el = ET.Element("utilityEventsHasChanges")
	el.text = "false"
	statusRoot.append(el)

	el = ET.Element("sensorConfigHasChanges")
	el.text = "false"
	statusRoot.append(el)

	el = ET.Element("sensorProfileHasChanges")
	el.text = "false"
	statusRoot.append(el)

	el = ET.Element("sensorDiagnosticHasChanges")
	el.text = "false"
	statusRoot.append(el)

	xmlBodyStr = ET.tostring(statusRoot, "utf-8")

	response = HttpResponse.okResponse()

	response.headers.append(("Cache-Control", "private"))
	response.addContentLengthHeader(len(xmlBodyStr))
	response.addContentTypeHeader("application/xml; charset=utf-8")
	response.addServerHeader()
	response.addRequestContextHeader()
	response.addAccessControlHeader()
	response.addDateHeader()

	response.body = xmlBodyStr

	return response


def urlSystemsStatus(request):

	global configFromDevice
	global statusZones
	global currentMode
	global tempUnits

	xmlStringData = request.bodyDict["data"][0]

	logging.debug("  SN={}".format(request.pathDict["serialNumber"]))

	xmlRoot = ET.fromstring(xmlStringData)

	if xmlRoot.attrib['version'] != "1.7":
		logging.warning("Unexpected client version: %s" % (xmlRoot.attrib['version'], ))
		return makeSystemsStatusResponse(request, False, False)

	currentMode = xmlRoot.find("./cfgtype").text
	tempUnits = xmlRoot.find("./cfgem").text

	statusZones = {}

	for zone in xmlRoot.findall("./zones/zone"):

		if zone.find("./enabled").text != "on":
			continue

		zoneId = zone.attrib['id']

		zoneObj = {
			"name": zone.find("./name").text,
			"activity": zone.find("./currentActivity").text,
			"temperature": zone.find("./rt").text,
			"humidity": zone.find("./rh").text,
			"heatTo": zone.find("./htsp").text,
			"coolTo": zone.find("./clsp").text,
			"fan": zone.find("./fan").text,
			"hold": zone.find("./hold").text,
			"until" : zone.find("./otmr").text,
			"zoneConditioning" : zone.find("./zoneconditioning").text
		}

		statusZones[zoneId] = zoneObj



	if pendingActionHold:
		logging.info("Returned has status changes")
		response = makeSystemsStatusResponse(request, True, True)
	elif not configFromDevice:
		logging.info("Returned want config")
		response = makeSystemsStatusResponse(request, True, True)
	else:
		logging.info("Returned NO status changes")
		response = makeSystemsStatusResponse(request, False, False)

	return response

addUrl("/systems/(?P<serialNumber>.+)/status$", urlSystemsStatus)



# I don't have utility events set up in the themostat to test this.
def urlSystemsUtilityEvents(request):

	logging.debug("  SN={}".format(request.pathDict["serialNumber"]))

	utilityXMLStr = '<utility_events version="1.42" xmlns:atom="http://www.w3.org/2005/Atom"/>'

	response = HttpResponse.okResponse()

	response.headers.append(("Cache-Control", "private"))
	response.addContentLengthHeader(len(utilityXMLStr))
	response.addContentTypeHeader("application/xml; charset=utf-8")
	response.addServerHeader()
	response.addRequestContextHeader()
	response.addAccessControlHeader()
	response.addDateHeader()

	response.body = utilityXMLStr

	return response

addUrl("/systems/(?P<serialNumber>.+)/utility_events$", urlSystemsUtilityEvents)



# The device tells us when it has made a change such as appling a new
# configuration.  This both confirms a configuration change that we may have
# requested in the .../config response, but also if a person changes the config
# on the thermostat's touch screen.
def makeSystemsNotificationsResponse():

	response = HttpResponse.okResponse()

	response.headers.append(("Cache-Control", "private"))
	response.addContentTypeHeader("application/xml; charset=utf-8")
	response.addServerHeader()
	response.addRequestContextHeader()
	response.addAccessControlHeader()
	response.addDateHeader()
	response.addContentLengthHeader(0)

	return response


def urlSystemsNotifications(request):

	xmlStringData = request.bodyDict["data"][0]

	logging.debug("  SN={}".format(request.pathDict["serialNumber"]))

	xmlRoot = ET.fromstring(xmlStringData)

	if xmlRoot.attrib['version'] != "1.7":
		logging.warning("Unexpected client version: %s" % (xmlRoot.attrib['version'], ))
		return makeSystemsNotificationsResponse()

	responseCode = xmlRoot.find("./notification/code").text
	responseMessage = xmlRoot.find("./notification/message").text

	if responseCode != "200":
		logging.warning("Thermostat responded with code: %s, message %s" % (responseCode, responseMessage))
		return makeSystemsNotificationsResponse()

	# Save for api access?

	logging.info("Thermostat notification: %s %s" % (responseCode, responseMessage))

	return makeSystemsNotificationsResponse()

addUrl("/systems/(?P<serialNumber>.+)/notifications$", urlSystemsNotifications)



# The device is requesting an updated configuration from us.
def makeSystemsConfigResponse(xmlBodyStr):

	response = HttpResponse.okResponse()

	response.headers.append(("Cache-Control", "private"))
	response.addContentLengthHeader(len(xmlBodyStr))
	response.addContentTypeHeader("application/xml; charset=utf-8")
	response.headers.append(("Etag", "\"00de388808d7b88cd8f146a1\""))
	response.addServerHeader()
	response.addRequestContextHeader()
	response.addAccessControlHeader()
	response.addDateHeader()

	response.body = xmlBodyStr

	return response


def urlSystemsConfig(request):

	global configFromDevice
	global pendingActionHold
	global pendingActionActivity
	global pendingActionUntil
	global pendingActionTemp


	serialNumber = request.pathDict["serialNumber"]

	logging.debug("  SN={}".format(serialNumber))

	# Can't return config unless we know what the device is already using
	if configFromDevice == None:
		return makeSystemsConfigResponse("")

	newConfigRoot = copy.deepcopy(configFromDevice)

	newConfigRoot.set("version", "1.42")
	newConfigRoot.set("xmlns:atom", "http://www.w3.org/2005/Atom")

	tsEl = ET.Element("timestamp")
	tsEl.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
	newConfigRoot.insert(0, tsEl)

	atomLink = ET.Element("atom:link")
	atomLink.set("rel", "http://www.api.ing.carrier.com/rels/system")
	atomLink.set("href", "http://www.api.ing.carrier.com/systems/" + serialNumber)
	newConfigRoot.insert(0, atomLink)

	atomLink = ET.Element("atom:link")
	atomLink.set("rel", "self")
	atomLink.set("href", "http://www.api.ing.carrier.com/systems/" + serialNumber + "/config")
	newConfigRoot.insert(0, atomLink)

	for zone in newConfigRoot.findall("./zones/zone"):

		if zone.find("./enabled").text != "on":
			continue

		if zone.attrib['id'] != "1":
			continue

		if pendingActionHold:
			if pendingActionActivity:
				zone.find("./hold").text = "on"
				zone.find("./holdActivity").text = pendingActionActivity
				zone.find("./otmr").text = pendingActionUntil
			else:
				zone.find("./hold").text = "off"
				zone.find("./holdActivity").text = ""
				zone.find("./otmr").text = ""

			if pendingActionActivity == "manual":
				for activity in zone.findall("./activities/activity"):

					if activity.attrib['id'] != "manual":
						continue

					activity.find("./htsp").text = str(pendingActionTemp)

	pendingActionHold = None
	pendingActionActivity = None
	pendingActionUntil = None
	pendingActionTemp = None

	xmlDataStr = ET.tostring(newConfigRoot, "utf-8")
	return makeSystemsConfigResponse(xmlDataStr)

addUrl("/systems/(?P<serialNumber>.+)/config$", urlSystemsConfig)



# The device is telling us about root causes of something?
def makeSystemsRootCauseResponse():

	response = HttpResponse.errorResponse(404, "Not found")
	#response = HttpResponse.okResponse()

	#response.headers.append(("Cache-Control", "private"))
	#response.addContentTypeHeader("application/xml; charset=utf-8")
	#response.addServerHeader()
	#response.addRequestContextHeader()
	#response.addAccessControlHeader()
	#response.addDateHeader()
	#response.addContentLengthHeader(0)

	return response


def urlSystemsRootCause(request):

	xmlStringData = request.bodyDict["data"][0]

	logging.info("Root Cause {}".format(xmlStringData))

	return makeSystemsRootCauseResponse()

addUrl("/systems/(?P<serialNumber>.+)/root_cause$", urlSystemsRootCause)



# The device is telling us about about faults in external devices?
def makeSystemsOduFaultsResponse():

	response = HttpResponse.errorResponse(404, "Not found")
	#response = HttpResponse.okResponse()

	#response.headers.append(("Cache-Control", "private"))
	#response.addContentTypeHeader("application/xml; charset=utf-8")
	#response.addServerHeader()
	#response.addRequestContextHeader()
	#response.addAccessControlHeader()
	#response.addDateHeader()
	#response.addContentLengthHeader(0)

	return response


def urlSystemsOduFaults(request):

	xmlStringData = request.bodyDict["data"][0]

	logging.info("ODU faults {}".format(xmlStringData))

	return makeSystemsOduFaultsResponse()

addUrl("/systems/(?P<serialNumber>.+)/odu_faults$", urlSystemsOduFaults)




# The device is telling us about its configuration.  It appears that just about
# anything that can be controlled on the touch screen will be included here,
# including the full activity schedule, and what devices are attached (gas, A/C,
# etc).
def makeSystemsResponse():

	response = HttpResponse.okResponse()

	response.headers.append(("Cache-Control", "private"))
	response.headers.append(("Etag", "\"0180958508d7b88afdc6a55c\""))
	response.addServerHeader()
	response.addRequestContextHeader()
	response.addAccessControlHeader()
	response.addDateHeader()
	response.addContentLengthHeader(0)

	return response



def urlSystems(request):

	global activeThermostatId
	global configFromDevice
	global configZones

	serialNumber = request.pathDict["serialNumber"]
	xmlStringData = request.bodyDict["data"][0]

	logging.debug("  SN={}".format(serialNumber))
	logging.debug("  body={}".format(xmlStringData))

	xmlRoot = ET.fromstring(xmlStringData)

	if xmlRoot.attrib['version'] != "1.7":
		logging.warning("Unexpected client version: %s" % (xmlRoot.attrib['version'], ))
		return makeSystemsResponse()

	currentMode = xmlRoot.find("./config/mode").text
	tempUnits = xmlRoot.find("./config/cfgem").text

	activeThermostatId = serialNumber
	configFromDevice = xmlRoot.find("./config")

	configZones = {}

	for zone in xmlRoot.findall("./config/zones/zone"):

		zoneId = zone.attrib['id']

		configZoneObj = {
			"activities": {},
			"schedule": {}
		}

		for activity in zone.findall("./activities/activity"):

			activityId = activity.attrib['id']

			activityObj = {
				"heatTo": activity.find("./htsp").text,
				"coolTo": activity.find("./clsp").text,
				"fan": activity.find("./fan").text
			}

			configZoneObj["activities"][activityId] = activityObj

		for day in zone.findall("./program/day"):

			dayId = day.attrib['id']

			periodList = {}

			for period in day.findall("./period"):

				periodId = int(period.attrib['id'])

				periodObj = {
					"activity": period.find("./activity").text,
					"time": period.find("./time").text,
					"enabled": period.find("./enabled").text == "on"
				}

				periodList[periodId] = periodObj

			configZoneObj["schedule"][dayId] = periodList

		configZones[zoneId] = configZoneObj


	return makeSystemsResponse()

addUrl("/systems/(?P<serialNumber>[^/]+)$", urlSystems)
