(define
	(problem beluga-medium_instance13)
	(:domain beluga)
  (:objects
		; Numbers: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 21, 22, 25, 26, 32}
		n00 - num
		n01 - num
		n02 - num
		n03 - num
		n04 - num
		n05 - num
		n06 - num
		n07 - num
		n08 - num
		n09 - num
		n10 - num
		n11 - num
		n12 - num
		n13 - num
		n14 - num
		n15 - num
		n17 - num
		n18 - num
		n21 - num
		n22 - num
		n25 - num
		n26 - num
		n32 - num
		; trailers:
		beluga_trailer_1 - trailer
		factory_trailer_1 - trailer
		; Racks:
		rack00 - rack
		rack01 - rack
		; Jigs:
		jig0001 - jig
		jig0002 - jig
		jig0003 - jig
		jig0004 - jig
		jig0005 - jig
		jig0006 - jig
		jig0007 - jig
		jig0008 - jig
		jig0009 - jig
		jig0010 - jig
		jig0011 - jig
		jig0012 - jig
		jig0013 - jig
		jig0014 - jig
		jig0015 - jig
		jig0016 - jig
		jig0017 - jig
		jig0018 - jig
		jig0019 - jig
		jig0020 - jig
		typeA - type
		typeB - type
		typeC - type
		typeD - type
		typeE - type
		; hangars:
		hangar1 - hangar
		; Beluga flights:
		beluga1 - beluga
		beluga2 - beluga
		beluga3 - beluga
		beluga4 - beluga
		beluga5 - beluga
		beluga6 - beluga
		beluga7 - beluga
		beluga8 - beluga
		; Slots for outgoing flights:
		slot0 - slot
		slot1 - slot
		; Production lines:
		pl0 - production-line
		pl1 - production-line
	)
  (:init
		; Number encoding
		; Sizes fitting rack: rack00
		(fit  n00  n04  n04 rack00)
		(fit  n01  n04  n05 rack00)
		(fit  n02  n04  n06 rack00)
		(fit  n03  n04  n07 rack00)
		(fit  n04  n04  n08 rack00)
		(fit  n00  n08  n08 rack00)
		(fit  n05  n04  n09 rack00)
		(fit  n01  n08  n09 rack00)
		(fit  n00  n09  n09 rack00)
		(fit  n06  n04  n10 rack00)
		(fit  n02  n08  n10 rack00)
		(fit  n01  n09  n10 rack00)
		(fit  n07  n04  n11 rack00)
		(fit  n03  n08  n11 rack00)
		(fit  n02  n09  n11 rack00)
		(fit  n00  n11  n11 rack00)
		(fit  n09  n04  n13 rack00)
		(fit  n05  n08  n13 rack00)
		(fit  n04  n09  n13 rack00)
		(fit  n02  n11  n13 rack00)
		(fit  n10  n04  n14 rack00)
		(fit  n06  n08  n14 rack00)
		(fit  n05  n09  n14 rack00)
		(fit  n03  n11  n14 rack00)
		(fit  n11  n04  n15 rack00)
		(fit  n07  n08  n15 rack00)
		(fit  n06  n09  n15 rack00)
		(fit  n04  n11  n15 rack00)
		(fit  n13  n04  n17 rack00)
		(fit  n09  n08  n17 rack00)
		(fit  n08  n09  n17 rack00)
		(fit  n06  n11  n17 rack00)
		(fit  n14  n04  n18 rack00)
		(fit  n10  n08  n18 rack00)
		(fit  n09  n09  n18 rack00)
		(fit  n07  n11  n18 rack00)
		(fit  n00  n18  n18 rack00)
		(fit  n18  n04  n22 rack00)
		(fit  n14  n08  n22 rack00)
		(fit  n13  n09  n22 rack00)
		(fit  n11  n11  n22 rack00)
		(fit  n04  n18  n22 rack00)
		(fit  n22  n04  n26 rack00)
		(fit  n18  n08  n26 rack00)
		(fit  n17  n09  n26 rack00)
		(fit  n15  n11  n26 rack00)
		(fit  n08  n18  n26 rack00)
		(fit  n01  n25  n26 rack00)
		; Sizes fitting rack: rack01
		(fit  n00  n04  n04 rack01)
		(fit  n01  n04  n05 rack01)
		(fit  n02  n04  n06 rack01)
		(fit  n04  n04  n08 rack01)
		(fit  n00  n08  n08 rack01)
		(fit  n05  n04  n09 rack01)
		(fit  n01  n08  n09 rack01)
		(fit  n00  n09  n09 rack01)
		(fit  n06  n04  n10 rack01)
		(fit  n02  n08  n10 rack01)
		(fit  n01  n09  n10 rack01)
		(fit  n08  n04  n12 rack01)
		(fit  n04  n08  n12 rack01)
		(fit  n03  n09  n12 rack01)
		(fit  n01  n11  n12 rack01)
		(fit  n09  n04  n13 rack01)
		(fit  n05  n08  n13 rack01)
		(fit  n04  n09  n13 rack01)
		(fit  n02  n11  n13 rack01)
		(fit  n13  n04  n17 rack01)
		(fit  n09  n08  n17 rack01)
		(fit  n08  n09  n17 rack01)
		(fit  n06  n11  n17 rack01)
		(fit  n17  n04  n21 rack01)
		(fit  n13  n08  n21 rack01)
		(fit  n12  n09  n21 rack01)
		(fit  n10  n11  n21 rack01)
		(fit  n03  n18  n21 rack01)
		; trailers (Beluga side):
		(empty beluga_trailer_1)
		(at-side beluga_trailer_1 bside)
		; trailers (Factory side):
		(empty factory_trailer_1)
		(at-side factory_trailer_1 fside)
		; Racks 2
		; Rack:rack00
		(at-side rack00 bside)
		(at-side rack00 fside)
		(free-space rack00 n02)
		(in jig0002 rack00)
		(clear jig0002 bside)
		(next-to jig0002 jig0001 bside)
		(next-to jig0001 jig0002 fside)
		(in jig0001 rack00)
		(next-to jig0001 jig0004 bside)
		(next-to jig0004 jig0001 fside)
		(in jig0004 rack00)
		(next-to jig0004 jig0005 bside)
		(next-to jig0005 jig0004 fside)
		(in jig0005 rack00)
		(clear jig0005 fside)
		; Rack:rack01
		(at-side rack01 bside)
		(at-side rack01 fside)
		(free-space rack01 n02)
		(in jig0006 rack01)
		(clear jig0006 bside)
		(next-to jig0006 jig0003 bside)
		(next-to jig0003 jig0006 fside)
		(in jig0003 rack01)
		(next-to jig0003 jig0007 bside)
		(next-to jig0007 jig0003 fside)
		(in jig0007 rack01)
		(clear jig0007 fside)
		; Jigs (size):
		(is_type jig0001 typeB)
		(size jig0001 n08)
		(empty-size jig0001 n08)
		(empty jig0001)
		(is_type jig0002 typeB)
		(size jig0002 n08)
		(empty-size jig0002 n08)
		(empty jig0002)
		(is_type jig0003 typeA)
		(size jig0003 n04)
		(empty-size jig0003 n04)
		(is_type jig0004 typeA)
		(size jig0004 n04)
		(empty-size jig0004 n04)
		(is_type jig0005 typeA)
		(size jig0005 n04)
		(empty-size jig0005 n04)
		(is_type jig0006 typeA)
		(size jig0006 n04)
		(empty-size jig0006 n04)
		(empty jig0006)
		(is_type jig0007 typeB)
		(size jig0007 n11)
		(empty-size jig0007 n08)
		(is_type jig0008 typeB)
		(size jig0008 n11)
		(empty-size jig0008 n08)
		(is_type jig0009 typeA)
		(size jig0009 n04)
		(empty-size jig0009 n04)
		(is_type jig0010 typeA)
		(size jig0010 n04)
		(empty-size jig0010 n04)
		(is_type jig0011 typeA)
		(size jig0011 n04)
		(empty-size jig0011 n04)
		(is_type jig0012 typeA)
		(size jig0012 n04)
		(empty-size jig0012 n04)
		(is_type jig0013 typeA)
		(size jig0013 n04)
		(empty-size jig0013 n04)
		(is_type jig0014 typeA)
		(size jig0014 n04)
		(empty-size jig0014 n04)
		(is_type jig0015 typeA)
		(size jig0015 n04)
		(empty-size jig0015 n04)
		(is_type jig0016 typeA)
		(size jig0016 n04)
		(empty-size jig0016 n04)
		(is_type jig0017 typeA)
		(size jig0017 n04)
		(empty-size jig0017 n04)
		(is_type jig0018 typeA)
		(size jig0018 n04)
		(empty-size jig0018 n04)
		(is_type jig0019 typeA)
		(size jig0019 n04)
		(empty-size jig0019 n04)
		(is_type jig0020 typeA)
		(size jig0020 n04)
		(empty-size jig0020 n04)
		; hangars:
		(empty hangar1)
		; Flight schedule initial phase:
		(processed-flight beluga1)
		; Flight order:
		(next-flight-to-process beluga1 beluga2)
		(next-flight-to-process beluga2 beluga3)
		(next-flight-to-process beluga3 beluga4)
		(next-flight-to-process beluga4 beluga5)
		(next-flight-to-process beluga5 beluga6)
		(next-flight-to-process beluga6 beluga7)
		(next-flight-to-process beluga7 beluga8)
		; Number of flights: 8
		; Incoming jigs unload order:
		; Finished Flights
		; No already completely finished Flights
		; Current Flight: beluga1
		; No jigs
		(to_unload dummy-jig beluga1)
		; To Process Flights
		; Flight: beluga2
		; No jigs
		(to_unload dummy-jig beluga2)
		; Flight: beluga3
		; 0: jig0008
		(to_unload jig0008 beluga3)
		(in jig0008 beluga3)
		(next_unload jig0008 dummy-jig)
		; Flight: beluga4
		; 0: jig0009 1: jig0010 2: jig0011 3: jig0012 4: jig0013
		(to_unload jig0009 beluga4)
		(in jig0009 beluga4)
		(next_unload jig0009 jig0010)
		(in jig0010 beluga4)
		(next_unload jig0010 jig0011)
		(in jig0011 beluga4)
		(next_unload jig0011 jig0012)
		(in jig0012 beluga4)
		(next_unload jig0012 jig0013)
		(in jig0013 beluga4)
		(next_unload jig0013 dummy-jig)
		; Flight: beluga5
		; No jigs
		(to_unload dummy-jig beluga5)
		; Flight: beluga6
		; 0: jig0014 1: jig0015 2: jig0016 3: jig0017 4: jig0018
		(to_unload jig0014 beluga6)
		(in jig0014 beluga6)
		(next_unload jig0014 jig0015)
		(in jig0015 beluga6)
		(next_unload jig0015 jig0016)
		(in jig0016 beluga6)
		(next_unload jig0016 jig0017)
		(in jig0017 beluga6)
		(next_unload jig0017 jig0018)
		(in jig0018 beluga6)
		(next_unload jig0018 dummy-jig)
		; Flight: beluga7
		; 0: jig0019 1: jig0020
		(to_unload jig0019 beluga7)
		(in jig0019 beluga7)
		(next_unload jig0019 jig0020)
		(in jig0020 beluga7)
		(next_unload jig0020 dummy-jig)
		; Flight: beluga8
		; No jigs
		(to_unload dummy-jig beluga8)
		; Outgoing jigs load order:
		; Finished Flights
		; No already completely finished Flights
		; Current Flight: beluga1
		; (0: typeB) (1: typeB)
		(to_load typeB slot0 beluga1)
		(next_load typeB slot0 slot1 beluga1)
		(next_load dummy-type slot1 dummy-slot beluga1)
		; To Process Flights
		; 0: typeA
		(to_load typeA slot0 beluga2)
		(next_load dummy-type slot0 dummy-slot beluga2)
		; 0: typeA 1: typeA
		(to_load typeA slot0 beluga3)
		(next_load typeA slot0 slot1 beluga3)
		(next_load dummy-type slot1 dummy-slot beluga3)
		; No jigs
		(to_load dummy-type dummy-slot beluga4)
		; 0: typeB 1: typeB
		(to_load typeB slot0 beluga5)
		(next_load typeB slot0 slot1 beluga5)
		(next_load dummy-type slot1 dummy-slot beluga5)
		; 0: typeA 1: typeA
		(to_load typeA slot0 beluga6)
		(next_load typeA slot0 slot1 beluga6)
		(next_load dummy-type slot1 dummy-slot beluga6)
		; 0: typeA 1: typeA
		(to_load typeA slot0 beluga7)
		(next_load typeA slot0 slot1 beluga7)
		(next_load dummy-type slot1 dummy-slot beluga7)
		; 0: typeA 1: typeA
		(to_load typeA slot0 beluga8)
		(next_load typeA slot0 slot1 beluga8)
		(next_load dummy-type slot1 dummy-slot beluga8)
		; Production schedule:
		; Production line: pl0
		; 0: jig0005 1: jig0007 2: jig0012 3: jig0011 4: jig0013 5: jig0016 6: jig0019
		(to_deliver jig0005 pl0)
		(next_deliver jig0005 jig0007)
		(next_deliver jig0007 jig0012)
		(next_deliver jig0012 jig0011)
		(next_deliver jig0011 jig0013)
		(next_deliver jig0013 jig0016)
		(next_deliver jig0016 jig0019)
		(next_deliver jig0019 dummy-jig)
		; Production line: pl1
		; 0: jig0004 1: jig0003 2: jig0008 3: jig0010 4: jig0009 5: jig0014 6: jig0018
		(to_deliver jig0004 pl1)
		(next_deliver jig0004 jig0003)
		(next_deliver jig0003 jig0008)
		(next_deliver jig0008 jig0010)
		(next_deliver jig0010 jig0009)
		(next_deliver jig0009 jig0014)
		(next_deliver jig0014 jig0018)
		(next_deliver jig0018 dummy-jig)
		; Action cost:
		(= (total-cost ) 0)
	)
  (:goal (and
		; All jigs empty (order defined by production schedule)
		(empty jig0005)
		(empty jig0007)
		(empty jig0012)
		(empty jig0011)
		(empty jig0013)
		(empty jig0016)
		(empty jig0019)
		(empty jig0004)
		(empty jig0003)
		(empty jig0008)
		(empty jig0010)
		(empty jig0009)
		(empty jig0014)
		(empty jig0018)
		; all Belugas fully unloaded:
		(to_unload dummy-jig beluga1)
		(to_unload dummy-jig beluga2)
		(to_unload dummy-jig beluga3)
		(to_unload dummy-jig beluga4)
		(to_unload dummy-jig beluga5)
		(to_unload dummy-jig beluga6)
		(to_unload dummy-jig beluga7)
		(to_unload dummy-jig beluga8)
		; all Belugas fully loaded:
		(to_load dummy-type dummy-slot beluga1)
		(to_load dummy-type dummy-slot beluga2)
		(to_load dummy-type dummy-slot beluga3)
		(to_load dummy-type dummy-slot beluga4)
		(to_load dummy-type dummy-slot beluga5)
		(to_load dummy-type dummy-slot beluga6)
		(to_load dummy-type dummy-slot beluga7)
		(to_load dummy-type dummy-slot beluga8)
	))
  (:metric minimize (total-cost))
)