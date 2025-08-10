import plotly.express as px

fig = px.bar(x=["A", "B", "C"], y=[1, 3, 2])
fig.write_image("test_image.png")
print("Image saved successfully.")