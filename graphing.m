L = height(oops)
x = linspace(1, 20, L);

figure;
plot(x, oops.VarName1)
xlabel("Time (s)", 'Fontsize', 12)
ylabel("Temperature (C)", 'Fontsize', 12)
title("Temperature Convergence", 'Fontsize', 18)
legend('\theta_{p1}', '\theta_{p2}', 'Average \theta_p')