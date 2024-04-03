from workout_module import Workout, CompareWorkout

detected_workout = Workout("detected_workout.txt")
correct_workout = Workout('correct_workout.txt')
test = CompareWorkout(detected_workout, correct_workout)
test.verify_all()