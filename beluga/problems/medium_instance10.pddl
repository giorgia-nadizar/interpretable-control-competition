(define
	(problem beluga-medium_instance10)
	(:domain beluga)
  (:objects
		; Numbers: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 32, 33, 36, 37}
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
		n23 - num
		n24 - num
		n25 - num
		n26 - num
		n27 - num
		n28 - num
		n29 - num
		n32 - num
		n33 - num
		n36 - num
		n37 - num
		; trailers:
		beluga_trailer_1 - trailer
		beluga_trailer_2 - trailer
		beluga_trailer_3 - trailer
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
		; Slots for outgoing flights:
		slot0 - slot
		slot1 - slot
		; Production lines:
		pl0 - production-line
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
		(fit  n19  n04  n23 rack00)
		(fit  n15  n08  n23 rack00)
		(fit  n14  n09  n23 rack00)
		(fit  n12  n11  n23 rack00)
		(fit  n05  n18  n23 rack00)
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
		(fit  n23  n04  n27 rack00)
		(fit  n19  n08  n27 rack00)
		(fit  n18  n09  n27 rack00)
		(fit  n16  n11  n27 rack00)
		(fit  n09  n18  n27 rack00)
		(fit  n02  n25  n27 rack00)
		(fit  n24  n04  n28 rack00)
		(fit  n20  n08  n28 rack00)
		(fit  n19  n09  n28 rack00)
		(fit  n17  n11  n28 rack00)
		(fit  n10  n18  n28 rack00)
		(fit  n03  n25  n28 rack00)
		(fit  n00  n32  n32 rack00)
		(fit  n28  n04  n32 rack00)
		(fit  n24  n08  n32 rack00)
		(fit  n23  n09  n32 rack00)
		(fit  n21  n11  n32 rack00)
		(fit  n14  n18  n32 rack00)
		(fit  n07  n25  n32 rack00)
		(fit  n04  n32  n36 rack00)
		(fit  n32  n04  n36 rack00)
		(fit  n28  n08  n36 rack00)
		(fit  n27  n09  n36 rack00)
		(fit  n25  n11  n36 rack00)
		(fit  n18  n18  n36 rack00)
		(fit  n11  n25  n36 rack00)
		; Sizes fitting rack: rack01
		(fit  n00  n04  n04 rack01)
		(fit  n01  n04  n05 rack01)
		(fit  n02  n04  n06 rack01)
		(fit  n03  n04  n07 rack01)
		(fit  n04  n04  n08 rack01)
		(fit  n00  n08  n08 rack01)
		(fit  n05  n04  n09 rack01)
		(fit  n01  n08  n09 rack01)
		(fit  n00  n09  n09 rack01)
		(fit  n06  n04  n10 rack01)
		(fit  n02  n08  n10 rack01)
		(fit  n01  n09  n10 rack01)
		(fit  n07  n04  n11 rack01)
		(fit  n03  n08  n11 rack01)
		(fit  n02  n09  n11 rack01)
		(fit  n00  n11  n11 rack01)
		(fit  n08  n04  n12 rack01)
		(fit  n04  n08  n12 rack01)
		(fit  n03  n09  n12 rack01)
		(fit  n01  n11  n12 rack01)
		(fit  n09  n04  n13 rack01)
		(fit  n05  n08  n13 rack01)
		(fit  n04  n09  n13 rack01)
		(fit  n02  n11  n13 rack01)
		(fit  n10  n04  n14 rack01)
		(fit  n06  n08  n14 rack01)
		(fit  n05  n09  n14 rack01)
		(fit  n03  n11  n14 rack01)
		(fit  n11  n04  n15 rack01)
		(fit  n07  n08  n15 rack01)
		(fit  n06  n09  n15 rack01)
		(fit  n04  n11  n15 rack01)
		(fit  n12  n04  n16 rack01)
		(fit  n08  n08  n16 rack01)
		(fit  n07  n09  n16 rack01)
		(fit  n05  n11  n16 rack01)
		(fit  n13  n04  n17 rack01)
		(fit  n09  n08  n17 rack01)
		(fit  n08  n09  n17 rack01)
		(fit  n06  n11  n17 rack01)
		(fit  n14  n04  n18 rack01)
		(fit  n10  n08  n18 rack01)
		(fit  n09  n09  n18 rack01)
		(fit  n07  n11  n18 rack01)
		(fit  n00  n18  n18 rack01)
		(fit  n15  n04  n19 rack01)
		(fit  n11  n08  n19 rack01)
		(fit  n10  n09  n19 rack01)
		(fit  n08  n11  n19 rack01)
		(fit  n01  n18  n19 rack01)
		(fit  n16  n04  n20 rack01)
		(fit  n12  n08  n20 rack01)
		(fit  n11  n09  n20 rack01)
		(fit  n09  n11  n20 rack01)
		(fit  n02  n18  n20 rack01)
		(fit  n17  n04  n21 rack01)
		(fit  n13  n08  n21 rack01)
		(fit  n12  n09  n21 rack01)
		(fit  n10  n11  n21 rack01)
		(fit  n03  n18  n21 rack01)
		(fit  n18  n04  n22 rack01)
		(fit  n14  n08  n22 rack01)
		(fit  n13  n09  n22 rack01)
		(fit  n11  n11  n22 rack01)
		(fit  n04  n18  n22 rack01)
		(fit  n20  n04  n24 rack01)
		(fit  n16  n08  n24 rack01)
		(fit  n15  n09  n24 rack01)
		(fit  n13  n11  n24 rack01)
		(fit  n06  n18  n24 rack01)
		(fit  n21  n04  n25 rack01)
		(fit  n17  n08  n25 rack01)
		(fit  n16  n09  n25 rack01)
		(fit  n14  n11  n25 rack01)
		(fit  n07  n18  n25 rack01)
		(fit  n00  n25  n25 rack01)
		(fit  n22  n04  n26 rack01)
		(fit  n18  n08  n26 rack01)
		(fit  n17  n09  n26 rack01)
		(fit  n15  n11  n26 rack01)
		(fit  n08  n18  n26 rack01)
		(fit  n01  n25  n26 rack01)
		(fit  n24  n04  n28 rack01)
		(fit  n20  n08  n28 rack01)
		(fit  n19  n09  n28 rack01)
		(fit  n17  n11  n28 rack01)
		(fit  n10  n18  n28 rack01)
		(fit  n03  n25  n28 rack01)
		(fit  n25  n04  n29 rack01)
		(fit  n21  n08  n29 rack01)
		(fit  n20  n09  n29 rack01)
		(fit  n18  n11  n29 rack01)
		(fit  n11  n18  n29 rack01)
		(fit  n04  n25  n29 rack01)
		(fit  n01  n32  n33 rack01)
		(fit  n29  n04  n33 rack01)
		(fit  n25  n08  n33 rack01)
		(fit  n24  n09  n33 rack01)
		(fit  n22  n11  n33 rack01)
		(fit  n15  n18  n33 rack01)
		(fit  n08  n25  n33 rack01)
		(fit  n05  n32  n37 rack01)
		(fit  n33  n04  n37 rack01)
		(fit  n29  n08  n37 rack01)
		(fit  n28  n09  n37 rack01)
		(fit  n26  n11  n37 rack01)
		(fit  n19  n18  n37 rack01)
		(fit  n12  n25  n37 rack01)
		; trailers (Beluga side):
		(empty beluga_trailer_1)
		(at-side beluga_trailer_1 bside)
		(empty beluga_trailer_2)
		(at-side beluga_trailer_2 bside)
		(empty beluga_trailer_3)
		(at-side beluga_trailer_3 bside)
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
		(in jig0004 rack00)
		(clear jig0004 bside)
		(next-to jig0004 jig0003 bside)
		(next-to jig0003 jig0004 fside)
		(in jig0003 rack00)
		(clear jig0003 fside)
		; Rack:rack01
		(at-side rack01 bside)
		(at-side rack01 fside)
		(free-space rack01 n03)
		(in jig0005 rack01)
		(clear jig0005 bside)
		(next-to jig0005 jig0001 bside)
		(next-to jig0001 jig0005 fside)
		(in jig0001 rack01)
		(next-to jig0001 jig0002 bside)
		(next-to jig0002 jig0001 fside)
		(in jig0002 rack01)
		(next-to jig0002 jig0006 bside)
		(next-to jig0006 jig0002 fside)
		(in jig0006 rack01)
		(clear jig0006 fside)
		; Jigs (size):
		(is_type jig0001 typeA)
		(size jig0001 n04)
		(empty-size jig0001 n04)
		(empty jig0001)
		(is_type jig0002 typeC)
		(size jig0002 n18)
		(empty-size jig0002 n09)
		(is_type jig0003 typeD)
		(size jig0003 n25)
		(empty-size jig0003 n18)
		(is_type jig0004 typeB)
		(size jig0004 n08)
		(empty-size jig0004 n08)
		(empty jig0004)
		(is_type jig0005 typeB)
		(size jig0005 n08)
		(empty-size jig0005 n08)
		(empty jig0005)
		(is_type jig0006 typeA)
		(size jig0006 n04)
		(empty-size jig0006 n04)
		(is_type jig0007 typeC)
		(size jig0007 n18)
		(empty-size jig0007 n09)
		(is_type jig0008 typeC)
		(size jig0008 n18)
		(empty-size jig0008 n09)
		(is_type jig0009 typeC)
		(size jig0009 n18)
		(empty-size jig0009 n09)
		(is_type jig0010 typeC)
		(size jig0010 n18)
		(empty-size jig0010 n09)
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
		; Number of flights: 7
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
		; 0: jig0007 1: jig0008
		(to_unload jig0007 beluga4)
		(in jig0007 beluga4)
		(next_unload jig0007 jig0008)
		(in jig0008 beluga4)
		(next_unload jig0008 dummy-jig)
		; Flight: beluga5
		; No jigs
		(to_unload dummy-jig beluga5)
		; Flight: beluga6
		; 0: jig0009 1: jig0010
		(to_unload jig0009 beluga6)
		(in jig0009 beluga6)
		(next_unload jig0009 jig0010)
		(in jig0010 beluga6)
		(next_unload jig0010 dummy-jig)
		; Flight: beluga7
		; No jigs
		(to_unload dummy-jig beluga7)
		; Outgoing jigs load order:
		; Finished Flights
		; No already completely finished Flights
		; Current Flight: beluga1
		; (0: typeA)
		(to_load typeA slot0 beluga1)
		(next_load dummy-type slot0 dummy-slot beluga1)
		; To Process Flights
		; 0: typeB 1: typeB
		(to_load typeB slot0 beluga2)
		(next_load typeB slot0 slot1 beluga2)
		(next_load dummy-type slot1 dummy-slot beluga2)
		; 0: typeD
		(to_load typeD slot0 beluga3)
		(next_load dummy-type slot0 dummy-slot beluga3)
		; 0: typeC
		(to_load typeC slot0 beluga4)
		(next_load dummy-type slot0 dummy-slot beluga4)
		; 0: typeA
		(to_load typeA slot0 beluga5)
		(next_load dummy-type slot0 dummy-slot beluga5)
		; No jigs
		(to_load dummy-type dummy-slot beluga6)
		; 0: typeC
		(to_load typeC slot0 beluga7)
		(next_load dummy-type slot0 dummy-slot beluga7)
		; Production schedule:
		; Production line: pl0
		; 0: jig0003 1: jig0006 2: jig0002 3: jig0007 4: jig0008 5: jig0010
		(to_deliver jig0003 pl0)
		(next_deliver jig0003 jig0006)
		(next_deliver jig0006 jig0002)
		(next_deliver jig0002 jig0007)
		(next_deliver jig0007 jig0008)
		(next_deliver jig0008 jig0010)
		(next_deliver jig0010 dummy-jig)
		; Action cost:
		(= (total-cost ) 0)
	)
  (:goal (and
		; All jigs empty (order defined by production schedule)
		(empty jig0003)
		(empty jig0006)
		(empty jig0002)
		(empty jig0007)
		(empty jig0008)
		(empty jig0010)
		; all Belugas fully unloaded:
		(to_unload dummy-jig beluga1)
		(to_unload dummy-jig beluga2)
		(to_unload dummy-jig beluga3)
		(to_unload dummy-jig beluga4)
		(to_unload dummy-jig beluga5)
		(to_unload dummy-jig beluga6)
		(to_unload dummy-jig beluga7)
		; all Belugas fully loaded:
		(to_load dummy-type dummy-slot beluga1)
		(to_load dummy-type dummy-slot beluga2)
		(to_load dummy-type dummy-slot beluga3)
		(to_load dummy-type dummy-slot beluga4)
		(to_load dummy-type dummy-slot beluga5)
		(to_load dummy-type dummy-slot beluga6)
		(to_load dummy-type dummy-slot beluga7)
	))
  (:metric minimize (total-cost))
)