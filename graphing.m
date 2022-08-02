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

filename = Untitled8;

time = filename.time - filename.time(1);

goal_temp = 37;
hitter = 81;

x = linspace(filename.temp(1), goal_temp, hitter);

figure;
plot(time(1:hitter), x)
hold on
plot(time, filename.temp)
ylabel("Temperature (C)", 'Fontsize', 12)
yyaxis right
plot(time, filename.control)
ylim([-10000, 35000])
xlabel("Time (s)", 'Fontsize', 12)
ylabel("Motor Command", "Fontsize", 12)
title("Heating Thermal Profile", 'Fontsize', 18)
legend('Target Thermal Profile', 'Temperature', 'Motor Command')

%% square wave shape

filename = Untitled1;

time = filename.time - filename.time(1);
t1 = 3075;
x = 7000 - t1 - 1481;

goal_temp = 16;

x = [linspace(filename.temp(1), goal_temp, t1), linspace(goal_temp, goal_temp, 1481), ...
    linspace(goal_temp, filename.temp(1), x)];

figure;
plot(time(1:7000), x(1:7000))
hold on
plot(time(1:7000), filename.temp(1:7000))
ylabel("Temperature (C)", 'Fontsize', 12)
yyaxis right
plot(time(1:7000), filename.control(1:7000))
ylim([-35000, 35000])
xlabel("Time (s)", 'Fontsize', 12)
ylabel("Motor Command", "Fontsize", 12)
title("Square Wave Heating Thermal Profile", 'Fontsize', 18)
legend('Target Thermal Profile', 'Temperature', 'Motor Command')

%% double wave shape

filename = Untitled4;

time = filename.time - filename.time(1);

factor = 0.0013632;
t1 = 7.87/factor;
t2 = 13.44/factor;
t3 = 18.1404/factor;
t4 = 25/factor;

goal_temp = 15.5;

x = [linspace(filename.temp(1), goal_temp, t1), linspace(goal_temp, 20, t2-t1), ....
    linspace(20, goal_temp, t3-t2), linspace(goal_temp, filename.temp(1), t4-t3)];

t = time(1:length(x));

figure;
plot(t, x)
hold on
plot(time, filename.temp)
ylabel("Temperature (C)", 'Fontsize', 12)
yyaxis right
plot(time, filename.control)
ylim([-35000, 35000])
xlabel("Time (s)", 'Fontsize', 12)
ylabel("Motor Command", "Fontsize", 12)
title("Dpuble Wave Heating Thermal Profile", 'Fontsize', 18)
legend('Target Thermal Profile', 'Temperature', 'Motor Command')

%% ramp shape

filename = Untitled2;

time = filename.time - filename.time(1);
peak = 5094;
x = height(time) - peak;

goal_temp = 15;

x = [linspace(filename.temp(1), goal_temp, peak), linspace(goal_temp, filename.temp(1), x)];

figure;
plot(time, x)
hold on
plot(time, filename.temp)
ylabel("Temperature (C)", 'Fontsize', 12)
yyaxis right
plot(time, filename.control)
ylim([-35000, 35000])
xlabel("Time (s)", 'Fontsize', 12)
ylabel("Motor Command", "Fontsize", 12)
title("Ramp Heating Thermal Profile", 'Fontsize', 18)
legend('Target Thermal Profile', 'Temperature', 'Motor Command')
