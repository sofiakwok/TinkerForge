filename = Untitled1;

time = filename.time - filename.time(1);

goal_temp = 25;

figure;
plot(time, linspace(goal_temp, goal_temp, height(time)), 'r')
hold on
plot(time, linspace(goal_temp + 0.1, goal_temp + 0.1, height(time)), '--r')
plot(time, linspace(goal_temp - 0.1, goal_temp - 0.1, height(time)), '--r')
plot(time, filename.temp)
ylabel("Temperature (C)", 'Fontsize', 12)
yyaxis right
plot(time, filename.control)
xlabel("Time (s)", 'Fontsize', 12)
ylabel("Motor Command", "Fontsize", 12)
title("Temperature Convergence (1, 0.1, 0.1)", 'Fontsize', 18)
legend('Target Temperature', 'Temperature', 'Motor Command')