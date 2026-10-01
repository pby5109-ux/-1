#include "pid.h"
#include "key.h"
struct FPID XPid;
struct FPID YPid;
struct FPID MotorL;//速度环
struct FPID MotorR;
struct FPID deer;//转向环
struct FPID loca;//转向环
int16_t X_pwm=0;
int16_t Y_pwm=0;
int16_t deer_pwm=0;


// 定义位置PID控制结构
struct FPID PositionPid; // 新增位置PID控制



void Pid_Init(void)
{
    XPid.Kp = 0.8;  // 比例增益
    XPid.Ki = 0.15;  // 积分增益
    XPid.Kd = 0.9;  // 微分增益
    XPid.Kout = 0;
    XPid.voltage = 0;
    XPid.integral = 0;
    XPid.err = 0;
    XPid.err_last = 0;
	
		YPid.Kp = 0.8;  // 比例增益
    YPid.Ki = 0.15;  // 积分增益
    YPid.Kd = 0.9;  // 微分增益
    YPid.Kout = 0;
    YPid.voltage = 0;
    YPid.integral = 0;
    YPid.err = 0;
    YPid.err_last = 0;   
	
		MotorL.Kp = 40;  // 比例增益
    MotorL.Ki = 4;  // 积分增益
    MotorL.Kd = 0.5;  // 微分增益
    MotorL.Kout = 0;
    MotorL.voltage = 0;
    MotorL.integral = 0;
    MotorL.err = 0;
    MotorL.err_last = 0;
		MotorL.err_last_last=0;
		
		
		MotorR.Kp = 40;  // 比例增益
    MotorR.Ki = 2;  // 积分增益
    MotorR.Kd = 0.5;  // 微分增益
    MotorR.Kout = 0;
    MotorR.voltage = 0;
    MotorR.integral = 0;
    MotorR.err = 0;
    MotorR.err_last = 0;   
		MotorR.err_last_last=0;
		
		deer.Kp = 75.5;  // 比例增益
    deer.Ki = 0;  // 积分增益
    deer.Kd = 700.3;  // 微分增益
    deer.Kout = 0;
    deer.voltage = 0;
    deer.integral = 0;
    deer.err = 0;
    deer.err_last = 0;   
		
		PositionPid.Kp = 380;  // 比例增益
    PositionPid.Ki = 0;  // 积分增益
    PositionPid.Kd = 580.8;  // 微分增益
    PositionPid.Kout = 0;
    PositionPid.voltage = 0;
    PositionPid.integral = 0;
    PositionPid.err = 0;
    PositionPid.err_last = 0;   
		
		loca.Kp = 0.1;  // 比例增益
    loca.Ki = 0;  // 积分增益
    loca.Kd =1;  // 微分增益
    loca.Kout = 0;
    loca.voltage = 0;
    loca.integral = 0;
    loca.err = 0;
    loca.err_last = 0;   
}
int32_t Xs_pid(float a,float b)
{
    int t;

    XPid.Set      = b;
    XPid.Actual   = a;
    XPid.err      = XPid.Actual - XPid.Set;
    XPid.integral = XPid.integral + XPid.err;
    XPid.voltage = XPid.Kp*XPid.err
                + XPid.Ki*XPid.integral
                + XPid.Kd*(XPid.err-XPid.err_last)
                + XPid.Kout;
    XPid.err_last = XPid.err;
    t=XPid.voltage;
    return t;
}

int32_t Ys_pid(float a,float b)
{
    int t;

    YPid.Set      = b;
    YPid.Actual   = a;
    YPid.err      = YPid.Actual - YPid.Set;


    YPid.integral = YPid.integral + YPid.err;

    YPid.voltage = YPid.Kp*YPid.err
                + YPid.Ki*YPid.integral
                + YPid.Kd*(YPid.err-YPid.err_last)
                + YPid.Kout;

    YPid.err_last = YPid.err;

    t=YPid.voltage;

    return t;
}


int32_t MotorL_pid(float a, float b)
{
    int t;
    float delta_u;

    MotorL.Set      = b;
    MotorL.Actual   = a;
    MotorL.err      = MotorL.Set - MotorL.Actual;

    // 增量式PID
    delta_u = MotorL.Kp * (MotorL.err - MotorL.err_last)
            + MotorL.Ki * MotorL.err
            + MotorL.Kd * (MotorL.err - 2 * MotorL.err_last + MotorL.err_last_last);

    MotorL.voltage += delta_u;

    // 更新误差
    MotorL.err_last_last = MotorL.err_last;
    MotorL.err_last  = MotorL.err;

    t = MotorL.voltage;
    return t;
}

int32_t MotorR_pid(float a, float b)
{
    int t;
    float delta_u;

    MotorR.Set      = b;
    MotorR.Actual   = a;
    MotorR.err      = MotorR.Set - MotorR.Actual;

    // 增量式PID
    delta_u = MotorR.Kp * (MotorR.err - MotorR.err_last)
            + MotorR.Ki * MotorR.err
            + MotorR.Kd * (MotorR.err - 2 * MotorR.err_last + MotorR.err_last_last);

    MotorR.voltage += delta_u;

    // 更新误差
    MotorR.err_last_last = MotorR.err_last;
    MotorR.err_last  = MotorR.err;

    t = MotorR.voltage;
    return t;
}
// ...existing code...
int32_t deer_pid(float a,float b)
{
    int t;

    deer.Set      = b;
    deer.Actual   = a;
    deer.err      = deer.Actual - deer.Set;


    deer.integral = deer.integral + deer.err;

    deer.voltage = deer.Kp*deer.err
                + deer.Ki*deer.integral
                + deer.Kd*(deer.err-deer.err_last)
                + deer.Kout;

    deer.err_last = deer.err;

    t=deer.voltage;

    return t;
}
int32_t position_pid(float a,float b)
{
    int t;

    PositionPid.Set      = b;
    PositionPid.Actual   = a;
    PositionPid.err      = PositionPid.Actual - PositionPid.Set;


    PositionPid.integral = PositionPid.integral + PositionPid.err;

    PositionPid.voltage = PositionPid.Kp*PositionPid.err
                + PositionPid.Ki*PositionPid.integral
                + PositionPid.Kd*(PositionPid.err-PositionPid.err_last)
                + PositionPid.Kout;

    PositionPid.err_last = PositionPid.err;

    t=PositionPid.voltage;

    return t;
}


int32_t loca_pid(float a,float b)
{
    int t;

    loca.Set      = b;
    loca.Actual   = a;
    loca.err      = loca.Actual - loca.Set;


    loca.integral = loca.integral + loca.err;

    loca.voltage = loca.Kp*loca.err
                + loca.Ki*loca.integral
                + loca.Kd*(loca.err-loca.err_last)
                + loca.Kout;

    loca.err_last = loca.err;

    t=loca.voltage;

    return t;
}

