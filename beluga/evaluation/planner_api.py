from abc import ABC, abstractmethod
from beluga_lib.beluga_problem import BelugaProblem
from beluga_lib.problem_state import BelugaProblemState
import json

# ============================================================================
# Basic action and plan descrition
# ============================================================================

class BelugaAction(ABC):

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def to_json_obj(self):
        pass

    def to_json_str(self):
        return json.dumps(self.to_json_obj())

    def __repr__(self):
        return self.to_json_str()


class LoadBeluga(BelugaAction):

    name = 'load_beluga'

    def __init__(self, jig : str, flight : str, trailer : str):
        super(LoadBeluga, self).__init__(LoadBeluga.name)
        self.jig = jig
        self.flight = flight
        self.trailer = trailer

    def to_json_obj(self):
        return {'name' : LoadBeluga.name,
                'j' : self.jig,
                'b' : self.flight,
                't' : self.trailer}

    def from_json_obj(json_obj : dict, prb : BelugaProblem):
        assert json_obj['name'] == LoadBeluga.name
        jig = json_obj['j']
        flight = json_obj['b']
        trailer = json_obj['t']
        return LoadBeluga(jig, flight, trailer)


class UnloadBeluga(BelugaAction):

    name = 'unload_beluga'

    def __init__(self, jig : str, flight : str, trailer : str):
        super(UnloadBeluga, self).__init__(UnloadBeluga.name)
        self.jig = jig
        self.flight = flight
        self.trailer = trailer

    def to_json_obj(self):
        return {'name' : UnloadBeluga.name,
                'j' : self.jig,
                'b' : self.flight,
                't' : self.trailer}

    def from_json_obj(json_obj : dict, prb : BelugaProblem):
        assert json_obj['name'] == UnloadBeluga.name
        jig = json_obj['j']
        flight = json_obj['b']
        trailer = json_obj['t']
        return UnloadBeluga(jig, flight, trailer)


class GetFromHangar(BelugaAction):

    name = 'get_from_hangar'

    def __init__(self, jig : str, hangar : str, trailer : str):
        super(GetFromHangar, self).__init__(GetFromHangar.name)
        self.jig = jig
        self.hangar = hangar
        self.trailer = trailer

    def to_json_obj(self):
        return {'name' : GetFromHangar.name,
                'j' : self.jig,
                'h' : self.hangar,
                't' : self.trailer}

    def from_json_obj(json_obj : dict, prb : BelugaProblem):
        assert json_obj['name'] == GetFromHangar.name
        jig = json_obj['j']
        hangar = json_obj['h']
        trailer = json_obj['t']
        return GetFromHangar(jig, hangar, trailer)


class DeliverToHangar(BelugaAction):

    name = 'deliver_to_hangar'

    def __init__(self, jig : str, hangar : str, trailer : str, pl : str):
        super(DeliverToHangar, self).__init__(DeliverToHangar.name)
        self.jig = jig
        self.hangar = hangar
        self.trailer = trailer
        self.pl = pl

    def to_json_obj(self):
        return {'name' : DeliverToHangar.name,
                'j' : self.jig,
                'h' : self.hangar,
                't' : self.trailer,
                'pl' : self.pl}

    def from_json_obj(json_obj : dict, prb : BelugaProblem):
        assert json_obj['name'] == DeliverToHangar.name
        jig = json_obj['j']
        hangar = json_obj['h']
        trailer = json_obj['t']
        pl = json_obj['pl']
        return DeliverToHangar(jig, hangar, trailer, pl)


class PutDownRack(BelugaAction):

    name = 'put_down_rack'

    def __init__(self, jig : str, trailer : str, rack : str, side : str):
        super(PutDownRack, self).__init__(PutDownRack.name)
        self.jig = jig
        self.trailer = trailer
        self.rack = rack
        self.side = side

    def to_json_obj(self):
        return {'name' : PutDownRack.name,
                'j' : self.jig,
                't' : self.trailer,
                'r' : self.rack,
                's' : self.side}

    def from_json_obj(json_obj : dict, prb : BelugaProblem):
        assert json_obj['name'] == PutDownRack.name
        jig = json_obj['j']
        trailer = json_obj['t']
        rack = json_obj['r']
        side = json_obj['s']
        return PutDownRack(jig, trailer, rack, side)


class PickUpRack(BelugaAction):

    name = 'pick_up_rack'

    def __init__(self, jig : str, trailer : str, rack : str, side : str):
        super(PickUpRack, self).__init__(PickUpRack.name)
        self.jig = jig
        self.trailer = trailer
        self.rack = rack
        self.side = side

    def to_json_obj(self):
        return {'name' : PickUpRack.name,
                'j' : self.jig,
                't' : self.trailer,
                'r' : self.rack,
                's' : self.side}

    def from_json_obj(json_obj : dict, prb : BelugaProblem):
        assert json_obj['name'] == PickUpRack.name
        jig = json_obj['j']
        trailer = json_obj['t']
        rack = json_obj['r']
        side = json_obj['s']
        return PickUpRack(jig, trailer, rack, side)


# class SwitchToBeluga(BelugaAction):

#     name = 'switch_to_beluga'

#     def __init__(self, flight : str):
#         super(SwitchToBeluga, self).__init__(SwitchToBeluga.name)
#         self.flight = flight

#     def to_json_obj(self):
#         return {'name' : SwitchToBeluga.name,
#                 'b' : self.flight}

#     def from_json_obj(json_obj : dict, prb : BelugaProblem):
#         flight = json_obj['b']
#         return SwitchToBeluga(flight)


class SwitchToNextBeluga(BelugaAction):

    name = 'switch_to_next_beluga'

    def __init__(self):
        super(SwitchToNextBeluga, self).__init__(SwitchToNextBeluga.name)

    def to_json_obj(self):
        return {'name' : SwitchToNextBeluga.name}

    def from_json_obj(json_obj : dict, prb : BelugaProblem):
        assert json_obj['name'] == SwitchToNextBeluga.name
        return SwitchToNextBeluga()



def action_from_json_obj(json_obj : dict, prb : BelugaProblem):
    # Check whether an action
    if 'name' not in json_obj:
        raise ValueError('Invalid action, missing "name" field')
    # Parse the action arguments depending on their type
    res = None
    if json_obj['name'] == LoadBeluga.name:
        res = LoadBeluga.from_json_obj(json_obj, prb)
    elif json_obj['name'] == UnloadBeluga.name:
        res = UnloadBeluga.from_json_obj(json_obj, prb)
    elif json_obj['name'] == GetFromHangar.name:
        res = GetFromHangar.from_json_obj(json_obj, prb)
    elif json_obj['name'] == DeliverToHangar.name:
        res = DeliverToHangar.from_json_obj(json_obj, prb)
    elif json_obj['name'] == PutDownRack.name:
        res = PutDownRack.from_json_obj(json_obj, prb)
    elif json_obj['name'] == PickUpRack.name:
        res = PickUpRack.from_json_obj(json_obj, prb)
    elif json_obj['name'] == SwitchToNextBeluga.name:
        res = SwitchToNextBeluga.from_json_obj(json_obj, prb)
    else:
        raise ValueError('Invalid action name "{}"'.format(json_obj['name']))
    return res


class BelugaPlan:

    def __init__(self, actions=None):
        if actions is None:
            self.actions = []
        else:
            self.actions = actions

    def append(self, action : BelugaAction):
        self.actions.append(action)

    def to_json_obj(self):
        return [a.to_json_obj() if a is not None else None for a in self.actions]

    def to_json_str(self):
        return json.dumps(self.to_json_obj())

    def __repr__(self):
        return '\n'.join(a.to_json_str() for a in self.actions)
        # return self.to_json_str()

    def from_json_obj(json_obj, prb: BelugaProblem):
        actions = [action_from_json_obj(o, prb) for o in json_obj]
        return BelugaPlan(actions)

# ============================================================================
# Deterministic Planning
# ============================================================================

class DeterministicPlannerAPI(ABC):
    """Abstract API for a deterministic planner"""

    def __init__(self):
        pass

    def setup(self):
        pass

    @abstractmethod
    def build_plan(self, prb : BelugaProblem):
        pass


# ============================================================================
# Probabilistic Planning
# ============================================================================

class ProbabilisticPlanningMetatada:

    def __init__(self, current_step, elapsed_time):
        self.current_step = current_step
        self.elapsed_time = elapsed_time

    def to_json_obj(self):
        return {'current_step': self.current_step,
                'elapsed_time': self.elapsed_time }

    def to_json_str(self, **args):
        return json.dumps(self.to_json_obj(), **args)

    def from_json_obj(json_obj):
        return ProbabilisticPlanningMetatada(json_obj['current_step'],
                                             json_obj['elapsed_time'])


class ProbabilisticPlannerAPI(ABC):

    def __init__(self):
        pass

    def setup(self, prb: BelugaProblem):
        pass

    def setup_episode(self):
        pass

    @abstractmethod
    def next_action(self,
                    state : BelugaProblemState,
                    metadata : ProbabilisticPlanningMetatada):
        pass

