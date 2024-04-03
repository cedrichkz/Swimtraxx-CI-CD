from ser_connect import *
from workout_module import *
#test push new
print("----------- START TEST --------------")
server = True
# setup connection
if server:  # run on server
    ser = serial.Serial(port='/dev/ttyACM0', baudrate=11520, timeout=1)
else:  # run on local device
    ser = serial.Serial(port='/dev/tty.usbmodem0000000000001', baudrate=11520, timeout=1)
sleep(3)  # delay for startup routine

run_workout(ser) # run swimulation
erase_file("detected_workout_raw.txt")
erase_file("detected_workout.txt")
raw_new_workout = store_workout(ser, "detected_workout_raw.txt") # store new workout data
new_workout = read_events("detected_workout_raw.txt") # convert workout data to readable events
with open("detected_workout.txt", 'a') as f:
    for event in new_workout:
        f.write(str(event) + "\n")

# Validate new workout
detected_workout_file = "detected_workout.txt"
correct_workout_file = "correct_workout.txt"
detected_workout = Workout(detected_workout_file)
correct_workout = Workout(correct_workout_file)
test = CompareWorkout(detected_workout, correct_workout)
test.verify_all()
ser.close()

print("\n----------- END TEST --------------")