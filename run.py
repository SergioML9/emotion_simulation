from model.SOMENModel import SOMENModel

model = SOMENModel(1)
for i in range(721):
    model.step()
