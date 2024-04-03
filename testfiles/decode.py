import binascii
import struct
import numpy as np
import pandas as pd
import json


def read_events(filepath: str, n_sessions: int = None) -> list:
    """
    Read raw device data stored in a text file.

    Parameters
    ----------
    filepath : str
        Path to the text file.

    Returns
    -------
    sessions : list
        Logs of all events detected by the Swimtraxx algorithm.
    """
    sessions = []

    def parse_event_type(code):
        SWIMTRAXX_ID_PUSH = "00"
        SWIMTRAXX_ID_STROKE = "01"
        SWIMTRAXX_ID_TURNSTART = "02"
        SWIMTRAXX_ID_FINISH = "03"
        SWIMTRAXX_ID_HR = "04"
        if code == SWIMTRAXX_ID_PUSH:
            return "push"
        elif code == SWIMTRAXX_ID_STROKE:
            return "stroke"
        elif code == SWIMTRAXX_ID_TURNSTART:
            return "turn"
        elif code == SWIMTRAXX_ID_FINISH:
            return "finish"
        elif code == SWIMTRAXX_ID_HR:
            return "hr"
        else:
            return code

    def parse_stroke_type(code):
        st_fl = "00"
        st_bk = "01"
        st_br = "02"
        st_fr = "03"
        st_kk = "04"
        if code == st_fl:
            return "FL"
        elif code == st_bk:
            return "BK"
        elif code == st_br:
            return "BR"
        elif code == st_fr:
            return "FR"
        elif code == st_kk:
            return "KK"
        else:
            return code

    def parse_turn_type(code):
        tt = "00"
        ot = "01"
        if code == tt:
            return "tumble"
        elif code == ot:
            return "open"
        else:
            return code

    def parse_breath_type(code):
        n = "00"
        b = "01"
        if code == n:
            return 0
        elif code == b:
            return 1
        else:
            return code

    with open(filepath, "r") as f:
        status_prev = None
        events = []
        for line in f:
            line = line.rstrip()
            if line == "0" * 32:
                break

            # Get status
            status = line[:2]

            # Process data
            if status == "06":
                if status_prev == "06":
                    continue
                # Start of session
                # events = [] no start of session recorded
            elif status == "05":
                if status_prev == "05":
                    continue
                # End of session
                sessions.append(events)
            elif status == "08":
                assert line[2:4] == "aa"
                stroke_type = parse_stroke_type(line[4:6])
                assert line[6:8] == "bb"
                event_type = parse_event_type(line[8:10])
                assert line[10:12] == "cc"
                if event_type == "turn":
                    turn_type = parse_turn_type(line[12:14])
                elif event_type == "stroke":
                    breath = parse_breath_type(line[12:14])
                assert line[14:16] == "dd"
                skin_detected = line[16:18] == "FF"
                assert line[18:24] == "000000"
                sample_number = int(line[24:32], base=16)
                if event_type == "push":
                    events.append(
                        {
                            "timestamp": sample_number,
                            "type": "push",
                        }
                    )
                elif event_type == "stroke":
                    events.append(
                        {
                            "timestamp": sample_number,
                            "type": "stroke",
                            "strokeType": stroke_type,
                            "breath": breath,
                        }
                    )
                elif event_type == "turn":
                    events.append(
                        {
                            "timestamp": sample_number,
                            "type": "turn",
                            "strokeType": stroke_type,
                            "turnType": turn_type,
                        }
                    )
                elif event_type == "finish":
                    events.append(
                        {
                            "timestamp": sample_number,
                            "type": "finish",
                            "strokeType": stroke_type,
                        }
                    )

            status_prev = status

    if status != "05":
        sessions.append(events)

    if n_sessions is None:
        return sessions[-1]
    else:
        return sessions[-n_sessions:]

