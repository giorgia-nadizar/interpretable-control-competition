(define
	(problem beluga-medium_instance15)
	(:domain beluga)
  (:objects
		; Numbers: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 24, 25, 29, 32, 33}
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
		n16 - num
		n17 - num
		n18 - num
		n20 - num
		n21 - num
		n22 - num
		n24 - num
		n25 - num
		n29 - num
		n32 - num
		n33 - num
		; trailers:
		beluga_trailer_1 - trailer
		factory_trailer_1 - trailer
		factory_trailer_2 - trailer
		factory_trailer_3 - trailer
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
		typeA - type
		typeB - type
		typeC - type
		typeD - type
		typeE - type
		; hangars:
		hangar1 - hangar
		hangar2 - hangar
		hangar3 - hangar
		; Beluga flights:
		beluga1 - beluga
		beluga2 - beluga
		beluga3 - beluga
		beluga4 - beluga
		beluga5 - beluga
		; Slots for outgoing flights:
		slot0 - slot
		slot1 - slot
		slot2 - slot
		slot3 - slot
		slot4 - slot
		; Production lines:
		pl0 - production-line
		pl1 - production-line
		pl2 - production-line
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
		(fit  n08  n04  n12 rack00)
		(fit  n04  n08  n12 rack00)
		(fit  n03  n09  n12 rack00)
		(fit  n01  n11  n12 rack00)
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
		(fit  n12  n04  n16 rack00)
		(fit  n08  n08  n16 rack00)
		(fit  n07  n09  n16 rack00)
		(fit  n05  n11  n16 rack00)
		(fit  n13  n04  n17 rack00)
		(fit  n09  n08  n17 rack00)
		(fit  n08  n09  n17 rack00)
		(fit  n06  n11  n17 rack00)
		(fit  n14  n04  n18 rack00)
		(fit  n10  n08  n18 rack00)
		(fit  n09  n09  n18 rack00)
		(fit  n07  n11  n18 rack00)
		(fit  n00  n18  n18 rack00)
		(fit  n16  n04  n20 rack00)
		(fit  n12  n08  n20 rack00)
		(fit  n11  n09  n20 rack00)
		(fit  n09  n11  n20 rack00)
		(fit  n02  n18  n20 rack00)
		(fit  n17  n04  n21 rack00)
		(fit  n13  n08  n21 rack00)
		(fit  n12  n09  n21 rack00)
		(fit  n10  n11  n21 rack00)
		(fit  n03  n18  n21 rack00)
		(fit  n18  n04  n22 rack00)
		(fit  n14  n08  n22 rack00)
		(fit  n13  n09  n22 rack00)
		(fit  n11  n11  n22 rack00)
		(fit  n04  n18  n22 rack00)
		(fit  n20  n04  n24 rack00)
		(fit  n16  n08  n24 rack00)
		(fit  n15  n09  n24 rack00)
		(fit  n13  n11  n24 rack00)
		(fit  n06  n18  n24 rack00)
		(fit  n21  n04  n25 rack00)
		(fit  n17  n08  n25 rack00)
		(fit  n16  n09  n25 rack00)
		(fit  n14  n11  n25 rack00)
		(fit  n07  n18  n25 rack00)
		(fit  n00  n25  n25 rack00)
		(fit  n25  n04  n29 rack00)
		(fit  n21  n08  n29 rack00)
		(fit  n20  n09  n29 rack00)
		(fit  n18  n11  n29 rack00)
		(fit  n11  n18  n29 rack00)
		(fit  n04  n25  n29 rack00)
		(fit  n01  n32  n33 rack00)
		(fit  n29  n04  n33 rack00)
		(fit  n25  n08  n33 rack00)
		(fit  n24  n09  n33 rack00)
		(fit  n22  n11  n33 rack00)
		(fit  n15  n18  n33 rack00)
		(fit  n08  n25  n33 rack00)
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
		(empty factory_trailer_2)
		(at-side factory_trailer_2 fside)
		(empty factory_trailer_3)
		(at-side factory_trailer_3 fside)
		; Racks 2
		; Rack:rack00
		(at-side rack00 bside)
		(at-side rack00 fside)
		(free-space rack00 n00)
		(in jig0007 rack00)
		(clear jig0007 bside)
		(next-to jig0007 jig0003 bside)
		(next-to jig0003 jig0007 fside)
		(in jig0003 rack00)
		(next-to jig0003 jig0001 bside)
		(next-to jig0001 jig0003 fside)
		(in jig0001 rack00)
		(clear jig0001 fside)
		; Rack:rack01
		(at-side rack01 bside)
		(at-side rack01 fside)
		(free-space rack01 n00)
		(in jig0006 rack01)
		(clear jig0006 bside)
		(next-to jig0006 jig0005 bside)
		(next-to jig0005 jig0006 fside)
		(in jig0005 rack01)
		(next-to jig0005 jig0004 bside)
		(next-to jig0004 jig0005 fside)
		(in jig0004 rack01)
		(next-to jig0004 jig0002 bside)
		(next-to jig0002 jig0004 fside)
		(in jig0002 rack01)
		(clear jig0002 fside)
		; Jigs (size):
		(is_type jig0001 typeD)
		(size jig0001 n25)
		(empty-size jig0001 n18)
		(is_type jig0002 typeC)
		(size jig0002 n09)
		(empty-size jig0002 n09)
		(empty jig0002)
		(is_type jig0003 typeA)
		(size jig0003 n04)
		(empty-size jig0003 n04)
		(empty jig0003)
		(is_type jig0004 typeA)
		(size jig0004 n04)
		(empty-size jig0004 n04)
		(empty jig0004)
		(is_type jig0005 typeA)
		(size jig0005 n04)
		(empty-size jig0005 n04)
		(empty jig0005)
		(is_type jig0006 typeA)
		(size jig0006 n04)
		(empty-size jig0006 n04)
		(empty jig0006)
		(is_type jig0007 typeA)
		(size jig0007 n04)
		(empty-size jig0007 n04)
		(empty jig0007)
		(is_type jig0008 typeA)
		(size jig0008 n04)
		(empty-size jig0008 n04)
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
		(is_type jig0018 typeB)
		(size jig0018 n11)
		(empty-size jig0018 n08)
		; hangars:
		(empty hangar1)
		(empty hangar2)
		(empty hangar3)
		; Flight schedule initial phase:
		(processed-flight beluga1)
		; Flight order:
		(next-flight-to-process beluga1 beluga2)
		(next-flight-to-process beluga2 beluga3)
		(next-flight-to-process beluga3 beluga4)
		(next-flight-to-process beluga4 beluga5)
		; Number of flights: 5
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
		; No jigs
		(to_unload dummy-jig beluga3)
		; Flight: beluga4
		; 0: jig0008 1: jig0009 2: jig0010 3: jig0011 4: jig0012 5: jig0013 6: jig0014 7: jig0015 8: jig0016 9: jig0017
		(to_unload jig0008 beluga4)
		(in jig0008 beluga4)
		(next_unload jig0008 jig0009)
		(in jig0009 beluga4)
		(next_unload jig0009 jig0010)
		(in jig0010 beluga4)
		(next_unload jig0010 jig0011)
		(in jig0011 beluga4)
		(next_unload jig0011 jig0012)
		(in jig0012 beluga4)
		(next_unload jig0012 jig0013)
		(in jig0013 beluga4)
		(next_unload jig0013 jig0014)
		(in jig0014 beluga4)
		(next_unload jig0014 jig0015)
		(in jig0015 beluga4)
		(next_unload jig0015 jig0016)
		(in jig0016 beluga4)
		(next_unload jig0016 jig0017)
		(in jig0017 beluga4)
		(next_unload jig0017 dummy-jig)
		; Flight: beluga5
		; 0: jig0018
		(to_unload jig0018 beluga5)
		(in jig0018 beluga5)
		(next_unload jig0018 dummy-jig)
		; Outgoing jigs load order:
		; Finished Flights
		; No already completely finished Flights
		; Current Flight: beluga1
		; (0: typeC)
		(to_load typeC slot0 beluga1)
		(next_load dummy-type slot0 dummy-slot beluga1)
		; To Process Flights
		; 0: typeA 1: typeA 2: typeA 3: typeA 4: typeA
		(to_load typeA slot0 beluga2)
		(next_load typeA slot0 slot1 beluga2)
		(next_load typeA slot1 slot2 beluga2)
		(next_load typeA slot2 slot3 beluga2)
		(next_load typeA slot3 slot4 beluga2)
		(next_load dummy-type slot4 dummy-slot beluga2)
		; 0: typeD
		(to_load typeD slot0 beluga3)
		(next_load dummy-type slot0 dummy-slot beluga3)
		; No jigs
		(to_load dummy-type dummy-slot beluga4)
		; 0: typeA 1: typeA 2: typeA 3: typeA 4: typeA
		(to_load typeA slot0 beluga5)
		(next_load typeA slot0 slot1 beluga5)
		(next_load typeA slot1 slot2 beluga5)
		(next_load typeA slot2 slot3 beluga5)
		(next_load typeA slot3 slot4 beluga5)
		(next_load dummy-type slot4 dummy-slot beluga5)
		; Production schedule:
		; Production line: pl0
		; 0: jig0008 1: jig0012 2: jig0011 3: jig0017
		(to_deliver jig0008 pl0)
		(next_deliver jig0008 jig0012)
		(next_deliver jig0012 jig0011)
		(next_deliver jig0011 jig0017)
		(next_deliver jig0017 dummy-jig)
		; Production line: pl1
		; 0: jig0001 1: jig0014 2: jig0016
		(to_deliver jig0001 pl1)
		(next_deliver jig0001 jig0014)
		(next_deliver jig0014 jig0016)
		(next_deliver jig0016 dummy-jig)
		; Production line: pl2
		; 0: jig0010 1: jig0013 2: jig0009 3: jig0015
		(to_deliver jig0010 pl2)
		(next_deliver jig0010 jig0013)
		(next_deliver jig0013 jig0009)
		(next_deliver jig0009 jig0015)
		(next_deliver jig0015 dummy-jig)
		; Action cost:
		(= (total-cost ) 0)
	)
  (:goal (and
		; All jigs empty (order defined by production schedule)
		(empty jig0008)
		(empty jig0012)
		(empty jig0011)
		(empty jig0017)
		(empty jig0001)
		(empty jig0014)
		(empty jig0016)
		(empty jig0010)
		(empty jig0013)
		(empty jig0009)
		(empty jig0015)
		; all Belugas fully unloaded:
		(to_unload dummy-jig beluga1)
		(to_unload dummy-jig beluga2)
		(to_unload dummy-jig beluga3)
		(to_unload dummy-jig beluga4)
		(to_unload dummy-jig beluga5)
		; all Belugas fully loaded:
		(to_load dummy-type dummy-slot beluga1)
		(to_load dummy-type dummy-slot beluga2)
		(to_load dummy-type dummy-slot beluga3)
		(to_load dummy-type dummy-slot beluga4)
		(to_load dummy-type dummy-slot beluga5)
	))
  (:metric minimize (total-cost))
)