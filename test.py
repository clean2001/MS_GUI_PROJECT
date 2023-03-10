import plotly.graph_objects as go 

fig = go.Figure(data=[go.Bar(
    x=df['mz_array'],
    y=df['intensity'],
    width = 1
)])

fig.show()