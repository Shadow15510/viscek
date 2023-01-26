# ┌──────────────────────────────────┐ #
# │          Viscek — 1.5.0          │ #
# │ Alexis Peyroutet & Antoine Royer │ #
# │ GNU General Public Licence v3.0+ │ #
# └──────────────────────────────────┘ #

import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random


__name__ = "Viscek"
__version__ = "1.5.0"


# ┌─────────┐ #
# │ Classes │ #
# └─────────┘ #

class Agent:
    """Simule un agent avec sa position, sa vitesse, et le bruit associé qui traduit sa tendance naturelle à suivre le groupe ou pas."""

    def __init__(self, position: np.array, speed: np.array, velocity: int, noise: int, sight: int, field_sight: float=7*math.pi/36, agent_type: int=0):
        """
        position    : vecteur position (sous forme d'un tableau numpy de trois entiers)
        speed       : direction du vecteur vitesse (tableau de trois entiers)
        velocity    : norme de la vitesse
        noise       : taux de bruit qui traduit le comportement de l'agent par rapport aux autres (0 suit les autres, 1 ne suit pas les autres)
        sight       : distance à laquelle l'agent voit les autres
        field_sight : angle de vision de l'agent de chaque côté du vecteur vitesse
        agent_type  : type d'agent (0 : agent normal ; 1 : agent répulsif)
        """
        self.position = position.copy()
        self.speed = speed.copy()
        self.velocity = velocity
        self.noise = noise
        self.sight = sight
        self.field_sight = field_sight
        self.agent_type = agent_type

    def __str__(self):
        """Affiche l'agent avec ses paramètres."""
        return f"Agent(\n\tposition={list(self.position)},\n\tspeed={list(self.speed)},\n\tvelocity={self.velocity},\n\tnoise={self.noise},\n\tsight={self.sight},\n\tfield_sight={self.field_sight * 360 / math.pi},\n\ttype={self.agent_type}\n)"
    
    __repr__ = __str__

    def __sub__(self, agent):
        """
        agent : un autre agent
        Retourne la distance entre les deux agents.
        """
        return math.sqrt(sum((self.position - agent.position) ** 2))

    __rsub__ = __sub__

    def __eq__(self, agent):
        """
        agent : un autre agent
        Retourne True si les agents ont les mêmes positions, False sinon.
        """
        return list(self.position) == list(agent.position)

    def copy(self):
        """Renvoie une copie profonde de l'agent."""
        return Agent(self.position.copy(), self.speed.copy(), self.velocity, self.noise, self.sight, self.field_sight, self.agent_type)

    def next_step(self, neighbours: list, dim: int):
        """
        neighbours : liste des agents voisins
        dim        : dimension de l'espace
        """
        average_speed = np.zeros((dim))
        for agent in neighbours:
            if agent.agent_type == 1:
                average_speed = (self.position - agent.position)
                break
            average_speed += agent.speed

        self.position += self.velocity * 0.5 * self.speed
        self.speed = average_speed + (self.noise * np.random.randint(0, math.floor(self.velocity) + 1, dim))
        self.speed /= norm(self.speed)


class Group:
    """Simule un groupe d'agents, permet de le faire évoluer et de l'afficher"""
    
    def __init__(self, agents: list, dim: int=2):
        """
        agents : liste des agents du groupe
        dim    : dimension de l'espace considéré (2 ou 3)
        """
        self.agents = agents
        self.nb_agents = len(agents)
        
        if not dim in (2, 3):
            raise DimensionError("dim must be 2 or 3")
        self.dimension = dim

        for agent in agents:
            if len(agent.position) != dim or len(agent.speed) != dim:
                raise DimensionError("dimension of agents don't match")
    
    def copy(self):
        """Renvoie une copie profonde du groupe."""
        return Group([agent.copy() for agent in self.agents], self.dimension)

    def add_agent(self, agent: Agent):
        if len(agent.position) != self.dimension or len(agent.speed) != self.dimension:
                raise DimensionError("dimension of agents don't match")
        self.agents.append(agent.copy())
        self.nb_agents += 1

    def get_neighbours(self, targeted_agent: Agent, dmin: int, check_field: bool=True):
        """
        targeted_agent : agent servant de référence pour le calcul de distance
        dmin           : distance minimale à considérer
        check_field    : prise en compte de l'angle de vue de l'agent (True par défaut)
        Retourne une liste d'agents appartenant au groupe et étant à une distance inférieure ou égale à dmin.
        """
        agents = [agent for agent in self.agents if (targeted_agent - agent) <= dmin]

        if not check_field:
            return agents
        else:
            visible_agents = []
            for agent in agents:
                if agent == targeted_agent: visible_agents.append(agent)
                else:
                    vect = agent.position - targeted_agent.position
                    vect /= norm(vect)
                    angle = sum(vect * targeted_agent.speed) / (norm(vect) * norm(targeted_agent.speed))
                    if abs(math.acos(angle)) <= targeted_agent.field_sight: visible_agents.append(agent)

            return visible_agents

    def get_agents_parameters(self):
        """Retourne un tuple de tableaux numpy contenant les positions et les vitesses de tous les agents du groupe."""
        positions = np.zeros((self.nb_agents, self.dimension))
        speeds = np.zeros((self.nb_agents, self.dimension))

        for index, agent in enumerate(self.agents):
            positions[index] = agent.position
            speeds[index] = agent.velocity * agent.speed

        return positions, speeds

    def compute_figure(self):
        """Génère une figure matplotlib avec le groupe d'agents sous forme d'un nuage de points en deux ou trois dimensions avec les vecteurs vitesses."""
        positions, speeds = self.get_agents_parameters()

        fig = plt.figure()
        if self.dimension == 2:
            ax = plt.axes()
            ax.scatter(positions[:, 0], positions[:, 1], s=5, c="black")
            for agent_index in range(self.nb_agents):
                ax.quiver(positions[agent_index, 0], positions[agent_index, 1], speeds[agent_index, 0], speeds[agent_index, 1], color="black", width=0.002, scale=0.25, scale_units="xy", headwidth=0, headaxislength=0, headlength=0)
            ax.axes.set_xlim(-50, 50)
            ax.axes.set_ylim(-50, 50)
        else:
            ax = plt.axes(projection="3d")
            ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], s=5, c="black")
            for agent_index in range(self.nb_agents):
                ax.quiver(positions[agent_index, 0], positions[agent_index, 1], positions[agent_index, 2], speeds[agent_index, 0], speeds[agent_index, 1], speeds[agent_index, 2], color="black")
            ax.axes.set_xlim3d(-20, 20)
            ax.axes.set_ylim3d(-20, 20)
            ax.axes.set_zlim3d(-20, 20)

        return fig
        
    def show(self):
        """Affiche le groupe d'agent."""
        self.compute_figure()
        plt.show()

    def run(self, frames: int=20, interval: int=100, check_field: bool=True):
        """
        frames      : nombre d'image voulues dans l'animation (20 par défaut)
        interval    : intervale entre deux images de l'animation en ms (100 ms par défaut)
        check_field : vérification de l'angle de vue (True par defaut)
        Génère une animation.
        """
        def compute_animation(*args):
            positions = np.zeros((self.nb_agents, self.dimension))

            if self.dimension == 2:
                ax = plt.axes()
                ax.axes.set_xlim(-50, 50)
                ax.axes.set_ylim(-50, 50)

                for index, agent in enumerate(self.agents):
                    if agent.agent_type == 0: agent.next_step(self.get_neighbours(agent, agent.sight, check_field), self.dimension)
                    positions[index] = agent.position
                    ax.quiver(agent.position[0], agent.position[1], agent.velocity * agent.speed[0], agent.velocity * agent.speed[1], color="black", width=0.002, scale=0.25, scale_units="xy", headwidth=0, headaxislength=0, headlength=0)

                ax.scatter(positions[:, 0], positions[:, 1], s=5, c="black")

            else:
                ax = plt.axes(projection="3d")
                ax.axes.set_xlim3d(-20, 20)
                ax.axes.set_ylim3d(-20, 20)
                ax.axes.set_zlim3d(-20, 20)

                for index, agent in enumerate(self.agents):
                    if agent.agent_type == 0: agent.next_step(self.get_neighbours(agent, agent.sight), self.dimension)
                    positions[index] = agent.position
                    ax.quiver(agent.position[0], agent.position[1], agent.position[2], agent.speed[0], agent.speed[1], agent.speed[2], color="black")

            return ax

        fig = self.compute_figure()
        ani = animation.FuncAnimation(fig, compute_animation, frames=frames, interval=interval)
        ani.save("viscek.gif")


class DimensionError(Exception):
    pass


# ┌───────────┐ #
# │ Fonctions │ #
# └───────────┘ #

def group_generator(nb: int, position_min: int=-25, position_max: int=25, speed_min: int=-2, speed_max: int=2, sight_min: int=1, sight_max: int=6, dim: int=2):
    """
    nb: nombre d'agents à générer
    Retourne un groupe d'agents générés aléatoirement.
    """
    rlist = lambda minimum, maximum: minimum + (maximum - minimum) * np.random.random(dim)
    agents = [Agent(rlist(position_min, position_max), np.zeros(dim), 0, random.random(), random.randint(sight_min, sight_max)) for _ in range(nb)]
    for agent in agents:
        velocity = 0
        while velocity == 0:
            agent.speed = rlist(speed_min, speed_max)
            velocity = norm(agent.speed)

        agent.speed /= velocity
        agent.velocity = velocity
  
    return Group(agents, dim)


def norm(vect: np.array):
    """
    vect : tableau numpy
    Renvoie la norme du vecteur passé en argument.
    """
    return math.sqrt(sum(vect ** 2))


# ┌─────────┐ #
# │ Données │ #
# └─────────┘ #

group_20 = group_generator(20, dim=2)
group_20.add_agent(Agent(
    np.array([0., 0.]),
    np.array([0., 0.]),
    0,
    0,
    0,
    0,
    agent_type=1
))

group_40 = group_generator(40, dim=2)
