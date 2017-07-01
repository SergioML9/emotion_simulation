from model.SOMENModel import SOMENModel

model = SOMENModel(10)
for i in range(14400):
    model.step()
