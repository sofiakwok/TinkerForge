filename = Untitled16;

time = filename.time - filename.time(1);

goal_temp = 32;

figure;
hold on
plot(time, filename.temp)
ylabel("Temperature (C)", 'Fontsize', 12)
yyaxis right
plot(time, filename.control)
ylabel("Motor Command", "Fontsize", 12)
yyaxis left
plot(time, linspace(goal_temp, goal_temp, height(time)), 'r')
plot(time, linspace(goal_temp + 0.1, goal_temp + 0.1, height(time)), '--r')
plot(time, linspace(goal_temp - 0.1, goal_temp - 0.1, height(time)), '--r')
xlabel("Time (s)", 'Fontsize', 12)
title("Temperature Convergence (2, 0.4, 0.1)", 'Fontsize', 18)
legend('Temperature', 'Target Temperature', '+0.1', '-0.1', 'Motor Command')

%% thermal profiles

filename = Untitled12;

time = filename.time - filename.time(1);

goal_temp = 35;
hitter = 87;

x = linspace(filename.temp(1), goal_temp, hitter);

figure;
plot(time(1:hitter), x)
hold on
plot(time, filename.temp)
ylabel("Temperature (C)", 'Fontsize', 12)
yyaxis right
plot(time, filename.control)
ylim([0, 35000])
xlabel("Time (s)", 'Fontsize', 12)
ylabel("Motor Command", "Fontsize", 12)
title("Heating Thermal Profile", 'Fontsize', 18)
legend('Target Thermal Profile', 'Temperature', 'Motor Command')