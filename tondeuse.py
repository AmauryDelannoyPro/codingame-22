import copy
from dataclasses import dataclass, field
import sys
import math

from operator import attrgetter

# region dataclass
@dataclass
class Joueur:
    id: int
    matter : int = field(default_factory=int)
    # si on ne fait pas field mais direct le type, on aura une variable de classe au lieu de variable d'instance
    cases: list = field(default_factory=list)
    robots: dict = field(default_factory=dict)
    recycleurs: dict = field(default_factory=dict)

    def reset(self):
        self.matter = 0
        self.cases.clear()
        self.robots.clear()
        self.recycleurs.clear()


@dataclass(eq=False)
class Coord:
    x: int
    y: int

    def __repr__(self):
        return f"({self.x},{self.y})"


@dataclass(eq=False)
class Case(Coord):
    scrap_amount : int = field(default_factory=int)
    owner : int = field(default_factory=int)
    nb_unit : int = field(default_factory=int)
    nb_recycler : int = field(default_factory=int)
    # TODO utiliser ces cases, nom de nom !
    can_build : bool = field(default_factory=bool)
    can_spawn : bool = field(default_factory=bool)
    in_recycler_range : bool = field(default_factory=bool)
    scrap_value = 0  # Total scrap avec case adjacente
    is_recycled = False

    def __init__(self, c: Coord):
        super().__init__(c.x, c.y)

    def __repr__(self):
        return f"Case{super().__repr__()} a {self.owner} [({self.scrap_amount}-{self.scrap_value}) S/ {self.nb_unit} U/ {self.nb_recycler} R]"

    def calcul_scrap_value(self):
        self.scrap_value = scrap_amount
        # UP
        if self.y > 0:
            case = get_case(self.x, self.y-1)
            if not case.is_recycled:
                self.scrap_value += case.scrap_amount
        # DOWN
        if self.y < height - 1:
            case = get_case(self.x, self.y + 1)
            if not case.is_recycled:
                self.scrap_value += case.scrap_amount
        # LEFT
        if self.x > 0:
            case = get_case(self.x - 1, self.y)
            if not case.is_recycled:
                self.scrap_value += case.scrap_amount
        # RIGHT
        if self.x < width - 1:
            case = get_case(self.x + 1, self.y)
            if not case.is_recycled:
                self.scrap_value += case.scrap_amount


    def calcul_is_recycled(self):
        if self.nb_recycler > 0:
            self.is_recycled = True
        else :
            # UP
            if self.y > 0:
                self.is_recycled = self.is_recycled or get_case(self.x, self.y-1).nb_recycler > 0
            # DOWN
            if self.y < height - 1:
                self.is_recycled = self.is_recycled or get_case(self.x, self.y + 1).nb_recycler > 0
            # LEFT
            if self.x > 0:
                self.is_recycled = self.is_recycled or get_case(self.x - 1, self.y).nb_recycler > 0
            # RIGHT
            if self.x < width - 1:
                self.is_recycled = self.is_recycled or get_case(self.x + 1, self.y).nb_recycler > 0

# @dataclass
# class Robot(Coord):
#     def __init__(self, c: Coord):
#         super().__init__(c.x, c.y)
#
#
# @dataclass
# class Recycleur(Coord):
#     def __init__(self, c: Coord):
#         super().__init__(c.x, c.y)
# endregion dataclass

# region globals
map_table = []
width, height = [int(i) for i in input().split()]
j_ally, j_ennemy, j_neutre = Joueur(1), Joueur(0), Joueur(-1)
output = []
# endregion globals


# region helper
def debug(msg):
    print(msg, file=sys.stderr, flush=True)


def afficheMap():
    # TODO faire mieux quand on aura la motiv
    debug(map_table)


def get_case(x,y) -> Case:
    return map_table[y][x]
# endregion helper


def move_all_to(dest : Coord):
    robots = j_ally.robots
    for coord, nb_robot in robots.items():
        output.append(f"MOVE {nb_robot} {coord.x} {coord.y} {dest.x} {dest.y}")


def attack_recycler():
    recyclers = j_ennemy.recycleurs
    if len(recyclers) > 0:
        move_all_to(list(recyclers.keys())[0])
    else:
        # TODO gerer le else
        move_all_to(Coord(5,5))


def build_recycler():
    """
    On regarde si construire un recycler peut rapporter +10 mat??riaux
    Si oui, on prend celui qui rapporte un max
    """

    # LIMIT NB RECYCLER ?? 3 max
    if len(j_ally.recycleurs) < 3:
        if j_ally.matter >= 10:
            # TODO Utiliser les infos de debug 'can_build' et l'autre
            # TODO la recherche est pt??t pas top.
            # Parfois on empiete sur des recycleurs, le calcul indique 35 scrap alors qu'il devrait y avoir 26
            # On a build sur une case qui avait 22 alors qu'une 24 ??tait dispo

            # deepcopy : copy liste et sous liste sans ref a l'original
            copy_my_cases = copy.deepcopy(j_ally.cases)
            for case in copy_my_cases:
                case.calcul_is_recycled()
                case.calcul_scrap_value()

            not_recycling_spots = [c for c in copy_my_cases if c.is_recycled == False and c.can_build]
            if len(not_recycling_spots) > 0:
                better_spot = max(not_recycling_spots, key=attrgetter('scrap_value'))

                # ??a a l'air worth, on construit
                if better_spot.scrap_value > 10:
                    output.append(f"BUILD {better_spot.x} {better_spot.y}")


def attack_closest_ennemy_cases():
    """
    On va vers la case ennemi la plus proche
    :return:
    """
    RATIO_DISTANCE = 5
    for my_robot_coord, nb_robot in j_ally.robots.items():
        ally_coord = [my_robot_coord.x, my_robot_coord.y]
        closest_ennemy = find_closest_in_list(ally_coord, j_ennemy.cases)
        closest_neutral = find_closest_in_list(ally_coord, j_neutre.cases)
        # TODO v??rifier si on a pas de l'herbe (car impraticable)

        # Si la case ennemi est RATION_DISTANCE fois plus proche, on va vesr celle-ci
        if list(closest_ennemy.values())[0] <= list(closest_neutral.values())[0] * RATIO_DISTANCE:
            target_coord = Coord(list(closest_ennemy.keys())[0].x, list(closest_ennemy.keys())[0].y)
        else:
            target_coord = Coord(list(closest_neutral.keys())[0].x, list(closest_neutral.keys())[0].y)
        output.append(f"MOVE {nb_robot} {my_robot_coord.x} {my_robot_coord.y} {target_coord.x} {target_coord.y}")



def find_closest_in_list(ally_coord, list_to_browse):
    closest = {}
    for target_case in list_to_browse:
        target_coord = [target_case.x, target_case.y]
        distance = math.dist(ally_coord, target_coord)

        if len(closest) == 0 or distance < list(closest.values())[0]:
            closest.clear()
            closest.update({Coord(target_coord[0], target_coord[1]): distance})
    return closest


def spawn_closest_ennemy_cases():
    closest = {}
    for my_case in j_ally.cases:
        if my_case.can_spawn:
            ally_coord = [my_case.x, my_case.y]
            for ennemy_case in j_ennemy.cases:
                ennemy_coord = [ennemy_case.x, ennemy_case.y]
                distance = math.dist(ally_coord, ennemy_coord)

                if len(closest) == 0 or distance < list(closest.values())[0]:
                    closest.clear()
                    debug(f"Closest spawn : {my_case}")
                    closest.update({my_case: distance})

    if len(closest) > 0:
        nb_robot = j_ally.matter // 10 #On construit autant de robot que possible
        output.append(f"SPAWN {nb_robot} {list(closest.keys())[0].x} {list(closest.keys())[0].y}")


while True:
    # Vide les infos des joueurs
    [joueur.reset() for joueur in [j_ally, j_ennemy, j_neutre]]
    output = []

    # Nb mati??re a dispo par joueur
    j_ally.matter, j_ennemy.matter = [int(i) for i in input().split()]

    for i in range(height):
        map_table.append([])
        for j in range(width):
            # owner: 1 = me, 0 = foe, -1 = neutral
            scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = [int(k) for k in
                                                                                                input().split()]
            coord = Coord(j,i)
            new_case = Case(coord)
            if owner == -1:
                current_owner = j_neutre
            elif owner == 0:
                current_owner = j_ennemy
            else:
                current_owner = j_ally

            # INIT CASES
            new_case.scrap_amount = scrap_amount
            new_case.owner = owner
            new_case.nb_unit = units
            new_case.nb_recycler = recycler
            new_case.can_build = can_build
            new_case.can_spawn = can_spawn
            new_case.in_recycler_range = in_range_of_recycler

            map_table[i].append(new_case)

            # INIT JOUEUR
            current_owner.cases.append(new_case)
            # Add robots
            if units > 0:
                current_owner.robots.update({coord: units})
            # Add recycler
            if recycler > 0:
                current_owner.recycleurs.update({coord:recycler})

    # REFRESH CASE WITH SCRAP POSSIBLE VALUE
    for i in range(height):
        for j in range(width):
            get_case(j,i).calcul_scrap_value()

    # BUILD
    build_recycler()
    # MOVE
    attack_closest_ennemy_cases()
    # attack_recycler()
    # SPAWN
    spawn_closest_ennemy_cases()

    print("WAIT") if len(output) == 0 else print(";".join(output))
