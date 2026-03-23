(define
	(problem beluga-large_instance14)
	(:domain beluga)
  (:objects
		; Numbers: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 28, 29, 32, 33, 37}
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
		n19 - num
		n20 - num
		n21 - num
		n22 - num
		n24 - num
		n25 - num
		n26 - num
		n28 - num
		n29 - num
		n32 - num
		n33 - num
		n37 - num
		; trailers:
		beluga_trailer_1 - trailer
		beluga_trailer_2 - trailer
		factory_trailer_1 - trailer
		factory_trailer_2 - trailer
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
		jig0021 - jig
		jig0022 - jig
		jig0023 - jig
		jig0024 - jig
		jig0025 - jig
		jig0026 - jig
		jig0027 - jig
		jig0028 - jig
		typeA - type
		typeB - type
		typeC - type
		typeD - type
		typeE - type
		; hangars:
		hangar1 - hangar
		hangar2 - hangar
		; Beluga flights:
		beluga1 - beluga
		beluga2 - beluga
		beluga3 - beluga
		beluga4 - beluga
		beluga5 - beluga
		beluga6 - beluga
		beluga7 - beluga
		beluga8 - beluga
		beluga9 - beluga
		beluga10 - beluga
		beluga11 - beluga
		beluga12 - beluga
		beluga13 - beluga
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
		(fit  n15  n04  n19 rack00)
		(fit  n11  n08  n19 rack00)
		(fit  n10  n09  n19 rack00)
		(fit  n08  n11  n19 rack00)
		(fit  n01  n18  n19 rack00)
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
		(fit  n22  n04  n26 rack00)
		(fit  n18  n08  n26 rack00)
		(fit  n17  n09  n26 rack00)
		(fit  n15  n11  n26 rack00)
		(fit  n08  n18  n26 rack00)
		(fit  n01  n25  n26 rack00)
		(fit  n24  n04  n28 rack00)
		(fit  n20  n08  n28 rack00)
		(fit  n19  n09  n28 rack00)
		(fit  n17  n11  n28 rack00)
		(fit  n10  n18  n28 rack00)
		(fit  n03  n25  n28 rack00)
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
		(fit  n05  n32  n37 rack00)
		(fit  n33  n04  n37 rack00)
		(fit  n29  n08  n37 rack00)
		(fit  n28  n09  n37 rack00)
		(fit  n26  n11  n37 rack00)
		(fit  n19  n18  n37 rack00)
		(fit  n12  n25  n37 rack00)
		; Sizes fitting rack: rack01
		(fit  n00  n04  n04 rack01)
		(fit  n01  n04  n05 rack01)
		(fit  n03  n04  n07 rack01)
		(fit  n04  n04  n08 rack01)
		(fit  n00  n08  n08 rack01)
		(fit  n05  n04  n09 rack01)
		(fit  n01  n08  n09 rack01)
		(fit  n00  n09  n09 rack01)
		(fit  n07  n04  n11 rack01)
		(fit  n03  n08  n11 rack01)
		(fit  n02  n09  n11 rack01)
		(fit  n00  n11  n11 rack01)
		(fit  n08  n04  n12 rack01)
		(fit  n04  n08  n12 rack01)
		(fit  n03  n09  n12 rack01)
		(fit  n01  n11  n12 rack01)
		(fit  n12  n04  n16 rack01)
		(fit  n08  n08  n16 rack01)
		(fit  n07  n09  n16 rack01)
		(fit  n05  n11  n16 rack01)
		(fit  n16  n04  n20 rack01)
		(fit  n12  n08  n20 rack01)
		(fit  n11  n09  n20 rack01)
		(fit  n09  n11  n20 rack01)
		(fit  n02  n18  n20 rack01)
		; trailers (Beluga side):
		(empty beluga_trailer_1)
		(at-side beluga_trailer_1 bside)
		(empty beluga_trailer_2)
		(at-side beluga_trailer_2 bside)
		; trailers (Factory side):
		(empty factory_trailer_1)
		(at-side factory_trailer_1 fside)
		(empty factory_trailer_2)
		(at-side factory_trailer_2 fside)
		; Racks 2
		; Rack:rack00
		(at-side rack00 bside)
		(at-side rack00 fside)
		(free-space rack00 n03)
		(in jig0008 rack00)
		(clear jig0008 bside)
		(next-to jig0008 jig0005 bside)
		(next-to jig0005 jig0008 fside)
		(in jig0005 rack00)
		(next-to jig0005 jig0004 bside)
		(next-to jig0004 jig0005 fside)
		(in jig0004 rack00)
		(next-to jig0004 jig0003 bside)
		(next-to jig0003 jig0004 fside)
		(in jig0003 rack00)
		(next-to jig0003 jig0002 bside)
		(next-to jig0002 jig0003 fside)
		(in jig0002 rack00)
		(clear jig0002 fside)
		; Rack:rack01
		(at-side rack01 bside)
		(at-side rack01 fside)
		(free-space rack01 n00)
		(in jig0007 rack01)
		(clear jig0007 bside)
		(next-to jig0007 jig0006 bside)
		(next-to jig0006 jig0007 fside)
		(in jig0006 rack01)
		(next-to jig0006 jig0001 bside)
		(next-to jig0001 jig0006 fside)
		(in jig0001 rack01)
		(next-to jig0001 jig0009 bside)
		(next-to jig0009 jig0001 fside)
		(in jig0009 rack01)
		(clear jig0009 fside)
		; Jigs (size):
		(is_type jig0001 typeA)
		(size jig0001 n04)
		(empty-size jig0001 n04)
		(is_type jig0002 typeD)
		(size jig0002 n18)
		(empty-size jig0002 n18)
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
		(is_type jig0006 typeB)
		(size jig0006 n08)
		(empty-size jig0006 n08)
		(empty jig0006)
		(is_type jig0007 typeA)
		(size jig0007 n04)
		(empty-size jig0007 n04)
		(empty jig0007)
		(is_type jig0008 typeA)
		(size jig0008 n04)
		(empty-size jig0008 n04)
		(empty jig0008)
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
		(is_type jig0015 typeC)
		(size jig0015 n18)
		(empty-size jig0015 n09)
		(is_type jig0016 typeB)
		(size jig0016 n11)
		(empty-size jig0016 n08)
		(is_type jig0017 typeB)
		(size jig0017 n11)
		(empty-size jig0017 n08)
		(is_type jig0018 typeB)
		(size jig0018 n11)
		(empty-size jig0018 n08)
		(is_type jig0019 typeB)
		(size jig0019 n11)
		(empty-size jig0019 n08)
		(is_type jig0020 typeD)
		(size jig0020 n25)
		(empty-size jig0020 n18)
		(is_type jig0021 typeA)
		(size jig0021 n04)
		(empty-size jig0021 n04)
		(is_type jig0022 typeA)
		(size jig0022 n04)
		(empty-size jig0022 n04)
		(is_type jig0023 typeA)
		(size jig0023 n04)
		(empty-size jig0023 n04)
		(is_type jig0024 typeA)
		(size jig0024 n04)
		(empty-size jig0024 n04)
		(is_type jig0025 typeA)
		(size jig0025 n04)
		(empty-size jig0025 n04)
		(is_type jig0026 typeA)
		(size jig0026 n04)
		(empty-size jig0026 n04)
		(is_type jig0027 typeA)
		(size jig0027 n04)
		(empty-size jig0027 n04)
		(is_type jig0028 typeA)
		(size jig0028 n04)
		(empty-size jig0028 n04)
		; hangars:
		(empty hangar1)
		(empty hangar2)
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
		(next-flight-to-process beluga8 beluga9)
		(next-flight-to-process beluga9 beluga10)
		(next-flight-to-process beluga10 beluga11)
		(next-flight-to-process beluga11 beluga12)
		(next-flight-to-process beluga12 beluga13)
		; Number of flights: 13
		; Incoming jigs unload order:
		; Finished Flights
		; No already completely finished Flights
		; Current Flight: beluga1
		; No jigs
		(to_unload dummy-jig beluga1)
		; To Process Flights
		; Flight: beluga2
		; 0: jig0010 1: jig0011 2: jig0012 3: jig0013 4: jig0014
		(to_unload jig0010 beluga2)
		(in jig0010 beluga2)
		(next_unload jig0010 jig0011)
		(in jig0011 beluga2)
		(next_unload jig0011 jig0012)
		(in jig0012 beluga2)
		(next_unload jig0012 jig0013)
		(in jig0013 beluga2)
		(next_unload jig0013 jig0014)
		(in jig0014 beluga2)
		(next_unload jig0014 dummy-jig)
		; Flight: beluga3
		; No jigs
		(to_unload dummy-jig beluga3)
		; Flight: beluga4
		; 0: jig0015
		(to_unload jig0015 beluga4)
		(in jig0015 beluga4)
		(next_unload jig0015 dummy-jig)
		; Flight: beluga5
		; 0: jig0016
		(to_unload jig0016 beluga5)
		(in jig0016 beluga5)
		(next_unload jig0016 dummy-jig)
		; Flight: beluga6
		; No jigs
		(to_unload dummy-jig beluga6)
		; Flight: beluga7
		; No jigs
		(to_unload dummy-jig beluga7)
		; Flight: beluga8
		; 0: jig0017 1: jig0018 2: jig0019
		(to_unload jig0017 beluga8)
		(in jig0017 beluga8)
		(next_unload jig0017 jig0018)
		(in jig0018 beluga8)
		(next_unload jig0018 jig0019)
		(in jig0019 beluga8)
		(next_unload jig0019 dummy-jig)
		; Flight: beluga9
		; No jigs
		(to_unload dummy-jig beluga9)
		; Flight: beluga10
		; No jigs
		(to_unload dummy-jig beluga10)
		; Flight: beluga11
		; 0: jig0020
		(to_unload jig0020 beluga11)
		(in jig0020 beluga11)
		(next_unload jig0020 dummy-jig)
		; Flight: beluga12
		; 0: jig0021 1: jig0022 2: jig0023 3: jig0024 4: jig0025 5: jig0026 6: jig0027 7: jig0028
		(to_unload jig0021 beluga12)
		(in jig0021 beluga12)
		(next_unload jig0021 jig0022)
		(in jig0022 beluga12)
		(next_unload jig0022 jig0023)
		(in jig0023 beluga12)
		(next_unload jig0023 jig0024)
		(in jig0024 beluga12)
		(next_unload jig0024 jig0025)
		(in jig0025 beluga12)
		(next_unload jig0025 jig0026)
		(in jig0026 beluga12)
		(next_unload jig0026 jig0027)
		(in jig0027 beluga12)
		(next_unload jig0027 jig0028)
		(in jig0028 beluga12)
		(next_unload jig0028 dummy-jig)
		; Flight: beluga13
		; No jigs
		(to_unload dummy-jig beluga13)
		; Outgoing jigs load order:
		; Finished Flights
		; No already completely finished Flights
		; Current Flight: beluga1
		; (0: typeA) (1: typeA) (2: typeA) (3: typeA) (4: typeA)
		(to_load typeA slot0 beluga1)
		(next_load typeA slot0 slot1 beluga1)
		(next_load typeA slot1 slot2 beluga1)
		(next_load typeA slot2 slot3 beluga1)
		(next_load typeA slot3 slot4 beluga1)
		(next_load dummy-type slot4 dummy-slot beluga1)
		; To Process Flights
		; 0: typeB
		(to_load typeB slot0 beluga2)
		(next_load dummy-type slot0 dummy-slot beluga2)
		; 0: typeD
		(to_load typeD slot0 beluga3)
		(next_load dummy-type slot0 dummy-slot beluga3)
		; 0: typeA
		(to_load typeA slot0 beluga4)
		(next_load dummy-type slot0 dummy-slot beluga4)
		; 0: typeA
		(to_load typeA slot0 beluga5)
		(next_load dummy-type slot0 dummy-slot beluga5)
		; 0: typeA 1: typeA 2: typeA 3: typeA
		(to_load typeA slot0 beluga6)
		(next_load typeA slot0 slot1 beluga6)
		(next_load typeA slot1 slot2 beluga6)
		(next_load typeA slot2 slot3 beluga6)
		(next_load dummy-type slot3 dummy-slot beluga6)
		; 0: typeC
		(to_load typeC slot0 beluga7)
		(next_load dummy-type slot0 dummy-slot beluga7)
		; 0: typeA
		(to_load typeA slot0 beluga8)
		(next_load dummy-type slot0 dummy-slot beluga8)
		; 0: typeB
		(to_load typeB slot0 beluga9)
		(next_load dummy-type slot0 dummy-slot beluga9)
		; 0: typeB 1: typeB 2: typeB
		(to_load typeB slot0 beluga10)
		(next_load typeB slot0 slot1 beluga10)
		(next_load typeB slot1 slot2 beluga10)
		(next_load dummy-type slot2 dummy-slot beluga10)
		; No jigs
		(to_load dummy-type dummy-slot beluga11)
		; No jigs
		(to_load dummy-type dummy-slot beluga12)
		; 0: typeA
		(to_load typeA slot0 beluga13)
		(next_load dummy-type slot0 dummy-slot beluga13)
		; Production schedule:
		; Production line: pl0
		; 0: jig0011 1: jig0012 2: jig0015 3: jig0018 4: jig0027
		(to_deliver jig0011 pl0)
		(next_deliver jig0011 jig0012)
		(next_deliver jig0012 jig0015)
		(next_deliver jig0015 jig0018)
		(next_deliver jig0018 jig0027)
		(next_deliver jig0027 dummy-jig)
		; Production line: pl1
		; 0: jig0009 1: jig0013 2: jig0016 3: jig0019 4: jig0026
		(to_deliver jig0009 pl1)
		(next_deliver jig0009 jig0013)
		(next_deliver jig0013 jig0016)
		(next_deliver jig0016 jig0019)
		(next_deliver jig0019 jig0026)
		(next_deliver jig0026 dummy-jig)
		; Production line: pl2
		; 0: jig0001 1: jig0010 2: jig0014 3: jig0017 4: jig0024
		(to_deliver jig0001 pl2)
		(next_deliver jig0001 jig0010)
		(next_deliver jig0010 jig0014)
		(next_deliver jig0014 jig0017)
		(next_deliver jig0017 jig0024)
		(next_deliver jig0024 dummy-jig)
		; Action cost:
		(= (total-cost ) 0)
	)
  (:goal (and
		; All jigs empty (order defined by production schedule)
		(empty jig0011)
		(empty jig0012)
		(empty jig0015)
		(empty jig0018)
		(empty jig0027)
		(empty jig0009)
		(empty jig0013)
		(empty jig0016)
		(empty jig0019)
		(empty jig0026)
		(empty jig0001)
		(empty jig0010)
		(empty jig0014)
		(empty jig0017)
		(empty jig0024)
		; all Belugas fully unloaded:
		(to_unload dummy-jig beluga1)
		(to_unload dummy-jig beluga2)
		(to_unload dummy-jig beluga3)
		(to_unload dummy-jig beluga4)
		(to_unload dummy-jig beluga5)
		(to_unload dummy-jig beluga6)
		(to_unload dummy-jig beluga7)
		(to_unload dummy-jig beluga8)
		(to_unload dummy-jig beluga9)
		(to_unload dummy-jig beluga10)
		(to_unload dummy-jig beluga11)
		(to_unload dummy-jig beluga12)
		(to_unload dummy-jig beluga13)
		; all Belugas fully loaded:
		(to_load dummy-type dummy-slot beluga1)
		(to_load dummy-type dummy-slot beluga2)
		(to_load dummy-type dummy-slot beluga3)
		(to_load dummy-type dummy-slot beluga4)
		(to_load dummy-type dummy-slot beluga5)
		(to_load dummy-type dummy-slot beluga6)
		(to_load dummy-type dummy-slot beluga7)
		(to_load dummy-type dummy-slot beluga8)
		(to_load dummy-type dummy-slot beluga9)
		(to_load dummy-type dummy-slot beluga10)
		(to_load dummy-type dummy-slot beluga11)
		(to_load dummy-type dummy-slot beluga12)
		(to_load dummy-type dummy-slot beluga13)
	))
  (:metric minimize (total-cost))
)