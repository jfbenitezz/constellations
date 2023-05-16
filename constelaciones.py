import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import numpy  as np

def load_stars():
  # Lee txt como archivo y limpia
  df = pd.read_csv('stars.txt', sep=' ', header=None, names=["x","y","z","Id_Henry_Draper","Brillo","Id_Harvard","Nombre", 'col7', 'col8', 'col9', 'col10'])
  df = df.fillna(value=pd.np.nan)
  df['Nombre'] = df.apply(lambda x: ' '.join(str(val) for val in x[6:10] if str(val) != "nan"), axis=1)
  df = df.iloc[:, :-4]
  df = df.drop('z', axis=1)

  # Pasa df diccionario
  stars = df.to_dict(orient='index')

  # Asignamos un valor hex del azual al rojo a cada estrella segun el brillo
  cmap = plt.get_cmap('bwr')
  norm = mcolors.Normalize(vmin=df["Brillo"].min(), vmax=df["Brillo"].max())
  hex_colors = [mcolors.to_hex(cmap(norm(item['Brillo']))) for item in stars.values()]
  for key, value in zip(stars.keys(), hex_colors):
      stars[key]['hex'] = value
  
    
  # Crea un diccionario donde el nombre sea la llave y contenga una tupla de cordenadas
  # Para acceso mas inmediato a las estrellas relevantes en las constelaciones
  star_coords = {star['Nombre']: (star['x'], star['y']) for star in stars.values()}

  # Separamos las estrellas con varios nombres para acceder a ellas
  for star in stars.values():
      coords = (star['x'], star['y'])
      names = star['Nombre'].split('; ')
      if len(names) > 1:
        del star_coords[star['Nombre']]
      for name in names:
          star_coords[name] = coords
  return stars,star_coords


def draw_stars(stars):
  # create an empty list to store the scatter plot traces
  scatter_traces = []

  # loop through the dictionary and create a scatter plot trace for each star
  for key, value in stars.items():
      x = value['x']
      y = value['y']
      brillo = value['hex']
      scatter_traces.append(go.Scatter(x=[x], y=[y], mode='markers', 
          marker=dict( size=5,color=brillo), name=value['Nombre']))

  # create the layout and add a title
  layout = go.Layout(title='Stars', xaxis=dict(range=[-1.1, 1.1], scaleratio=1), yaxis=dict(range=[-1.1, 1], scaleratio=1), width=900, height=900, showlegend=False)

  # create the figure and add the scatter plot traces and layout
  fig = go.Figure(data=scatter_traces, layout=layout)

  # set the background color to black
  fig.update_layout(plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'),)
  return fig

def traza_const(fig,cords,file):
  with open(f'{file}.txt', 'r') as f:
      connections = f.readlines()
  connections = [element.strip("\n") for element in connections]

  segmentos = []
  for connection in connections:
      star1, star2 = connection.strip().split(",")
      x1, y1 = cords[star1]
      x2, y2 = cords[star2]
      segment = go.Scatter(x=[x1, x2],
                          y=[y1, y2],
                          mode='lines',
                          line=dict(color='rgb(234, 241, 91)'),
                          name=f"{star1} to {star2}")
      segmentos.append(segment)
  fig.add_traces(segmentos)

def Mostrar_est(fig):
  fig = draw_stars(stars)


def Mostrar_const(fig,star_coords):
  constelacion_txt=input("Introduzca nombre de constelacion ")
  traza_const(fig,star_coords,constelacion_txt)


def Mostrar_todo(fig,star_coords):
  text_list=["Boyero","Casiopea","Cazo","Cygnet","Geminis","Hydra","OsaMayor","OsaMenor"]
  for x in text_list:
    traza_const(fig,star_coords,x)
