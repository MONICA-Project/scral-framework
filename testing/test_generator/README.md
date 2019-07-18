# CrowdHeatmapSimulation

It includes Java project that allows to simulate crowd people in a specific area.

## Wristband Simulation

Derives from Arnaud source code that allows to push simulated position on SCRAL. Instruction to build:

### Pre-Requirements

- Ensure having Java installed (Version 1.8)
- Download and install gradle [See this link for Windows][https://www.tutorialspoint.com/gradle/gradle_installation.htm]

### Build Procedure

- Go to folder $REPOROOT\wristband_simulation
- Type command: 

	```console
	$ gradle uberJar
	```
## Execute Simulation

- Go to folder $REPOROOT\wristband_simulation\build\libs
- Type command: 

	```console
	$ java -jar $JAR_CREATED $PATH_SETTINGS
	```
	
 where: 
 
-	$PATH_SETTINGS is the path of settings (see [$REPOROOT\settings\settingsApplication.conf](settings/settingsApplication.conf))
-	$NUMBER_WRISTBANDS (number of wristband)
-	$START_INDEX (index start for wristband creation)
-	$VERSIONJAR (version jar indicated in build.gradle file
-	$PUSH_URL=http://monappdwp3.monica-cloud.eu:8420/scral/v1.0/wristband-gw/wearable/localization (url for pushing simulated data)
-	$JAR_CREATED=Toto-$VERSIONJAR.jar (Jar to launch)

## Scripts

- Folder $REPOROOT\wristband_simulation:

	```console
	$ sh buidProject
	```
	It launches build java project
	```console
	$ sh launch.sh
	```	
	It launches simulation with associated file settings reported in [$REPOROOT\settings\settingsApplication.conf](settings/settingsApplication.conf)

## Settings

Content of file settings (see [$REPOROOT\settings\settingsApplication.conf](settings/settingsApplication.conf)): 
 
-	**URL**: SCRAL URL TO PUT Observation and Registration(default=http://monapp-lst.monica-cloud.eu:8490/scral/v1.0/wristband-gw/wearable/localization) 
-	**Latitude**:  GroundPlanePosition Latitude, the reference position for localization random simulation 
-	**Longitude**: GroundPlanePosition Longitude, the reference position for localization random simulation 
-	**MaxDistanceNorth_meters**: Max Distance North (in meters) for random placement of the position observation generated 
-	**MaxDistanceEast_meters**: Max Distance East (in meters) for random placement of the position observation generated 
-	**NumberWristbands**: Number of Wristbands simulated 
-	**VariableNumberWristband**: Increase between two differen DeviceID (keep to 1) 
-	**AreaId**: Fixed content message field 
-	**DeviceType**: Fixed content message field (default: 868) 
-	**Device**: Fixed content message field (default: wearable) 
-	**Sensor**: Fixed content message field (default: tag) 
-	**ObservationType**: Fixed content message field (default: proprietary) 
-	**UnitOfMeasurements**: Fixed content message field (default: meters) 
-	**IntervalSendingSecs**: Interval between two different slots of location observations of all devices (in seconds) 
-	**PrefixDevice**: Prefix for Device Id or tagID for JSON message (default: GeoTag). Simulation creates deviceID=${PrefixDevice}ID, with ID in range(0, NumberWristbands) 
-	**EnableRegistrationPhase**: Enable Registration Phase at beginning of simulation, 1 to enable 0 to disable. NOTE: Registration is mandatory when there is some difference in deviceIDs generated from the past 
-	**EnableObservationPhase**: Enable Observation Sending Phase. NOTE: Each DeviceID must be registered 
-	**TimeoutWaitingBetweenObservations_ms**: Timeout (in milliseconds) to wait between two different observations from two different devices in specific Thread created 
-	**CounterDevicePerThread**: Number of devices passed for each Thread generated. NOTE: The number of thread generated is equal to ceil(NumberWristbands/CounterDevicePerThread) 
-	**TimeoutWaitLaunchSingleThreadms**: Timeout (in millisecond) for initial delay in single thread launch 
-	**PathFileOutput**: Path to redirect standard output. NOTE: it acts only if SendStdOutToFile is enabled (set to 1). The user must take care about local path set (Check if folder exists) 
-	**PathFileError**: Path to redirect standard error. NOTE: it acts only if SendStdErrorToFile is enabled (set to 1). The user must take care about local path set (Check if folder exists) 
-	**SendStdErrorToFile**: Enable Standard Output redirect to file, 1: Enabled to PathFileOutput, 0 to maintain it in console 
-	**SendStdOutToFile**: Enable Standard Error redirect to file, 1: Enabled to PathFileError, 0 to maintain it in console 
