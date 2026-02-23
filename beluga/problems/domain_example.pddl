(define (domain beluga)
  (:requirements :typing :equality :action-costs)
  (:types
		beluga -         location
		hangar -         location
		jig -         location
		location -         object
		num -         object
		production-line -         object
		rack -         location
		side -         object
		slot -         object
		trailer -         location
		type -         object
)
  (:constants
		bside - side
		dummy-jig - jig
		dummy-slot - slot
		dummy-type - type
		fside - side
	)


  (:predicates
		(at-side ?l - location ?s - side) ; location l? accessible from side ?s
		(clear ?j - jig ?s - side) ; there is no jig before ?j on the rack when looking from ?s
		(empty ?l - location)
		(empty-size ?j - jig ?es - num) ; size of jig ?j when it was unloaded in an hangar
		(fit ?nspace - num ?jsize - num ?fspace - num ?r - rack) ; on rack ?r: ?nspace = ?jsize + ?fspace
		(free-space ?r - rack ?n - num) ; space available on rack ?r
		(in ?j - jig ?l - location)
		(is_type ?j - jig ?jt - type)
		(next-flight-to-process ?b - beluga ?nb - beluga) ; ?nb is the next flight to be processed
		(next-to ?j - jig ?nj - jig ?s - side) ; jig ?nj is before/next to jig ?j on the rack when looking from ?s
		(next_deliver ?j - jig ?jn - jig) ; ?jn is successor of ?j in delivery order to the production line
		(next_load ?jt - type ?s - slot ?ns - slot ?b - beluga)
		(next_unload ?j - jig ?nj - jig) ; ?nj is successor ?j in unload order
		(processed-flight ?b - beluga) ; Beluga ?b is currently loaded/unloaded
		(size ?j - jig ?s - num) ; current size of jig ?j
		(to_deliver ?j - jig ?pl - production-line) ; jig ?j must be delivered to production line ?pl
		(to_load ?jt - type ?s - slot ?b - beluga) ; jig of type ?jt must be loaded into slot ?s Beluga ?b
		(to_unload ?j - jig ?b - beluga) ; jig ?j must be next unload from Beluga ?b
	)


  (:functions
		(total-cost )
	)


	(:action load-beluga
		:parameters (?j - jig ?jt - type ?njt - type ?b - beluga ?t - trailer ?s - slot ?ns - slot)
		:precondition (and
			(in ?j ?t)
			(empty ?j)
			(is_type ?j ?jt)
			(processed-flight ?b)
			(to_load ?jt ?s ?b)
			(next_load ?njt ?s ?ns ?b)
			(at-side ?t bside)
		)
		:effect (and
			(in ?j ?b)
			(not (in ?j ?t))
			(empty ?t)
			(not (to_load ?jt ?s ?b))
			(to_load ?njt ?ns ?b)
			(increase (total-cost ) 1)
		)
	)





	(:action unload-beluga
		:parameters (?j - jig ?nj - jig ?t - trailer ?b - beluga)
		:precondition (and
			(in ?j ?b)
			(empty ?t)
			(at-side ?t bside)
			(processed-flight ?b)
			(to_unload ?j ?b)
			(next_unload ?j ?nj)
		)
		:effect (and
			(not (in ?j ?b))
			(in ?j ?t)
			(not (empty ?t))
			(not (to_unload ?j ?b))
			(to_unload ?nj ?b)
			(increase (total-cost ) 1)
		)
	)





	(:action get-from-hangar
		:parameters (?j - jig ?h - hangar ?t - trailer)
		:precondition (and
			(in ?j ?h)
			(empty ?t)
			(at-side ?t fside)
		)
		:effect (and
			(not (in ?j ?h))
			(in ?j ?t)
			(not (empty ?t))
			(empty ?h)
			(increase (total-cost ) 1)
		)
	)





	(:action deliver-to-hangar
		:parameters (?j - jig ?jn - jig ?t - trailer ?h - hangar ?pl - production-line ?s - num ?es - num)
		:precondition (and
			(in ?j ?t)
			(empty ?h)
			(at-side ?t fside)
			(to_deliver ?j ?pl)
			(next_deliver ?j ?jn)
			(size ?j ?s)
			(empty-size ?j ?es)
		)
		:effect (and
			(empty ?t)
			(empty ?j)
			(in ?j ?h)
			(not (in ?j ?t))
			(not (empty ?h))
			(not (to_deliver ?j ?pl))
			(to_deliver ?jn ?pl)
			(increase (total-cost ) 1)
			(not (size ?j ?s))
			(size ?j ?es)
		)
	)





	(:action put-down-rack
		:parameters (?j - jig ?t - trailer ?r - rack ?s - side ?jsize - num ?fspace - num ?nspace - num)
		:precondition (and
			(in ?j ?t)
			(empty ?r)
			(at-side ?t ?s)
			(at-side ?r ?s)
			(size ?j ?jsize)
			(free-space ?r ?fspace)
			(fit ?nspace ?jsize ?fspace ?r)
		)
		:effect (and
			(in ?j ?r)
			(not (in ?j ?t))
			(empty ?t)
			(not (empty ?r))
			(clear ?j bside)
			(clear ?j fside)
			(increase (total-cost ) 1)
			(not (free-space ?r ?fspace))
			(free-space ?r ?nspace)
		)
	)





	(:action stack-rack
		:parameters (?j - jig ?nj - jig ?t - trailer ?r - rack ?s - side ?os - side ?jsize - num ?fspace - num ?nspace - num)
		:precondition (and
			(not (= ?s ?os))
			(in ?j ?t)
			(in ?nj ?r)
			(at-side ?t ?s)
			(at-side ?r ?s)
			(clear ?nj ?s)
			(size ?j ?jsize)
			(free-space ?r ?fspace)
			(fit ?nspace ?jsize ?fspace ?r)
		)
		:effect (and
			(in ?j ?r)
			(not (in ?j ?t))
			(empty ?t)
			(not (clear ?nj ?s))
			(clear ?j ?s)
			(next-to ?j ?nj ?s)
			(next-to ?nj ?j ?os)
			(increase (total-cost ) 1)
			(not (free-space ?r ?fspace))
			(free-space ?r ?nspace)
		)
	)





	(:action pick-up-rack
		:parameters (?j - jig ?t - trailer ?r - rack ?s - side ?os - side ?jsize - num ?fspace - num ?nspace - num)
		:precondition (and
			(not (= ?s ?os))
			(empty ?t)
			(in ?j ?r)
			(at-side ?t ?s)
			(at-side ?r ?s)
			(clear ?j bside)
			(clear ?j fside)
			(size ?j ?jsize)
			(free-space ?r ?fspace)
			(fit ?fspace ?jsize ?nspace ?r)
		)
		:effect (and
			(in ?j ?t)
			(not (in ?j ?r))
			(empty ?r)
			(not (empty ?t))
			(not (clear ?j bside))
			(not (clear ?j fside))
			(increase (total-cost ) 1)
			(free-space ?r ?nspace)
			(not (free-space ?r ?fspace))
		)
	)





	(:action unstack-rack
		:parameters (?j - jig ?nj - jig ?t - trailer ?r - rack ?s - side ?os - side ?jsize - num ?fspace - num ?nspace - num)
		:precondition (and
			(not (= ?s ?os))
			(empty ?t)
			(in ?j ?r)
			(in ?nj ?r)
			(at-side ?t ?s)
			(at-side ?r ?s)
			(clear ?j ?s)
			(next-to ?j ?nj ?s)
			(next-to ?nj ?j ?os)
			(size ?j ?jsize)
			(free-space ?r ?fspace)
			(fit ?fspace ?jsize ?nspace ?r)
		)
		:effect (and
			(in ?j ?t)
			(not (in ?j ?r))
			(not (empty ?t))
			(not (next-to ?j ?nj ?s))
			(not (next-to ?nj ?j ?os))
			(clear ?nj ?s)
			(increase (total-cost ) 1)
			(free-space ?r ?nspace)
			(not (free-space ?r ?fspace))
		)
	)





	(:action beluga-complete
		:parameters (?b - beluga ?nb - beluga)
		:precondition (and
			(processed-flight ?b)
			(next-flight-to-process ?b ?nb)
			(to_unload dummy-jig ?b)
			(to_load dummy-type dummy-slot ?b)
		)
		:effect (and
			(not (processed-flight ?b))
			(processed-flight ?nb)
			(increase (total-cost ) 1)
		)
	)


)