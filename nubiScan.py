import sys
import os
import argparse
import logging
import time
from ttsPlayer import ttsPlayer
from ET1 import nubiInventory
from kbdPicker.kbdPicker import kbdPicker, kbdPickerErrorUnPlugged

USER_INACTIVITY_TIMEOUT_SEC = (3 * 60) # 3 minutes
NETWORK_ERROR_MSG = f"Network error, please try again later."
SCANNER_PLUGGED_IN_MSG = f"Scanner plugged in"
SCANNER_UNPLUGGED_MSG = f"Scanner unplugged"

def main():
    # Manage the command line options
    cmdLineArgs = argparse.ArgumentParser(description='Runs the nubi bar code scanner.')
    cmdLineArgs.add_argument('-f', '--file', default='', type=str, help='file to pull input from')
    args = cmdLineArgs.parse_args()

    # init our basic services
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[
                            logging.FileHandler("nubiScan.log"),
                            logging.StreamHandler()
                        ])
    logging.info(f"nubiScan started")
    file = args.file
    os.system('amixer cset numid=1 400') # on a raspberry pi this turns up the volume to 100%
    userName = None
    usbPort = '1.3'
    lastUsed = time.time() - USER_INACTIVITY_TIMEOUT_SEC # Always make sure we init this to the past
    networkUp = True # start off assuming that the network is up
    kbd = kbdPicker()
    tts = ttsPlayer()
    while True:
        try:
            ET1 = nubiInventory()
        except nubiInventory.NetworkErrorException:
            if networkUp:
                networkUp = False
                try:
                    tts.quePlayback(NETWORK_ERROR_MSG) # assume that this is already cached
                except:
                    # ignore asserts; this would happen if the network is down and the above message is not cached
                    pass
            logging.error(f"Network error; not connected")
            time.sleep(2)
        else:
            if not networkUp:
                tts.quePlayback(f"Network up") # assume that this is already cached
            break

    while True:
        try:
            # cache these voice prompts for off line use
            tts.voiceCacheAdd(NETWORK_ERROR_MSG)
            tts.voiceCacheAdd(SCANNER_PLUGGED_IN_MSG)
            tts.voiceCacheAdd(SCANNER_UNPLUGGED_MSG)
        except tts.NetworkErrorException:
            logging.error(f"Network error; not connected")
            time.sleep(2)
        else:
            break

    while True:
        try:
            if file == '':
                #Read from the bar code scanner
                kbd.waitForDeviceByPhysicalUsbPort(usbPort)
                assert kbd.setDeviceByPhysicalUsbPort(usbPort) == True
                nubiScanGetLine = kbd.readline
                deviceName = kbd.getDeviceName()
                logging.info(f"{deviceName} plugged in")
                tts.quePlayback(SCANNER_PLUGGED_IN_MSG)
            else:
                #we want to read input from a test file
                fp = open(file)
                nubiScanGetLine = fp.readline

            while True:
                try:
                    logging.info(f"---------------------------------------------------------------------------")
                    #Read in the next bar code
                    while True:
                        nubiCode = nubiScanGetLine()
                        if nubiCode == '':
                            #Note: This only happens when reading from a file; when using the -f option.
                            tts.stop()
                            logging.info(f"Cya later")
                            sys.exit(0)
                        elif nubiCode.split('-')[0] != 'NUBI':
                            print(f"Unknown code :'{nubiCode}'")
                        else:
                            nubiCode = nubiCode.replace('\n', '') #remove line feeds
                            break;

                    #We got a 'NUBI' scan code. Next step is to find the process ID associated with it. 
                    try:
                        processId = nubiCode.split('-')[1]
                    except:
                        logging.warning(f"Scanned junk: [{nubiCode}]")
                        continue

                    if time.time() > lastUsed + USER_INACTIVITY_TIMEOUT_SEC:
                        #If no one has used this since the timeout period then clear the username
                        userName = None
                    lastUsed = time.time()

                    if processId == 'Name':
                        #This is a special process ID that is reserved for passing names to other processes. 
                        userName = nubiCode.split('-')[2]
                        logging.info(f"Hello {userName}")
                        tts.quePlayback(f"Hello {userName}") 
                    elif processId == 'ET1':
                        #This is the process used by the ET for checking out equipment.
                        logging.info(f"Running the {processId} process with {userName}-->{nubiCode}")
                        if userName == None:
                            tts.quePlayback(f"Please scan your name first.")
                        else:
                            try:
                                message = ET1.run(userName, nubiCode)
                                tts.quePlayback(message)
                                logging.info(message)
                            except (nubiInventory.NetworkErrorException, tts.NetworkErrorException):
                                logging.error(f"Process interrupted due to network error.")
                                tts.quePlayback(NETWORK_ERROR_MSG)
                            except Exception as e:
                                tts.quePlayback(f"{e.args[-1]}")
                                logging.error(f"{e.args[-1]}")
                                logging.error(f"{e}")
                                raise e
                                tts.quePlayback(f"Could not run ET1 process")

                    #Add new process handling here. So far we only have test processes.
                    elif processId == 'TEST1':
                        tts.quePlayback(f"process ID: {processId.lower()}")
                        print(f"{processId}")
                    elif processId == 'TEST2':
                        tts.quePlayback(f"process ID: {processId.lower()}")
                        print(f"{processId}")
                    else:
                        tts.quePlayback(f"Unknown process ID: {processId}")
                        logging.error(f"Unknown process ID: {processId}")
                except (nubiInventory.NetworkErrorException, tts.NetworkErrorException):
                    logging.error(f"Process interrupted due to network error.")
                    tts.quePlayback(NETWORK_ERROR_MSG)

        except kbdPickerErrorUnPlugged:
            logging.info(f"{deviceName} Unplugged")
            tts.quePlayback(SCANNER_UNPLUGGED_MSG)
        except KeyboardInterrupt as error:
            tts.stop()
            logging.info(f"Cya later")
            sys.exit(0)

if __name__ == "__main__":
    main()
