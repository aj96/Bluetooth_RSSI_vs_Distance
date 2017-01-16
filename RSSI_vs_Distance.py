

import os
import sys
import struct
import bluetooth._bluetooth as bluez
import bluetooth
import datetime




def print_col_list(mylist):
    for i in mylist:
        print(i)

def print_list(mylist):
    count = 0
    for i in mylist:
        print("%d: " % count,)
        count = count + 1
        print(i)

def clear_list(mylist):
    count = 0
    for i in mylist:
        mylist.remove(mylist[count])
        count = count + 1

def avg(mylist):
    length = len(mylist)
    total = sum(mylist)
    average = total/length
    return average

def print_dict(mydict):
    for key in mydict:
        print("distance:",key,"rssi_vals:",mydict[key])

def printpacket(pkt):
    for c in pkt:
        sys.stdout.write("%02x " % struct.unpack("B",c)[0])
    print()   


def read_inquiry_mode(sock):
    """returns the current mode, or -1 on failure"""
    # save current filter
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # Setup socket filter to receive only events related to the
    # read_inquiry_mode command
    flt = bluez.hci_filter_new()
    opcode = bluez.cmd_opcode_pack(bluez.OGF_HOST_CTL, 
            bluez.OCF_READ_INQUIRY_MODE)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(flt, bluez.EVT_CMD_COMPLETE);
    bluez.hci_filter_set_opcode(flt, opcode)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

    # first read the current inquiry mode.
    bluez.hci_send_cmd(sock, bluez.OGF_HOST_CTL, 
            bluez.OCF_READ_INQUIRY_MODE )

    pkt = sock.recv(255)

    status,mode = struct.unpack("xxxxxxBB", pkt)
    if status != 0: mode = -1

    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
    return mode

def write_inquiry_mode(sock, mode):
    """returns 0 on success, -1 on failure"""
    # save current filter
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # Setup socket filter to receive only events related to the
    # write_inquiry_mode command
    flt = bluez.hci_filter_new()
    opcode = bluez.cmd_opcode_pack(bluez.OGF_HOST_CTL, 
            bluez.OCF_WRITE_INQUIRY_MODE)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    bluez.hci_filter_set_event(flt, bluez.EVT_CMD_COMPLETE);
    bluez.hci_filter_set_opcode(flt, opcode)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

    # send the command!
    bluez.hci_send_cmd(sock, bluez.OGF_HOST_CTL, 
            bluez.OCF_WRITE_INQUIRY_MODE, struct.pack("B", mode) )

    pkt = sock.recv(255)

    status = struct.unpack("xxxxxxB", pkt)[0]

    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
    if status != 0: return -1
    return 0

def search(sock):
    # save current filter
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )

    duration = 4
    max_responses = 255
    cmd_pkt = struct.pack("BBBBB", 0x33, 0x8b, 0x9e, duration, max_responses)
    bluez.hci_send_cmd(sock, bluez.OGF_LINK_CTL, bluez.OCF_INQUIRY, cmd_pkt)

    results = []


    pkt = sock.recv(255)
    ptype, event, plen = struct.unpack("BBB", pkt[:3])

    return_list = [pkt,event,old_filter,ptype,plen]
    return return_list
            
def device_inquiry_with_with_rssi(sock):
    
    myADDR = "2C:BE:08:30:85:FE" # mac address to search for
    my_rssi_list = []
    num_data_points = 15
    sample_time = 0.1

    mydict = {} # Distance vs List of RSSI values for that distance (I know this dictionary is poorly named; I was too lazy to change it)
    dist_vs_avg_rssi = {} # Distance vs Average RSSI value
    dist_vs_min_rssi = {} # Distance vs Minimum RSSI value
    dist_vs_max_rssi = {} # Distance vs Maximum RSSI value
    time_between_packets_dict = {} # Distance vs Total Time (in seconds) between packets
    dist_vs_list_of_timestamps_dict = {} # Distance vs List of all Timestamps for that distance

    dist_val = input("Enter the distance value (enter q to quit): ")
    while dist_val not in ['Q','q']:
        dist_val = float(dist_val)
        count = 0
        temp_rssi_list = [] # Temporary list of RSSI values
        temp_ts_list = [] ## Temporary list of total seconds (obtained from timestamp) 
        temp_time_between_packets = [] # Temporary list of time between packets 
        temp_timestamp_list = [] # Temporary list of timestamps 
        while count < num_data_points:
            return_list = search(sock)
            pkt = return_list[0]
            event = return_list[1]
            old_filter = return_list[2]
            
            if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
                pkt = pkt[3:]
                nrsp = bluetooth.get_byte(pkt[0])
                for i in range(nrsp):
                    addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
                    rssi = bluetooth.byte_to_signed_int(
                            bluetooth.get_byte(pkt[1+13*nrsp+i]))
                    

                   
                    #results.append( ( addr, rssi ) )
                    ## ADAM BEGINS EDITING
                    if addr == myADDR:
                        print("Found iphone: %s" % addr)
                        rssi = bluetooth.byte_to_signed_int(
                            bluetooth.get_byte(pkt[1+13*nrsp+i]))
                        rssi = float(rssi)
                        print("%d: %.2f dbm" % (count,rssi))
                        temp_rssi_list.append(rssi)

                        ts = datetime.datetime.now() # Get current time stamp
                        ts_str = str(ts)
                        temp_timestamp_list.append(ts_str)
                        print("Current time stamp: %s" % ts)
                        total_seconds = ts.day*86400 + ts.hour*3600 + ts.minute*60 + ts.second + ts.microsecond*(10**-6)
                        temp_ts_list.append(total_seconds)
                        if len(temp_ts_list) > 1: ## Time Stamp Line
                            time_between_packets = (temp_ts_list[count] - temp_ts_list[count-1]) ## Time Stamp Line
                            temp_time_between_packets.append(time_between_packets)
                            print("time between packets: %f\n" % time_between_packets) ## Time Stamp Line
                        

                        count = count + 1

        temp_avg = avg(temp_rssi_list)
        temp_min = min(temp_rssi_list)
        temp_max = max(temp_rssi_list)
        time_between_packets_avg = avg(temp_time_between_packets) ## Time Stamp Line

        print("Average: %.6f db" % temp_avg)
        print("Min: %.6f db" % temp_min)
        print("Max: %.6f db" % temp_max)
        print("Average time_between packets: %.4f s" % time_between_packets_avg) ## Time Stamp Line

        dist_vs_avg_rssi[dist_val] = temp_avg
        dist_vs_min_rssi[dist_val] = temp_min
        dist_vs_max_rssi[dist_val] = temp_max
        mydict[dist_val] = temp_rssi_list
        time_between_packets_dict[dist_val] = time_between_packets_avg ## Time Stamp Line
        dist_vs_list_of_timestamps_dict[dist_val] = temp_timestamp_list ## Time Stamp Line

        try:
            dist_val = input("Enter the distance value: ")
        except:
            break
        

    print("mydict: ")
    print_dict(mydict)
    print("dist_vs_avg_rssi: ")
    print_dict(dist_vs_avg_rssi)
    print("dist_vs_min_rssi: ")
    print_dict(dist_vs_min_rssi)
    print("dist_vs_max_rssi: ")
    print_dict(dist_vs_max_rssi)

    """ Saving data to Text Files """

    open("dist_vs_avg_rssi_data.txt",'w').close()
    for key in dist_vs_avg_rssi:
        with open("dist_vs_avg_rssi_data.txt",'a') as f:
            f.write("%.2f : %.6f\n" % (key,dist_vs_avg_rssi[key]))

    open("dist_vs_min_rssi_data.txt",'w').close()
    for key in dist_vs_min_rssi:
        with open("dist_vs_min_rssi_data.txt",'a') as f:
            f.write("%.2f: %.6f\n" % (key,dist_vs_min_rssi[key]))

    open("dist_vs_max_rssi_data.txt",'w').close()
    for key in dist_vs_max_rssi:
        with open("dist_vs_max_rssi_data.txt",'a') as f:
            f.write("%.2f: %.6f\n" % (key,dist_vs_max_rssi[key]))


            
    open("dist_vs_list_rssi_data.txt",'w').close()

    with open("dist_vs_list_rssi_data.txt",'a') as f:
        for key in mydict:
            mystring = ''
            for index in mydict[key]:
                mystring = mystring + ("%s " % index)
                
            
            f.write(("%.2f : " % key)+mystring+"\n")

    open("dist_vs_time_between_packets.txt",'w').close() 
    for key in time_between_packets_dict: 
        with open("dist_vs_time_between_packets.txt",'a') as f: 
            f.write("%.2f: %.4f\n" % (key,time_between_packets_dict[key])) 

                                
    open("dist_vs_list_of_timestamps_dict.txt",'w').close()
    with open("dist_vs_list_of_timestamps_dict.txt",'a') as f:
        for key in dist_vs_list_of_timestamps_dict:
            mystring = ''
            for index in dist_vs_list_of_timestamps_dict[key]:
                mystring = mystring + ("%s | " % index)

            f.write(("%.2f : " % key)+mystring+"\n")                        
                    
                
            ## print("[%s] RSSI: [%d]" % (addr, rssi))
##        elif event == bluez.EVT_INQUIRY_COMPLETE:
##            done = True
##            print("Inquiry Complete")
##            #count = num_data_points
##        elif event == bluez.EVT_CMD_STATUS:
##            status, ncmd, opcode = struct.unpack("BBH", pkt[3:7])
##            if status != 0:
##                print("uh oh...")
##                printpacket(pkt[3:7])
##                done = True
##                count = num_data_points
##        elif event == bluez.EVT_INQUIRY_RESULT:
##            pkt = pkt[3:]
##            nrsp = bluetooth.get_byte(pkt[0])
##            for i in range(nrsp): 
##                addr = bluez.ba2str( pkt[1+6*i:1+6*i+6] )
##                results.append( ( addr, -1 ) )
##                print("[%s] (no RRSI)" % addr)
##        else:
##            print("unrecognized packet type 0x%02x" % ptype)
             #print("event ", event)


    # restore old filter
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )

    #return results

dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
except:
    print("error accessing bluetooth device...")
    sys.exit(1)

try:
    mode = read_inquiry_mode(sock)
except Exception as e:
    print("error reading inquiry mode.  ")
    print("Are you sure this a bluetooth 1.2 device?")
    print(e)
    sys.exit(1)
print("current inquiry mode is %d" % mode)

if mode != 1:
    print("writing inquiry mode...")
    try:
        result = write_inquiry_mode(sock, 1)
    except Exception as e:
        print("error writing inquiry mode.  Are you sure you're root?")
        print(e)
        sys.exit(1)
    if result != 0:
        print("error while setting inquiry mode")
    print("result: %d" % result)

device_inquiry_with_with_rssi(sock)
