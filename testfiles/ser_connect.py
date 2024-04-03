import serial
from time import sleep
from tqdm import tqdm
from decode import read_events

""""
Serial Commands:
-e Erase the flash memory
-r Read the flash memory
-m Start measurement
-q Quit the measurement
-a Turn of bluetooth/airplane mode
-w Wake up the bluetooth connection
-f Get device state feedback
-d Put the device in deepsleep mode
"""


# measure accelerometer
def start_meas(connection):
    connection.write(b'm')


def stop_meas(connection):
    connection.write(b'q')


def wake_ble(connection):
    connection.write(b'w')


def sleep_mode(connection):
    connection.write(b'd')


def erase_flash(connection):
    connection.write(b'e')
    connection.write(b'e')
    # read_flash(connection)
    connection.readline().decode('ascii')
    print("FLASH ERASED")


def read_flash(connection):
    connection.write(b'r')

def run_workout(connection):
    erase_flash(connection)
    print("START WORKOUT")
    connection.write(b't')
    sleep(10)  # wait until end of workout
    for i in range(3):
        connection.readline().decode('ascii')
    print("WORKOUT DONE")

def test_meas(connection):
    start_meas()  # start measurement
    receivedData = connection.readline().decode('ascii')  # read out data
    print(receivedData)
    # wait 5 seconds
    for i in tqdm(range(5)):
        sleep(1)
    stop_meas()  # stop measuring
    receivedData = connection.readline().decode('ascii')
    print(receivedData)


def erase_file(file):
    # open file
    t = open(file, "r+")
    # absolute file positioning
    t.seek(0)
    # to erase all data
    t.truncate()


def write_to_file(connection, file):
    erase_file(file)
    validData = True
    while validData:
        line = connection.readline().decode('utf-8')
        if line == "":
            with open(file, "a") as f:
                f.write(line)
        else:  # stop when all data is read
            validData = False

def compare_workouts_list(correct, new):
    print(f'Total lines correct:', len(correct))
    print(f'Total lines new:', len(new))
def compare_workouts_files(filePathA,size_a,filePathB, size_b):
    # compare 2 sets
    # reading files
    f1 = open(filePathA, "r")
    f2 = open(filePathB, "r")
    # size_f1 = len(f1.readlines())
    # size_f2 = len(f2.readlines())

    print(f"Correct workout contains {size_a} events")
    print(f"New workout contains {size_b} events")

    i = 0

    passed = True
    for line1 in f2:
        i += 1

        for line2 in f1:

            # matching line1 from both files
            if line1 == line2:
                # print IDENTICAL if similar
                print("Line ", i, ": IDENTICAL")
            else:
                passed = False
                print("Line ", i, ":")
                # else print that line from both files
                print("\tFile 1:", line1, end='')
                print("\tFile 2:", line2, end='')
            break

    # closing files
    f1.close()
    f2.close()

    if not passed:
        raise Exception("Workout measurements are different")
# save workout result in array and file
def store_workout(connection, filepath):
    read_flash(connection)
    erase_file(filepath)
    setA = []
    while True:
        line = connection.readline().decode('utf-8')
        if line =='':
            # End of session
            break
        elif line == "0" * 32:
            break
        else:
            setA.append(line.rstrip('\r\n'))
            with open(filepath, "a") as f:
                f.write(line)
    return setA

def store_workout_test(connection, filepath):
    erase_file(filepath)
    setA = []
    i = 1
    while True:
        all = connection.readlines()
        line = str(connection.readlines()) #.decode('utf-8')
        print(f"Line {i}: " + all)
        # setA.append(line.rstrip('\r\n'))
        with open(filepath, "a") as f:
            f.write(line)
        i+=1

    return setA

def store_flash(ser,filePath):

    read_flash(ser)
    resultSet = store_workout(ser, filePath)  # store result set in array and file
    ser.close()


def make_reference_array(file):
    referenceSet = []
    f = open(file, "r")
    for line in f:
        referenceSet.append(line.rstrip('\n'))
    return referenceSet