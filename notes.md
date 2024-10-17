fivethirtyeight - How Our NBA Predictions Work

### **Model I - ELO Rating (exclusively)**

Good when tracking a team's trajectory. But only knows who won each game, the margin of victory and where the game was played.
NOT player injuries or tradings (ELO would take a long time to figure that out).


### **Model II - CARMELO (ELO x CARMELO player projections)**

Used the ELO framework to handle game results, but also used CARMELO player projections to incorporate offseason transactions.

Problem? It had trouble figuring out whether a team was having problems heading to the play-offs or was simply reserving energies.


### **Model III - RAPTOR**

Team ratings ENTIRELY based on player forecasts. Each team is judged according to the current level of talent on its roster and how much that talent is expected to play going forward.

**Talent Ratings**

Player projections forecast a player’s future by looking to the past, finding the most similar historical comparables and using their careers as a template for how a current player might fare over the rest of his playing days.

The player ratings are currently based on our RAPTOR metric, which uses a blend of basic box score stats, player tracking metrics and plus/minus data to estimate a player’s effect (per 100 possessions) on his team’s offensive or defensive efficiency.

*Aquí podemos ver ejemplos de RAPTOR metrics: https://projects.fivethirtyeight.com/nba-player-ratings/. Menciona el artículo que antes de 2014 tenían menos información disponible y que tuvieron que adaptar el modelo para poder tener en cuenta todos los datos previos a ese año.*

RAPTOR ratings start with an estimate based on a player’s history, but as the season unfolds, these ratings are adjusted using current-season performance, with younger players' ratings updating faster than those of experienced veterans (Bayesian Prior). *Habría que coger tambien información de la NBA para los jugadores que vienen de allí.*

To make the talent ratings more stable during the early stages of the regular season and playoffs, we don’t adjust a player’s rating based on in-season RAPTOR data at all until he has played 100 minutes, and the current-season numbers are phased in more slowly between 100 and 1,000 minutes during the regular season (or 750 for the playoffs).

**Overnight Updates**

*No entiendo muy bien porqué hacen esto. Imagino que es porque la información de un partido individual a un jugador tarda varios días en actualizarse, cosa que me sorprende.*

**Playing-time Projections**

Team-level based combination (court time).

combinaciones entre los mejores 5 jugadores??