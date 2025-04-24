from typing import Any, Literal, Optional, List, Tuple



from pydantic import Field

from wei import ExperimentClient

from wei.types.experiment_types import CampaignDesign, ExperimentDesign

from pydantic import BaseModel

from ulid import ULID

import datetime

from pathlib import Path

import pandas as pd
verbose = 0

# cells = ["A1","B1","C1","A2", "B2", "C2"] # red (sampled) side  ============== six cells
cells = ["A1","B1"]
sources = "AMEWS_6cell_input.csv"
path = "."
AS = True # run AS
rack = 90 # 90 tube rack
blank = True # collect red side blanks first
fictive = 0.1 # uL of fictitous addition to the red side, for container bookkeeping
fill = 1000 # uL fill of the green side
volume = 250 # ul sampling of the red side
chaser = 1000 # uL chaser
delay = 0.10 # minutes to wait after each sampling
laps = 2 # laps of sample collection
aliquots = [volume/2] # uL aliquots for calibrations - adjust
unprocessed_containers = []
last_log = None 

def make_lists(cells):
        n = len(cells)
        cells_list = ",".join(cells)
        counters = [] # green side
        for c in cells:
            c_ = "%s%d" % (c[0], 2 + int(c[1:]))
            counters.append(c_)
        counters_list = ",".join(counters)
        if verbose: 
            print(">> Sample wells (%d) = %s" %  (n, cells_list))
            print(">> Counter wells (%d) = %s" % (n, counters_list))
        return cells_list, counters_list, counters
cells_list, counters_list, counters = make_lists(cells)

experiment = ExperimentDesign(

        experiment_name="Test_Experiment",

        experiment_description="An experiment for automated testing",

        email_addresses=[],

    )

    

exp = ExperimentClient(experiment=experiment)



wf_path = Path(__file__).parent.parent / "workflows" 



def update_workflow(exp, worfklow_run):

    if worfklow_run is not None:

        return exp.query_run(worfklow_run.run_id)

    else:

        return None

    

#Setup

NUM_INPUTS = 1


pickup_ur_locations = ["ur_aarl200.supply_rack_icp1", "ur_aarl200.supply_rack_icp2", "ur_aarl200.supply_rack_icp3"]
pickup_rail_locations = [175, 211, 247]
trash_ur_locations = ["ur_aarl200.trash_rack_icp1", "ur_aarl200.trash_rack_icp2", "ur_aarl200.trash_rack_icp3"]
trash_rail_locations = [282, 318, 353]



ICP_workflow = None

BK_workflow = None

ICP_container = None

measured_counter = 0

sample_counter = 0

trash_counter = 0

last_container = {}

icp_working = True

chem = None
prompts = None
ID = None
data_path = Path("/home/aarl/Dropbox/Instruments cloud/Robotics/RESULTS")
run_path = data_path / ("run6_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
run_path.mkdir()
master_log = []
while trash_counter < NUM_INPUTS:

    ICP_workflow = update_workflow(exp, ICP_workflow)

    BK_workflow = update_workflow(exp, BK_workflow)



    #First, if the PAL is finished, move the sample back to its home location

    if (BK_workflow is not None and BK_workflow.status == "completed"):
        #run the workflow that transfers from the PAL back the starting location
        run_info = exp.start_run(wf_path / "transfer_out_of_bk.yaml", payload={"arm_safe_joints": "ur_aarl200.supply_station_safe_joints", "arm_position": pickup_ur_locations[sample_counter], "rail_position": pickup_rail_locations[sample_counter]})
        sample_counter += 1
        datapoint_id = BK_workflow.get_datapoint_id_by_label("ID")
        ID = exp.get_datapoint_value(datapoint_id)["value"]
        datapoint_id = BK_workflow.get_datapoint_id_by_label("chem")
        chem = exp.get_datapoint_value(datapoint_id)["value"]
        datapoint_id = BK_workflow.get_datapoint_id_by_label("prompts")
        prompts = exp.get_datapoint_value(datapoint_id)["value"]
        datapoint_id = BK_workflow.get_datapoint_id_by_label("containers")
        unprocessed_containers.append(exp.get_datapoint_value(datapoint_id)["value"][0])
        last_container = exp.get_datapoint_value(datapoint_id)["value"][0]
        datapoint_id = BK_workflow.get_datapoint_id_by_label("digest_vols")
        log_file_info = exp.get_datapoint_info(datapoint_id)
        log_file_name = Path(log_file_info.path).name
        log_file_info = exp.save_datapoint_value(datapoint_id, run_path / log_file_name)
        datapoint_id = BK_workflow.get_datapoint_id_by_label("raw_log")
        log_file_info = exp.get_datapoint_info(datapoint_id)
        log_file_name = Path(log_file_info.path).name
        barcode = "asdf"
        master_log.append({"ID": ID, "category": "run"+str(sample_counter), "container": last_container["code"], "AS log": str(log_file_name), "barcode": barcode})
        df = pd.DataFrame(master_log)
        df.to_csv(run_path / "AS_sequence_log.csv", index=False)

        BK_workflow = None
        if sample_counter == NUM_INPUTS:
            exp.start_run(wf_path / "close_door.workflow.yaml")




    if BK_workflow is None and sample_counter < NUM_INPUTS:

        #Run the workflow that transfers the empty tubes into the PAL
        #if sample_counter == 0:
            #exp.start_run(wf_path / "open_door.workflow.yaml")
        #exp.start_run(wf_path / "transfer_in_to_bk.yaml", payload={"arm_safe_joints": "ur_aarl200.supply_station_safe_joints", "arm_position": pickup_ur_locations[sample_counter], "rail_position": pickup_rail_locations[sample_counter]}, blocking=True)
        if sample_counter == 0:
            wf_run = exp.start_run(
            workflow= wf_path / "bk_startup.workflow.yaml",
            payload={
                "blank_args": {
                    "cells_list": cells_list,
                    "rack": rack,
                    "prep": 0,
                    "path": path,
                    "sources": sources,
                    "volume" : volume,
                    "chaser": chaser,
                    "fictive": fictive,
                    "verbose": verbose,

                },

                "fill_args": {
                    "counters_list": counters_list,
                    "rack":rack,
                    "path": path,
                    "sources": sources,
                    "fill": fill,
                    "verbose": verbose,
                            },

            },

            )
            datapoint_id = wf_run.get_datapoint_id_by_label("prep_containers")
            prep_container = exp.get_datapoint_value(datapoint_id)["value"][0]
            datapoint_id = BK_workflow.get_datapoint_id_by_label("blank_ID")
            ID = exp.get_datapoint_value(datapoint_id)["value"]
            datapoint_id = BK_workflow.get_datapoint_id_by_label("blank_log")
            log_file_info = exp.get_datapoint_info(datapoint_id)
            log_file_name = Path(log_file_info.path).name
            log_file_info = exp.save_datapoint_value(datapoint_id, run_path / log_file_name)
            barcode = "asdf"
            master_log.append({"ID": ID, "category": "blank1", "container": prep_container["code"], "AS log": str(log_file_name), "barcode": barcode})
            datapoint_id = wf_run.get_datapoint_id_by_label("fill_containers")
            fill_container = exp.get_datapoint_value(datapoint_id)["value"][0]
            datapoint_id = BK_workflow.get_datapoint_id_by_label("fill_ID")
            fill_ID = exp.get_datapoint_value(datapoint_id)["value"]
            datapoint_id = BK_workflow.get_datapoint_id_by_label("fill_log")
            log_file_info = exp.get_datapoint_info(datapoint_id)
            log_file_name = Path(log_file_info.path).name
            log_file_info = exp.save_datapoint_value(datapoint_id, run_path / log_file_name)
            barcode = "asdf"
            master_log.append({"ID": fill_ID, "category": "fill1", "container": fill_container["code"], "AS log": str(log_file_name), "barcode": barcode})
            df = pd.DataFrame(master_log)
            df.to_csv(run_path / "AS_sequence_log.csv", index=False)

            wf_run = exp.start_run(
            workflow= wf_path / "bk_calibrate.workflow.yaml",
            payload={
                "calibrate_args":{
                    "counters_list": counters_list,
                    "counters": counters,
                    "prep": len(cells),
                    "rack": rack,
                    "path": path,
                    "sources": sources,
                    "fill": fill,
                    "chaser": chaser,
                    "aliquots": [volume/2],
                    "verbose": verbose,
                    "prep_container": prep_container
                }
            },
            
            )
            

            prep = len(cells) + len(cells)*len(aliquots)
            datapoint_id = wf_run.get_datapoint_id_by_label("containers")
            prep_container  = exp.get_datapoint_value(datapoint_id)["value"][0]
            datapoint_id = BK_workflow.get_datapoint_id_by_label("ID")
            ID = exp.get_datapoint_value(datapoint_id)["value"]
            datapoint_id = BK_workflow.get_datapoint_id_by_label("raw_log")
            log_file_info = exp.get_datapoint_info(datapoint_id)
            log_file_name = Path(log_file_info.path).name
            log_file_info = exp.save_datapoint_value(datapoint_id, run_path / log_file_name)
            barcode = "asdf"
            master_log.append({"ID": fill_ID, "category": "calibrate1", "container": prep_container["code"], "AS log": str(log_file_name), "barcode": barcode})
            df = pd.DataFrame(master_log)
            df.to_csv(run_path / "AS_sequence_log.csv", index=False)

            BK_workflow = exp.start_run(wf_path /"bk_sample_first.workflow.yaml", payload={
            "protocol_args": {
                "cells_list": cells_list,
                "rack": rack,
                "prep": prep,
                "path": path,
                "sources": sources,
                "volume": volume,
                "chaser": chaser,
                "fictive": fictive,
                "delay": delay,
                "verbose": verbose,
                "prep_container": prep_container
                
            }
            }
            )
        else:
            prep = 0
            BK_workflow = exp.start_run(wf_path /"bk_sample_rest.workflow.yaml", payload={
            "protocol_args": {
                "cells_list": cells_list,
                "rack": rack,
                "prep": prep,
                "path": path,
                "sources": sources,
                "volume": volume,
                "chaser": chaser,
                "fictive": fictive,
                "delay": delay,
                "verbose": verbose,
                "lap": sample_counter,
                "ID" : ID,
                "prompts": prompts,
                "chem": chem,
                "prep_container": last_container

                
            }
        
        }, blocking=False)

    #Third, if the ICP is done, move the container from the icp to the trash

    # if ICP_workflow is not None and ICP_workflow.status == "completed":

    #     #run the workflow that transfers the sample to the trash
    #     datapoint_id = BK_workflow.get_datapoint_id_by_label("result")
    #     result = exp.get_datapoint_value(datapoint_id)["value"]
    #     datapoint_id = BK_workflow.get_datapoint_id_by_label("last_id")
    #     last_id = exp.get_datapoint_value(datapoint_id)["value"]
    #     datapoint_id = BK_workflow.get_datapoint_id_by_label("result_file")
    #     exp.save_datapoint_value(datapoint_id, run_path / ("run_%s.csv" % last_id))
    #     datapoint_id = BK_workflow.get_datapoint_id_by_label("converted_file")
    #     exp.save_datapoint_value(datapoint_id, run_path / ("run_%s_converted.csv" % last_id))
    #     datapoint_id = BK_workflow.get_datapoint_id_by_label("result_file")
    #     exp.save_datapoint_value(datapoint_id, run_path / ("log_%s.json" % last_id))
    #     if result in [1, 2, 3]:
    #         exp.start_run(wf_path /"transfer_icp_to_trash.yaml", payload={"arm_position": trash_ur_locations[trash_counter], "rail_position": trash_rail_locations[trash_counter]}, blocking=True)
    #         ICP_workflow = None
    #         trash_counter += 1
    #     else:
    #         icp_working = False

        

    # #Second, if there is nothing on the ICP, move the first sample that has been sampled but not measured to the ICP

    # if ICP_workflow is None and measured_counter < sample_counter and icp_working:

    #     #run the workflow that transfers the next sample into the icp

    #     exp.start_run(wf_path / "transfer_to_icp.yaml", payload={"arm_position": pickup_ur_locations[measured_counter], "rail_position": pickup_rail_locations[measured_counter]}, blocking=True)

    #     #run the ICP in the background

    #     ICP_workflow = exp.start_run(wf_path / "run_icp.workflow.yaml", payload={"container": unprocessed_containers.pop(0)}, blocking=False)

    #     measured_counter += 1

