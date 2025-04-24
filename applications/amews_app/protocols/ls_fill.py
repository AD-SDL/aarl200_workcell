def main(counters_list, rack, path, sources, fill, verbose):
    ld = LS_open(counters_list, rack, path, sources, verbose, "fill cells")
    i=0
    for plate, well, _ in ld.tm.lib_from:
        ld.dispense_chem(ld.input_names[i],
                             plate,
                             well,
                             fill, # added volume
                             "1tip", # "1tip", # actual addition
                             True # add to sourcing log
                             )
        i+=1
    ld.finish()
    return ld, None  
def LS_open(cells, rack, path, sources, verbose=False, name = "sampling",): 
    from CustomService import CustomLS10
    import os
    ld = CustomLS10()
    ld.create_lib(name)
    COUNT = 1
    ld.disp.COUNT = COUNT

    print("\n\n")
    print("#" * 80)
    print("#\t\tAMEWS %s" % name.upper())
    print("#" * 80)
    print("\n\n")

    ld.add_param("Delay","Time","min")
    ld.add_param("StirRate","Stir Rate","rpm")
    ld.add_param("Pause","Text","")
    ld.get_params() 

    # making a substrate library
    ld.pt.add("source1","Rack 2x4 20mL Vial","Deck 10-11 Position 2")
    ld.pt.add("plate1","Rack 3x4 six Kaufmann H-cells","Deck 12-13 Heat-Cool-Stir 1")

    if 'fill' not in name:
        if rack==90: 
            ld.pt.add("ICP1","Rack 6x15 ICP robotic","Deck 16-17 Waste 1")
        if rack==60:
            ld.pt.add("ICP1","Rack 5x12 ICP robotic","Deck 16-17 Waste 1")

    # adding all plates 
    ld.add_all_plates()

    # adding off deck and plate sources
    ld.add_chem(None,"solvent")

    # making the transfer map
    if verbose: print("\n ==== map from ==== ")
    ld.tm.add_from(ld.pt,"plate1",cells,0) # by column  red compartments
    ld.tm.report_from()

    # input from a CSV file
    f = os.path.join(path, sources)
    ld.log_input(f) # input from a CSV table

    ld.Stir("plate1", 500) # rpm
    ld.dummy_fill("plate1", 1e5) # 100 mL

    # sourcing and dispensing chemicals
    source = ld.tm.full_plate(ld.pt, "source1", 1)
    return ld
