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


@dataclass
class Case(Coord):
    scrap_amount : int = field(default_factory=int)
    owner : int = field(default_factory=int)
    nb_unit : int = field(default_factory=int)
    nb_recycler : int = field(default_factory=int)
    can_build = False
    can_spawn = False
    in_recycler_range = False
    scrap_value = 0  # Total scrap avec case adjacente

    def __init__(self, c: Coord):
        super().__init__(c.x, c.y)

    def __repr__(self):
        return f"Case{super().__repr__()} a {self.owner} [({self.scrap_amount}-{self.scrap_value}) S/ {self.nb_unit} U/ {self.nb_recycler} R]"

    def calcul_scrap_value(self):
        self.scrap_value = scrap_amount
        # UP
        if self.y > 0:
            self.scrap_value += get_case(self.x, self.y-1).scrap_amount
        # DOWN
        if self.y < height - 1:
            self.scrap_value += get_case(self.x, self.y + 1).scrap_amount
        # LEFT
        if self.x > 0:
            self.scrap_value += get_case(self.x - 1, self.y).scrap_amount
        # RIGHT
        if self.x < width - 1:
            self.scrap_value += get_case(self.x + 1, self.y).scrap_amount

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
    On regarde si construire un recycler peut rapporter +10 matériaux
    Si oui, on prend celui qui rapporte un max
    """
    if j_ally.matter >= 10:
        # TODO gérer si la case est déja miné
        # TODO la recherche est ptét pas top. On a build sur une case qui avait 22 alors qu'une 24 était dispo
        not_recycling_spots = [c for c in j_ally.cases if c.nb_recycler ==0]
        better_spot = max(not_recycling_spots, key=attrgetter('scrap_value'))
        debug(better_spot)

        # ça a l'air worth, on construit
        if better_spot.scrap_value > 10:
            output.append(f"BUILD {better_spot.x} {better_spot.y}")


def build_robot():
    """
    Après avoir fait des recyclers, s'il reste des matériaux
    On voit pour construire des robots
    """
    # TODO
    pass


while True:
    # Vide les infos des joueurs
    [joueur.reset() for joueur in [j_ally, j_ennemy, j_neutre]]
    output = []

    # Nb matière a dispo par joueur
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
    build_robot()
    # MOVE
    attack_recycler()
    # SPAWN

    print("WAIT") if len(output) == 0 else print(";".join(output))
