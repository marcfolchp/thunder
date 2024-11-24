Estoy haciendo un proyecto en python de un sistema de puntuación de performance de jugadores en partidos. Para ello cuento con unas 50 estadísticas individuales. He clasificado los jugadores en 3 grupos por posición: def, mid, off. Cada estadísticas es asignada una importancia o peso para cada grupo de posición.
Para calcular la puntuación:
1. Se compara mediante una división la estadśitica del jugador en ese partido con la media para esa estadśitica en las últimas temporadas o jornadas para ese grupo de posición.
2. El numero resultante del paso anterior se multiplica por el peso asignado a la estadśitica en cuestión para el grupo de posición determinado

Fórmula:
$$
Puntuación_\text{inicial} = \sum_\text{estadísticas} w_i \times \left( \frac{\text{Estadística partido}_i}{\text{Media}_\text{estadística, 40 jornadas}} \right)
$$