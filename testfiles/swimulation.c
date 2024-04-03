/*

a copy of the simulation workout function on the firmware for debugging

*/
/*run 1 simulation workout*/
void run_workout()
{
    reset_algo_parameters_before_workout();
    NRF_LOG_INFO("====== START WORKOUT ========");
    volatile enum stroketypes strtype = st_fr;
    enum turn_types turntype = tumble_turn;
    uint32_t iteration_of_reference_data = 0;
    int32_t  reference_data_ind = -1;
    int16_t  p_incoming_sample[NB_CHANNELS][FIFO_SZ] = { 0 };
    while(1)
    {
        // inertial_sensor_clear_fifo_new_data_flag();
        reference_data_ind++;
        // NRF_LOG_INFO("mix set_{0}: %i", mix_set[0][0][0]);
        reference_data_to_array((mix_set + reference_data_ind)[0],
                                p_incoming_sample); // data_start_20200624
        state_ID = dsp_fun_state_id(p_incoming_sample,
                                false,
                                reference_data_ind + iteration_of_reference_data,
                                state_ID,
                                timer_pre);
        NRF_LOG_INFO("timer_pre: %i", timer_pre);
        NRF_LOG_INFO("Algo state: %i", state_ID);
        buffer_ind_a = reference_data_ind * FIFO_SZ;
        NRF_LOG_INFO("reference index: %i", reference_data_ind);
        nrf_drv_wdt_channel_feed(m_channel_id); //feed the watchdog timer
        if (reference_data_ind >= 312) { // magic number the size of the sample data 109 data_freestyle
          // NRF_LOG_INFO("end of file");
          NRF_LOG_INFO("====== END WORKOUT ========");
          // reference_data_ind = 0;
          // iteration_of_reference_data += 312;
          NRF_LOG_INFO("iteration of reference data: %i", iteration_of_reference_data);
          break;
          // simulation_time_stamp =
          // (reference_data_ind +
          // iteration_of_reference_data)*FIFO_SZ;
          // stop_sensor_periodic_measuring(); //This will stop the
          // example workout from reading beyond the sample data
        }
                if (state_ID == 1)
                {
                    state_ID = 2;
                }
                else if (state_ID == 2)
                {
                    if (prediction_stroke == 1)
                    {
                        strtype = st_fl;
                    }
                    else if (prediction_stroke == 2)
                    {
                        strtype = st_bk;
                    }
                    else if (prediction_stroke == 3)
                    {
                        strtype = st_br;
                    }
                    else if (prediction_stroke == 4)
                    {
                        strtype = st_fr;
                    }
                    state_ID = 3;
                    NRF_LOG_INFO("Print push addlogd");
                    addLog(strtype, SWIMTRAXX_ID_PUSH, 0, first_start_ind);
                    push_ind = first_start_ind;
                }
                else if (state_ID == 3)
                {
                    if (p_confirmed_turns->all_turns[p_confirmed_turns->counter - 1].turn_start == prev_turn)
                    {
                        if (prediction_stroke == 1)
                        {
                            strtype = st_fl;
                        }
                        else if (prediction_stroke == 2)
                        {
                            strtype = st_bk;
                        }
                        else if (prediction_stroke == 3)
                        {
                            strtype = st_br;
                        }
                        else if (prediction_stroke == 4)
                        {
                            strtype = st_fr;
                        }
                    }

                    // int32_t lap_time_fin = buffer_ind_a - 50 -
                    // ACCZ_WINDOW_START - push_ind; if(lap_time_fin>3000){
                    //   addLog(strtype, SWIMTRAXX_ID_FINISH, 0,
                    //   buffer_ind_a-GENERAL_BUFF_RIGHT); // Forced finish
                    //   state_ID = 0;
                    //   reset_finish();
                    //   reset_strokes();
                    //   reset_start();
                    //   reset_turn();
                    //   reset_confirmed_turns();
                    //   reset_stroke_classsifier();
                    // }
                    if (p_confirmed_turns->counter > 0)
                    {
                        if (p_confirmed_turns->all_turns[p_confirmed_turns->counter - 1].turn_start
                            >= (prev_turn + 100))
                        {
                            if (is_stroke_sent == false)
                            {
                                if (strtype == st_fr)
                                {
                                    for (int32_t j = 0; j < p_stroke->stroke_count_temp; j++)
                                    {
                                        addLog(strtype,
                                               SWIMTRAXX_ID_STROKE,
                                               p_stroke->breath_type[j],
                                               p_stroke->stroke_ind_estimates[j]);
                                    }
                                }
                                if (strtype == st_fl)
                                {
                                    uint32_t fl_votes;
                                    uint32_t br_botes;
                                    fl_votes = count_element_equal_to_int8(
                                        br_fly_classifier_results.classes, BR_FLY_STRUCT_ARRAY_LEN, 1);
                                    br_botes = count_element_equal_to_int8(
                                        br_fly_classifier_results.classes, BR_FLY_STRUCT_ARRAY_LEN, 3);
                                    strtype = fl_votes > br_botes ? st_fl : st_br;
                                    reset_classification_results(&br_fly_classifier_results);
                                }
                                if (strtype == st_br)
                                {
                                    for (int32_t j = 0; j < p_stroke->br_count; j++)
                                    {
                                        addLog(strtype, SWIMTRAXX_ID_STROKE, 1, p_stroke->br_ind_a[j]);
                                    }
                                }
                                else if (strtype == st_fl)
                                {
                                    for (int32_t j = 0; j < p_stroke->br_count; j++)
                                    {
                                        addLog(strtype, SWIMTRAXX_ID_STROKE, 0, p_stroke->br_ind_a[j]);
                                    }
                                }
                                else if (strtype == st_bk)
                                {
                                    for (int32_t j = 0; j < p_stroke->bk_count; j++)
                                    {
                                        addLog(strtype, SWIMTRAXX_ID_STROKE, 1, p_stroke->bk_ind_a[j]);
                                    }
                                }

                                reset_strokes();
                                is_stroke_sent = true;
                            }
                            if (is_true_turn)
                            {
                                turn_counter += 1;
                                push_ind = p_confirmed_turns->all_turns[p_confirmed_turns->counter - 1].push;
                                // if (turn_counter == 1)
                                //{
                                //     addLog(strtype,
                                //            SWIMTRAXX_ID_PUSH,
                                //            0,
                                //            first_start_ind); // Start when followed
                                //                              // by turns
                                // }
                                if (p_confirmed_turns->all_turns[p_confirmed_turns->counter - 1].turn_type == 0)
                                {
                                    turntype = tumble_turn;
                                }
                                else
                                {
                                    turntype = open_turn;
                                }
                                // type tt = 0, ot(accx) = 1, bk = 2, co = 3,
                                // ot(accz) = 4, ot(no acc) = 5/** < which type
                                // of turn it is to be used for debugging */
                                addLog(strtype,
                                       SWIMTRAXX_ID_TURNSTART,
                                       p_confirmed_turns->all_turns[p_confirmed_turns->counter - 1].turn_type,
                                       p_confirmed_turns->all_turns[p_confirmed_turns->counter - 1].turn_start);
                                addLog(strtype,
                                       SWIMTRAXX_ID_PUSH,
                                       turn_counter,
                                       p_confirmed_turns->all_turns[p_confirmed_turns->counter - 1].push);
                                prev_turn = p_confirmed_turns->all_turns[p_confirmed_turns->counter - 1].turn_start;
                                reset_turn();
                                is_stroke_sent = false;
                                is_true_turn   = false;
                            }
                        }
                    }
                }
                else if (state_ID == 10)
                // this stage can' be reached from state id 3
                {
                    if (first_finish_ind <= first_start_ind + MIN_LAP_TIME_DIST)
                    {
                        state_ID = 0;
                        reset_finish();
                        reset_strokes();
                        reset_start();
                        reset_turn();
                        reset_confirmed_turns();
                        reset_stroke_classsifier();
                    }
                    else
                    {
                        if (prediction_stroke == 1)
                        {
                            strtype = st_fl;
                        }
                        else if (prediction_stroke == 2)
                        {
                            strtype = st_bk;
                        }
                        else if (prediction_stroke == 3)
                        {
                            strtype = st_br;
                        }
                        else if (prediction_stroke == 4)
                        {
                            strtype = st_fr;
                        }
                        if (strtype == st_fl)
                        {
                            uint32_t fl_votes;
                            uint32_t br_botes;
                            fl_votes = count_element_equal_to_int8(
                                br_fly_classifier_results.classes, BR_FLY_STRUCT_ARRAY_LEN, 1);
                            br_botes = count_element_equal_to_int8(
                                br_fly_classifier_results.classes, BR_FLY_STRUCT_ARRAY_LEN, 3);
                            strtype = fl_votes > br_botes ? st_fl : st_br;
                            reset_classification_results(&br_fly_classifier_results);
                        }
                        // if (p_confirmed_turns->counter == 0)
                        //{
                        //     addLog(strtype,
                        //            SWIMTRAXX_ID_PUSH,
                        //            0,
                        //            first_start_ind); // Start ind when followed
                        //                              // by a finish
                        // }
                        if (strtype == st_fr)
                        {
                            for (int32_t j = 0; j < p_stroke->stroke_count_temp; j++)
                            {
                                addLog(strtype,
                                       SWIMTRAXX_ID_STROKE,
                                       p_stroke->breath_type[j],
                                       p_stroke->stroke_ind_estimates[j]);
                            }
                        }
                        if (strtype == st_br)
                        {
                            for (int32_t j = 0; j < p_stroke->br_count; j++)
                            {
                                addLog(strtype, SWIMTRAXX_ID_STROKE, 1, p_stroke->br_ind_a[j]);
                            }
                        }
                        else if (strtype == st_fl)
                        {
                            for (int32_t j = 0; j < p_stroke->br_count; j++)
                            {
                                addLog(strtype, SWIMTRAXX_ID_STROKE, 0, p_stroke->br_ind_a[j]);
                            }
                        }
                        else if (strtype == st_bk)
                        {
                            for (int32_t j = 0; j < p_stroke->bk_count; j++)
                            {
                                addLog(strtype, SWIMTRAXX_ID_STROKE, 1, p_stroke->bk_ind_a[j]);
                            }
                        }
                        reset_strokes();
                        addLog(strtype, SWIMTRAXX_ID_FINISH, 0,
                               first_finish_ind); // Actual finish
                        reset_finish();
                        reset_strokes();
                        reset_start();
                        reset_turn();
                        reset_confirmed_turns();
                        reset_stroke_classsifier();
                        turn_counter   = 0;
                        prev_turn      = 0;
                        state_ID       = 0;
                        is_stroke_sent = false;
                        is_true_turn   = false;
                    }
                }
            }



}

