import serial
from time import sleep
from tqdm import tqdm

import workout_module
from decode import read_events
import itertools
import ast

"""
T (sec) = timestamp/50
snelste 130 slagen / minuut -> 0.5s / slag
marge min = 20 samples
"""

class CompareWorkout:
    """
    Create object to compare 2 workouts
    :parameter
    2 Workout objects
    """
    # Validation criteria's
    MARGINS = {
        "DEFAULT": 20,
        "PUSH": 20,
        "BK": 20,
        "BR": 20,
        "FL": 20,
        "FR": 20,
        "FINISH": 20,
        "TURN": 20
    }
    VALID_SET_BAR = 90
    VALID_TEST_BAR = 90

    def __init__(self, detected_workout, correct_workout):
        self.detected_workout = detected_workout
        self.correct_workout = correct_workout

    def check_event(self, correct_event: dict, detected_set: list) -> list:
        """
        find all events in the detected set that are within the margin of given correct event
        set = events of the same type (i.e. all BK strokes)
        """
        found_events = []
        correct_timestamp = correct_event['timestamp']
        for detected_event in detected_set:
            detected_timestamp = detected_event['timestamp']
            detected_event_type = detected_event['type']
            if detected_event_type == "stroke":
                detected_event_type = detected_event['strokeType']
            difference = detected_timestamp - correct_timestamp
            if abs(difference) <= self.MARGINS[(detected_event_type).upper()]:
                found_events.append(detected_event)
        return found_events

    def check_sets(self, detected_set, correct_set):
        """
        compare detected set to correct set to see if detected events are valid
        :return
        * number of valid events
        * number of missing events
        * number of duplicated events
        * number of out of bounds events
        * number of valid events
        * percentage of valid events in set
        * if set passed the check
        """
        valid_set = False
        total_valid = 0
        multiple_detected = 0
        not_detected_events = 0
        extra_event = 0
        size_detected_set = len(detected_set)
        size_correct_set = len(correct_set)
        size_set_error = size_detected_set - size_correct_set
        size_set_error_log = ""
        if size_set_error != 0:
            size_set_error_log = f"\n{size_detected_set} detected events, expected {size_correct_set} events"

        for correct_event in correct_set:
            found_events = self.check_event(correct_event, detected_set)
            if len(found_events) > 2:
                multiple_detected += 1
            elif len(found_events) == 0:
                not_detected_events += 1
            else: # 1 or 2 found events
                total_valid += 1
        for detected_event in detected_set:
            found_events_reverse = self.check_event(detected_event, correct_set)
            if len(found_events_reverse) == 0:
                extra_event += 1

        valid_events_percentage =  ( float(total_valid) / float(size_correct_set) )*100
        if valid_events_percentage >= self.VALID_SET_BAR:
            valid_set = True

        not_detected_log = ""
        if not_detected_events:
            not_detected_log = f"\n{not_detected_events} events have not been detected"
        multiple_detected_log = ""
        if multiple_detected:
            multiple_detected_log = f"\n{multiple_detected} events have multiple detections associated to them"
        extra_event_log = ""
        if extra_event:
            extra_event_log = f"\n{extra_event} out of bounds events detected"

        log = f"{str(valid_set).upper()} - {total_valid}/{size_correct_set} detections are correct {size_set_error_log}{not_detected_log}{multiple_detected_log}{extra_event_log}"
        result = {
            "result": valid_set,
            "log": log,
            "percentage": valid_events_percentage,
            "totalValid": total_valid
        }

        return result

    def verify_all(self, valid_test = VALID_TEST_BAR):
        """
        validate detected workout based on correct workout
        :return
        * average result of all sets
        """
        detected_events_collections = self.detected_workout.get_all_collections()
        correct_events_collections = self.correct_workout.get_all_collections()
        sets_percentage = []
        for name, set in detected_events_collections.items():
            print(f"{name.upper()} EVENTS")
            check_set = self.check_sets(detected_events_collections[name], correct_events_collections[name])
            set_valid = check_set["result"]
            set_results = check_set["percentage"]
            print(check_set["log"] + "\n")
            sets_percentage.append(check_set["percentage"])

        workout_avg = sum(sets_percentage) / len(sets_percentage)
        print(f"Total score of workout: {round(workout_avg,2)}% (required: {valid_test}%)")
        assert workout_avg >= valid_test, "The test failed"
        return "Test passed"

class Workout:
    def __init__(self, path):
        self.filepath = path
        self.workout = self.read_workout_file()
        self.all_collections = {
            "BR": [],
            "FL": [],
            "BK": [],
            "FR": [],
            "push": [],
            "finish": [],
            "turn": []
        }
        self.sort_events()

    def read_workout_file(self):
        # put events of workout in a list
        workout = []
        with open(self.filepath, 'r') as f:
            for event in f:
                event_dict = ast.literal_eval(event.strip())
                workout.append(event_dict)
        return workout

    def sort_events(self):
        # add event to correct list based on type
        for event in self.workout:
            match event["type"]:
                case "push":
                    self.all_collections["push"].append(event)
                case "turn":
                    self.all_collections["turn"].append(event)
                case "finish":
                    self.all_collections["finish"].append(event)
                case "stroke":
                    match event["strokeType"]:
                        case "FL":
                            self.all_collections["FL"].append(event)
                        case "BK":
                            self.all_collections["BK"].append(event)
                        case "BR":
                            self.all_collections["BR"].append(event)
                        case "FR":
                            self.all_collections["FR"].append(event)

    def get_all_collections(self):
        return self.all_collections

    def get_fl_set(self):
        return self.all_collections["FL"]

    def get_br_set(self):
        return self.all_collections["BR"]

    def get_bk_set(self):
        return self.all_collections["BK"]

    def get_fr_set(self):
        return self.all_collections["FR"]

    def get_turn_set(self):
        return self.all_collections["turn"]

    def get_push_set(self):
        return self.all_collections["push"]

    def get_finish_set(self):
        return self.all_collections["finish"]
