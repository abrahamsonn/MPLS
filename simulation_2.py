from network_2 import Router, Host
from link_2 import Link, LinkLayer
import threading
from time import sleep
import sys
from copy import deepcopy

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 10 #give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads at the end
    
    #create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    host_3 = Host('H3')
    object_L.append(host_3)
    
    #create routers and routing tables for connected clients (subnets)
    encap_tbl_D =  {0:{'H3':0}, 2:{'H3':1}}    # table used to encapsulate network packets into MPLS frames
    frwd_tbl_D = {0:1, 1:3}     # table used to forward MPLS frames
    decap_tbl_D = {1:{2:0}}    # table used to decapsulate network packets from MPLS frames
    router_a = Router(name='RA', 
                              intf_capacity_L=[500,500, 500, 500],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D, 
                              max_queue_size=router_queue_size)
    object_L.append(router_a)

    encap_tbl_D = {}
    frwd_tbl_D = {0:1}
    decap_tbl_D = {}
    router_b = Router(name='RB', 
                              intf_capacity_L=[500,100],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_b)

    encap_tbl_D = {}
    frwd_tbl_D = {1:1}
    decap_tbl_D = {}
    router_C = Router(name='RC',
                      intf_capacity_L=[500,500],
                      encap_tbl_D = encap_tbl_D,
                      frwd_tbl_D = frwd_tbl_D,
                      decap_tbl_D = decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_C)

    encap_tbl_D = {}
    frwd_tbl_D = {0:1, 1:1}
    decap_tbl_D = {0:{0:1}, 2:{1:1}}
    router_D = Router(name='RD',
                      intf_capacity_L=[500,500,500],
                      encap_tbl_D = encap_tbl_D,
                      frwd_tbl_D = frwd_tbl_D,
                      decap_tbl_D = decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_D)
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)
    
    #add all the links - need to reflect the connectivity in cost_D tables above
    link_layer.add_link(Link(host_1, 0, router_a, 0))
    link_layer.add_link(Link(host_2, 0, router_a, 2))
    link_layer.add_link(Link(router_a, 1, router_b, 0))
    link_layer.add_link(Link(router_a, 3, router_C, 0))
    link_layer.add_link(Link(router_b, 1, router_D, 0))
    link_layer.add_link(Link(router_C, 1, router_D, 2))
    link_layer.add_link(Link(router_D, 1, host_3, 0))
    
    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run)) 
    
    for t in thread_L:
        t.start()
    
    #create some send events    
    priority = 2
    host_1.udt_send('H3', 'MESSAGE_FROM_H1', priority)
    print("Sending message from H1 to H3 with priority %d: \"MESSAGE_FROM_H1\"" % priority)
    host_2.udt_send('H3', 'MESSAGE_FROM_H2', priority)
    print("Sending message from H2 to H3 with priority %d: \"MESSAGE_FROM_H2\"\n" % priority)
        
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    #print("All simulation threads joined")
