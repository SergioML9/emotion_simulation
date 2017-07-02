from model.SOMENModel import SOMENModel
import matplotlib.pyplot as plt
import matplotlib

model = SOMENModel(10)

for i in range(6780):
    model.step()

workers_data = model.worker_collector.get_agent_vars_dataframe()
sensor_data = model.sensor_collector.get_agent_vars_dataframe()
time_data = model.time_collector.get_agent_vars_dataframe()
model_data = model.model_collector.get_model_vars_dataframe()

#workers_data.drop(workers_data[workers_data.Step < 50].index)
#workers_data = workers_data.drop(0, level='Step')
#print(workers_data.columns)
print(sensor_data)
print(workers_data)
print(model_data)
print(time_data)

# matplotlib.rc('xtick', labelsize=8)
# plt.plot(time_data.Time, sensor_data.Temperature)
# ax = plt.gca()
# #["{}{:02}".format(b_, a_) for a_, b_ in zip(a, b)]
# ax.set_xticklabels(["Day {}\n{:%H:%M}".format(b_, a_) for a_, b_ in zip(time_data.Time, time_data.Day)])
# ax.set_yticklabels(["{:.0f} ºC".format(a) for a in sensor_data.Temperature])
# #ax.set_xticklabels(["(Day %d%s)" % t for t in zip(time_data.Time, time_data.Day)])
# plt.show()

time_data["period"] = time_data.Day.map(str) + time_data.Time.map(str)

matplotlib.rc('xtick', labelsize=8)

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
temp_line = ax1.plot(range(0, len(time_data.Day.index)), sensor_data.Temperature, 'g-')
stress_line = ax2.plot(range(0,len(time_data.Day.index)), model_data, 'b-', label='Stress')

#ax1.set_xlabel('Days')
#ax1.set_ylabel('Temperature', color='g')
#ax2.set_ylabel('Stress', color='b')
plt.xticks(range(0, len(time_data.Day.index)), ["Day {} {:%H:%M}".format(b_, a_) for a_, b_ in zip(time_data.Time, time_data.Day)], size='small')
ax1.set_yticklabels(["{:.0f} ºC".format(a) for a in sensor_data.Temperature])
ax1.set_xticklabels(["Day {} {:%H:%M}".format(b_, a_) for a_, b_ in zip(time_data.Time, time_data.Day)], rotation=90)
xticks = ax1.xaxis.get_major_ticks()
i = 0
for xtick in xticks:
    if i % 4 != 0:
        xtick.label1.set_visible(False)
    i += 1
#temp_line.set_label('Temperature')
#stress_line.set_label('Stress')

# added these three lines
lns = temp_line+stress_line
labs = [l.get_label() for l in lns]
ax1.legend(lns, labs, loc='upper left')

plt.show()
