clc
clear

motor1=1000;
motor2=1000;
motor3=1500;
motor4=1000;
motor_all=1000;
motor_all_en=true;
nano = serialport("COM7",115200);
writeline(nano,"Connesso");

while true
    motor1 = round(motor1);
    motor2 = round(motor2);
    motor3 = round(motor3);
    motor4 = round(motor4);
    motor_all = round(motor_all);
    if motor_all_en
        motor1=motor_all;
        motor2=motor_all;
        motor3=motor_all;
        motor4=motor_all;
    end
    str = sprintf('%d,%d,%d,%d', motor1, motor2, motor3, motor4);
    writeline(nano,str);
    disp(['Motor1 Value: ', num2str(motor1)]);
    disp(str);
    pause(0.1);
end